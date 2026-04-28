from pydantic import BaseModel
from typing import List, Optional

class SearchResult(BaseModel):
    id: int
    latitude: float
    longitude: float
    similarity: float
    tile_size: int
    google_maps_link: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    search_time_ms: int

class SearchRequest(BaseModel):
    # bbox: List[List[float]] # [[lat, lon], ...]
    threshold: float = 0.55
    top_k: int = 10
