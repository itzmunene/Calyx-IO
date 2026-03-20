from typing import Any, Dict
import numpy as np
from PIL import Image


def extract_pose_traits(img: Image.Image) -> Dict[str, Any]:
    arr = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    h, w, _ = arr.shape

    # crude centre prior
    cx = w / 2.0
    cy = h / 2.0

    # central window brightness/contrast proxy
    x1, x2 = int(w * 0.35), int(w * 0.65)
    y1, y2 = int(h * 0.35), int(h * 0.65)
    centre_patch = arr[y1:y2, x1:x2]

    if centre_patch.size == 0:
        return {
            "centre_visible": False,
            "view_angle": "unknown",
            "petal_flow": "unknown",
            "stem_visible": False,
            "sepal_visible": False,
            "pose_confidence": 0.0,
            "centre_point": None,
        }

    contrast = float(np.std(centre_patch))
    centre_visible = contrast > 0.08

    return {
        "centre_visible": centre_visible,
        "view_angle": "front-facing" if centre_visible else "angled_or_unclear",
        "petal_flow": "surrounding_centre" if centre_visible else "unclear",
        "stem_visible": False,
        "sepal_visible": False,
        "pose_confidence": round(min(max(contrast * 3.0, 0.0), 1.0), 3),
        "centre_point": (round(cx, 1), round(cy, 1)),
    }