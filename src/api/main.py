
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

from src.utils.logger import get_logger
from config.settings import settings

from src.database import init_db
from src.api.middleware import RateLimitMiddleware, get_allowed_origins

from src.api.routes import upload, jobs, clients

logger = get_logger("api")

app = FastAPI(
    title="Data Preprocessing API",
    description="Professional data preprocessing service for AI/ML companies",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate limiting middleware (add before CORS)
app.add_middleware(RateLimitMiddleware)

# CORS middleware with configurable origins
allowed_origins = get_allowed_origins()
# Allow all origins in development if CORS_ORIGINS is not set
if os.getenv("CORS_ORIGINS") is None and os.getenv("ENVIRONMENT", "development") == "development":
    allowed_origins = ["*"]
    logger.warning("CORS: Allowing all origins (development mode). Set CORS_ORIGINS env var for production.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(clients.router)
app.include_router(upload.router)
app.include_router(jobs.router)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Data Preprocessing API")
    settings.create_directories()
    
    init_db()
    logger.info("Database initialized")
    
    logger.info("API ready to accept requests")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Data Preprocessing API")


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "Data Preprocessing API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "clients": "/clients",
            "upload": "/upload",
            "jobs": "/jobs"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "settings": settings.get_config_dict()
    }
