"""
YOLOv8-OBB object detection service for satellite imagery.

Uses YOLOv8s-OBB (trained on DOTA dataset) to detect oriented objects
such as planes, ships, storage tanks, vehicles, etc. in satellite images.

The model is loaded once (singleton) and reused across requests.
The .pt file (~22 MB) auto-downloads on first run via ultralytics.
"""

import asyncio
import logging
import math
import time
from io import BytesIO
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image

from ..schemas.search import SearchResult

logger = logging.getLogger(__name__)

# Constants for tiling
TILE_ZOOM = 17           # High resolution for accurate detection
TILE_OVERLAP = 0.10      # 10% overlap to catch objects on edges
MAX_TILES = 100          # allow large airports/regions

# Limit concurrent Google Maps API requests to prevent timeouts
MAPS_CONCURRENCY_LIMIT = 8
_maps_semaphore = asyncio.Semaphore(MAPS_CONCURRENCY_LIMIT)

# Alternative zoom levels for fallback
FALLBACK_ZOOM_TIERS = [
    {"max_tiles": 100, "zoom": 17},   # Best quality
    {"max_tiles": 200, "zoom": 16},   # Good quality
    {"max_tiles": 400, "zoom": 15},   # Acceptable quality
]

# Pre-computed lat span at each zoom (approximate)
TILE_SPAN_AT_ZOOM = {
    17: 0.005,
    16: 0.010,
    15: 0.020,
    14: 0.040,
}

# ── Singleton model ──────────────────────────────────────────────────────────

_model = None


def get_model():
    """Lazy-load YOLOv8s-OBB model (singleton). Auto-downloads on first call."""
    global _model
    if _model is None:
        from ultralytics import YOLO

        logger.info("Loading YOLOv8s-OBB model (first load may download ~22 MB)...")
        start = time.time()
        _model = YOLO("yolov8s-obb.pt")
        elapsed = time.time() - start
        logger.info(f"YOLOv8s-OBB loaded in {elapsed:.2f}s. Classes: {list(_model.names.values())}")
    return _model


def get_available_classes() -> List[str]:
    """Return all object classes the DOTA-trained model can detect."""
    model = get_model()
    return list(model.names.values())


# ── Coordinate conversion ────────────────────────────────────────────────────


def pixel_to_latlon(
    px: float,
    py: float,
    center_lat: float,
    center_lon: float,
    zoom: int,
    img_w: int,
    img_h: int,
) -> Tuple[float, float]:
    """
    More accurate Web Mercator conversion.
    Uses the same math as Google Maps JavaScript API.
    """
    TILE_SIZE = 256
    
    # World coordinates of the center
    sin_y = math.sin(math.radians(center_lat))
    sin_y = max(-0.9999, min(0.9999, sin_y))
    
    center_world_x = TILE_SIZE * (0.5 + center_lon / 360)
    center_world_y = TILE_SIZE * (0.5 - math.log((1 + sin_y) / (1 - sin_y)) / (4 * math.pi))
    
    # Pixel offset from center
    scale = 2 ** zoom
    
    # Convert pixel position to world coordinates
    pixel_offset_x = (px - img_w / 2) / scale
    pixel_offset_y = (py - img_h / 2) / scale
    
    world_x = center_world_x + pixel_offset_x
    world_y = center_world_y + pixel_offset_y
    
    # Convert world coordinates back to lat/lon
    lon = (world_x / TILE_SIZE - 0.5) * 360
    
    n = math.pi * (1 - 2 * world_y / TILE_SIZE)
    lat = math.degrees(math.atan(math.sinh(n)))
    
    return lat, lon


# ── Auto zoom selection ──────────────────────────────────────────────────────


def _select_zoom(bbox: List[List[float]]) -> int:
    """Auto-select Google Maps zoom level based on bbox size."""
    lats = [p[0] for p in bbox]
    lat_diff = max(lats) - min(lats)

    if lat_diff > 0.10:
        return 12
    elif lat_diff > 0.05:
        return 13
    elif lat_diff > 0.02:
        return 14
    elif lat_diff > 0.01:
        return 15
    else:
        return 16


def _is_inside_bbox(lat: float, lon: float, bbox: List[List[float]]) -> bool:
    """Check if a lat/lon point is strictly inside the user's bounding box."""
    lats = [p[0] for p in bbox]
    lons = [p[1] for p in bbox]
    return (min(lats) <= lat <= max(lats) and 
            min(lons) <= lon <= max(lons))


# ── Tiling Logic ─────────────────────────────────────────────────────────────

