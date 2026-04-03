from typing import Any, Dict
from PIL import Image

from backend.services.color_extractor import extract_color_traits
from backend.services.shape_extractor import extract_shape_traits
from backend.services.pose_extractor import extract_pose_traits
from backend.services.reproductive_extractor import extract_reproductive_traits

from backend.services.trait_validator import validate_traits


def extract_traits(img: Image.Image) -> Dict[str, Any]:
    pose_traits = extract_pose_traits(img)
    color_traits = extract_color_traits(img, pose_traits=pose_traits)
    shape_traits = extract_shape_traits(img, pose_traits=pose_traits)
    reproductive_traits = extract_reproductive_traits(img, pose_traits=pose_traits)

    traits = {
        **pose_traits,
        **color_traits,
        **shape_traits,
        **reproductive_traits,
    }

    validate_traits(traits)

    return traits

# print ("[TRAITS], traits")