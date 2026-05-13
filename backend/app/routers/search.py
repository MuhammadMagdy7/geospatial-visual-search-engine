"""Search router — handles AI detection, image, and text based search."""

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
    search_mode: str = Form("ai_detection", description="ai_detection | visual_similarity | text_search"),
    query_image: Optional[UploadFile] = File(None),
    query_text: Optional[str] = Form(None),
    # AI Detection params
    target_class: str = Form("plane"),
    confidence_threshold: float = Form(0.50),
    # RemoteCLIP params
    threshold: float = Form(0.55),
    top_k: int = Form(50),
    tile_size: int = Form(120),
    db: AsyncSession = Depends(get_db),
):
    """
    Search for objects within a geographic region.

    Supports three modes:
    - ai_detection: YOLOv8-OBB object detection (only requires bbox + target_class)
    - visual_similarity: RemoteCLIP image search (requires bbox + query_image)
    - text_search: RemoteCLIP text search (requires bbox + query_text)
    """
    # Validate search mode
    valid_modes = ("ai_detection", "visual_similarity", "text_search")
    if search_mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid search_mode '{search_mode}'. Must be one of: {valid_modes}",
        )

    # Parse bbox
    try:
        bbox_list = json.loads(bbox)
        if not isinstance(bbox_list, list) or len(bbox_list) < 2:
            raise ValueError("bbox must have at least 2 points")
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid bbox: {e}")

    # ── Mode-specific validation ──────────────────────────────────────────

    pil_image = None
    text_query = None

    if search_mode == "ai_detection":
        # AI Detection only needs bbox + target_class (already provided via Form defaults)
        pass

    elif search_mode == "visual_similarity":
        # Validate RemoteCLIP model is loaded
        service = get_embedding_service()
        if not service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="ML model not loaded. Check /api/v1/ml/health for details.",
            )

        # Require query image
        has_image = query_image is not None and query_image.filename
        if not has_image:
            raise HTTPException(
                status_code=400,
                detail="query_image is required for visual_similarity mode.",
            )
        try:
            contents = await query_image.read()
            pil_image = Image.open(BytesIO(contents)).convert("RGB")
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to read uploaded image: {e}"
            )

    elif search_mode == "text_search":
        # Validate RemoteCLIP model is loaded
        service = get_embedding_service()
        if not service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="ML model not loaded. Check /api/v1/ml/health for details.",
            )

        # Require query text
        has_text = query_text is not None and query_text.strip()
        if not has_text:
            raise HTTPException(
                status_code=400,
                detail="query_text is required for text_search mode.",
            )
        text_query = query_text.strip()

    # ── Execute search ────────────────────────────────────────────────────

    try:
        return await perform_search(
            bbox=bbox_list,
            search_mode=search_mode,
            db=db,
            target_class=target_class,
            confidence_threshold=confidence_threshold,
            query_image=pil_image,
            query_text=text_query,
            threshold=threshold,
            top_k=top_k,
            tile_size=tile_size,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ModelNotLoadedError:
        raise HTTPException(status_code=503, detail="ML model not available.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")


@router.get("/classes")
async def list_classes():
    """Return all object classes the YOLOv8-OBB model can detect (DOTA dataset)."""
    try:
        from ..services.yolo_service import get_available_classes

        classes = get_available_classes()
        return {
            "classes": classes,
            "default": "plane",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to load YOLO model classes: {e}"
        )
