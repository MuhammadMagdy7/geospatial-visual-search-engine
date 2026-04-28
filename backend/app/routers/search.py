from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List, Optional
import json
from ..schemas.search import SearchResponse
from ..services.search_service import perform_search

router = APIRouter(prefix="/api/v1/search", tags=["search"])

@router.post("", response_model=SearchResponse)
async def search(
    query_image: UploadFile = File(...),
    bbox: str = Form(...), # Expecting JSON string: [[lat, lon], ...]
    threshold: float = Form(0.55),
    top_k: int = Form(10)
):
    bbox_list = json.loads(bbox)
    # We ignore the actual image content for now as we are mocking
    return await perform_search(bbox_list, threshold, top_k)
