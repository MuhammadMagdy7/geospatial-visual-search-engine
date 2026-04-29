"""Search request/response schemas."""

from pydantic import BaseModel
from typing import List, Optional


class SearchResult(BaseModel):
    id: int
    latitude: float
    longitude: float
    similarity: float
    tile_size: int
    google_maps_link: str
    tile_x: Optional[int] = None
    tile_y: Optional[int] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    search_time_ms: int
    tiles_processed: int = 0
    tiles_from_cache: int = 0
    query_type: str = "image"
