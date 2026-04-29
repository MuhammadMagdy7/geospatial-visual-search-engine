"""
Main search orchestration service.

Coordinates tile fetching, embedding, and similarity ranking.
Supports both image and text queries via RemoteCLIP.
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

logger = logging.getLogger(__name__)


async def perform_search(
    bbox: List[List[float]],
    threshold: float,
    top_k: int,
    db: AsyncSession,
    query_image: Optional[Image.Image] = None,
    query_text: Optional[str] = None,
    tile_size: int = 120,
    zoom: int = 17,
) -> SearchResponse:
    """
    Execute a visual similarity search within a geographic region.

    Args:
        bbox: Bounding box coordinates [[lat, lon], ...]
        threshold: Minimum similarity score (0-1)
        top_k: Maximum number of results to return
        db: Database session
        query_image: PIL Image to search for (mutually exclusive with query_text)
        query_text: Text description to search for (mutually exclusive with query_image)
        tile_size: Size of tiles in pixels
        zoom: Google Maps zoom level

    Returns:
        SearchResponse with ranked results
    """
    start_time = time.time()
    embedding_service = get_embedding_service()

    # Step 1: Generate query embedding
    logger.info(f"Search started: bbox={bbox}, threshold={threshold}, top_k={top_k}")
    if query_image is not None:
        query_embedding = await embedding_service.encode_image(query_image)
        query_type = "image"
    elif query_text is not None:
        query_embedding = await embedding_service.encode_text(query_text)
        query_type = "text"
    else:
        raise ValueError("Either query_image or query_text must be provided")

    # Step 2: Compute tile grid for this bbox
    tiles_info = bbox_to_tile_centers(
        bbox, tile_size_px=tile_size, image_size_px=1280, zoom=zoom
    )
    logger.info(f"Generated {len(tiles_info)} tile positions")

    # Step 3: Fetch the satellite image covering the bbox center
    lats = [p[0] for p in bbox]
    lons = [p[1] for p in bbox]
    center_lat = (min(lats) + max(lats)) / 2
    center_lon = (min(lons) + max(lons)) / 2

    satellite_image = await fetch_satellite_image(
        center_lat, center_lon, zoom=zoom
    )

    # Step 4: Crop tiles from the satellite image
    tile_crops = await crop_tiles(satellite_image, tiles_info)

    # Step 5: Get embeddings (from cache or compute new ones)
    tile_embeddings, cache_hits = await get_or_compute_embeddings(tile_crops, zoom, db)

    # Step 6: Compute cosine similarity between query and all tiles
    # Since both query and tile embeddings are L2-normalized,
    # cosine similarity = dot product
    results = []

    for tile_info, tile_emb in tile_embeddings:
        if tile_emb is None:
            continue

        similarity = float(np.dot(query_embedding, tile_emb))

        if similarity >= threshold:
            results.append(
                SearchResult(
                    id=hash(tile_info["tile_hash"]) % (10**9),  # temp ID from hash
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

    elapsed_ms = int((time.time() - start_time) * 1000)
    logger.info(
        f"Search complete: {len(results)} results in {elapsed_ms}ms "
        f"(tiles={len(tiles_info)}, query_type={query_type})"
    )

    return SearchResponse(
        results=results,
        total=len(results),
        search_time_ms=elapsed_ms,
        tiles_processed=len(tiles_info),
        tiles_from_cache=cache_hits,
        query_type=query_type,
    )
