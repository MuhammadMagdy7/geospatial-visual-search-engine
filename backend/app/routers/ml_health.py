"""Health check endpoint for the ML/embedding service."""

from fastapi import APIRouter, Depends

from ..ml.embedding_service import EmbeddingService, get_embedding_service
from ..ml.model_loader import EMBEDDING_DIM

router = APIRouter(prefix="/api/v1/ml", tags=["ml"])


@router.get("/health")
async def ml_health(
    service: EmbeddingService = Depends(get_embedding_service),
) -> dict:
    """Return the current state of the embedding service."""
    return {
        "model_loaded": service.is_loaded,
        "model_name": "RemoteCLIP-ViT-B-32",
        "architecture": "ViT-B-32 (OpenCLIP)",
        "device": service.device if service.is_loaded else None,
        "embedding_dim": EMBEDDING_DIM,
        "load_time_seconds": round(service.load_time_seconds, 2) if service.is_loaded else None,
    }
