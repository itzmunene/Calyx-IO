from typing import Any, Dict, List

import cv2
import numpy as np
from PIL import Image


# =========================
# CONFIG
# =========================

MAX_CLUSTERS = 6

MIN_CLUSTER_AREA = 500

LINEARITY_RATIO_THRESHOLD = 10.0

PROXIMITY_MERGE_THRESHOLD = 80


# =========================
# TEXTURE FILTER
# =========================

def _compute_texture_mask(
    gray: np.ndarray
) -> np.ndarray:

    gray_f = gray.astype(np.float32)

    mean = cv2.boxFilter(
        gray_f,
        -1,
        (5, 5)
    )

    mean_sq = cv2.boxFilter(
        gray_f ** 2,
        -1,
        (5, 5)
    )

    variance = mean_sq - (mean ** 2)

    variance = np.maximum(
        variance,
        0
    )

    std_dev = np.sqrt(variance)

    # KEEP textured / detailed regions
    texture_mask = (
        std_dev > 18
    ).astype(np.uint8) * 255

    edge_restore = cv2.Canny(
        gray,
        80,
        160
    )

    edge_restore = cv2.dilate(
        edge_restore,
        np.ones((3, 3), np.uint8),
        iterations=1
    )

    texture_mask = cv2.bitwise_or(
        texture_mask,
        edge_restore
    )

    # reconnect soft petal interiors
    texture_mask = cv2.morphologyEx(
        texture_mask,
        cv2.MORPH_CLOSE,
        np.ones((5, 5), np.uint8),
        iterations=2
    )

    texture_mask = cv2.GaussianBlur(
        texture_mask,
        (5, 5),
        0
    )

    _, texture_mask = cv2.threshold(
        texture_mask,
        127,
        255,
        cv2.THRESH_BINARY
    )

    return texture_mask

# =========================
# RADIAL SYMMETRY
# =========================

def _compute_radial_symmetry(
    contour,
    centre
) -> float:

    cx, cy = centre

    points = contour.reshape(-1, 2)

    distances = np.sqrt(
        (points[:, 0] - cx) ** 2 +
        (points[:, 1] - cy) ** 2
    )

    if len(distances) < 10:
        return 0.0

    mean_dist = np.mean(distances)

    if mean_dist <= 1e-6:
        return 0.0

    std_dist = np.std(distances)

    # lower variance = more symmetric
    symmetry_score = 1.0 - (
        std_dist / mean_dist
    )

    return float(
        np.clip(symmetry_score, 0.0, 1.0)
    )

# =========================
# FLOWER CORE TEST
# =========================

def _compute_core_score(
    contour: np.ndarray
) -> float:

    x, y, bw, bh = cv2.boundingRect(contour)

    if bw <= 2 or bh <= 2:
        return 0.0

    # local mask only
    local_mask = np.zeros(
        (bh + 4, bw + 4),
        dtype=np.uint8
    )

    # translate contour into local space
    shifted = contour.copy()

    shifted[:, 0, 0] -= x - 2
    shifted[:, 0, 1] -= y - 2

    cv2.drawContours(
        local_mask,
        [shifted],
        -1,
        255,
        thickness=-1
    )

    dist = cv2.distanceTransform(
        local_mask,
        cv2.DIST_L2,
        5
    )

    _, max_val, _, max_loc = cv2.minMaxLoc(dist)

    if max_val <= 1:
        return 0.0

    cx, cy = max_loc

    rel_x = cx / max(bw, 1)
    rel_y = cy / max(bh, 1)

    edge_dist = min(
        rel_x,
        rel_y,
        1.0 - rel_x,
        1.0 - rel_y
    )

    score = (
        edge_dist * 0.7 +
        min(max_val / 40.0, 1.0) * 0.3
    )

    return float(
        np.clip(score, 0.0, 1.0)
    )

# =========================
# BORDER CONTACT GATE
# =========================

def _get_border_contact_ratio(
    contour: np.ndarray,
    img_width: int,
    img_height: int,
    margin: int = 8
) -> float:
    """
    Measures how much of the contour perimeter
    touches the image boundary.

    Partial flowers cut by the camera frame
    tend to have very high border contact.
    """

    pts = contour.reshape(-1, 2)

    touches_left = pts[:, 0] <= margin

    touches_right = (
        pts[:, 0] >= (img_width - margin)
    )

    touches_top = pts[:, 1] <= margin

    touches_bottom = (
        pts[:, 1] >= (img_height - margin)
    )

    is_on_border = (
        touches_left |
        touches_right |
        touches_top |
        touches_bottom
    )

    contact_count = np.sum(is_on_border)

    total_points = len(pts)

    if total_points == 0:
        return 0.0

    return float(
        contact_count / total_points
    )

