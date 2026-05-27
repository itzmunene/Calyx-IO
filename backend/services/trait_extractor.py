# backend/services/trait_extractor.py

from typing import Any, Dict, cast
from PIL import Image
import numpy as np

from backend.services.shape_extractor import extract_shape_traits
from backend.services.pose_extractor import extract_pose_traits


def _make_json_safe(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: _make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_json_safe(v) for v in obj]
    return obj


def _strip_internal_pose(pose_traits: dict) -> dict:
    return {
        k: v for k, v in pose_traits.items()
        if k not in ["cluster_masks", "global_mask"]
    }


async def extract_traits(
    img: Image.Image,
    image_metadata: Dict[str, Any] | None = None
) -> Dict[str, Any]:

    # ✅ ONLY WHAT WORKS
    pose_traits = await extract_pose_traits(img)
    shape_traits = await extract_shape_traits(img, pose_traits)

    clean_pose = _strip_internal_pose(pose_traits)

    traits = {
        **clean_pose,
        **shape_traits,
    }

    # ✅ MINIMAL compatibility fields (avoid crashes downstream)
    traits["color_primary"] = []
    traits["centre_color_primary"] = []

    return cast(Dict[str, Any], _make_json_safe(traits))