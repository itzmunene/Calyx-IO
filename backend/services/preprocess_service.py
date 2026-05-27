# backend/services/preprocess_service.py
from dataclasses import dataclass
import hashlib
import io
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
import numpy as np
from typing import Optional, Dict, Any

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 5 * 1024 * 1024  # 5MB


@dataclass
class ProcessedImage:
    image_bytes: bytes
    image_hash: str
    pil_image: Image.Image
    filename: str
    content_type: str
    image_metadata: Optional[Dict[str, Any]] = None


async def process_upload(image: UploadFile) -> ProcessedImage:

    Image.MAX_IMAGE_PIXELS = 20_000_000

    if image is None:
        raise HTTPException(status_code=400, detail="No file uploaded")

    filename = image.filename or "unknown"
    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file extension. Please upload a JPG, PNG, or WEBP image.",
        )

    if image.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported image.",
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(image_bytes) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum allowed size is 5MB.",
        )

    # ✅ VERIFY IMAGE
    try:
        Image.open(io.BytesIO(image_bytes)).verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image or is corrupted.",
        )

    # ✅ REOPEN IMAGE
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    width, height = pil_image.size

    # ✅ SIZE CHECK
    if width < 64 or height < 64:
        raise HTTPException(
            status_code=400,
            detail="Image is too small. Please upload a clearer flower photo.",
        )

    # ✅ ASPECT RATIO CHECK
    aspect_ratio = width / (height + 1e-6)
    if aspect_ratio > 10 or aspect_ratio < 0.1:
        raise HTTPException(
            status_code=400,
            detail="Image aspect ratio is not suitable for processing.",
        )

    # ✅ PIXEL CHECKS
    arr = np.asarray(pil_image, dtype=np.uint8)

    # uniform / blank detection
    if arr.std() < 5:
        raise HTTPException(
            status_code=400,
            detail="Image appears too uniform or blank.",
        )

    # ------------------------
    # entropy + vibrance signals (soft handling)
    # ------------------------

    # entropy (distribution complexity)
    hist = np.histogram(arr, bins=256)[0]
    prob = hist / (hist.sum() + 1e-6)
    entropy = float(-np.sum(prob * np.log2(prob + 1e-9)))

    # vibrance proxy (pixel variation)
    std_val = float(arr.std())

    # ------------------------
    # soft penalty (NO blocking)
    # ------------------------

    noise_penalty = 1.0

    if entropy > 7.95 and std_val > 0.35:
        noise_penalty = 0.85
    elif entropy > 7.85:
        noise_penalty = 0.92

    # ------------------------
    # visual finish classification (🔥 new signal)
    # ------------------------

    if std_val < 0.12:
        color_finish = "matte"
    elif std_val < 0.22:
        color_finish = "soft"
    elif entropy > 7.9 and std_val > 0.30:
        color_finish = "vivid_textured"
    else:
        color_finish = "natural"

    image_hash = hashlib.sha256(image_bytes).hexdigest()

    return ProcessedImage(
        image_bytes=image_bytes,
        image_hash=image_hash,
        pil_image=pil_image,
        filename=filename,
        content_type=image.content_type or "application/octet-stream",
        
        image_metadata={
            "entropy": round(entropy, 3),
            "vibrance": round(std_val, 3),
            "color_finish": color_finish,
            "noise_penalty": noise_penalty
        }
    )
