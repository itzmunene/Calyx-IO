# backend/config.py
import os
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = Path(__file__).resolve().parent

load_dotenv(ROOT / ".env")
load_dotenv(BACKEND_DIR / ".env")


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Calyx.io API")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    APP_DESCRIPTION: str = os.getenv(
        "APP_DESCRIPTION",
        "Zero-budget flower identification API",
    )

    CORS_ORIGINS: list[str] = _split_csv(os.getenv("CORS_ORIGINS", ""))

    MAX_IMAGE_BYTES: int = int(os.getenv("MAX_IMAGE_BYTES", str(5 * 1024 * 1024)))
    MAX_CATALOGUE_LIMIT: int = int(os.getenv("MAX_CATALOGUE_LIMIT", "100"))
    MAX_POPULAR_LIMIT: int = int(os.getenv("MAX_POPULAR_LIMIT", "50"))


settings = Settings()