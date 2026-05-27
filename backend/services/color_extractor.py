from logging import DEBUG
from typing import Any, Dict, List, Tuple
import colorsys

import numpy as np
from PIL import Image


COLOR_RANGES = [
    {"label": "red", "hue_ranges": [(0, 12), (345, 360)], "min_sat": 0.20, "min_val": 0.15},
    {"label": "crimson", "hue_ranges": [(345, 360), (0, 8)], "min_sat": 0.30, "min_val": 0.12},
    {"label": "pink", "hue_ranges": [(320, 345)], "min_sat": 0.15, "min_val": 0.20},
    {"label": "rose", "hue_ranges": [(335, 360), (0, 15)], "min_sat": 0.12, "min_val": 0.18},
    {"label": "magenta", "hue_ranges": [(300, 320)], "min_sat": 0.25, "min_val": 0.18},
    {"label": "purple", "hue_ranges": [(270, 300)], "min_sat": 0.20, "min_val": 0.15},
    {"label": "violet", "hue_ranges": [(255, 285)], "min_sat": 0.18, "min_val": 0.16},
    {"label": "blue", "hue_ranges": [(200, 255)], "min_sat": 0.18, "min_val": 0.18},
    {"label": "lavender", "hue_ranges": [(250, 290)], "min_sat": 0.08, "min_val": 0.35},
    {"label": "yellow", "hue_ranges": [(45, 70)], "min_sat": 0.22, "min_val": 0.25},
    {"label": "gold", "hue_ranges": [(38, 52)], "min_sat": 0.30, "min_val": 0.22},
    {"label": "orange", "hue_ranges": [(20, 44)], "min_sat": 0.25, "min_val": 0.20},
    {"label": "peach", "hue_ranges": [(12, 28)], "min_sat": 0.10, "min_val": 0.35},
    {"label": "coral", "hue_ranges": [(8, 22)], "min_sat": 0.22, "min_val": 0.28},
    {"label": "white", "hue_ranges": [(0, 360)], "min_sat": 0.00, "min_val": 0.75},
    {"label": "cream", "hue_ranges": [(35, 70)], "min_sat": 0.04, "min_val": 0.72},
]

COLOR_FAMILY_MAP = {
    "crimson": "red",
    "rose": "pink",
    "magenta": "pink",
    "violet": "purple",
    "lavender": "purple",
    "gold": "yellow",
    "peach": "orange",
    "coral": "orange",
    "cream": "white",
}

COLOR_FAMILIES = {
    "red": ["red", "crimson"],
    "pink": ["pink", "magenta"],
    "yellow": ["yellow"],
    "orange": ["orange", "peach", "coral"],
    "white": ["white", "cream"],
    "blue": ["blue"],
    "purple": ["purple", "violet", "lavender"],
}

def _to_hsv_pixels(img: Image.Image) -> np.ndarray:
    rgb = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    pixels = rgb.reshape(-1, 3)

    hsv_pixels = np.zeros_like(pixels)
    for i, (r, g, b) in enumerate(pixels):
        h, s, v = colorsys.rgb_to_hsv(float(r), float(g), float(b))
        hsv_pixels[i] = [h * 360.0, s, v]

    return hsv_pixels


def _matches_hue_range(hue: float, ranges: List[Tuple[float, float]]) -> bool:
    for start, end in ranges:
        if start <= end:
            if start <= hue <= end:
                return True
        else:
            if hue >= start or hue <= end:
                return True
    return False


def _classify_hsv_pixel(h: float, s: float, v: float) -> str:
    if s < 0.08 and v > 0.78:
        return "white"
    if s < 0.18 and v > 0.68 and 30 <= h <= 75:
        return "cream"
    if s < 0.10 and v > 0.65:
        return "white"

    for rule in COLOR_RANGES:
        if s >= rule["min_sat"] and v >= rule["min_val"] and _matches_hue_range(h, rule["hue_ranges"]):
            return rule["label"]

    if s < 0.12 and v > 0.70:
        return "white"
    if 300 <= h <= 345:
        return "pink"
    if 20 <= h <= 44:
        return "orange"
    if 45 <= h <= 70:
        return "yellow"
    if 200 <= h <= 255:
        return "blue"
    if 255 <= h <= 300:
        return "purple"

    return "red"


