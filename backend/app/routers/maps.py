from fastapi import APIRouter, Response
from ..services.maps_service import get_satellite_image

router = APIRouter(prefix="/api/v1/satellite", tags=["maps"])

@router.get("")
async def get_satellite(lat: float, lon: float, zoom: int, width: int = 640, height: int = 640):
    image_data = await get_satellite_image(lat, lon, zoom, width, height)
    return Response(content=image_data, media_type="image/png")
