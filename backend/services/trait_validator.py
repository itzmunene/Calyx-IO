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