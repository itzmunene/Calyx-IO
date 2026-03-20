# backend/services/preprocess_service.py
from dataclasses import dataclass
import hashlib
import io
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError


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


async def process_upload(image: UploadFile) -> ProcessedImage:
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
            detail="Unsupported file type. Please upload a JPG, PNG, or WEBP image.",
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(image_bytes) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum allowed size is 5MB.",
        )

    try:
        pil_image = Image.open(io.BytesIO(image_bytes))
        pil_image.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image or is corrupted.",
        )

    # reopen after verify(), because PIL closes the image file internally
    try:
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="The image could not be processed.",
        )

    width, height = pil_image.size
    if width < 64 or height < 64:
        raise HTTPException(
            status_code=400,
            detail="Image is too small. Please upload a clearer flower photo.",
        )

    image_hash = hashlib.sha256(image_bytes).hexdigest()

    return ProcessedImage(
        image_bytes=image_bytes,
        image_hash=image_hash,
        pil_image=pil_image,
        filename=filename,
        content_type=image.content_type or "application/octet-stream",
    )