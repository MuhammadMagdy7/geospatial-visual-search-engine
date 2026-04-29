"""
Loads the RemoteCLIP model with offline-first strategy.

RemoteCLIP is a CLIP variant fine-tuned on remote sensing imagery, which makes 
it ideal for satellite/aerial visual search. It's built on OpenCLIP's ViT-B/32 
architecture, so we instantiate the architecture from open_clip and load the 
RemoteCLIP weights on top.

Model details:
- Repo: chendelong/RemoteCLIP
- File: RemoteCLIP-ViT-B-32.pt
- Output dimension: 512
- Architecture: ViT-B/32
"""

import logging
import os
from pathlib import Path
from typing import Tuple

import open_clip
import torch
from huggingface_hub import hf_hub_download

from .exceptions import ModelLoadError

logger = logging.getLogger(__name__)

# Constants
HF_REPO_ID = "chendelong/RemoteCLIP"
HF_FILENAME = "RemoteCLIP-ViT-B-32.pt"
ARCHITECTURE = "ViT-B-32"
EMBEDDING_DIM = 512


def _get_cache_dir() -> Path:
    """Get the HuggingFace cache directory from env or default."""
    return Path(os.getenv("HF_HOME", "/data/hf_cache"))


def _find_cached_checkpoint() -> Path | None:
    """
    Search for an already-downloaded RemoteCLIP checkpoint in the cache.
    Returns the path if found, None otherwise.
    """
    cache_dir = _get_cache_dir()
    if not cache_dir.exists():
        return None

    for path in cache_dir.rglob(HF_FILENAME):
        if path.is_file() and path.stat().st_size > 1_000_000:
            logger.info(f"Found cached checkpoint: {path}")
            return path

    return None


def _download_checkpoint() -> Path:
    """Download the RemoteCLIP checkpoint from HuggingFace Hub."""
    cache_dir = _get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(
            f"Downloading RemoteCLIP checkpoint from {HF_REPO_ID} "
            f"to {cache_dir}..."
        )
        path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=HF_FILENAME,
            cache_dir=str(cache_dir),
        )
        logger.info(f"Download complete: {path}")
        return Path(path)
    except Exception as e:
        raise ModelLoadError(
            f"Failed to download {HF_FILENAME} from {HF_REPO_ID}. "
            f"This may be due to network restrictions. Error: {e}"
        ) from e


def get_or_download_checkpoint() -> Path:
    """Three-tier strategy: cache -> download -> error."""
    cached = _find_cached_checkpoint()
    if cached is not None:
        return cached

    logger.warning(
        f"RemoteCLIP checkpoint not found in cache. Attempting download. "
        f"This requires internet access on first run."
    )
    return _download_checkpoint()


def load_model(device: str = "cpu") -> Tuple[torch.nn.Module, callable, callable]:
    """Load RemoteCLIP model, preprocessor, and tokenizer."""
    checkpoint_path = get_or_download_checkpoint()

    try:
        logger.info(f"Building {ARCHITECTURE} architecture (no pretrained weights)...")
        model, _, preprocess = open_clip.create_model_and_transforms(
            ARCHITECTURE,
            pretrained=None,
        )
        tokenizer = open_clip.get_tokenizer(ARCHITECTURE)
    except Exception as e:
        raise ModelLoadError(
            f"Failed to build {ARCHITECTURE} architecture: {e}"
        ) from e

    try:
        logger.info(f"Loading RemoteCLIP weights from {checkpoint_path}...")
        checkpoint = torch.load(
            checkpoint_path,
            map_location="cpu",
            weights_only=False,
        )
        message = model.load_state_dict(checkpoint)
        logger.info(f"State dict load message: {message}")
    except Exception as e:
        raise ModelLoadError(
            f"Failed to load RemoteCLIP weights: {e}"
        ) from e

    try:
        model = model.to(device).eval()
        logger.info(f"Model ready on device: {device}")
    except Exception as e:
        raise ModelLoadError(
            f"Failed to move model to device '{device}': {e}"
        ) from e

    return model, preprocess, tokenizer
