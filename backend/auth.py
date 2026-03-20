from fastapi import Header, HTTPException
from typing import Optional
import os

API_KEY = os.getenv("CALYX_API_KEY", "")

def require_api_key(authorization: Optional[str] = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()

    if not API_KEY:
        raise HTTPException(status_code=500, detail="Server API key not configured")

    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return token