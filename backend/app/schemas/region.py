from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RegionBase(BaseModel):
    name: str
    zoom_level: Optional[int] = None

class RegionCreate(RegionBase):
    bbox: List[List[float]] # [[lat, lon], [lat, lon], ...]

class Region(RegionBase):
    id: int
    is_processed: bool
    created_at: datetime

    class Config:
        from_attributes = True
