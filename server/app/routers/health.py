from fastapi import APIRouter
import docker
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health", summary="Health check")
async def health_check():
    """Returns the health status of the API and Docker daemon."""
    docker_status = "unavailable"
    try:
        client = docker.from_env()
        client.ping()
        docker_status = "healthy"
    except Exception as e:
        logger.warning(f"Docker ping failed: {e}")
        docker_status = "unhealthy"

    return {
        "status": "ok",
        "service": "CodeX Execution Engine",
        "version": "1.0.0",
        "docker": docker_status,
    }
