import time

from fastapi import APIRouter, Depends

from backend.dependencies import get_db, get_vision

router = APIRouter()


@router.get("/")
async def root(db=Depends(get_db)):
    return {
        "name": "Calyx.io API",
        "version": "0.1.0",
        "status": "operational",
        "flowers_count": await db.get_species_count(),
    }


@router.get("/health")
async def health_check(db=Depends(get_db), vision=Depends(get_vision)):
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "database": "connected" if db.is_connected() else "disconnected",
        "model": "loaded" if vision.is_loaded() else "loading",
    }


@router.get("/supabase/ping")
async def supabase_ping(db=Depends(get_db)):
    count = await db.get_species_count()
    return {
        "ok": True,
        "connected": db.is_connected(),
        "species_count": count,
    }