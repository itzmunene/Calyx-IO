# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.api.routes import catalogue, feedback, health, identify, search, species
from backend.config import settings
from backend.main_state import vision


def rate_limit_key(request: Request) -> str:
    user_id = getattr(request.state, "user_id", None)
    return user_id or get_remote_address(request)


limiter = Limiter(key_func=rate_limit_key)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore[arg-type]

origins = settings.CORS_ORIGINS
if not origins:
    origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

print("✅ CORS_ORIGINS raw:", ",".join(settings.CORS_ORIGINS))
print("✅ CORS allow_origins:", origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await vision.load_model()
    print("✅ Vision model loaded")


app.include_router(health.router, tags=["system"])
app.include_router(identify.router, prefix="/api/v1", tags=["identify"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(species.router, prefix="/api/v1", tags=["species"])
app.include_router(catalogue.router, prefix="/api/v1", tags=["catalogue"])
app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
        },
    )