# backend/api/routes/catalogue.py
from fastapi import APIRouter, Depends

from backend.config import settings
from backend.dependencies import get_db
from backend.models import SortBy

router = APIRouter()


@router.get("/catalogue")
async def get_catalogue(
    name: str | None = None,
    color: str | None = None,
    country: str | None = None,
    sort_by: SortBy = SortBy.alphabetical,
    page: int = 1,
    limit: int = 20,
    db=Depends(get_db),
):
    if limit > settings.MAX_CATALOGUE_LIMIT:
        limit = settings.MAX_CATALOGUE_LIMIT

    colors = color.split(",") if color else None

    return await db.get_catalogue(
        name_filter=name,
        color_filter=colors,
        country_filter=country,
        sort_by=sort_by.value,
        page=page,
        limit=limit,
    )


@router.get("/catalogue/filters")
async def get_available_filters(db=Depends(get_db)):
    filters = await db.get_available_filters()

    return {
        "colors": filters.get("colors", []),
        "countries": filters.get("countries", []),
        "sort_options": [
            {"value": "name", "label": "Alphabetical (A-Z)"},
            {"value": "popularity", "label": "Most Popular"},
            {"value": "recent", "label": "Recently Added"},
        ],
    }


@router.get("/catalogue/popular")
async def get_popular_flowers(limit: int = 10, db=Depends(get_db)):
    if limit > settings.MAX_POPULAR_LIMIT:
        limit = settings.MAX_POPULAR_LIMIT

    popular = await db.get_popular_flowers(limit)

    return {
        "popular_flowers": popular,
        "count": len(popular),
    }