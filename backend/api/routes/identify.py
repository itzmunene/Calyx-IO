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
    return await identify_flower_service(
        image=image,
        use_cache=use_cache,
        db=db,
        vision=vision,
    )