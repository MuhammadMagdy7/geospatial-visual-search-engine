from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TileBase(BaseModel):
    tile_hash: str
    tile_size_px: int
    zoom_level: int
    source: str = "google_maps"

class TileCreate(TileBase):
    pass

class Tile(TileBase):
    id: int
    image_path: Optional[str] = None
    similarity: Optional[float] = None
    captured_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
