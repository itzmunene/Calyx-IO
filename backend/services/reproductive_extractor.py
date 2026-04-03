from typing import Any, Dict, Optional, Tuple
import numpy as np
from PIL import Image
import colorsys


def _edge_strength(gray: np.ndarray) -> np.ndarray:
    gx = np.abs(np.diff(gray, axis=1, prepend=gray[:, :1]))
    gy = np.abs(np.diff(gray, axis=0, prepend=gray[:1, :]))
    return gx + gy


def _extract_patch(
    arr: np.ndarray,
    centre_point: tuple[float, float] | None,
    ratio: float = 0.22,
) -> np.ndarray:
    h, w, _ = arr.shape

    if centre_point is None:
        cx, cy = w / 2.0, h / 2.0
    else:
        cx, cy = centre_point

    patch_w = max(int(w * ratio), 24)
    patch_h = max(int(h * ratio), 24)

    x1 = max(int(cx - patch_w / 2), 0)
    x2 = min(int(cx + patch_w / 2), w)
    y1 = max(int(cy - patch_h / 2), 0)
    y2 = min(int(cy + patch_h / 2), h)

    return arr[y1:y2, x1:x2]


def _rgb_to_hsv_array(patch: np.ndarray) -> np.ndarray:
    if patch.size == 0:
        return np.zeros((*patch.shape[:2], 3), dtype=np.float32)

    if patch.dtype != np.float32:
        patch = patch.astype(np.float32)
        if patch.max() > 1.0:
            patch /= 255.0

    flat = patch.reshape(-1, 3)
    hsv = np.zeros_like(flat)

    for i, (r, g, b) in enumerate(flat):
        h, s, v = colorsys.rgb_to_hsv(float(r), float(g), float(b))
        hsv[i] = [h * 360.0, s, v]

    return hsv.reshape(patch.shape)


def _find_reproductive_hotspot(
    arr: np.ndarray,
    centre_point: tuple[float, float] | None,
    search_ratio: float = 0.40,
    patch_ratio: float = 0.16,
) -> Tuple[tuple[float, float], np.ndarray]:

    h, w, _ = arr.shape

    if centre_point is None:
        cx, cy = w / 2.0, h / 2.0
    else:
        cx, cy = centre_point

    search_w = max(int(w * search_ratio), 40)
    search_h = max(int(h * search_ratio), 40)

    sx1 = max(int(cx - search_w / 2), 0)
    sx2 = min(int(cx + search_w / 2), w)
    sy1 = max(int(cy - search_h / 2), 0)
    sy2 = min(int(cy + search_h / 2), h)

    search = arr[sy1:sy2, sx1:sx2]

    if search.size == 0:
        fallback_patch = _extract_patch(arr, centre_point, ratio=patch_ratio)
        return (cx, cy), fallback_patch

    hsv = _rgb_to_hsv_array(search)
    gray = search.mean(axis=2)
    edges = _edge_strength(gray)

    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]

    warm_mask = ((hue >= 5) & (hue <= 40))
    sat_mask = sat > 0.28
    val_mask = val < 0.80

    hotspot_score = (
        warm_mask.astype(np.float32) * 0.55 +
        sat_mask.astype(np.float32) * 0.20 +
        val_mask.astype(np.float32) * 0.10 +
        np.clip(edges * 2.5, 0.0, 1.0) * 0.15
    )

    if hotspot_score.size == 0:
        fallback_patch = _extract_patch(arr, centre_point, ratio=patch_ratio)
        return (cx, cy), fallback_patch

    max_idx = np.unravel_index(np.argmax(hotspot_score), hotspot_score.shape)
    hy, hx = max_idx

    hotspot_cx = float(sx1 + hx)
    hotspot_cy = float(sy1 + hy)

    patch = _extract_patch(arr, (hotspot_cx, hotspot_cy), ratio=patch_ratio)
    return (float(hotspot_cx), float(hotspot_cy)), patch


def extract_reproductive_traits(
    img: Image.Image,
    pose_traits: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    pose_traits = pose_traits or {}
    centre_visible = bool(pose_traits.get("centre_visible", False))
    pose_confidence = float(pose_traits.get("pose_confidence", 0.0))
    centre_point = pose_traits.get("centre_point")

    if not centre_visible or pose_confidence < 0.18:
        return {
            "stamen_visible": False,
            "anther_visible": False,
            "stigma_visible": False,
            "centre_morphology": "obscured_or_unclear",
            "reproductive_confidence": 0.0,
            "reproductive_hotspot": None,
        }

    arr = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    hotspot_point, patch = _find_reproductive_hotspot(arr, centre_point)

    if patch.size == 0:
        return {
            "stamen_visible": False,
            "anther_visible": False,
            "stigma_visible": False,
            "centre_morphology": "obscured_or_unclear",
            "reproductive_confidence": 0.0,
            "reproductive_hotspot": hotspot_point,
        }

    hsv = _rgb_to_hsv_array(patch)
    gray = patch.mean(axis=2)
    edges = _edge_strength(gray)

    edge_score = float(edges.mean())
    contrast_score = float(gray.std())

    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]

    warm_mask = ((hue >= 5) & (hue <= 40)) & (sat > 0.28) & (val < 0.85)
    dark_mask = val < 0.45
    bright_mask = val > 0.80

    warm_ratio = float(np.mean(warm_mask))
    bright_ratio = float(np.mean(bright_mask))

    anther_visible = warm_ratio > 0.015 and contrast_score > 0.06
    stamen_visible = (edge_score > 0.12 and contrast_score > 0.05) or anther_visible
    stigma_visible = contrast_score > 0.10 and warm_ratio < 0.010 and bright_ratio < 0.75

    if anther_visible and stamen_visible:
        centre_morphology = "filament_cluster_visible"
    elif warm_ratio > 0.03:
        centre_morphology = "anther_cluster_visible"
    elif contrast_score > 0.08:
        centre_morphology = "visible_but_unclassified"
    else:
        centre_morphology = "soft_centre_or_enclosed"

    confidence = (
        min(edge_score * 1.5, 0.35) +
        min(contrast_score * 2.0, 0.35) +
        min(warm_ratio * 6.0, 0.30)
    )
    confidence = round(float(min(confidence, pose_confidence + 0.25, 1.0)), 3)

    return {
        "stamen_visible": bool(stamen_visible),
        "anther_visible": bool(anther_visible),
        "stigma_visible": bool(stigma_visible),
        "centre_morphology": centre_morphology,
        "reproductive_confidence": confidence,
        "reproductive_hotspot": (round(hotspot_point[0], 1), round(hotspot_point[1], 1)),
    }