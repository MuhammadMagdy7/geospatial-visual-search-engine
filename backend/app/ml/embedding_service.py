"""
Singleton embedding service for RemoteCLIP.
"""

import asyncio
import logging
import time
from typing import List, Optional

import numpy as np
import torch
from PIL import Image

from .exceptions import EmbeddingFailedError, ModelNotLoadedError
from .model_loader import EMBEDDING_DIM, load_model

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Singleton service that wraps RemoteCLIP for image/text embedding."""

    _instance: Optional["EmbeddingService"] = None

    def __init__(self):
        self._model: Optional[torch.nn.Module] = None
        self._preprocess = None
        self._tokenizer = None
        self._device: str = "cpu"
        self._load_time: float = 0.0
        self._loaded: bool = False

    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def init(self, device: str = "cpu") -> None:
        """Synchronously load the model. Call once at app startup."""
        if self._loaded:
            logger.info("Embedding service already initialized, skipping.")
            return

        start = time.time()
        logger.info(f"Initializing RemoteCLIP embedding service on device '{device}'...")

        self._model, self._preprocess, self._tokenizer = load_model(device=device)
        self._device = device
        self._load_time = time.time() - start
        self._loaded = True

        logger.info(
            f"Embedding service ready in {self._load_time:.2f}s "
            f"(device={device}, embedding_dim={EMBEDDING_DIM})"
        )

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            raise ModelNotLoadedError(
                "Embedding service has not been initialized. "
                "Call EmbeddingService.get_instance().init() at app startup."
            )

    # ---------- Synchronous core inference ----------

    def _encode_image_sync(self, image: Image.Image) -> np.ndarray:
        self._ensure_loaded()
        try:
            tensor = self._preprocess(image.convert("RGB")).unsqueeze(0).to(self._device)
            with torch.no_grad():
                emb = self._model.encode_image(tensor)
                emb = emb / emb.norm(dim=-1, keepdim=True)
            return emb.cpu().numpy().squeeze(0).astype(np.float32)
        except Exception as e:
            raise EmbeddingFailedError(f"Image embedding failed: {e}") from e

    def _encode_images_batch_sync(self, images: List[Image.Image]) -> np.ndarray:
        self._ensure_loaded()
        if not images:
            return np.zeros((0, EMBEDDING_DIM), dtype=np.float32)
        try:
            tensors = torch.stack([
                self._preprocess(img.convert("RGB")) for img in images
            ]).to(self._device)
            with torch.no_grad():
                emb = self._model.encode_image(tensors)
                emb = emb / emb.norm(dim=-1, keepdim=True)
            return emb.cpu().numpy().astype(np.float32)
        except Exception as e:
            raise EmbeddingFailedError(f"Batch image embedding failed: {e}") from e

    def _encode_text_sync(self, text: str) -> np.ndarray:
        self._ensure_loaded()
        try:
            tokens = self._tokenizer([text]).to(self._device)
            with torch.no_grad():
                emb = self._model.encode_text(tokens)
                emb = emb / emb.norm(dim=-1, keepdim=True)
            return emb.cpu().numpy().squeeze(0).astype(np.float32)
        except Exception as e:
            raise EmbeddingFailedError(f"Text embedding failed: {e}") from e

    # ---------- Async public API ----------

    async def encode_image(self, image: Image.Image) -> np.ndarray:
        return await asyncio.to_thread(self._encode_image_sync, image)

    async def encode_images_batch(self, images: List[Image.Image]) -> np.ndarray:
        return await asyncio.to_thread(self._encode_images_batch_sync, images)

    async def encode_text(self, text: str) -> np.ndarray:
        return await asyncio.to_thread(self._encode_text_sync, text)

    # ---------- Introspection ----------

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def device(self) -> str:
        return self._device

    @property
    def load_time_seconds(self) -> float:
        return self._load_time

    @property
    def embedding_dim(self) -> int:
        return EMBEDDING_DIM


def get_embedding_service() -> EmbeddingService:
    """FastAPI dependency function for injecting the embedding service."""
    return EmbeddingService.get_instance()
