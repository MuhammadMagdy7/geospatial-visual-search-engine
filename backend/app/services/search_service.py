"""
Main search orchestration service.

Dispatches search requests to the appropriate backend based on search mode:
- ai_detection: YOLOv8-OBB object detection (best for known object classes)
- visual_similarity: RemoteCLIP image-to-image search (experimental)
- text_search: RemoteCLIP text-to-image search (experimental)
"""

import logging
import time
from typing import List, Optional

import numpy as np
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from ..ml.embedding_service import get_embedding_service
from ..schemas.search import SearchResponse, SearchResult
from ..utils.geo import bbox_to_tile_centers
from .tile_service import (
    crop_tiles,
    fetch_satellite_image,
    get_or_compute_embeddings,
)
from .yolo_service import detect_objects

logger = logging.getLogger(__name__)


async def perform_search(
    bbox: List[List[float]],
    search_mode: str,
    db: AsyncSession,
    # AI Detection params
    target_class: str = "plane",
    confidence_threshold: float = 0.50,
    # RemoteCLIP params
    query_image: Optional[Image.Image] = None,
    query_text: Optional[str] = None,
    threshold: float = 0.55,
    tile_size: int = 120,
    zoom: int = 17,
    # Shared
    top_k: int = 50,
) -> SearchResponse:
    """
    Execute a search within a geographic region using the specified mode.

    Args:
        bbox: Bounding box coordinates [[lat, lon], ...]
        search_mode: One of "ai_detection", "visual_similarity", "text_search"
        db: Database session (used by RemoteCLIP modes for embedding cache)
        target_class: DOTA class name for AI Detection mode
        confidence_threshold: Min detection confidence for AI Detection mode
        query_image: PIL Image for visual_similarity mode
        query_text: Text query for text_search mode
        threshold: Min similarity score for RemoteCLIP modes
        tile_size: Tile size in pixels for RemoteCLIP modes
        zoom: Google Maps zoom level for RemoteCLIP modes
        top_k: Max number of results

    Returns:
        SearchResponse with ranked results
    """
    if search_mode == "ai_detection":
        return await _search_yolo(bbox, target_class, confidence_threshold, top_k)
    elif search_mode == "visual_similarity":
        return await _search_remoteclip_image(
            bbox, threshold, top_k, db, query_image, tile_size, zoom
        )
    elif search_mode == "text_search":
        return await _search_remoteclip_text(
            bbox, threshold, top_k, db, query_text, tile_size, zoom
        )
    else:
        raise ValueError(f"Unknown search mode: {search_mode}")


# ── AI Detection (YOLOv8-OBB) ────────────────────────────────────────────────


async def _search_yolo(
    bbox: List[List[float]],
    target_class: str,
    confidence_threshold: float,
    top_k: int,
) -> SearchResponse:
    """Run YOLOv8-OBB object detection on satellite imagery."""
    start_time = time.time()

    results, tiles_processed, warnings = await detect_objects(
        bbox=bbox,
        target_class=target_class,
        confidence_threshold=confidence_threshold,
        top_k=top_k,
    )

    elapsed_ms = int((time.time() - start_time) * 1000)
    logger.info(f"AI Detection complete: {len(results)} results in {elapsed_ms}ms")

    return SearchResponse(
        results=results,
        total=len(results),
        search_time_ms=elapsed_ms,
        tiles_processed=tiles_processed,
        tiles_from_cache=0,
        query_type="ai_detection",
        search_mode="ai_detection",
        warnings=warnings,
    )


# ── Visual Similarity (RemoteCLIP Image) ──────────────────────────────────────


