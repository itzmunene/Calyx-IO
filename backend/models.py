from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel

class SortBy(str, Enum):
    alphabetical = "name"      
    popularity = "popularity"
    recent = "recent"

class FilterParams(BaseModel):
    name: Optional[str] = None
    color: Optional[List[str]] = None
    country: Optional[str] = None
    sort_by: SortBy = SortBy.alphabetical
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
    """Response model for flower identification"""
    species_id: str
    scientific_name: str
    common_names: List[str]
    confidence: float
    primary_image_url: Optional[str] = None
    method: str
    traits_extracted: dict
    alternatives: List[dict] = []
    response_time_ms: int
    # NEW: Add growing info to identification results
    growing_info: Optional[GrowingInfo] = None


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
    traits: dict
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