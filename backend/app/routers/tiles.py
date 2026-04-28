from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..schemas.tile import Tile
from ..models.tile import SatelliteTile
from sqlalchemy import select

router = APIRouter(prefix="/api/v1/tiles", tags=["tiles"])

@router.get("/{tile_id}", response_model=Tile)
async def get_tile(tile_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SatelliteTile).where(SatelliteTile.id == tile_id))
    tile = result.scalar_one_or_none()
    if not tile:
        raise HTTPException(status_code=404, detail="Tile not found")
    return tile
