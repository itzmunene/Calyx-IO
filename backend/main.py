# backend/main.py
import os
import time
import io
import hashlib
from backend.models import SortBy
from backend.models import FilterParams

from typing import Optional, List
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel

from backend.database import SupabaseClient
from backend.vision import VisionModel
from backend.models import (
    IdentificationResponse,
    SearchResponse,
    SpeciesDetail,
)

# Optional but highly recommended: load .env locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


app = FastAPI(
    title="Calyx.io API",
    version="0.1.0",
    description="Zero-budget flower identification API",
)

# CORS
cors_env = os.getenv("CORS_ORIGINS", "")
origins = [o.strip() for o in cors_env.split(",") if o.strip()]

if not origins:
    origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialise services
db = SupabaseClient()
vision = VisionModel()


@app.on_event("startup")
async def startup_event():
    await vision.load_model()
    print("✅ Vision model loaded")


@app.get("/")
async def root():
    return {
        "name": "Calyx.io API",
        "version": "0.1.0",
        "status": "operational",
        "flowers_count": await db.get_species_count(),
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "database": "connected" if db.is_connected() else "disconnected",
        "model": "loaded" if vision.is_loaded() else "loading",
    }


@app.get("/supabase/ping")
async def supabase_ping():
    # quick “is env + client OK?” check
    count = await db.get_species_count()
    return {"ok": True, "connected": db.is_connected(), "species_count": count}


@app.post("/api/v1/identify", response_model=IdentificationResponse)
async def identify_flower(image: UploadFile = File(...), use_cache: bool = True):
    start_time = time.time()

    try:
        image_bytes = await image.read()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_hash = hashlib.sha256(image_bytes).hexdigest()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")

    if use_cache:
        cached = await db.get_cached_identification(image_hash)
        if cached:
            await db.increment_cache_hit(cached["id"])
            return IdentificationResponse(
                **cached,
                response_time_ms=int((time.time() - start_time) * 1000),
                method="cache_hit",
            )

    try:
        traits = await vision.extract_traits(img)
        embedding = await vision.get_embedding(img)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision model error: {str(e)}")

    candidates = await db.search_by_traits(traits)

    if len(candidates) == 0:
        candidates = await db.search_by_embedding(embedding)
        method = "vector_match"
    elif len(candidates) > 1:
        candidates = await db.refine_with_embedding(candidates, embedding)
        method = "trait_elimination"
    else:
        method = "trait_elimination"

    if len(candidates) == 0:
        raise HTTPException(status_code=404, detail="No matching flowers found")

    top_match = candidates[0]

    await db.cache_identification(
        image_hash=image_hash,
        species_id=top_match["id"],
        confidence=top_match["confidence"],
        traits=traits,
        method=method,
    )

    response_time = int((time.time() - start_time) * 1000)

    return IdentificationResponse(
        species_id=top_match["id"],
        scientific_name=top_match["scientific_name"],
        common_names=top_match["common_names"],
        confidence=top_match["confidence"],
        primary_image_url=top_match.get("primary_image_url"), # type: ignore
        method=method,
        traits_extracted=traits,
        alternatives=candidates[1:4],
        response_time_ms=response_time,
    )


@app.get("/api/v1/search", response_model=List[SearchResponse])
async def search_flowers(q: str, limit: int = 20):
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Query too short")

    results = await db.text_search(q, limit)
    return [SearchResponse(**r) for r in results]


@app.get("/api/v1/species/{species_id}", response_model=SpeciesDetail)
async def get_species(species_id: str):
    species = await db.get_species_by_id(species_id)
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    return SpeciesDetail(**species)


@app.post("/api/v1/feedback")
async def submit_feedback(
    identification_id: str,
    is_correct: bool,
    correct_species_id: Optional[str] = None,
    notes: Optional[str] = None,
):
    await db.save_feedback(
        identification_id=identification_id,
        is_correct=is_correct,
        correct_species_id=correct_species_id,
        notes=notes,
    )
    return {"status": "success", "message": "Feedback recorded"}


@app.get("/api/v1/stats")
async def get_stats():
    return await db.get_stats()


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
        },
    )

@app.get("/api/v1/catalogue")
async def get_catalogue(
    name: Optional[str] = None,
    color: Optional[str] = None,  # Can be comma-separated: "red,pink,yellow"
    country: Optional[str] = None,
    sort_by: SortBy = SortBy.name, # type: ignore
    page: int = 1,
    limit: int = 20
):
    """
    Get paginated flower catalogue with filtering and sorting
    
    Query Parameters:
    - name: Filter by flower name (partial match)
    - color: Filter by color(s) - comma-separated (e.g., "red,pink")
    - country: Filter by country/region (e.g., "Kenya", "US", "UK")
    - sort_by: Sort order - "name", "popularity", "recent"
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    
    Returns:
    - items: List of flower species
    - total: Total count
    - page: Current page
    - pages: Total pages
    - has_next: Boolean
    - has_prev: Boolean
    """
    
    # Validate limit
    if limit > 100:
        limit = 100
    
    # Parse colors if provided
    colors = color.split(',') if color else None
    
    # Get catalogue data
    result = await db.get_catalogue(
        name_filter=name,
        color_filter=colors,
        country_filter=country,
        sort_by=sort_by.value,
        page=page,
        limit=limit
    )
    
    return result


@app.get("/api/v1/catalogue/filters")
async def get_available_filters():
    """
    Get available filter options for the catalogue
    
    Returns all unique values for:
    - colors (from species traits)
    - countries (from species native regions)
    """
    
    filters = await db.get_available_filters()
    
    return {
        "colors": filters.get("colors", []),
        "countries": filters.get("countries", []),
        "sort_options": [
            {"value": "name", "label": "Alphabetical (A-Z)"},
            {"value": "popularity", "label": "Most Popular"},
            {"value": "recent", "label": "Recently Added"}
        ]
    }


@app.get("/api/v1/catalogue/popular")
async def get_popular_flowers(limit: int = 10):
    """
    Get most popular flowers (by search count)
    
    Query Parameters:
    - limit: Number of results (default: 10, max: 50)
    """
    
    if limit > 50:
        limit = 50
    
    popular = await db.get_popular_flowers(limit)
    
    return {
        "popular_flowers": popular,
        "count": len(popular)
    }


