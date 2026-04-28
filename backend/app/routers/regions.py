from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_db
from ..schemas.region import Region, RegionCreate
from ..models.region import SavedRegion
from sqlalchemy import select
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon

router = APIRouter(prefix="/api/v1/regions", tags=["regions"])

@router.post("", response_model=Region)
async def create_region(region_in: RegionCreate, db: AsyncSession = Depends(get_db)):
    # Convert bbox list to a shapely polygon
    poly = Polygon(region_in.bbox)
    
    db_region = SavedRegion(
        name=region_in.name,
        zoom_level=region_in.zoom_level,
        geom=from_shape(poly, srid=4326)
    )
    db.add(db_region)
    await db.commit()
    await db.refresh(db_region)
    return db_region

@router.get("", response_model=List[Region])
async def list_regions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SavedRegion))
    return result.scalars().all()