# =========================
# EDGE ADHESION SCORE
# =========================

def _compute_edge_adhesion(
    contour: np.ndarray,
    gradient_mag: np.ndarray,
    hsv: np.ndarray,
    sample_step: int = 4
) -> float:

    pts = contour.reshape(-1, 2)

    if len(pts) < 12:
        return 0.0

    edge_strengths = []

    contrasts = []

    h, w = gradient_mag.shape

    for i in range(0, len(pts), sample_step):

        p_prev = pts[i - 1]
        p_curr = pts[i]
        p_next = pts[(i + 1) % len(pts)]

        tangent = p_next - p_prev

        norm = np.linalg.norm(tangent)

        if norm <= 1e-6:
            continue

        tangent = tangent / norm

        # perpendicular normal
        normal = np.array([
            -tangent[1],
             tangent[0]
        ])

        x, y = p_curr.astype(np.float32)

        # OUTSIDE SAMPLE
        ox = int(x + normal[0] * 2)
        oy = int(y + normal[1] * 2)

        # INSIDE SAMPLE
        ix = int(x - normal[0] * 2)
        iy = int(y - normal[1] * 2)

        # bounds check
        if (
            ox < 0 or oy < 0 or
            ox >= w or oy >= h
        ):
            continue

        if (
            ix < 0 or iy < 0 or
            ix >= w or iy >= h
        ):
            continue

        # =========================
        # EDGE GRADIENT
        # =========================

        edge_strengths.append(
            gradient_mag[int(y), int(x)]
        )

        # =========================
        # HSV CONTRAST
        # =========================

        hsv_in = hsv[iy, ix].astype(np.float32)

        hsv_out = hsv[oy, ox].astype(np.float32)

        delta = np.linalg.norm(
            hsv_in - hsv_out
        )

        contrasts.append(delta)

    if not edge_strengths:
        return 0.0

    if not contrasts:
        return 0.0

    mean_edge = np.mean(edge_strengths) / 255.0

    mean_contrast = np.mean(contrasts) / 255.0

    # combined score
    score = (
        mean_edge * 0.55 +
        mean_contrast * 0.45
    )

    return float(
        np.clip(score, 0.0, 1.0)
    )

# =========================
# FLOWER MASK
# =========================

def _create_flower_mask(
    hsv: np.ndarray,
    gray: np.ndarray
) -> np.ndarray:

    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]

    # =========================
    # FLOWER CANDIDATES
    # =========================

    saturated_region = (
        s > 40
    )

    white_region = (
        (v > 145) &
        (s < 45)
    )

    subject = (
        saturated_region |
        white_region
    )

    color_mask = (
        subject
    ).astype(np.uint8) * 255

    # =========================
    # TEXTURE FILTER
    # =========================

    texture_mask = _compute_texture_mask(gray)

    mask = cv2.bitwise_and(
        color_mask,
        texture_mask
    )

    # =========================
    # SMART GREEN SUPPRESSION
    # =========================

    green_region = (
        (h >= 25) &
        (h <= 100) &
        (s >= 35) &
        (v >= 20)
    )

    probable_flower = (
        (
            (h <= 20) |
            (h >= 105)
        ) &
        (s >= 55)
    )

    green_penalty = (
        green_region &
        ~probable_flower
    ).astype(np.uint8) * 255

    green_penalty = cv2.GaussianBlur(
        green_penalty,
        (5, 5),
        0
    )

    mask = cv2.subtract(
        mask,
        (green_penalty * 0.75).astype(np.uint8)
    )

    # =========================
    # EDGE RECOVERY
    # =========================

    edges = cv2.Canny(
        gray,
        60,
        140
    )

    dilated_color = cv2.dilate(
        color_mask,
        np.ones((5, 5), np.uint8),
        iterations=2
    )

    safe_region = cv2.bitwise_not(
        green_penalty
    )

    edge_candidates = cv2.bitwise_and(
        edges,
        safe_region
    )

    edge_candidates = cv2.bitwise_and(
        edge_candidates,
        dilated_color
    )

    mask = cv2.bitwise_or(
        mask,
        edge_candidates
    )

    # =========================
    # CLEANUP
    # =========================

    kernel = np.ones((3, 3), np.uint8)

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=1
    )

    mask = cv2.medianBlur(mask, 3)

    _, mask = cv2.threshold(
        mask,
        127,
        255,
        cv2.THRESH_BINARY
    )

    return mask


