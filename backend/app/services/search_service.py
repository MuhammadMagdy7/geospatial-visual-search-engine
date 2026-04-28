import time
from typing import List
from .mock_data import generate_mock_results
from ..schemas.search import SearchResponse

async def perform_search(bbox: List[List[float]], threshold: float, top_k: int) -> SearchResponse:
    start_time = time.time()
    
    # In the future, this will involve DINOv2 and PostGIS/pgvector
    results = await generate_mock_results(bbox)
    
    # Filter by threshold (mock data already does some of this but let's be explicit)
    results = [r for r in results if r.similarity >= threshold][:top_k]
    
    end_time = time.time()
    search_time_ms = int((end_time - start_time) * 1000)
    
    return SearchResponse(
        results=results,
        total=len(results),
        search_time_ms=search_time_ms
    )
