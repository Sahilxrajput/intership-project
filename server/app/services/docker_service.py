import docker
import tempfile
import os
import time
from docker.errors import ContainerError, ImageNotFound, APIError
from app.models.schemas import Language, ExecutionStatus, ExecutionResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────
#  Language → Docker image + run command configuration
# ─────────────────────────────────────────────────────────────
LANGUAGE_CONFIG = {
    Language.PYTHON: {
        "image": "python:3.11-alpine",
        "filename": "solution.py",
        "run_cmd": "python solution.py",
        "compile_cmd": None,
    },
    Language.JAVASCRIPT: {
        "image": "node:18-alpine",
        "filename": "solution.js",
        "run_cmd": "node solution.js",
        "compile_cmd": None,
    },
    Language.JAVA: {
        "image": "openjdk:17-alpine",
        "filename": "Solution.java",
        "run_cmd": "java Solution",
        "compile_cmd": "javac Solution.java",
    },
    Language.CPP: {
        "image": "gcc:13-bookworm",
        "filename": "solution.cpp",
        "run_cmd": "./solution",
        "compile_cmd": "g++ -o solution solution.cpp",
    },
}

# Docker resource constraints — keeps containers lean & safe
DOCKER_RESOURCE_LIMITS = {
    "mem_limit": "128m",       # 128 MB RAM
    "memswap_limit": "128m",   # Disable swap
    "cpu_period": 100000,
    "cpu_quota": 50000,        # 50% of one CPU core
    "pids_limit": 50,          # Max 50 processes/threads
    "network_disabled": True,  # No internet inside container
    "read_only": False,        # We need to write the code file
}


class DockerExecutionService:
    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("✅ Docker client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Docker daemon: {e}")
            raise RuntimeError(
                "Docker daemon is not running or not accessible. "
                "Please start Docker and try again."
            ) from e

    def execute(self, language: Language, code: str, stdin: str = "", timeout: int = 10) -> ExecutionResponse:
        config = LANGUAGE_CONFIG[language]
        start_time = time.time()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Write user code to a temp file
            code_path = os.path.join(tmpdir, config["filename"])
            with open(code_path, "w") as f:
                f.write(code)

            # Compile step (Java / C++)
            if config["compile_cmd"]:
                compile_result = self._run_container(
                    image=config["image"],
                    command=f"sh -c 'cd /code && {config['compile_cmd']}'",
                    tmpdir=tmpdir,
                    stdin_data="",
                    timeout=30,  # Compilation can take longer
                )
                if compile_result["exit_code"] != 0:
                    return ExecutionResponse(
                        status=ExecutionStatus.COMPILE_ERROR,
                        stdout="",
                        stderr=compile_result["output"],
                        exit_code=compile_result["exit_code"],
                        execution_time_ms=(time.time() - start_time) * 1000,
                        language=language,
                        message="Compilation failed",
                    )

            # Run step
            run_result = self._run_container(
                image=config["image"],
                command=f"sh -c 'cd /code && echo {repr(stdin)} | {config['run_cmd']}'",
                tmpdir=tmpdir,
                stdin_data=stdin,
                timeout=timeout,
            )

        execution_time_ms = (time.time() - start_time) * 1000

        if run_result["timed_out"]:
            return ExecutionResponse(
                status=ExecutionStatus.TIMEOUT,
                stdout="",
                stderr=f"Execution timed out after {timeout} seconds",
                exit_code=124,
                execution_time_ms=execution_time_ms,
                language=language,
                message=f"Program exceeded {timeout}s time limit",
            )

        status = ExecutionStatus.SUCCESS if run_result["exit_code"] == 0 else ExecutionStatus.ERROR

        return ExecutionResponse(
            status=status,
            stdout=run_result["stdout"],
            stderr=run_result["stderr"],
            exit_code=run_result["exit_code"],
            execution_time_ms=execution_time_ms,
            language=language,
        )

    def _run_container(
        self,
        image: str,
        command: str,
        tmpdir: str,
        stdin_data: str,
        timeout: int,
    ) -> dict:
        container = None
        try:
            logger.debug(f"🐳 Pulling/using image: {image}")
            container = self.client.containers.run(
                image=image,
                command=command,
                volumes={tmpdir: {"bind": "/code", "mode": "rw"}},
                detach=True,
                stdout=True,
                stderr=True,
                **DOCKER_RESOURCE_LIMITS,
            )

            # Wait with timeout
            try:
                result = container.wait(timeout=timeout)
                exit_code = result.get("StatusCode", 1)
                logs = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
                err_logs = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")
                return {
                    "stdout": logs.strip(),
                    "stderr": err_logs.strip(),
                    "exit_code": exit_code,
                    "timed_out": False,
                    "output": logs + err_logs,  # Combined for compile errors
                }
            except Exception:
                # Timeout — kill the container
                container.kill()
                return {
                    "stdout": "",
                    "stderr": "",
                    "exit_code": 124,
                    "timed_out": True,
                    "output": "",
                }

        except ImageNotFound:
            logger.error(f"Docker image not found: {image}")
            return {"stdout": "", "stderr": f"Docker image '{image}' not found", "exit_code": 1, "timed_out": False, "output": ""}
        except APIError as e:
            logger.error(f"Docker API error: {e}")
            return {"stdout": "", "stderr": f"Docker error: {str(e)}", "exit_code": 1, "timed_out": False, "output": ""}
        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
