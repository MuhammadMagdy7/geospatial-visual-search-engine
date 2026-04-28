import httpx
import os
import hashlib
from ..config import settings

CACHE_DIR = "/data/cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR, exist_ok=True)

async def get_satellite_image(lat: float, lon: float, zoom: int, width: int = 640, height: int = 640):
    cache_key = hashlib.md5(f"{lat}_{lon}_{zoom}_{width}_{height}".encode()).hexdigest()
    file_path = os.path.join(CACHE_DIR, f"{cache_key}.png")

    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return f.read()

    url = "https://maps.googleapis.com/maps/api/staticmap"
    params = {
        "center": f"{lat},{lon}",
        "zoom": zoom,
        "size": f"{width}x{height}",
        "maptype": "satellite",
        "scale": 2,
        "key": settings.GOOGLE_MAPS_API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            image_data = response.content
            with open(file_path, "wb") as f:
                f.write(image_data)
            return image_data
        else:
            raise Exception(f"Failed to fetch image from Google Maps: {response.text}")
