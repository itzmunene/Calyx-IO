# backend/services/trait_validator.py

ALLOWED_VALUES = {
    "flower_size": {"small", "medium", "large"},
    "petal_shape_outer": {"rounded", "oval", "pointed", "irregular"},
    "petal_shape_inner": {"clustered", "tight", "none"},
    "petal_overlap": {"separate", "moderate", "layered"},
    "petal_margin": {"smooth", "serrated", "ruffled"},
    "bloom_openness": {"open", "partially_open", "closed"},
    "centre_morphology": {
        "filament_cluster_visible",
        "simple_centre",
        "dense_centre",
    },
    "petal_flow": {"surrounding_centre", "radial", "unclear"},
}

REQUIRED_KEYS = [
    "color_primary",
    "flower_size",
    "petal_count",
    "petal_shape_outer",
    "petal_shape_inner",
    "petal_overlap",
    "petal_margin",
    "bloom_openness",
    "centre_morphology",
    "stamen_visible",
    "anther_visible",
    "stigma_visible",
    "petal_flow",
]


def validate_traits(traits: dict):
    if not isinstance(traits, dict):
        raise ValueError("traits must be a dict")

    # Required keys
    for key in REQUIRED_KEYS:
        if key not in traits:
            raise ValueError(f"Missing key: {key}")

    # Type checks
    if not isinstance(traits["color_primary"], list):
        raise ValueError("color_primary must be a list")

    if not isinstance(traits["petal_count"], int):
        raise ValueError("petal_count must be int")

    for key in ["stamen_visible", "anther_visible", "stigma_visible"]:
        if not isinstance(traits[key], bool):
            raise ValueError(f"{key} must be boolean")

    # Allowed values
    for key, allowed in ALLOWED_VALUES.items():
        if traits[key] not in allowed:
            raise ValueError(f"{key} invalid: {traits[key]}")

    return True


def score_species(input_traits: dict, db_traits: dict) -> int:
    score = 0

    # -----------------------
    # 1. COLOR (soft filter)
    # -----------------------
    input_colors = set(input_traits.get("color_primary", []))
    db_colors = set(db_traits.get("color_primary", []))

    if input_colors & db_colors:
        score += 2

    # -----------------------
    # 2. SIZE (medium weight)
    # -----------------------
    if input_traits.get("flower_size") == db_traits.get("flower_size"):
        score += 3

    # -----------------------
    # 3. PETAL COUNT (tolerant 🔥)
    # -----------------------
    input_count = input_traits.get("petal_count")
    db_count = db_traits.get("petal_count")

    if input_count and db_count:
        if abs(db_count - input_count) <= 2:
            score += 2

    # -----------------------
    # 4. SHAPE (important)
    # -----------------------
    if input_traits.get("petal_shape_outer") == db_traits.get("petal_shape_outer"):
        score += 2

    if input_traits.get("petal_shape_inner") == db_traits.get("petal_shape_inner"):
        score += 2

    # -----------------------
    # 5. OVERLAP / STRUCTURE
    # -----------------------
    if input_traits.get("petal_overlap") == db_traits.get("petal_overlap"):
        score += 1

    # -----------------------
    # 6. REPRODUCTIVE (VERY STRONG)
    # -----------------------
    if input_traits.get("centre_morphology") == db_traits.get("centre_morphology"):
        score += 6

    if input_traits.get("stamen_visible") == db_traits.get("stamen_visible"):
        score += 2

    return score