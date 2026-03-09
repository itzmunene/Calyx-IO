# backend/main.py
import os
import time
import io
import hashlib
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.database import SupabaseClient
from backend.vision import VisionModel
from backend.auth import require_user
from backend.models import SortBy, IdentificationResponse, SearchResponse, SpeciesDetail


# -----------------------------
# Env loading (root + backend)
# -----------------------------
ROOT = Path(__file__).resolve().parents[1]         # .../Calyx IO
BACKEND_DIR = Path(__file__).resolve().parent      # .../Calyx IO/backend
load_dotenv(ROOT / ".env")
load_dotenv(BACKEND_DIR / ".env")


# -----------------------------
# Rate limiting (user id -> IP)
# -----------------------------
def rate_limit_key(request: Request) -> str:
    user_id = getattr(request.state, "user_id", None)
    return user_id or get_remote_address(request)

limiter = Limiter(key_func=rate_limit_key)


# -----------------------------
# App
# -----------------------------
app = FastAPI(
    title="Calyx.io API",
    version="0.1.0",
    description="Zero-budget flower identification API",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore[arg-type]


# -----------------------------
# CORS
# -----------------------------
cors_env = os.getenv("CORS_ORIGINS", "")
origins = [o.strip() for o in cors_env.split(",") if o.strip()]

# Optional fallback for local dev (keep if you want)
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


# -----------------------------
# Services
# -----------------------------
db = SupabaseClient()
vision = VisionModel()


@app.on_event("startup")
async def startup_event():
    await vision.load_model()
    print("✅ Vision model loaded")


# -----------------------------
# System endpoints
# -----------------------------
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
    count = await db.get_species_count()
    return {"ok": True, "connected": db.is_connected(), "species_count": count}


# -----------------------------
# Core API
# -----------------------------
@app.post("/api/v1/identify", response_model=IdentificationResponse)
@limiter.limit("5/minute")
async def identify_flower(
    request: Request,
    image: UploadFile = File(...),
    use_cache: bool = True,
    user=Depends(require_user),  # ✅ requires Supabase JWT
):
    start_time = time.time()

    # Validate content type
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail="Unsupported image type (jpeg/png/webp only)")

    # Read once
    image_bytes = await image.read()

    # Validate size (5MB)
    max_bytes = 5 * 1024 * 1024
    if len(image_bytes) > max_bytes:
        raise HTTPException(status_code=413, detail="File too large (max 5MB)")

    # Decode
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_hash = hashlib.sha256(image_bytes).hexdigest()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")

    # Cache
    if use_cache:
        cached = await db.get_cached_identification(image_hash)
        if cached:
            await db.increment_cache_hit(cached["id"])
            return IdentificationResponse(
                **cached,
                response_time_ms=int((time.time() - start_time) * 1000),
                method="cache_hit",
            )

    # Vision + matching
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
        primary_image_url=top_match.get("primary_image_url"),
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


@app.get("/api/v1/catalogue")
async def get_catalogue(
    name: Optional[str] = None,
    color: Optional[str] = None,  # comma-separated: "red,pink"
    country: Optional[str] = None,
    sort_by: SortBy = SortBy.alphabetical,
    page: int = 1,
    limit: int = 20,
):
    if limit > 100:
        limit = 100

    colors = color.split(",") if color else None

    return await db.get_catalogue(
        name_filter=name,
        color_filter=colors,
        country_filter=country,
        sort_by=sort_by.value,
        page=page,
        limit=limit,
    )


@app.get("/api/v1/catalogue/filters")
async def get_available_filters():
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


@app.get("/api/v1/catalogue/popular")
async def get_popular_flowers(limit: int = 10):
    if limit > 50:
        limit = 50
    popular = await db.get_popular_flowers(limit)
    return {"popular_flowers": popular, "count": len(popular)}


# -----------------------------
# Global exception handler
# -----------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )