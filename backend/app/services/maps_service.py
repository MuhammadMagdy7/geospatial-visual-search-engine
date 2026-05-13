import httpx
import os
import hashlib
from ..config import settings

CACHE_DIR = "/data/cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR, exist_ok=True)

from tenacity import retry, stop_after_attempt, wait_exponential

_http_client = None

def get_http_client():
    global _http_client
    if _http_client is None:
        limits = httpx.Limits(
            max_keepalive_connections=20,
            max_connections=30,
            keepalive_expiry=30.0
        )
        timeout = httpx.Timeout(30.0, connect=10.0)
        _http_client = httpx.AsyncClient(limits=limits, timeout=timeout)
    return _http_client

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    reraise=True
)
async def fetch_with_retry(url, params):
    client = get_http_client()
    response = await client.get(url, params=params)
    response.raise_for_status()
    return response.content

async def get_satellite_image(lat: float, lon: float, zoom: int, width: int = 640, height: int = 640):
    cache_key = hashlib.md5(f"{lat}_{lon}_{zoom}_{width}_{height}".encode()).hexdigest()
    file_path = os.path.join(CACHE_DIR, f"{cache_key}.png")

    if os.path.exists(file_path):
        import time
        age_hours = (time.time() - os.path.getmtime(file_path)) / 3600
        if age_hours < 24:
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

    try:
        image_data = await fetch_with_retry(url, params)
        with open(file_path, "wb") as f:
            f.write(image_data)
        return image_data
    except Exception as e:
        raise Exception(f"Failed to fetch image from Google Maps: {e}")
