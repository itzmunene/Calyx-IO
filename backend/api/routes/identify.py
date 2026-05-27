from unittest import result

from fastapi import APIRouter, Depends, File, Request, UploadFile

from backend.dependencies import get_db, get_vision
from backend.models import IdentificationResponse
from backend.services.identify_service import identify_flower_service

router = APIRouter()

@router.post("/identify", response_model=IdentificationResponse)
async def identify_flower(
    request: Request,
    image: UploadFile = File(...),
    use_cache: bool = True,
    db=Depends(get_db),
    vision=Depends(get_vision),
):
    result = await identify_flower_service(
        image=image,
        use_cache=request.query_params.get("use_cache", True),
        db=db,
        vision=vision,
        request=request,
    )

    return result

print("🚀 ROUTE RESULT:", result)