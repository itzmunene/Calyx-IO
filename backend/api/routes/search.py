from typing import List

from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies import get_db
from backend.models import SearchResponse

router = APIRouter()


@router.get("/search", response_model=List[SearchResponse])
async def search_flowers(q: str, limit: int = 20, db=Depends(get_db)):
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Query too short")

    results = await db.text_search(q, limit)
    return [SearchResponse(**r) for r in results]