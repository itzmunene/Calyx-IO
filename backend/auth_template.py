# backend/auth.py
from fastapi import Header, HTTPException, Request
from typing import Optional, Dict, Any, cast
import os
import time
import requests

import jwt  # PyJWT
from jwt.algorithms import RSAAlgorithm  # ✅ helps Pylance

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json" if SUPABASE_URL else ""

JWT_AUD = os.getenv("SUPABASE_JWT_AUD", "authenticated")
# For Supabase, issuer is usually: https://<project-ref>.supabase.co/auth/v1
JWT_ISS = os.getenv("SUPABASE_JWT_ISS", f"{SUPABASE_URL}/auth/v1" if SUPABASE_URL else "")

_jwks_cache: Dict[str, Any] = {}
_jwks_cache_ts: float = 0.0
JWKS_TTL_SECONDS = 60 * 60  # 1 hour


def _get_jwks() -> Dict[str, Any]:
    global _jwks_cache, _jwks_cache_ts

    if not JWKS_URL:
        raise RuntimeError("SUPABASE_URL is not set; cannot load JWKS")

    now = time.time()
    if not _jwks_cache or (now - _jwks_cache_ts) > JWKS_TTL_SECONDS:
        resp = requests.get(JWKS_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict) or "keys" not in data:
            raise RuntimeError("Invalid JWKS response from Supabase")
        _jwks_cache = cast(Dict[str, Any], data)
        _jwks_cache_ts = now

    return _jwks_cache


def require_user(
    request: Request,
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()
    jwks = _get_jwks()

    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        keys = jwks.get("keys", [])
        key = next((k for k in keys if k.get("kid") == kid), None)

        if not key:
            # force refresh in case of key rotation
            global _jwks_cache
            _jwks_cache = {}
            jwks = _get_jwks()
            key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
            if not key:
                raise HTTPException(status_code=401, detail="Invalid token key id")

        public_key = RSAAlgorithm.from_jwk(key)

        decode_kwargs: Dict[str, Any] = {
            "key": public_key,
            "algorithms": ["RS256"],
            "audience": JWT_AUD,
        }

        # Only verify issuer if set
        if JWT_ISS:
            decode_kwargs["issuer"] = JWT_ISS

        payload = jwt.decode(token, **decode_kwargs)

        # store user id for rate limiting
        request.state.user_id = payload.get("sub")
        return cast(Dict[str, Any], payload)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")