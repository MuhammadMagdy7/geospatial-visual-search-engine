"""Search router — handles image and text based visual search."""

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image
from io import BytesIO
from typing import Optional
import json

from ..database import get_db
from ..schemas.search import SearchResponse
from ..services.search_service import perform_search
from ..ml.embedding_service import get_embedding_service
from ..ml.exceptions import ModelNotLoadedError

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search(
    bbox: str = Form(..., description="JSON: [[lat, lon], [lat, lon], ...]"),
    query_image: Optional[UploadFile] = File(None),
    query_text: Optional[str] = Form(None),
    threshold: float = Form(0.55),
    top_k: int = Form(10),
    tile_size: int = Form(120),
    db: AsyncSession = Depends(get_db),
):
    """
    Search for visually similar objects within a geographic region.
    
    Provide EITHER query_image (upload a file) OR query_text (type a description).
    Both cannot be empty, and both cannot be provided simultaneously.
    """
    # Validate model is loaded
    service = get_embedding_service()
    if not service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="ML model not loaded. Check /api/v1/ml/health for details.",
        )

    # Validate query: exactly one of image or text
    has_image = query_image is not None and query_image.filename
    has_text = query_text is not None and query_text.strip()

    if not has_image and not has_text:
        raise HTTPException(
            status_code=400,
            detail="Either query_image or query_text must be provided.",
        )
    if has_image and has_text:
        raise HTTPException(
            status_code=400,
            detail="Provide only one of query_image or query_text, not both.",
        )

    # Parse bbox
    try:
        bbox_list = json.loads(bbox)
        if not isinstance(bbox_list, list) or len(bbox_list) < 2:
            raise ValueError("bbox must have at least 2 points")
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid bbox: {e}")

    # Process query
    pil_image = None
    text_query = None

    if has_image:
        try:
            contents = await query_image.read()
            pil_image = Image.open(BytesIO(contents)).convert("RGB")
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to read uploaded image: {e}"
            )
    else:
        text_query = query_text.strip()

    # Execute search
    try:
        return await perform_search(
            bbox=bbox_list,
            threshold=threshold,
            top_k=top_k,
            db=db,
            query_image=pil_image,
            query_text=text_query,
            tile_size=tile_size,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ModelNotLoadedError:
        raise HTTPException(status_code=503, detail="ML model not available.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")