def calculate_tile_grid_adaptive(bbox: List[List[float]]) -> Tuple[Optional[List[Tuple[float, float]]], Optional[int]]:
    """
    Try zoom=17 first. If too many tiles, try zoom=16, then 15.
    Only fall back to single image if even zoom=14 is too many tiles.
    Returns (tile_centers, zoom) or (None, None) if fallback.
    """
    lats = [p[0] for p in bbox]
    lons = [p[1] for p in bbox]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    lat_diff = max_lat - min_lat
    lon_diff = max_lon - min_lon
    
    for tier in FALLBACK_ZOOM_TIERS:
        zoom = tier["zoom"]
        tile_span = TILE_SPAN_AT_ZOOM[zoom]
        
        tile_lat_span = tile_span * (1 - TILE_OVERLAP)
        tile_lon_span = tile_span * (1 - TILE_OVERLAP) / math.cos(math.radians((min_lat + max_lat) / 2))
        
        lat_steps = math.ceil(lat_diff / tile_lat_span)
        lon_steps = math.ceil(lon_diff / tile_lon_span)
        total = lat_steps * lon_steps
        
        if total <= tier["max_tiles"]:
            logger.info(f"Using zoom={zoom}, {total} tiles for bbox (lat_diff={lat_diff:.4f}, lon_diff={lon_diff:.4f})")
            
            tile_centers = []
            for i in range(lat_steps):
                for j in range(lon_steps):
                    center_lat = min_lat + (i + 0.5) * tile_lat_span
                    center_lon = min_lon + (j + 0.5) * tile_lon_span
                    tile_centers.append((center_lat, center_lon))
            return tile_centers, zoom
            
    logger.warning("BBox extremely large, single image fallback")
    return None, None


