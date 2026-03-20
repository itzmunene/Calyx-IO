from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies import get_db
from backend.models import SpeciesDetail

router = APIRouter()


@router.get("/species/{species_id}", response_model=SpeciesDetail)
async def get_species(species_id: str, db=Depends(get_db)):
    species = await db.get_species_by_id(species_id)

    if not species:
        raise HTTPException(status_code=404, detail="Species not found")

    return SpeciesDetail(**species)