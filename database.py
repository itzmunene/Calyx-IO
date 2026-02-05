import os
from supabase import create_client, Client
from typing import List, Dict, Optional
import json
import numpy as np

class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.client: Client = create_client(url, key)
        self._connected = True
    
    def is_connected(self) -> bool:
        """Check if database connection is active"""
        return self._connected
    
    async def get_species_count(self) -> int:
        """Get total number of species in database"""
        try:
            result = self.client.table("species").select("id", count="exact").execute()
            return result.count or 0
        except Exception as e:
            print(f"Error getting species count: {e}")
            return 0
    
    async def search_by_traits(self, traits: Dict) -> List[Dict]:
        """
        Trait-based elimination search
        Uses PostgreSQL JSONB containment operator
        """
        try:
            query = self.client.table("species").select("*")
            
            # Color filter
            if "color_primary" in traits and traits["color_primary"]:
                query = query.contains("traits", {"color_primary": traits["color_primary"]})
            
            # Petal count filter
            if "petal_count" in traits and traits["petal_count"]:
                query = query.contains("traits", {"petal_count": traits["petal_count"]})
            
            # Size filter
            if "flower_size" in traits and traits["flower_size"]:
                query = query.contains("traits", {"flower_size": traits["flower_size"]})
            
            result = query.limit(10).execute()
            
            # Add confidence scores
            for species in result.data:
                species['confidence'] = 0.85  # Trait match confidence
            
            return result.data
        except Exception as e:
            print(f"Error in trait search: {e}")
            return []
    
    async def search_by_embedding(self, embedding: List[float]) -> List[Dict]:
        """
        Vector similarity search using pgvector
        """
        try:
            result = self.client.rpc(
                "match_species",
                {
                    "query_embedding": embedding,
                    "match_threshold": 0.5,
                    "match_count": 5
                }
            ).execute()
            
            # Format response
            formatted_results = []
            for r in result.data:
                formatted_results.append({
                    'id': r['species_id'],
                    'scientific_name': r['scientific_name'],
                    'common_names': r['common_names'],
                    'confidence': r['similarity']
                })
            
            return formatted_results
        except Exception as e:
            print(f"Error in vector search: {e}")
            return []
    
    async def refine_with_embedding(
        self,
        candidates: List[Dict],
        embedding: List[float]
    ) -> List[Dict]:
        """
        Refine trait-matched candidates using vector similarity
        """
        try:
            candidate_ids = [c['id'] for c in candidates]
            
            # Get embeddings for candidates
            result = self.client.table("species")\
                .select("id, scientific_name, common_names, primary_image_url, embedding")\
                .in_("id", candidate_ids)\
                .execute()
            
            # Calculate cosine similarity
            query_vec = np.array(embedding)
            
            scored_candidates = []
            for species in result.data:
                if species.get('embedding'):
                    species_vec = np.array(species['embedding'])
                    similarity = np.dot(query_vec, species_vec) / (
                        np.linalg.norm(query_vec) * np.linalg.norm(species_vec)
                    )
                    species['confidence'] = float(similarity)
                    scored_candidates.append(species)
            
            # Sort by similarity
            scored_candidates.sort(key=lambda x: x['confidence'], reverse=True)
            return scored_candidates
        except Exception as e:
            print(f"Error refining with embedding: {e}")
            return candidates
    
    async def text_search(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Text search on common names and scientific names
        """
        try:
            # Use ilike for case-insensitive partial match
            result = self.client.table("species")\
                .select("id, scientific_name, common_names, primary_image_url, family")\
                .or_(f"scientific_name.ilike.%{query}%,common_names.cs.{{{query}}}")\
                .limit(limit)\
                .execute()
            
            return result.data
        except Exception as e:
            print(f"Error in text search: {e}")
            return []
    
    async def get_species_by_id(self, species_id: str) -> Optional[Dict]:
        """Get full species details"""
        try:
            result = self.client.table("species")\
                .select("*")\
                .eq("id", species_id)\
                .single()\
                .execute()
            
            return result.data if result.data else None
        except Exception as e:
            print(f"Error getting species by ID: {e}")
            return None
    
    async def get_cached_identification(self, image_hash: str) -> Optional[Dict]:
        """Check cache for previous identification"""
        try:
            result = self.client.table("identification_cache")\
                .select("*, species(*)")\
                .eq("image_hash", image_hash)\
                .gt("expires_at", "now()")\
                .single()\
                .execute()
            
            if result.data:
                return {
                    'id': result.data['id'],
                    'species_id': result.data['species_id'],
                    'scientific_name': result.data['species']['scientific_name'],
                    'common_names': result.data['species']['common_names'],
                    'confidence': result.data['confidence'],
                    'primary_image_url': result.data['species']['primary_image_url'],
                    'traits_extracted': result.data['traits_extracted']
                }
            return None
        except Exception as e:
            # No cache found or error - not critical
            return None
    
    async def cache_identification(
        self,
        image_hash: str,
        species_id: str,
        confidence: float,
        traits: Dict,
        method: str
    ):
        """Cache identification result"""
        try:
            self.client.table("identification_cache").insert({
                "image_hash": image_hash,
                "species_id": species_id,
                "confidence": confidence,
                "traits_extracted": traits,
                "method": method
            }).execute()
        except Exception as e:
            print(f"Error caching identification: {e}")
    
    async def increment_cache_hit(self, cache_id: str):
        """Increment hit count for cached result"""
        try:
            # Get current hit count
            result = self.client.table("identification_cache")\
                .select("hit_count")\
                .eq("id", cache_id)\
                .single()\
                .execute()
            
            if result.data:
                new_count = result.data['hit_count'] + 1
                self.client.table("identification_cache")\
                    .update({"hit_count": new_count})\
                    .eq("id", cache_id)\
                    .execute()
        except Exception as e:
            print(f"Error incrementing cache hit: {e}")
    
    async def save_feedback(
        self,
        identification_id: str,
        is_correct: bool,
        correct_species_id: Optional[str],
        notes: Optional[str]
    ):
        """Save user feedback"""
        try:
            self.client.table("identification_feedback").insert({
                "cache_id": identification_id,
                "user_confirmed": is_correct,
                "correct_species_id": correct_species_id,
                "notes": notes
            }).execute()
        except Exception as e:
            print(f"Error saving feedback: {e}")
    
    async def get_stats(self) -> Dict:
        """Get API usage statistics"""
        try:
            total_identifications = self.client.table("identification_cache")\
                .select("id", count="exact")\
                .execute()
            
            cache_hits = self.client.table("identification_cache")\
                .select("hit_count")\
                .execute()
            
            total_hits = sum(row['hit_count'] for row in cache_hits.data) if cache_hits.data else 0
            total_count = total_identifications.count or 0
            
            return {
                "total_identifications": total_count,
                "total_cache_hits": total_hits,
                "cache_hit_rate": total_hits / max(total_count, 1)
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                "total_identifications": 0,
                "total_cache_hits": 0,
                "cache_hit_rate": 0.0
            }
