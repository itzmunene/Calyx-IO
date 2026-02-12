# backend/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import SupabaseClient  # same folder import (backend/main.py and backend/database.py)

app = FastAPI(title="Calyx API")

# --- CORS ---

cors_env = os.getenv("CORS_ORIGINS", "")
origins = [o.strip() for o in cors_env.split(",") if o.strip()]

# sensible dev defaults if env var is not set
if not origins:
    origins = [
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

# --- Single DB client instance (efficient) ---
db = SupabaseClient()

@app.get("/health")
async def health():
    return {"status": "healthy", "database": "connected" if db.is_connected() else "disconnected"}


# OPTIONAL:
# If you already have routers/endpoints in other files, plug them in here:
# from routes.api_v1 import router as api_v1_router
# app.include_router(api_v1_router, prefix="/api/v1")