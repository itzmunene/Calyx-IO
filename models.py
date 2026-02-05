from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class IdentificationRequest(BaseModel):
    """Request model for flower identification"""
    use_cache: bool = True

class IdentificationResponse(BaseModel):
    """Response model for flower identification"""
    species_id: str
    scientific_name: str
    common_names: List[str]
    confidence: float
    primary_image_url: str
    method: str  # 'trait_elimination', 'vector_match', 'cache_hit'
    traits_extracted: Dict
    alternatives: List[Dict] = []
    response_time_ms: int

class SearchResponse(BaseModel):
    """Response model for text search"""
    id: str
    scientific_name: str
    common_names: List[str]
    primary_image_url: Optional[str]
    family: Optional[str]

class SpeciesDetail(BaseModel):
    """Detailed species information"""
    id: str
    scientific_name: str
    common_names: List[str]
    family: Optional[str]
    description: Optional[str]
    care_tips: Optional[str]
    bloom_season: Optional[List[str]]
    traits: Dict
    primary_image_url: Optional[str]
    thumbnail_url: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class FeedbackRequest(BaseModel):
    """User feedback for identification accuracy"""
    identification_id: str
    is_correct: bool
    correct_species_id: Optional[str] = None
    notes: Optional[str] = None
