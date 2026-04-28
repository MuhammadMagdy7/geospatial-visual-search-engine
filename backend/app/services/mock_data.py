import random
import asyncio
from typing import List
from ..schemas.search import SearchResult

async def generate_mock_results(bbox: List[List[float]], count: int = 10) -> List[SearchResult]:
    """
    bbox is [[min_lat, min_lon], [max_lat, max_lon]] or similar
    """
    # Simple extraction of bounds from a 4-point rectangle or 2-point bbox
    lats = [p[0] for p in bbox]
    lons = [p[1] for p in bbox]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    results = []
    num_results = random.randint(5, 15)
    
    for i in range(num_results):
        lat = random.uniform(min_lat, max_lat)
        lon = random.uniform(min_lon, max_lon)
        score = random.uniform(0.45, 0.95)
        
        results.append(SearchResult(
            id=random.randint(1000, 9999),
            latitude=lat,
            longitude=lon,
            similarity=score,
            tile_size=120,
            google_maps_link=f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        ))
    
    # Sort by similarity descending
    results.sort(key=lambda x: x.similarity, reverse=True)
    
    # Simulate processing time asynchronously
    await asyncio.sleep(random.uniform(0.5, 2.0))
    
    return results