# =========================
# GEOMETRY
# =========================

def _compute_geometry(contour):

    area = cv2.contourArea(contour)

    M = cv2.moments(contour)

    if M["m00"] == 0:
        return None

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    major = 0
    minor = 0
    angle = 0
    ratio = 1.0

    if len(contour) >= 5:

        (_, _), (major, minor), angle = cv2.fitEllipse(contour)

        ratio = max(
            major,
            minor
        ) / (
            min(major, minor) + 1e-6
        )

    return {
        "centre": (cx, cy),
        "major": float(max(major, minor)),
        "minor": float(min(major, minor)),
        "angle": float(angle),
        "ratio": float(ratio),
        "area": float(area)
    }


# =========================
# CONTOUR SCORING
# =========================

def _score_contour(
    contour,
    geometry,
    image_centre,
    max_distance
):

    area_score = min(
        geometry["area"] / 50000,
        1.0
    )

    cx, cy = geometry["centre"]

    dist = np.linalg.norm([
        cx - image_centre[0],
        cy - image_centre[1]
    ])

    dist_score = 1.0 - (
        dist / max_distance
    )

    solidity = 0

    hull = cv2.convexHull(contour)

    hull_area = cv2.contourArea(hull)

    if hull_area > 0:
        solidity = geometry["area"] / hull_area

    score = (
        area_score * 0.5 +
        dist_score * 0.3 +
        solidity * 0.2
    )

    return score


# =========================
# CONTOUR GROUPING
# =========================

def _group_contours(
    contours
):

    grouped = []

    used = set()

    for i, c1 in enumerate(contours):

        if i in used:
            continue

        used.add(i)

        group = [c1]

        M1 = cv2.moments(c1)

        if M1["m00"] == 0:
            continue

        cx1 = M1["m10"] / M1["m00"]
        cy1 = M1["m01"] / M1["m00"]

        for j, c2 in enumerate(contours):

            if j <= i or j in used:
                continue

            M2 = cv2.moments(c2)

            if M2["m00"] == 0:
                continue

            cx2 = M2["m10"] / M2["m00"]
            cy2 = M2["m01"] / M2["m00"]

            dist = np.linalg.norm([
                cx1 - cx2,
                cy1 - cy2
            ])

            area1 = cv2.contourArea(c1)
            area2 = cv2.contourArea(c2)

            area_ratio = max(
                area1,
                area2
            ) / (
                min(area1, area2) + 1e-6
            )

            if area_ratio > 4.0:
                continue

            if dist < PROXIMITY_MERGE_THRESHOLD:

                group.append(c2)

                used.add(j)

        grouped.append(group)

    return grouped


# =========================
# MAIN
# =========================

