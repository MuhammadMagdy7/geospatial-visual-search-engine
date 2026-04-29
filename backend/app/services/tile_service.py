"""
Tile fetching, caching, and embedding service.

Handles the lifecycle of satellite image tiles:
1. Fetch a large satellite image from Google Maps (or cache).
2. Crop it into tiles.
3. Compute embeddings (batch) via RemoteCLIP.
4. Cache embeddings in PostgreSQL for subsequent searches.
"""

import hashlib
import logging
import os
from io import BytesIO
from typing import List, Tuple, Optional

import httpx
import numpy as np
from PIL import Image
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..ml.embedding_service import get_embedding_service
from ..models.tile import SatelliteTile
from ..utils.geo import bbox_to_tile_centers, make_tile_hash

logger = logging.getLogger(__name__)

# Filesystem cache for satellite images
TILE_CACHE_DIR = "/data/cache"
os.makedirs(TILE_CACHE_DIR, exist_ok=True)

# Batch size for embedding computation
EMBEDDING_BATCH_SIZE = 8


async def fetch_satellite_image(
    lat: float, lon: float, zoom: int = 17,
    width: int = 640, height: int = 640, scale: int = 2,
) -> Image.Image:
    """
    Fetch a satellite image from Google Maps Static API.
    Uses filesystem cache to avoid duplicate API calls.
    
    Returns a PIL Image of size (width*scale, height*scale).
    """
    cache_key = hashlib.md5(
        f"{lat:.7f}_{lon:.7f}_{zoom}_{width}_{height}_{scale}".encode()
    ).hexdigest()
    file_path = os.path.join(TILE_CACHE_DIR, f"{cache_key}.png")

    # Check filesystem cache first
    if os.path.exists(file_path):
        logger.debug(f"Satellite image cache hit: {cache_key}")
        return Image.open(file_path).convert("RGB")

    # Fetch from Google Maps
    if not settings.GOOGLE_MAPS_API_KEY:
        raise ValueError(
            "GOOGLE_MAPS_API_KEY is not set. Cannot fetch satellite imagery."
        )

    url = "https://maps.googleapis.com/maps/api/staticmap"
    params = {
        "center": f"{lat},{lon}",
        "zoom": zoom,
        "size": f"{width}x{height}",
        "scale": scale,
        "maptype": "satellite",
        "key": settings.GOOGLE_MAPS_API_KEY,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            raise RuntimeError(
                f"Google Maps API error (HTTP {response.status_code}): "
                f"{response.text[:200]}"
            )

        # Verify we got an actual image
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            raise RuntimeError(
                f"Google Maps returned non-image response: {content_type}. "
                f"Body: {response.text[:200]}"
            )

    # Save to cache
    with open(file_path, "wb") as f:
        f.write(response.content)

    logger.info(f"Satellite image fetched and cached: {cache_key}")
    return Image.open(BytesIO(response.content)).convert("RGB")


async def crop_tiles(
    image: Image.Image, tiles_info: List[dict]
) -> List[Tuple[dict, Image.Image]]:
    """Crop tile regions from the large satellite image."""
    results = []
    for info in tiles_info:
        x, y, size = info["x"], info["y"], info["tile_size"]
        tile_img = image.crop((x, y, x + size, y + size))
        results.append((info, tile_img))
    return results


async def get_or_compute_embeddings(
    tiles: List[Tuple[dict, Image.Image]],
    zoom: int,
    db: AsyncSession,
) -> Tuple[List[Tuple[dict, np.ndarray]], int]:
    """
    For each tile, check if embedding exists in DB (cache hit).
    For cache misses, compute embeddings in batches and store in DB.
    
    Returns tuple of (list of (tile_info, embedding) tuples, cache_hits count).
    """
    embedding_service = get_embedding_service()
    results = []
    tiles_to_embed = []  # (index_in_results, tile_info, tile_image)
    cache_hits = 0

    # Phase 1: Check DB cache for existing embeddings
    for tile_info, tile_img in tiles:
        tile_hash = make_tile_hash(
            tile_info["center_lat"],
            tile_info["center_lon"],
            zoom,
            tile_info["tile_size"],
        )
        tile_info["tile_hash"] = tile_hash

        # Query DB for cached embedding
        stmt = select(SatelliteTile.embedding).where(
            SatelliteTile.tile_hash == tile_hash
        )
        result = await db.execute(stmt)
        cached_emb = result.scalar_one_or_none()

        if cached_emb is not None:
            # Cache hit — use stored embedding
            results.append((tile_info, np.array(cached_emb, dtype=np.float32)))
            cache_hits += 1
        else:
            # Cache miss — mark for batch embedding
            idx = len(results)
            results.append((tile_info, None))  # placeholder
            tiles_to_embed.append((idx, tile_info, tile_img))

    logger.info(
        f"Embedding cache: {cache_hits} hits, {len(tiles_to_embed)} misses"
    )

    # Phase 2: Batch embed cache misses
    if tiles_to_embed:
        all_images = [img for _, _, img in tiles_to_embed]
        all_embeddings = []

        # Process in batches of EMBEDDING_BATCH_SIZE
        for i in range(0, len(all_images), EMBEDDING_BATCH_SIZE):
            batch = all_images[i : i + EMBEDDING_BATCH_SIZE]
            batch_emb = await embedding_service.encode_images_batch(batch)
            all_embeddings.append(batch_emb)

        # Concatenate all batch results
        all_embeddings = np.vstack(all_embeddings)

        # Phase 3: Store new embeddings in DB and fill results
        for j, (idx, tile_info, tile_img) in enumerate(tiles_to_embed):
            emb = all_embeddings[j]
            results[idx] = (tile_info, emb)

            # Store in DB for future cache hits
            new_tile = SatelliteTile(
                tile_hash=tile_info["tile_hash"],
                geom=f"SRID=4326;POLYGON(({tile_info['center_lon'] - 0.001} {tile_info['center_lat'] - 0.001}, "
                     f"{tile_info['center_lon'] + 0.001} {tile_info['center_lat'] - 0.001}, "
                     f"{tile_info['center_lon'] + 0.001} {tile_info['center_lat'] + 0.001}, "
                     f"{tile_info['center_lon'] - 0.001} {tile_info['center_lat'] + 0.001}, "
                     f"{tile_info['center_lon'] - 0.001} {tile_info['center_lat'] - 0.001}))",
                center_point=f"SRID=4326;POINT({tile_info['center_lon']} {tile_info['center_lat']})",
                embedding=emb.tolist(),
                tile_size_px=tile_info["tile_size"],
                zoom_level=17,
                source="google_maps",
            )
            db.add(new_tile)

        await db.commit()
        logger.info(f"Stored {len(tiles_to_embed)} new tile embeddings in DB")

    return results, cache_hits
