from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class SortBy(str, Enum):
    name = "name" # type: ignore
    popularity = "popularity"
    recent = "recent"


class FilterParams(BaseModel):
    name: str | None = None
    color: list[str] | None = None
    country: str | None = None
    sort_by: SortBy = SortBy.name # type: ignore
    page: int = 1
    limit: int = 20


class IdentificationRequest(BaseModel):
    use_cache: bool = True


class GrowingInfo(BaseModel):
    native_region: list[str] = []
    climate_zones: list[str] = []
    hardiness_zones: str | None = None
    light_requirement: str | None = None
    water_needs: str | None = None
    soil_preference: str | None = None
    ph_range: str | None = None
    growing_season: list[str] = []
    mature_height: str | None = None
    mature_spread: str | None = None
    growth_rate: str | None = None


class IdentificationResponse(BaseModel):
    species_id: str
    scientific_name: str
    common_names: List[str]
    confidence: float
    primary_image_url: str
    method: str
    traits_extracted: Dict
    alternatives: List[Dict] = []
    response_time_ms: int
    growing_info: GrowingInfo | None = None


class SearchResponse(BaseModel):
    id: str
    scientific_name: str
    common_names: List[str]
    primary_image_url: str | None = None
    family: str | None = None


class SpeciesDetail(BaseModel):
    id: str
    scientific_name: str
    common_names: List[str]
    family: str | None = None
    description: str | None = None
    care_tips: str | None = None
    bloom_season: list[str] | None = None
    traits: Dict
    primary_image_url: str | None = None
    thumbnail_url: str | None = None
    growing_info: GrowingInfo | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class FeedbackRequest(BaseModel):
    identification_id: str
    is_correct: bool
    correct_species_id: str | None = None
    notes: str | None = None