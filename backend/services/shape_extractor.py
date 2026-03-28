from typing import Any, Dict
import numpy as np
from PIL import Image


# ------------------------
# CORE SIGNALS
# ------------------------

def _to_gray(img: Image.Image) -> np.ndarray:
    return np.asarray(img.convert("L"), dtype=np.float32) / 255.0


def _edge_strength(gray: np.ndarray) -> np.ndarray:
    gx = np.abs(np.diff(gray, axis=1, prepend=gray[:, :1]))
    gy = np.abs(np.diff(gray, axis=0, prepend=gray[:1, :]))
    return gx + gy


def _ring_masks(h: int, w: int):
    yy, xx = np.mgrid[0:h, 0:w]
    cy, cx = h / 2.0, w / 2.0
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    dist /= (np.max(dist) + 1e-6)

    return (
        dist <= 0.20,
        (dist > 0.20) & (dist <= 0.40),
        (dist > 0.40) & (dist <= 0.85),
    )


# ------------------------
# BASIC ESTIMATES
# ------------------------

def estimate_flower_size(img: Image.Image) -> str:
    area = img.size[0] * img.size[1]

    if area < 80_000:
        return "small"
    if area < 180_000:
        return "medium"
    return "large"


def estimate_petal_count(img: Image.Image) -> int | None:
    area = img.size[0] * img.size[1]

    if area < 80_000:
        return 5
    if area < 180_000:
        return 6
    return 10


# ------------------------
# SHAPE LOGIC (FIXED 🔥)
# ------------------------

def estimate_structure(inner, middle, outer, centre_visible):
    if not centre_visible:
        return "closed"

    if outer > middle * 1.1:
        return "open"

    if inner > 0.10 and middle > 0.12:
        return "layered"

    return "moderate"


def estimate_petal_overlap(inner, middle, outer, centre_visible):
    if centre_visible:
        if inner > 0.11 and middle > 0.13:
            return "layered"

        if middle > outer:
            return "moderate"

    if outer > middle * 1.18:
        return "separate"

    return "moderate"


def estimate_petal_shapes(inner, middle, outer, centre_visible):
    if centre_visible:
        return "rounded", "clustered"

    if outer > middle:
        return "oval", "none"

    return "rounded", "none"


def estimate_margin(edge_map):
    variation = float(edge_map.std())

    if variation < 0.04:
        return "smooth"
    if variation < 0.08:
        return "slightly_serrated"
    return "ruffled"


def estimate_bloom_openness(centre_visible, structure):
    if not centre_visible:
        return "closed"
    if structure == "open":
        return "open"
    return "partially_open"


# ------------------------
# MAIN EXTRACTOR
# ------------------------

def extract_shape_traits(img: Image.Image, pose_traits: Dict[str, Any] | None = None) -> Dict[str, Any]:
    gray = _to_gray(img)
    edges = _edge_strength(gray)

    h, w = gray.shape
    inner_mask, middle_mask, outer_mask = _ring_masks(h, w)

    inner = float(edges[inner_mask].mean())
    middle = float(edges[middle_mask].mean())
    outer = float(edges[outer_mask].mean())

    centre_visible = bool((pose_traits or {}).get("centre_visible", False))

    structure = estimate_structure(inner, middle, outer, centre_visible)

    petal_outer, petal_inner = estimate_petal_shapes(inner, middle, outer, centre_visible)

    return {
        "flower_size": estimate_flower_size(img),
        "petal_count": estimate_petal_count(img),

        "petal_shape_outer": petal_outer,
        "petal_shape_inner": petal_inner,

        "petal_overlap": estimate_petal_overlap(inner, middle, outer, centre_visible),

        "petal_margin": estimate_margin(edges),

        "bloom_openness": estimate_bloom_openness(centre_visible, structure),
    }