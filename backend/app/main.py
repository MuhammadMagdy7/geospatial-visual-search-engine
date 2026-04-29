"""FastAPI application entrypoint with embedding service lifespan management."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import settings
from .middleware.cors import setup_cors
from .ml.embedding_service import EmbeddingService
from .routers import health, maps, ml_health, regions, search, tiles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On startup: initialize RemoteCLIP embedding service.
    On shutdown: nothing to clean up.
    
    If model loading fails, app starts in degraded mode (health endpoint
    returns model_loaded=False). This allows non-ML endpoints to keep working.
    """
    logger.info("=== Starting Geospatial Visual Search Engine ===")
    try:
        embedding_service = EmbeddingService.get_instance()
        embedding_service.init(device=settings.MODEL_DEVICE)
        logger.info("Startup complete. Model loaded successfully.")
    except Exception as e:
        logger.error(
            f"Failed to initialize embedding service: {e}. "
            f"App will start in DEGRADED MODE (search endpoints will fail).",
            exc_info=True,
        )

    yield

    logger.info("=== Shutting down ===")


app = FastAPI(
    title="Geospatial Visual Search Engine",
    description="API for searching visually similar objects in satellite imagery",
    version="0.2.0",
    lifespan=lifespan,
)

setup_cors(app)

app.include_router(health.router)
app.include_router(ml_health.router)
app.include_router(search.router)
app.include_router(tiles.router)
app.include_router(maps.router)
app.include_router(regions.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Geospatial Visual Search Engine API"}
