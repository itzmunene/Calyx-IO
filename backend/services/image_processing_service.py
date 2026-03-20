from dataclasses import dataclass
from typing import Optional

import numpy as np
from PIL import Image, ImageFilter


@dataclass
class PreparedImage:
    original: Image.Image
    working: Image.Image
    cropped_flower: Image.Image
    blur_score: float
    width: int
    height: int


def _resize_for_processing(img: Image.Image, max_side: int = 768) -> Image.Image:
    w, h = img.size
    scale = min(max_side / max(w, h), 1.0)
    new_size = (int(w * scale), int(h * scale))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def _estimate_blur(img: Image.Image) -> float:
    # simple variance-based blur estimate using grayscale edges
    gray = img.convert("L")
    arr = np.asarray(gray, dtype=np.float32)

    gx = np.diff(arr, axis=1)
    gy = np.diff(arr, axis=0)

    score = float(np.var(gx) + np.var(gy))
    return score


def _center_crop(img: Image.Image, ratio: float = 0.65) -> Image.Image:
    w, h = img.size
    crop_w = int(w * ratio)
    crop_h = int(h * ratio)

    left = max((w - crop_w) // 2, 0)
    top = max((h - crop_h) // 2, 0)
    right = min(left + crop_w, w)
    bottom = min(top + crop_h, h)

    return img.crop((left, top, right, bottom))


def _find_flower_like_crop(img: Image.Image) -> Optional[Image.Image]:
    """
    Very early heuristic:
    - prioritize center
    - prefer saturated areas likely to be petals
    """
    rgb = img.convert("RGB")
    arr = np.asarray(rgb, dtype=np.float32) / 255.0

    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    maxc = np.max(arr, axis=2)
    minc = np.min(arr, axis=2)
    sat = maxc - minc

    h, w = sat.shape

    # bias towards center of image
    yy, xx = np.mgrid[0:h, 0:w]
    cy, cx = h / 2.0, w / 2.0
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    dist = dist / (np.max(dist) + 1e-6)
    center_weight = 1.0 - dist

    score = sat * 0.7 + center_weight * 0.3

    threshold = np.percentile(score, 85)
    mask = score >= threshold

    ys, xs = np.where(mask)
    if len(xs) < 50 or len(ys) < 50:
        return None

    x1, x2 = int(xs.min()), int(xs.max())
    y1, y2 = int(ys.min()), int(ys.max())

    # pad the box a bit
    pad_x = int((x2 - x1) * 0.15) + 10
    pad_y = int((y2 - y1) * 0.15) + 10

    x1 = max(x1 - pad_x, 0)
    y1 = max(y1 - pad_y, 0)
    x2 = min(x2 + pad_x, w)
    y2 = min(y2 + pad_y, h)

    if (x2 - x1) < 64 or (y2 - y1) < 64:
        return None

    return img.crop((x1, y1, x2, y2))


def prepare_image(img: Image.Image) -> PreparedImage:
    working = _resize_for_processing(img)
    blur_score = _estimate_blur(working)

    crop = _find_flower_like_crop(working)
    if crop is None:
        crop = _center_crop(working)

    return PreparedImage(
        original=img,
        working=working,
        cropped_flower=crop,
        blur_score=blur_score,
        width=working.size[0],
        height=working.size[1],
    )