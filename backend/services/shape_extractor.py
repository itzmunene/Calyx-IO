from typing import Any, Dict, List
import numpy as np
from PIL import Image


# =========================
# CORE SIGNALS
# =========================

def _to_gray(arr: np.ndarray) -> np.ndarray:
    return np.dot(arr, [0.299, 0.587, 0.114])


def _edge_strength(gray: np.ndarray) -> np.ndarray:
    gx = np.abs(np.diff(gray, axis=1, prepend=gray[:, :1]))
    gy = np.abs(np.diff(gray, axis=0, prepend=gray[:1, :]))
    return gx + gy


# =========================
# FAST HSV (VECTORISED FIX)
# =========================

def _rgb_to_hsv(arr: np.ndarray) -> np.ndarray:
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    maxc = np.max(arr, axis=2)
    minc = np.min(arr, axis=2)
    v = maxc

    s = np.zeros_like(maxc)
    mask = maxc != 0
    s[mask] = (maxc - minc)[mask] / maxc[mask]

    h = np.zeros_like(maxc)

    rc = (maxc - r) / (maxc - minc + 1e-6)
    gc = (maxc - g) / (maxc - minc + 1e-6)
    bc = (maxc - b) / (maxc - minc + 1e-6)

    h[r == maxc] = (bc - gc)[r == maxc]
    h[g == maxc] = 2.0 + (rc - bc)[g == maxc]
    h[b == maxc] = 4.0 + (gc - rc)[b == maxc]

    h = (h / 6.0) % 1.0
    h *= 360

    return np.stack([h, s, v], axis=2)


# =========================
# IPS (INNER PETAL START)
# =========================

def _estimate_ips_radius(hsv, centre, max_radius):
    cx, cy = centre
    h, w = hsv.shape[:2]

    radii = np.linspace(5, max_radius, 20)
    best_radius = int(max_radius * 0.25)
    best_score = 0.0

    for r in radii:
        samples = []
        for i in range(36):
            theta = 2 * np.pi * (i / 36)
            x = int(cx + r * np.cos(theta))
            y = int(cy + r * np.sin(theta))

            if 0 <= x < w and 0 <= y < h:
                s = hsv[y, x, 1]
                v = hsv[y, x, 2]
                samples.append(s * v)

        if samples:
            score = np.mean(samples)
            if score > best_score:
                best_score = score
                best_radius = int(r)

    return best_radius


# =========================
# RADIAL SCAN
# =========================

def _radial_contrast_scan(gray, centre, ips_radius, max_radius, samples=90):
    cx, cy = centre
    h, w = gray.shape

    horizons = []

    for i in range(samples):
        theta = 2 * np.pi * (i / samples)
        values = []

        for r in range(ips_radius, max_radius):
            x = int(cx + r * np.cos(theta))
            y = int(cy + r * np.sin(theta))

            if 0 <= x < w and 0 <= y < h:
                values.append(gray[y, x])

        if len(values) < 5:
            continue

        values = np.array(values)
        diffs = np.abs(np.diff(values))
        threshold = diffs.mean() + diffs.std()

        spike_count = int(np.sum(diffs > threshold))
        horizons.append(spike_count)

    if not horizons:
        return 0, 0.0

    return int(np.mean(horizons)), float(np.std(horizons))


# =========================
# SHAPE LOGIC
# =========================

def _estimate_margin(edges):
    v = float(edges.std())
    if v < 0.04:
        return "smooth"
    if v < 0.08:
        return "slightly_serrated"
    return "ruffled"


def _classify_structure(horizon_count, spacing):
    if horizon_count <= 1:
        return "fused"
    if horizon_count > 6 and spacing < 2.5:
        return "layered"
    if horizon_count > 3:
        return "open"
    return "moderate"


def _estimate_overlap(structure):
    return {
        "layered": "layered",
        "fused": "moderate",
        "open": "separate"
    }.get(structure, "moderate")


def _estimate_shapes(structure):
    if structure == "layered":
        return "rounded", "clustered"
    if structure == "fused":
        return "oval", "none"
    return "rounded", "none"


def _estimate_bloom(structure):
    if structure == "fused":
        return "closed"
    if structure == "open":
        return "open"
    return "partially_open"


# =========================
# CLUSTER PROCESSOR
# =========================

def _process_cluster(arr, hsv, cluster):
    h, w = arr.shape[:2]

    cx = int(cluster["centre"][0] / 1000 * w)
    cy = int(cluster["centre"][1] / 1000 * h)

    major = int(cluster["bbox"]["major_axis"])
    max_radius = max(20, int(major * 0.6))

    gray = _to_gray(arr)
    edges = _edge_strength(gray)

    ips_radius = _estimate_ips_radius(hsv, (cx, cy), max_radius)
    horizon_count, spacing = _radial_contrast_scan(
        gray, (cx, cy), ips_radius, max_radius
    )

    structure = _classify_structure(horizon_count, spacing)
    petal_count = max(3, min(horizon_count * 2, 20))

    outer, inner = _estimate_shapes(structure)

    return {
        "cluster_id": cluster["id"],
        "petal_count": int(petal_count),
        "petal_shape_outer": outer,
        "petal_shape_inner": inner,
        "petal_overlap": _estimate_overlap(structure),
        "petal_margin": _estimate_margin(edges),
        "bloom_openness": _estimate_bloom(structure),

        # debug signals
        "ips_radius": int(ips_radius),
        "horizon_count": int(horizon_count),
        "horizon_variance": round(spacing, 3),
        "structure_type": structure,
    }


# =========================
# MAIN ENTRYPOINT (FIXED)
# =========================

async def extract_shape_traits(
    img: Image.Image,
    pose_data: Dict[str, Any]
) -> Dict[str, Any]:

    arr = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    hsv = _rgb_to_hsv(arr)

    clusters = pose_data.get("clusters", [])

    if not clusters:
        return {"cluster_shapes": []}

    results: List[Dict[str, Any]] = []

    for cluster in clusters:
        results.append(_process_cluster(arr, hsv, cluster))

    output = {
        "cluster_shapes": results
    }

    if results:
        output.update(results[0])  # primary cluster

    return output