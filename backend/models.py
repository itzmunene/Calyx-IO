from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional
from typing import Dict

from pydantic import BaseModel
from pydantic import Field
from pydantic import BaseModel, Field, field_validator

from pydantic import field_validator

class SortBy(str, Enum):
    alphabetical = "name"
    popularity = "popularity"
    recent = "recent"

class FilterParams(BaseModel):
    name: Optional[str] = None
    color: Optional[List[str]] = None
    country: Optional[str] = None
    sort_by: SortBy = SortBy.alphabetical
    limit: int = 20


class IdentificationRequest(BaseModel):
    use_cache: bool = True


class GrowingInfo(BaseModel):
    native_region: List[str] = Field(default_factory=list)
    climate_zones: List[str] = Field(default_factory=list)
    growing_season: List[str] = Field(default_factory=list)

    hardiness_zones: str | None = None
    light_requirement: str | None = None
    water_needs: str | None = None
    soil_preference: str | None = None
    ph_range: str | None = None
    mature_height: str | None = None
    mature_spread: str | None = None
    growth_rate: str | None = None

    @field_validator("native_region", "climate_zones", "growing_season", mode="before")
    @classmethod
    def fix_null_lists(cls, v):
        return v or []


class IdentificationResponse(BaseModel):
    species_id: Optional[str] = None
    scientific_name: str
    common_names: List[str]
    confidence: float
    primary_image_url: Optional[str] = None
    method: Optional[str] = None
    traits_extracted: Optional[dict] = None
    alternatives: Optional[list] = None
    response_time_ms: Optional[int] = None


class SearchResponse(BaseModel):
    """Response model for text search"""
    id: str
    scientific_name: str
    common_names: List[str]
    primary_image_url: Optional[str]
    family: Optional[str]
    # Optional: Add growing_info for search results
    growing_info: Optional[GrowingInfo] = None


class SpeciesDetail(BaseModel):
    """Detailed species information"""
    id: str
    scientific_name: str
    common_names: List[str]
    family: Optional[str]
    description: Optional[str]
    care_tips: Optional[str]
    bloom_season: Optional[List[str]]
    traits: Dict[str, Any] = Field(default_factory=dict)
    @field_validator("traits", mode="before")
    @classmethod
    def fix_null_traits(cls, v):    
            return v or {}
    primary_image_url: Optional[str]
    thumbnail_url: Optional[str]
    
    # NEW: Growing information
    growing_info: Optional[GrowingInfo] = None
    
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class FeedbackRequest(BaseModel):
    identification_id: str
    is_correct: bool
    correct_species_id: str | None = None
    notes: str | None = None