async def extract_pose_traits(
    img: Image.Image
) -> Dict[str, Any]:

    rgb = np.asarray(
        img.convert("RGB")
    )

    bgr = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2BGR
    )

    hsv = cv2.cvtColor(
        bgr,
        cv2.COLOR_BGR2HSV
    )

    gray = cv2.cvtColor(
        bgr,
        cv2.COLOR_BGR2GRAY
    )

    # =========================
    # GLOBAL GRADIENT FIELD
    # =========================

    grad_x = cv2.Sobel(
        gray,
        cv2.CV_32F,
        1,
        0,
        ksize=3
    )

    grad_y = cv2.Sobel(
        gray,
        cv2.CV_32F,
        0,
        1,
        ksize=3
    )

    gradient_mag = cv2.magnitude(
        grad_x,
        grad_y
    )

    # normalize for stable scoring
    gradient_mag = cv2.normalize(
        gradient_mag,
        dst=np.empty_like(gradient_mag),
        alpha=0,
        beta=255,
        norm_type=cv2.NORM_MINMAX
    ).astype(np.float32)

    mask = _create_flower_mask(
        hsv,
        gray
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    h, w = mask.shape

    image_centre = np.array([
        w / 2,
        h / 2
    ])

    max_distance = np.linalg.norm([
        w,
        h
    ])

    scored = []

    for contour in contours:

        area = cv2.contourArea(contour)

        if area < MIN_CLUSTER_AREA:
            continue

        # =========================
        # BORDER CONTACT REJECTION
        # =========================

        border_ratio = _get_border_contact_ratio(
            contour,
            w,
            h,
            margin=8
        )

        # heavily severed by frame edge
        border_penalty = border_ratio * 0.35

        geometry = _compute_geometry(contour)

        if geometry is None:
            continue

        symmetry_score = _compute_radial_symmetry(
            contour,
            geometry["centre"]
        )

        edge_score = _compute_edge_adhesion(
            contour,
            gradient_mag,
            hsv
        )

        core_score = _compute_core_score(
            contour
        )

        if geometry["ratio"] > LINEARITY_RATIO_THRESHOLD:
            continue

        # reject highly asymmetric fragments
        if symmetry_score < 0.18:
            continue

        # penalise fragments with low core completeness
        if core_score < 0.22:
            continue

        if edge_score < 0.08:
            continue

        score = _score_contour(
            contour,
            geometry,
            image_centre,
            max_distance
        )

        score -= border_penalty
        score += core_score * 0.25

        scored.append(
            (score, contour, geometry)
        )

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    contours = [
        s[1]
        for s in scored
    ]

    contour_groups = _group_contours(contours)

    results = []

    contour_data = []

    cluster_masks = []

    cluster_id = 1


    # for group in contour_groups[:MAX_CLUSTERS]:

    # TRAINING MODE:
    # Only use the highest-ranked cluster group
    for group in contour_groups[:1]:

        merged_mask = np.zeros(
            (h, w),
            dtype=np.uint8
        )

        group_contours = []

        total_area = 0

        weighted_cx = 0
        weighted_cy = 0

        group_confidence = 0

        best_geometry = None

        for contour in group:

            geometry = _compute_geometry(contour)

            if geometry is None:
                continue

            area = geometry["area"]

            total_area += area

            cx, cy = geometry["centre"]

            weighted_cx += cx * area
            weighted_cy += cy * area

            confidence = min(
                area / 150000,
                1.0
            )

            group_confidence = max(
                group_confidence,
                confidence
            )

            if (
                best_geometry is None or
                area > best_geometry["area"]
            ):
                best_geometry = geometry

            cv2.drawContours(
                merged_mask,
                [contour],
                -1,
                255,
                thickness=-1
            )

            contour_points = contour.reshape(
                -1,
                2
            ).tolist()

            group_contours.append(
                contour_points
            )

        if total_area == 0:
            continue

        if best_geometry is None:
           continue

        final_cx = int(
            weighted_cx / total_area
        )

        final_cy = int(
            weighted_cy / total_area
        )

        cluster_uid = (
            f"cluster_{cluster_id:03d}"
        )

        cluster_masks.append(
            merged_mask
        )

        contour_data.append(
            group_contours
        )

        results.append({

            "id": cluster_id,

            "uid": cluster_uid,

            "centre": (
                int((final_cx / w) * 1000),
                int((final_cy / h) * 1000),
            ),

            "bbox": {

                "major_axis": round(
                    best_geometry["major"],
                    2
                ),

                "minor_axis": round(
                    best_geometry["minor"],
                    2
                ),

                "orientation": round(
                    best_geometry["angle"],
                    2
                ),
            },

            "area": int(total_area),

            "petal_spread_ratio": round(
                best_geometry["ratio"],
                3
            ),

            "confidence": round(
                group_confidence,
                3
            ),
        })

        cluster_id += 1

    print("---- POSE DEBUG ----")
    print("Contours:", len(results))
    print("Mask coverage:", int(np.sum(mask > 0)))

    for c in results:
        print(
            f"Cluster {c['id']} centre:",
            c["centre"]
        )

    return {
        "clusters": results,
        "cluster_masks": cluster_masks,
        "contours": contour_data,
        "global_mask": mask,
        "cluster_count": len(results),
        "pose_confidence": round(
            results[0]["confidence"]
            if results else 0,
            3
        ),
        # "pose_confidence": round(
        #     len(results) * 0.25,
        #     3
        # ),
    }
