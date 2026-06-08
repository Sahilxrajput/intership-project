from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import execute, health
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="CodeX Execution Engine",
    description="Secure, sandboxed code execution backend using Docker",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(execute.router, prefix="/api/v1", tags=["Execution"])


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 CodeX Execution Engine is starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 CodeX Execution Engine is shutting down...")
