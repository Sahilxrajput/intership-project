from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import ExecutionRequest, ExecutionResponse
from app.services.docker_service import DockerExecutionService
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


def get_docker_service() -> DockerExecutionService:
    """Dependency injection for DockerExecutionService."""
    return DockerExecutionService()


@router.post(
    "/execute",
    response_model=ExecutionResponse,
    summary="Execute code in an isolated Docker container",
    response_description="Execution result with stdout, stderr, and metadata",
)
async def execute_code(
    request: ExecutionRequest,
    service: DockerExecutionService = Depends(get_docker_service),
):
    """
    Execute user-submitted code securely inside a Docker container.

    - **language**: One of `python`, `javascript`, `java`, `cpp`
    - **code**: The source code to run (max 10,000 characters)
    - **stdin**: Optional standard input to pipe into the program
    - **timeout**: Max seconds to allow (1–30, default 10)
    """
    logger.info(f"📥 Execution request | language={request.language} | timeout={request.timeout}s")

    try:
        result = service.execute(
            language=request.language,
            code=request.code,
            stdin=request.stdin or "",
            timeout=request.timeout or 10,
        )
        logger.info(f"✅ Execution complete | status={result.status} | time={result.execution_time_ms:.1f}ms")
        return result
    except RuntimeError as e:
        logger.error(f"❌ Docker runtime error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected error during execution: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during code execution")
