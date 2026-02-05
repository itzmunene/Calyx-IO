from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import time
from PIL import Image
import io

from database import SupabaseClient
from vision import VisionModel
from models import (
    IdentificationRequest,
    IdentificationResponse,
    SearchResponse,
    SpeciesDetail
)

app = FastAPI(
    title="Calyx.io API",
    version="0.1.0",
    description="Zero-budget flower identification API"
)

# CORS - allow iOS app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = SupabaseClient()
vision = VisionModel()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await vision.load_model()
    print("✅ Vision model loaded")

@app.get("/")
async def root():
    return {
        "name": "Calyx.io API",
        "version": "0.1.0",
        "status": "operational",
        "flowers_count": await db.get_species_count()
    }

@app.get("/health")
async def health_check():
    """Health check for Render"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "database": "connected" if db.is_connected() else "disconnected",
        "model": "loaded" if vision.is_loaded() else "loading"
    }

@app.post("/api/v1/identify", response_model=IdentificationResponse)
async def identify_flower(
    image: UploadFile = File(...),
    use_cache: bool = True
):
    """
    Main flower identification endpoint
    
    Process:
    1. Check cache by image hash
    2. Extract traits using CLIP
    3. Trait-based elimination (PostgreSQL JSONB query)
    4. Fallback to vector similarity if no matches
    5. Cache result for 7 days
    """
    start_time = time.time()
    
    # Read and validate image
    try:
        image_bytes = await image.read()
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Generate hash for caching
        image_hash = hashlib.sha256(image_bytes).hexdigest()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
    
    # Check cache first
    if use_cache:
        cached = await db.get_cached_identification(image_hash)
        if cached:
            await db.increment_cache_hit(cached['id'])
            return IdentificationResponse(
                **cached,
                response_time_ms=int((time.time() - start_time) * 1000),
                method='cache_hit'
            )
    
    # Extract traits from image
    try:
        traits = await vision.extract_traits(img)
        embedding = await vision.get_embedding(img)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision model error: {str(e)}")
    
    # Phase 1: Trait-based elimination
    candidates = await db.search_by_traits(traits)
    
    if len(candidates) == 0:
        # Phase 2: Vector similarity fallback
        candidates = await db.search_by_embedding(embedding)
        method = 'vector_match'
    elif len(candidates) > 1:
        # Refine with vector similarity
        candidates = await db.refine_with_embedding(candidates, embedding)
        method = 'trait_elimination'
    else:
        method = 'trait_elimination'
    
    if len(candidates) == 0:
        raise HTTPException(status_code=404, detail="No matching flowers found")
    
    # Top match
    top_match = candidates[0]
    
    # Cache result
    await db.cache_identification(
        image_hash=image_hash,
        species_id=top_match['id'],
        confidence=top_match['confidence'],
        traits=traits,
        method=method
    )
    
    response_time = int((time.time() - start_time) * 1000)
    
    return IdentificationResponse(
        species_id=top_match['id'],
        scientific_name=top_match['scientific_name'],
        common_names=top_match['common_names'],
        confidence=top_match['confidence'],
        primary_image_url=top_match['primary_image_url'],
        method=method,
        traits_extracted=traits,
        alternatives=candidates[1:4],  # Top 3 alternatives
        response_time_ms=response_time
    )

@app.get("/api/v1/search", response_model=List[SearchResponse])
async def search_flowers(
    q: str,
    limit: int = 20
):
    """
    Text-based flower search
    Searches common names and scientific names
    """
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    
    results = await db.text_search(q, limit)
    return [SearchResponse(**r) for r in results]

@app.get("/api/v1/species/{species_id}", response_model=SpeciesDetail)
async def get_species(species_id: str):
    """Get detailed information about a specific species"""
    species = await db.get_species_by_id(species_id)
    
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    
    return SpeciesDetail(**species)

@app.post("/api/v1/feedback")
async def submit_feedback(
    identification_id: str,
    is_correct: bool,
    correct_species_id: Optional[str] = None,
    notes: Optional[str] = None
):
    """
    User feedback for improving model accuracy
    """
    await db.save_feedback(
        identification_id=identification_id,
        is_correct=is_correct,
        correct_species_id=correct_species_id,
        notes=notes
    )
    
    return {"status": "success", "message": "Feedback recorded"}

@app.get("/api/v1/stats")
async def get_stats():
    """API usage statistics"""
    return await db.get_stats()

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if app.debug else "An error occurred"
        }
    )
