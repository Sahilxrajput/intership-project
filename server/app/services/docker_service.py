import docker
import tempfile
import os
import time

from docker.errors import ImageNotFound, APIError

from app.models.schemas import (
    Language,
    ExecutionStatus,
    ExecutionResponse,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────
# Language Configuration
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
        "image": "eclipse-temurin:17-jdk",
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

# ─────────────────────────────────────────────────────────────
# Docker Resource Limits
# ─────────────────────────────────────────────────────────────
DOCKER_RESOURCE_LIMITS = {
    "mem_limit": "128m",
    "memswap_limit": "128m",
    "cpu_period": 100000,
    "cpu_quota": 50000,
    "pids_limit": 50,
    "network_disabled": True,
    "read_only": False,
}


class DockerExecutionService:
    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Docker daemon: {e}")
            raise RuntimeError("Docker daemon is not running or not accessible.") from e

    def execute(
        self,
        language: Language,
        code: str,
        stdin: str = "",
        timeout: int = 10,
    ) -> ExecutionResponse:

        config = LANGUAGE_CONFIG[language]
        start_time = time.time()

        with tempfile.TemporaryDirectory() as tmpdir:

            # Write source file
            code_path = os.path.join(tmpdir, config["filename"])

            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code)

            logger.info(f"Temp directory: {tmpdir}")
            logger.info(f"Written file: {code_path}")

            # ─────────────────────────────
            # Compile Step (Java / C++)
            # ─────────────────────────────
            if config["compile_cmd"]:

                compile_command = f"cd /code && {config['compile_cmd']}"

                logger.info(f"Compile command: {compile_command}")

                compile_result = self._run_container(
                    image=config["image"],
                    command=compile_command,
                    tmpdir=tmpdir,
                    stdin_data="",
                    timeout=30,
                )

                logger.info(f"Compile result: {compile_result}")

                if compile_result["exit_code"] != 0:
                    return ExecutionResponse(
                        status=ExecutionStatus.COMPILE_ERROR,
                        stdout=compile_result["stdout"],
                        stderr=compile_result["stderr"],
                        exit_code=compile_result["exit_code"],
                        execution_time_ms=(time.time() - start_time) * 1000,
                        language=language,
                        message="Compilation failed",
                    )

            # ─────────────────────────────
            # Run Step
            # ─────────────────────────────
            escaped_input = repr(stdin)

            run_command = (
                f"cd /code && " f"printf '%s' {escaped_input} | " f"{config['run_cmd']}"
            )

            logger.info(f"Run command: {run_command}")

            run_result = self._run_container(
                image=config["image"],
                command=run_command,
                tmpdir=tmpdir,
                stdin_data=stdin,
                timeout=timeout,
            )

            logger.info(f"Run result: {run_result}")

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

        status = (
            ExecutionStatus.SUCCESS
            if run_result["exit_code"] == 0
            else ExecutionStatus.ERROR
        )

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

            logger.info(f"Starting container with image={image}")

            logger.info(f"Container command={command}")

            container = self.client.containers.run(
                image=image,
                command=["sh", "-c", command],
                working_dir="/code",
                volumes={
                    tmpdir: {
                        "bind": "/code",
                        "mode": "rw",
                    }
                },
                detach=True,
                stdout=True,
                stderr=True,
                **DOCKER_RESOURCE_LIMITS,
            )

            try:
                result = container.wait(timeout=timeout)

                exit_code = result.get(
                    "StatusCode",
                    1,
                )

                stdout = container.logs(
                    stdout=True,
                    stderr=False,
                ).decode(
                    "utf-8",
                    errors="replace",
                )

                stderr = container.logs(
                    stdout=False,
                    stderr=True,
                ).decode(
                    "utf-8",
                    errors="replace",
                )

                logger.info(
                    f"Container finished "
                    f"exit_code={exit_code} "
                    f"stdout={stdout} "
                    f"stderr={stderr}"
                )

                return {
                    "stdout": stdout.strip(),
                    "stderr": stderr.strip(),
                    "exit_code": exit_code,
                    "timed_out": False,
                    "output": (stdout + stderr).strip(),
                }

            except Exception as e:

                logger.error(f"Container timeout/error: {e}")

                try:
                    container.kill()
                except Exception:
                    pass

                return {
                    "stdout": "",
                    "stderr": "",
                    "exit_code": 124,
                    "timed_out": True,
                    "output": "",
                }

        except ImageNotFound:

            logger.error(f"Docker image not found: {image}")

            return {
                "stdout": "",
                "stderr": (f"Docker image '{image}' not found"),
                "exit_code": 1,
                "timed_out": False,
                "output": "",
            }

        except APIError as e:

            logger.error(f"Docker API error: {e}")

            return {
                "stdout": "",
                "stderr": f"Docker error: {str(e)}",
                "exit_code": 1,
                "timed_out": False,
                "output": "",
            }

        except Exception as e:

            logger.exception(f"Unexpected container error: {e}")

            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "timed_out": False,
                "output": str(e),
            }

        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