def _collapse_to_family(label: str) -> str:
    return COLOR_FAMILY_MAP.get(label, label)


def _region_masks(h: int, w: int, centre_point: tuple[float, float] | None = None):
    yy, xx = np.mgrid[0:h, 0:w]

    if centre_point is None:
        cx, cy = w / 2.0, h / 2.0
    else:
        cx, cy = centre_point

    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    dist = dist / (np.max(dist) + 1e-6)

    inner = dist <= 0.24
    outer = (dist > 0.24) & (dist <= 0.82)

    return inner, outer


def _filter_pixels_for_region(
    rgb_pixels: np.ndarray,
    hsv_pixels: np.ndarray,
    suppress_green: bool = True,
):
    r = rgb_pixels[:, 0]
    g = rgb_pixels[:, 1]
    b = rgb_pixels[:, 2]

    hue = hsv_pixels[:, 0]
    sat = hsv_pixels[:, 1]
    val = hsv_pixels[:, 2]

    too_dark = val < 0.12
    too_grey = sat < 0.05

    if suppress_green:
        green_heavy = (g > r + 0.10) & (g > b + 0.06) & (hue >= 70) & (hue <= 170)
        mask = ~(green_heavy | too_dark | too_grey)
    else:
        mask = ~(too_dark | too_grey)

    filtered_rgb = rgb_pixels[mask]
    filtered_hsv = hsv_pixels[mask]

    if len(filtered_rgb) == 0:
        return rgb_pixels, hsv_pixels

    # keep whites + allow saturation boost
    sat_mask = filtered_hsv[:, 1] > 0.12
    white_mask = (filtered_hsv[:, 1] < 0.10) & (filtered_hsv[:, 2] > 0.75)

    combined_mask = sat_mask | white_mask

    if np.sum(combined_mask) > 50:
        filtered_rgb = filtered_rgb[combined_mask]
        filtered_hsv = filtered_hsv[combined_mask]

    return filtered_rgb, filtered_hsv

def estimate_color_blending(arr:np.ndarray) -> str:
    #assume arr is RGB float [0-1]
    diff = np.abs(np.diff(arr, axis=1)).mean() + np.abs(np.diff(arr, axis=0)).mean()

    if diff < 0.05:
        return "smooth"
    elif diff < 0.12:
        return "blended"
    else:
        return "sharp"

def _summarise_region_colors(
    rgb_pixels: np.ndarray,
    hsv_pixels: np.ndarray
) -> Dict[str, Any]:

    if len(hsv_pixels) == 0:
        return {
            "primary": ["white"],
            "secondary": [],
            "detailed": ["white"],
            "confidence": 0.0,
        }

    # classify pixels
    labels: List[str] = []
    for h, s, v in hsv_pixels:
        labels.append(_classify_hsv_pixel(float(h), float(s), float(v)))

    # count labels
    label_counts: Dict[str, int] = {}
    for label in labels:
        label_counts[label] = label_counts.get(label, 0) + 1

    total = sum(label_counts.values())
    ranked = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)

    dominant_label, dominant_count = ranked[0]
    dominant_ratio = dominant_count / total

    dominant_family = _collapse_to_family(dominant_label)

    # 🔥 FIX: strong white override (handles lilies properly)
    white_ratio = label_counts.get("white", 0) / total
    if white_ratio > 0.35 and dominant_ratio < 0.60:
        primary = ["white"]
    elif dominant_ratio > 0.55:
        primary = [dominant_family]
    else:
        primary = [_collapse_to_family(label) for label, _ in ranked[:2]]

    # secondary
    secondary = []
    for label, count in ranked[1:4]:
        ratio = count / total
        if ratio > 0.15:
            secondary.append(_collapse_to_family(label))

    secondary = [c for c in dict.fromkeys(secondary) if c not in primary]

    detailed_colors = [label for label, _ in ranked[:3]]

    return {
        "primary": primary,
        "secondary": secondary,
        "detailed": detailed_colors,
        "confidence": round(float(dominant_ratio), 3),
    }


