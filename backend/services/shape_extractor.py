from typing import Any, Dict
import numpy as np
from PIL import Image


def estimate_flower_size(img: Image.Image) -> str:
    w, h = img.size
    area = w * h

    if area < 80_000:
        return "small"
    if area < 180_000:
        return "medium"
    return "large"


def estimate_petal_count(img: Image.Image) -> int:
    w, h = img.size
    ratio = (w * h) / 10000.0

    if ratio < 8:
        return 5
    if ratio < 15:
        return 6
    return 10


def _edge_strength(gray: np.ndarray) -> np.ndarray:
    gx = np.abs(np.diff(gray, axis=1, prepend=gray[:, :1]))
    gy = np.abs(np.diff(gray, axis=0, prepend=gray[:1, :]))
    return gx + gy


def _ring_masks(h: int, w: int):
    yy, xx = np.mgrid[0:h, 0:w]
    cy, cx = h / 2.0, w / 2.0
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    dist = dist / (np.max(dist) + 1e-6)

    inner = dist <= 0.20
    middle = (dist > 0.20) & (dist <= 0.35)
    outer = (dist > 0.35) & (dist <= 0.82)

    return inner, middle, outer


def estimate_petal_overlap(
    img: Image.Image,
    pose_traits: Dict[str, Any] | None = None,
    petal_count: int | None = None,
    petal_shape: str | None = None,
) -> str:
    gray = np.asarray(img.convert("L"), dtype=np.float32) / 255.0
    h, w = gray.shape

    edges = _edge_strength(gray)
    inner, middle, outer = _ring_masks(h, w)

    inner_score = float(edges[inner].mean()) if np.any(inner) else 0.0
    middle_score = float(edges[middle].mean()) if np.any(middle) else 0.0
    outer_score = float(edges[outer].mean()) if np.any(outer) else 0.0

    centre_visible = bool((pose_traits or {}).get("centre_visible", False))

    print(
        f"[SHAPE DEBUG] inner_score={inner_score:.4f}, "
        f"middle_score={middle_score:.4f}, outer_score={outer_score:.4f}"
    )

    if centre_visible and inner_score > 0.11 and middle_score > 0.13:
        return "dense_layered"

    if centre_visible and (
        (inner_score > 0.075 and middle_score > 0.095) or
        (middle_score > outer_score * 1.05 and inner_score > 0.065)
    ):
        return "layered"

    # heuristic bias for rose-like profiles
    if centre_visible and petal_count is not None and petal_count >= 10 and petal_shape == "rounded":
        return "layered"

    if outer_score > middle_score * 1.18:
        return "separate"

    return "moderate"


def estimate_petal_shape(img: Image.Image, pose_traits: Dict[str, Any] | None = None) -> str:
    centre_visible = bool((pose_traits or {}).get("centre_visible", False))
    if centre_visible:
        return "rounded"
    return "unclear"


def estimate_petal_margin(img: Image.Image) -> str:
    return "smooth"


def estimate_bloom_openness(img: Image.Image, pose_traits: Dict[str, Any] | None = None) -> str:
    pose_traits = pose_traits or {}
    centre_visible = bool(pose_traits.get("centre_visible", False))
    pose_confidence = float(pose_traits.get("pose_confidence", 0.0))

    if centre_visible and pose_confidence > 0.6:
        return "open"
    if centre_visible:
        return "partially_open"
    return "closed_or_unclear"


def extract_shape_traits(img: Image.Image, pose_traits: Dict[str, Any] | None = None) -> Dict[str, Any]:
    flower_size = estimate_flower_size(img)
    petal_count = estimate_petal_count(img)
    petal_shape = estimate_petal_shape(img, pose_traits=pose_traits)

    return {
        "flower_size": flower_size,
        "petal_count": petal_count,
        "petal_shape": petal_shape,
        "petal_overlap": estimate_petal_overlap(
            img,
            pose_traits=pose_traits,
            petal_count=petal_count,
            petal_shape=petal_shape,
        ),
        "petal_margin": estimate_petal_margin(img),
        "bloom_openness": estimate_bloom_openness(img, pose_traits=pose_traits),
    }