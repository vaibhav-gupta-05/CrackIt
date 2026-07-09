import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from src.api.routers import jobs, resources


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Configure logging
    settings = get_settings()
    settings.configure_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("Initializing CrackIT API Backend...")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API Backend...")


app = FastAPI(
    title="CrackIT API",
    description="Backend for the AI-driven job aggregator.",
    version="0.1.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(jobs.router, prefix="/api")
app.include_router(resources.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "crackit-api"}