async def _search_remoteclip_image(
    bbox: List[List[float]],
    threshold: float,
    top_k: int,
    db: AsyncSession,
    query_image: Optional[Image.Image],
    tile_size: int,
    zoom: int,
) -> SearchResponse:
    """Run RemoteCLIP image-to-image similarity search."""
    if query_image is None:
        raise ValueError("query_image is required for visual_similarity mode")

    start_time = time.time()
    embedding_service = get_embedding_service()

    # Generate query embedding from uploaded image
    query_embedding = await embedding_service.encode_image(query_image)

    # Run tile-based search
    results, tiles_info, cache_hits = await _run_tile_search(
        bbox, query_embedding, threshold, top_k, db, tile_size, zoom
    )

    elapsed_ms = int((time.time() - start_time) * 1000)
    logger.info(
        f"Visual similarity search complete: {len(results)} results in {elapsed_ms}ms "
        f"(tiles={len(tiles_info)}, cache_hits={cache_hits})"
    )

    return SearchResponse(
        results=results,
        total=len(results),
        search_time_ms=elapsed_ms,
        tiles_processed=len(tiles_info),
        tiles_from_cache=cache_hits,
        query_type="image",
        search_mode="visual_similarity",
    )


# ── Text Search (RemoteCLIP Text) ────────────────────────────────────────────


async def _search_remoteclip_text(
    bbox: List[List[float]],
    threshold: float,
    top_k: int,
    db: AsyncSession,
    query_text: Optional[str],
    tile_size: int,
    zoom: int,
) -> SearchResponse:
    """Run RemoteCLIP text-to-image similarity search."""
    if not query_text:
        raise ValueError("query_text is required for text_search mode")

    start_time = time.time()
    embedding_service = get_embedding_service()

    # Generate query embedding from text description
    query_embedding = await embedding_service.encode_text(query_text)

    # Run tile-based search
    results, tiles_info, cache_hits = await _run_tile_search(
        bbox, query_embedding, threshold, top_k, db, tile_size, zoom
    )

    elapsed_ms = int((time.time() - start_time) * 1000)
    logger.info(
        f"Text search complete: {len(results)} results in {elapsed_ms}ms "
        f"(tiles={len(tiles_info)}, cache_hits={cache_hits})"
    )

    return SearchResponse(
        results=results,
        total=len(results),
        search_time_ms=elapsed_ms,
        tiles_processed=len(tiles_info),
        tiles_from_cache=cache_hits,
        query_type="text",
        search_mode="text_search",
    )


# ── Shared RemoteCLIP tile pipeline ──────────────────────────────────────────


async def _run_tile_search(
    bbox: List[List[float]],
    query_embedding: np.ndarray,
    threshold: float,
    top_k: int,
    db: AsyncSession,
    tile_size: int,
    zoom: int,
) -> tuple:
    """
    Shared tile-based search logic used by both RemoteCLIP modes.

    Returns:
        (results, tiles_info, cache_hits)
    """
    # Compute tile grid for this bbox
    tiles_info = bbox_to_tile_centers(
        bbox, tile_size_px=tile_size, image_size_px=1280, zoom=zoom
    )
    logger.info(f"Generated {len(tiles_info)} tile positions")

    # Fetch the satellite image covering the bbox center
    lats = [p[0] for p in bbox]
    lons = [p[1] for p in bbox]
    center_lat = (min(lats) + max(lats)) / 2
    center_lon = (min(lons) + max(lons)) / 2

    satellite_image = await fetch_satellite_image(
        center_lat, center_lon, zoom=zoom
    )

    # Crop tiles from the satellite image
    tile_crops = await crop_tiles(satellite_image, tiles_info)

    # Get embeddings (from cache or compute new ones)
    tile_embeddings, cache_hits = await get_or_compute_embeddings(
        tile_crops, zoom, db
    )

    # Compute cosine similarity between query and all tiles
    results = []
    for tile_info, tile_emb in tile_embeddings:
        if tile_emb is None:
            continue

        similarity = float(np.dot(query_embedding, tile_emb))

        if similarity >= threshold:
            results.append(
                SearchResult(
                    id=hash(tile_info["tile_hash"]) % (10**9),
                    latitude=tile_info["center_lat"],
                    longitude=tile_info["center_lon"],
                    similarity=round(similarity, 4),
                    tile_size=tile_info["tile_size"],
                    google_maps_link=(
                        f"https://www.google.com/maps/search/?api=1"
                        f"&query={tile_info['center_lat']},{tile_info['center_lon']}"
                    ),
                    tile_x=tile_info["x"],
                    tile_y=tile_info["y"],
                )
            )

    # Sort by similarity descending
    results.sort(key=lambda r: r.similarity, reverse=True)
    results = results[:top_k]

    return results, tiles_info, cache_hits
