"""Geographic utility functions for tile coordinate conversion."""

import math
from typing import List, Tuple


def bbox_to_tile_centers(
    bbox: List[List[float]],
    tile_size_px: int = 120,
    image_size_px: int = 1280,
    zoom: int = 17,
) -> List[dict]:
    """
    Given a bounding box, compute a grid of tile centers within it.
    
    The approach:
    1. Fetch one large satellite image covering the bbox (from Google Maps).
    2. Split it into tile_size_px × tile_size_px tiles with overlap.
    3. Convert each tile's pixel position back to lat/lon coordinates.

    Args:
        bbox: [[lat1, lon1], [lat2, lon2], ...] defining the search region.
        tile_size_px: Size of each tile in pixels.
        image_size_px: Size of the fetched satellite image (scale=2 → 1280).
        zoom: Google Maps zoom level.

    Returns:
        List of dicts: [{x, y, center_lat, center_lon, tile_size}, ...]
    """
    lats = [p[0] for p in bbox]
    lons = [p[1] for p in bbox]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2

    # Compute meters-per-pixel at this zoom level
    # At zoom z, one pixel ≈ 156543.03 * cos(lat) / 2^z meters (at scale=1)
    # With scale=2, each pixel covers half that distance
    meters_per_pixel = 156543.03 * math.cos(math.radians(center_lat)) / (2 ** zoom) / 2

    # How many degrees per pixel
    lat_per_pixel = meters_per_pixel / 111320  # 1 degree lat ≈ 111320 meters
    lon_per_pixel = meters_per_pixel / (111320 * math.cos(math.radians(center_lat)))

    # Generate tile grid with 25% overlap
    overlap = 0.25
    step = int(tile_size_px * (1 - overlap))
    tiles = []

    for y in range(0, image_size_px - tile_size_px + 1, step):
        for x in range(0, image_size_px - tile_size_px + 1, step):
            # Center of this tile in pixel coordinates (relative to image center)
            tile_center_x = x + tile_size_px / 2 - image_size_px / 2
            tile_center_y = -(y + tile_size_px / 2 - image_size_px / 2)  # y-axis inverted

            # Convert pixel offset to geographic coordinates
            tile_lat = center_lat + tile_center_y * lat_per_pixel
            tile_lon = center_lon + tile_center_x * lon_per_pixel

            tiles.append({
                "x": x,
                "y": y,
                "center_lat": tile_lat,
                "center_lon": tile_lon,
                "tile_size": tile_size_px,
            })

    return tiles


def make_tile_hash(lat: float, lon: float, zoom: int, tile_size: int) -> str:
    """Create a deterministic hash key for a tile location."""
    import hashlib
    raw = f"{lat:.7f}_{lon:.7f}_{zoom}_{tile_size}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
