# backend/api/routes/feedback.py
from fastapi import APIRouter, Depends

from backend.dependencies import get_db
from backend.models import FeedbackRequest

router = APIRouter()


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest, db=Depends(get_db)):
    await db.save_feedback(
        identification_id=request.identification_id,
        is_correct=request.is_correct,
        correct_species_id=request.correct_species_id,
        notes=request.notes,
    )

    return {"status": "success", "message": "Feedback recorded"}


@router.get("/stats")
async def get_stats(db=Depends(get_db)):
    return await db.get_stats()