def _haversine_distance(lat1, lon1, lat2, lon2):
    """Distance in meters between two lat/lon points."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def _deduplicate_detections(detections: List[SearchResult], min_distance_meters=20):
    """
    Remove duplicate detections from overlapping tiles.
    Two detections within min_distance_meters are considered the same object.
    """
    if not detections:
        return []
    
    # Sort by confidence (keep highest confidence duplicate)
    detections.sort(key=lambda r: r.similarity, reverse=True)
    
    kept = []
    for det in detections:
        is_duplicate = False
        for existing in kept:
            distance = _haversine_distance(
                det.latitude, det.longitude,
                existing.latitude, existing.longitude
            )
            if distance < min_distance_meters:
                is_duplicate = True
                break
        if not is_duplicate:
            kept.append(det)
    
    return kept


async def _detect_single_tile(
    center_lat: float,
    center_lon: float,
    zoom: int,
    target_class: str,
    confidence_threshold: float,
) -> List[SearchResult]:
    """Run YOLO on a single specific tile."""
    from .maps_service import get_satellite_image

    logger.info(
        f"YOLO tile detection: center=({center_lat:.5f}, {center_lon:.5f}), "
        f"zoom={zoom}, target={target_class}, conf>={confidence_threshold}"
    )

    # Fetch satellite image (uses existing Google Maps proxy with caching)
    image_bytes = await get_satellite_image(center_lat, center_lon, zoom)
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    img_w, img_h = image.size
    
    # Scale=2 in Google Maps API means zoom level effectively increases by 1 for pixel math
    effective_zoom = zoom + 1
    
    # Run YOLOv8-OBB detection
    model = get_model()
    yolo_results = model.predict(
        image, conf=confidence_threshold, iou=0.45, verbose=False
    )

    results: List[SearchResult] = []
    det = yolo_results[0]
    
    if det.obb is not None and len(det.obb) > 0:
        for box in det.obb:
            cls_id = int(box.cls)
            class_name = model.names[cls_id]
            confidence = float(box.conf)

            if class_name != target_class:
                continue

            # OBB provides 4 corner points as xyxyxyxy
            xyxyxyxy = box.xyxyxyxy[0].cpu().numpy()
            center_x = float(xyxyxyxy[:, 0].mean())
            center_y = float(xyxyxyxy[:, 1].mean())

            # Convert pixel center to real geographic coordinates
            lat, lon = pixel_to_latlon(
                center_x, center_y, center_lat, center_lon, effective_zoom, img_w, img_h
            )

            # Compute object size in pixels (longest edge of the OBB)
            edge1 = np.linalg.norm(xyxyxyxy[1] - xyxyxyxy[0])
            edge2 = np.linalg.norm(xyxyxyxy[2] - xyxyxyxy[1])
            obj_size = int(max(edge1, edge2))

            results.append(
                SearchResult(
                    id=0,
                    latitude=round(lat, 6),
                    longitude=round(lon, 6),
                    similarity=round(confidence, 3),
                    tile_size=obj_size,
                    google_maps_link=f"https://www.google.com/maps/@{lat},{lon},19z",
                    detected_class=class_name,
                )
            )
            
    return results


async def _detect_single_tile_limited(
    center_lat: float,
    center_lon: float,
    zoom: int,
    target_class: str,
    confidence_threshold: float,
) -> List[SearchResult]:
    """Wrapper that limits concurrent Google Maps requests."""
    async with _maps_semaphore:
        return await _detect_single_tile(center_lat, center_lon, zoom, target_class, confidence_threshold)


async def process_tile_with_progress(
    idx: int, 
    total: int, 
    center_lat: float, 
    center_lon: float, 
    zoom: int, 
    target_class: str, 
    confidence_threshold: float
) -> List[SearchResult]:
    logger.info(f"Processing tile {idx}/{total} at ({center_lat:.4f}, {center_lon:.4f})")
    return await _detect_single_tile_limited(center_lat, center_lon, zoom, target_class, confidence_threshold)


async def _detect_single(
    bbox: List[List[float]],
    target_class: str,
    confidence_threshold: float,
    top_k: int
) -> List[SearchResult]:
    """Single image detection for small bboxes (legacy mode)."""
    lats = [p[0] for p in bbox]
    lons = [p[1] for p in bbox]
    center_lat = (min(lats) + max(lats)) / 2
    center_lon = (min(lons) + max(lons)) / 2
    
    # Auto-select zoom based on bbox size
    zoom = _select_zoom(bbox)
    
    results = await _detect_single_tile(
        center_lat, center_lon, zoom, target_class, confidence_threshold
    )
    
    # Filter to bbox
    filtered = [r for r in results if _is_inside_bbox(r.latitude, r.longitude, bbox)]
    logger.info(f"YOLO single detection complete: {len(filtered)} '{target_class}' objects found inside bbox")
    
    filtered.sort(key=lambda r: r.similarity, reverse=True)
    return filtered[:top_k]


async def _detect_tiled(
    bbox: List[List[float]],
    target_class: str,
    confidence_threshold: float,
    top_k: int
) -> Tuple[List[SearchResult], int, List[str]]:
    """Tile-based detection for large bboxes. Returns (results, tiles_processed, warnings)."""
    tile_centers, zoom = calculate_tile_grid_adaptive(bbox)
    
    if tile_centers is None:
        # Too many tiles - fall back to single image with warning
        logger.warning("BBox too large for tiling, using single zoom-out image")
        results = await _detect_single(bbox, target_class, confidence_threshold, top_k)
        return results, 1, ["BBox too large for tiling, using single zoom-out image"]
    
    logger.info(f"Tiling: processing {len(tile_centers)} tiles in parallel at zoom={zoom}")
    
    # Process all tiles in parallel
    tasks = [
        process_tile_with_progress(i + 1, len(tile_centers), lat, lon, zoom, target_class, confidence_threshold)
        for i, (lat, lon) in enumerate(tile_centers)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Flatten results and handle individual failures gracefully
    all_detections = []
    failed_count = 0
    for r in results:
        if isinstance(r, Exception):
            logger.warning(f"Tile failed: {r}")
            failed_count += 1
        else:
            all_detections.extend(r)
            
    warnings = []
    if failed_count > 0:
        warning_msg = f"{failed_count}/{len(tile_centers)} tiles failed, results may be incomplete"
        logger.warning(warning_msg)
        warnings.append(warning_msg)
    
    logger.info(f"Tiling: collected {len(all_detections)} raw detections")
    
    # Filter to bbox
    filtered = [
        d for d in all_detections
        if _is_inside_bbox(d.latitude, d.longitude, bbox)
    ]
    
    # Remove duplicates from overlap zones
    # Use different deduplication distances based on target class
    min_dist = 20
    if target_class == "ship":
        min_dist = 50
    elif target_class in ["small-vehicle", "large-vehicle"]:
        min_dist = 5
        
    deduped = _deduplicate_detections(filtered, min_distance_meters=min_dist)
    
    logger.info(f"Tiling: {len(filtered)} in bbox -> {len(deduped)} after dedup")
    
    # Sort and limit
    deduped.sort(key=lambda r: r.similarity, reverse=True)
    return deduped[:top_k], len(tile_centers), warnings


async def detect_with_tiling(
    bbox: List[List[float]],
    target_class: str,
    confidence_threshold: float,
    top_k: int
) -> Tuple[List[SearchResult], int, List[str]]:
    """
    Run YOLO detection on multiple tiles covering the bbox,
    then merge results and remove duplicates.
    Returns (results, tiles_processed, warnings).
    """
    # Decide: tiling or single image?
    lats = [p[0] for p in bbox]
    lons = [p[1] for p in bbox]
    lat_diff = max(lats) - min(lats)
    lon_diff = max(lons) - min(lons)
    
    if lat_diff > 0.008 or lon_diff > 0.008:
        # Large bbox -> use tiling
        return await _detect_tiled(bbox, target_class, confidence_threshold, top_k)
    else:
        # Small bbox -> single image (existing logic)
        results = await _detect_single(bbox, target_class, confidence_threshold, top_k)
        return results, 1, []


# ── Main entry point ─────────────────────────────────────────────────────────

async def detect_objects(
    bbox: List[List[float]],
    target_class: str = "plane",
    confidence_threshold: float = 0.50,
    top_k: int = 50,
) -> Tuple[List[SearchResult], int, List[str]]:
    """
    Detect objects in satellite imagery using YOLOv8-OBB.
    Automatically handles large bboxes by splitting them into tiles.
    """
    results, tiles_processed, warnings = await detect_with_tiling(bbox, target_class, confidence_threshold, top_k)
    
    # Re-index ids
    for i, r in enumerate(results):
        r.id = i + 1
        
    return results, tiles_processed, warnings
