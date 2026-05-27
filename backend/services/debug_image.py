from PIL import Image, ImageDraw
from typing import Dict, Any
from fastapi import Request

import uuid
from pathlib import Path

import numpy as np


# =========================
# CONFIG
# =========================

DEBUG_DIR = Path("/tmp/calyx_debug")

BLUE = (0, 180, 255)


# =========================
# MAIN DEBUG RENDER
# =========================

def generate_debug_image(
    img: Image.Image,
    pose_data: Dict[str, Any],
    shape_data: Dict[str, Any] | None = None
) -> Image.Image:

    # preserve original image
    img_out = img.convert("RGB")

    draw = ImageDraw.Draw(img_out)

    contours = pose_data.get("contours", [])

    # =========================
    # DRAW CONTOURS
    # =========================

    clusters = pose_data.get(
        "clusters",
        []
    )

    for idx, contour_group in enumerate(contours):

        if idx >= len(clusters):
            continue

        cluster = clusters[idx]

        uid = cluster.get(
            "uid",
            f"cluster_{idx}"
        )

        confidence = cluster.get(
            "confidence",
            0
        )

        centre = cluster.get(
            "centre",
            (0, 0)
        )

        cx = int(
            (centre[0] / 1000)
            * img_out.width
        )

        cy = int(
            (centre[1] / 1000)
            * img_out.height
        )

        color = (
            int(50 + (idx * 40) % 205),
            int(120 + (idx * 70) % 135),
            int(200 - (idx * 30) % 120),
        )

        for contour in contour_group:

            scaled = []

            for point in contour:

                if isinstance(point[0], list):
                    x, y = point[0]
                else:
                    x, y = point

                scaled.append(
                    (int(x), int(y))
                )

            if len(scaled) > 2:

                draw.line(
                    scaled + [scaled[0]],
                    fill=color,
                    width=4
                )

        draw.ellipse(
            (
                cx - 6,
                cy - 6,
                cx + 6,
                cy + 6
            ),
            fill=(255, 0, 0)
        )

        draw.text(
            (cx + 10, cy - 10),
            f"{uid} | {confidence:.2f}",
            fill=(255, 255, 255)
        )

    return img_out


# =========================
# SAVE IMAGE
# =========================

def save_debug_image(image: Image.Image) -> str:

    DEBUG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = f"{uuid.uuid4().hex}.jpg"

    filepath = DEBUG_DIR / filename

    image.save(
        filepath,
        "JPEG",
        quality=95
    )

    return filename


# =========================
# BUILD URL
# =========================

def build_debug_url(
    request: Request,
    filename: str
) -> str:

    base = str(request.base_url).rstrip("/")

    return f"{base}/debug/{filename}"