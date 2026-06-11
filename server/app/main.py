import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import execute, health, files
from app.utils.logger import get_logger
from contextlib import asynccontextmanager
from app.utils.cleanup import cleanup_worker

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    threading.Thread(
        target=cleanup_worker,
        daemon=True,
    ).start()

    yield


app = FastAPI(
    title="CodeX Execution Engine",
    lifespan=lifespan,
    description="Secure, sandboxed code execution backend using Docker",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CLIENT_URL],  # Tighten in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(execute.router, prefix="/api/v1", tags=["Execution"])
app.include_router(files.router, prefix="/api/v1", tags=["Files"])


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 CodeX Execution Engine is starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 CodeX Execution Engine is shutting down...")