def extract_color_traits(
    img: Image.Image,
    pose_traits: Dict[str, Any] | None = None,
    image_metadata: Dict[str, Any] | None = None
) -> Dict[str, Any]:

    pose_traits = pose_traits or {}
    image_metadata = image_metadata or {}

    centre_point = pose_traits.get("centre_point")

    std_val = float(image_metadata.get("vibrance", 0.0))
    entropy_val = float(image_metadata.get("entropy", 0.0))

    rgb = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    h, w, _ = rgb.shape

    # fallback safety
    if std_val == 0.0:
        std_val = float(rgb.std())

    if entropy_val == 0.0:
        gray = np.mean(rgb, axis=2)
        hist = np.histogram(gray, bins=256)[0]
        prob = hist / (hist.sum() + 1e-6)
        entropy_val = float(-np.sum(prob * np.log2(prob + 1e-9)))

    hsv = _to_hsv_pixels(img).reshape(h, w, 3)

    inner_mask, outer_mask = _region_masks(h, w, centre_point=centre_point)

    inner_rgb = rgb[inner_mask]
    inner_hsv = hsv[inner_mask]

    outer_rgb = rgb[outer_mask]
    outer_hsv = hsv[outer_mask]

    inner_rgb, inner_hsv = _filter_pixels_for_region(inner_rgb, inner_hsv, suppress_green=False)
    outer_rgb, outer_hsv = _filter_pixels_for_region(outer_rgb, outer_hsv, suppress_green=True)

    centre_colors = _summarise_region_colors(inner_rgb, inner_hsv)
    petal_colors = _summarise_region_colors(outer_rgb, outer_hsv)

    if DEBUG:
        print(f"[COLOR DEBUG] centre={centre_colors}, petal={petal_colors}")

    combined_detailed = list(dict.fromkeys(
        petal_colors["detailed"] + centre_colors["detailed"]
    ))[:4]

    combined_confidence = max(
        petal_colors["confidence"],
        centre_colors["confidence"] * 0.8,
    )

    # finish classification
    if std_val < 0.08:
        color_finish = "matte"
    elif entropy_val > 7.5 and std_val > 0.18:
        color_finish = "vivid_textured"
    elif std_val > 0.22:
        color_finish = "grainy"
    else:
        color_finish = "soft_gradient"

    return {
        "petal_color": {
            "primary": expand_and_normalize_colors(petal_colors["primary"], expand=False),
            "secondary": expand_and_normalize_colors(petal_colors["secondary"], expand=True),
            "detailed": petal_colors["detailed"],
            "confidence": petal_colors["confidence"],
        },

        "centre_color": {
            "primary": expand_and_normalize_colors(centre_colors["primary"], expand=False),
            "secondary": expand_and_normalize_colors(centre_colors["secondary"], expand=True),
            "detailed": centre_colors["detailed"],
            "confidence": centre_colors["confidence"],
        },

        # 🔥 optional combined (keep this, it's useful)
        "color": {
            "primary": expand_and_normalize_colors(petal_colors["primary"], expand=False),
            "secondary": expand_and_normalize_colors(petal_colors["secondary"], expand=True),
            "detailed": combined_detailed,
            "confidence": combined_confidence,
        },

        # metadata
        "color_finish": color_finish,
        "color_vibrance": round(std_val, 3),
        "color_entropy": round(entropy_val, 3),
    }

def expand_and_normalize_colors(colors, expand: bool = False):
    expanded = set()

    for c in colors:
        base = _collapse_to_family(c)
        expanded.add(base)

        if expand:
            expanded.update(COLOR_FAMILIES.get(base, [])[:2])

    return sorted(expanded)
    