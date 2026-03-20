from backend.database import SupabaseClient
from backend.vision import VisionModel
from backend.main_state import db, vision


def get_db() -> SupabaseClient:
    return db


def get_vision() -> VisionModel:
    return vision