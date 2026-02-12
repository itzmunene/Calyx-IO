# backend/database.py
import os
from typing import Any, Dict, List, Optional, cast

import numpy as np
from supabase import create_client, Client


JSONDict = Dict[str, Any]

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
            result = self.client.table("species").select("id", count=cast(Any, "exact")).execute()
            return int(result.count or 0)
        except Exception as e:
            print(f"Error getting species count: {e}")
            return 0

    async def search_by_traits(self, traits: Dict[str, Any]) -> List[JSONDict]:
        """
        Trait-based elimination search
        Uses PostgreSQL JSONB containment operator
        """
        try:
            query = self.client.table("species").select("*")

            if traits.get("color_primary"):
                query = query.contains("traits", {"color_primary": traits["color_primary"]})

            if traits.get("petal_count"):
                query = query.contains("traits", {"petal_count": traits["petal_count"]})

            if traits.get("flower_size"):
                query = query.contains("traits", {"flower_size": traits["flower_size"]})

            result = query.limit(10).execute()

            data = cast(List[JSONDict], result.data or [])

            for species in data:
                species["confidence"] = 0.85

            return data

        except Exception as e:
            print(f"Error in trait search: {e}")
            return []

    async def search_by_embedding(self, embedding: List[float]) -> List[JSONDict]:
        """
        Vector similarity search using pgvector
        """
        try:
            result = self.client.rpc(
                "match_species",
                {"query_embedding": embedding, "match_threshold": 0.5, "match_count": 5},
            ).execute()

            rows = cast(List[JSONDict], result.data or [])

            formatted_results: List[JSONDict] = []
            for r in rows:
                formatted_results.append(
                    {
                        "id": r.get("species_id"),
                        "scientific_name": r.get("scientific_name"),
                        "common_names": r.get("common_names"),
                        "confidence": r.get("similarity"),
                    }
                )

            return formatted_results
        except Exception as e:
            print(f"Error in vector search: {e}")
            return []

    async def refine_with_embedding(self, candidates: List[JSONDict], embedding: List[float]) -> List[JSONDict]:
        """
        Refine trait-matched candidates using vector similarity
        """
        try:
            candidate_ids = [c["id"] for c in candidates if "id" in c]

            if not candidate_ids:
                return []

            result = (
                self.client.table("species")
                .select("id, scientific_name, common_names, primary_image_url, embedding")
                .in_("id", candidate_ids)
                .execute()
            )

            rows = cast(List[JSONDict], result.data or [])

            query_vec = np.array(embedding, dtype=float)

            scored_candidates: List[JSONDict] = []
            for species in rows:
                emb = species.get("embedding")
                if emb:
                    species_vec = np.array(emb, dtype=float)
                    denom = (np.linalg.norm(query_vec) * np.linalg.norm(species_vec))
                    if denom == 0:
                        continue
                    similarity = float(np.dot(query_vec, species_vec) / denom)
                    species["confidence"] = similarity
                    scored_candidates.append(species)

            scored_candidates.sort(key=lambda x: float(x.get("confidence", 0.0)), reverse=True)
            return scored_candidates

        except Exception as e:
            print(f"Error refining with embedding: {e}")
            return candidates

    async def text_search(self, query: str, limit: int = 20) -> List[JSONDict]:
        """
        Text search on common names and scientific names
        """
        try:
            result = (
                self.client.table("species")
                .select("id, scientific_name, common_names, primary_image_url, family")
                .or_(f"scientific_name.ilike.%{query}%,common_names.cs.{{{query}}}")
                .limit(limit)
                .execute()
            )
            return cast(List[JSONDict], result.data or [])
        except Exception as e:
            print(f"Error in text search: {e}")
            return []

    async def get_species_by_id(self, species_id: str) -> Optional[JSONDict]:
        """Get full species details including growing information"""
        try:
            result = (
                self.client.table("species")
                .select(
                    "id, scientific_name, common_names, family, "
                    "description, care_tips, bloom_season, traits, "
                    "primary_image_url, thumbnail_url, "
                    "native_region, climate_zones, hardiness_zones, "
                    "light_requirement, water_needs, soil_preference, "
                    "ph_range, growing_season, mature_height, "
                    "mature_spread, growth_rate, "
                    "created_at, updated_at"
                )
                .eq("id", species_id)
                .single()
                .execute()
            )

            data = cast(Optional[JSONDict], result.data)
            if not data:
                return None

            growing_info = {
                "native_region": data.get("native_region", []),
                "climate_zones": data.get("climate_zones", []),
                "hardiness_zones": data.get("hardiness_zones"),
                "light_requirement": data.get("light_requirement"),
                "water_needs": data.get("water_needs"),
                "soil_preference": data.get("soil_preference"),
                "ph_range": data.get("ph_range"),
                "growing_season": data.get("growing_season", []),
                "mature_height": data.get("mature_height"),
                "mature_spread": data.get("mature_spread"),
                "growth_rate": data.get("growth_rate"),
            }

            data["growing_info"] = growing_info
            return data

        except Exception as e:
            print(f"Error getting species by ID: {e}")
            return None

    async def get_cached_identification(self, image_hash: str) -> Optional[JSONDict]:
        """Check cache for previous identification"""
        try:
            result = (
                self.client.table("identification_cache")
                .select("*, species(*)")
                .eq("image_hash", image_hash)
                .gt("expires_at", "now()")
                .single()
                .execute()
            )

            data = cast(Optional[JSONDict], result.data)
            if not data:
                return None

            species = cast(JSONDict, data.get("species") or {})

            return {
                "id": data.get("id"),
                "species_id": data.get("species_id"),
                "scientific_name": species.get("scientific_name"),
                "common_names": species.get("common_names"),
                "confidence": data.get("confidence"),
                "primary_image_url": species.get("primary_image_url"),
                "traits_extracted": data.get("traits_extracted"),
            }

        except Exception:
            return None

    async def cache_identification(
        self,
        image_hash: str,
        species_id: str,
        confidence: float,
        traits: Dict[str, Any],
        method: str,
    ) -> None:
        """Cache identification result"""
        try:
            self.client.table("identification_cache").insert(
                {
                    "image_hash": image_hash,
                    "species_id": species_id,
                    "confidence": confidence,
                    "traits_extracted": traits,
                    "method": method,
                }
            ).execute()
        except Exception as e:
            print(f"Error caching identification: {e}")

    async def increment_cache_hit(self, cache_id: str) -> None:
        """Increment hit count for cached result"""
        try:
            result = (
                self.client.table("identification_cache")
                .select("hit_count")
                .eq("id", cache_id)
                .single()
                .execute()
            )

            data = cast(Optional[JSONDict], result.data)
            if not data:
                return

            current = int(data.get("hit_count") or 0)
            (
                self.client.table("identification_cache")
                .update({"hit_count": current + 1})
                .eq("id", cache_id)
                .execute()
            )
        except Exception as e:
            print(f"Error incrementing cache hit: {e}")

    async def save_feedback(
        self,
        identification_id: str,
        is_correct: bool,
        correct_species_id: Optional[str],
        notes: Optional[str],
    ) -> None:
        """Save user feedback"""
        try:
            self.client.table("identification_feedback").insert(
                {
                    "cache_id": identification_id,
                    "user_confirmed": is_correct,
                    "correct_species_id": correct_species_id,
                    "notes": notes,
                }
            ).execute()
        except Exception as e:
            print(f"Error saving feedback: {e}")

    async def get_stats(self) -> JSONDict:
        """Get API usage statistics"""
        try:
            total_identifications = (
                self.client.table("identification_cache").select("id", count=cast(Any, "exact")).execute()
            )

            cache_hits = self.client.table("identification_cache").select("hit_count").execute()
            rows = cast(List[JSONDict], cache_hits.data or [])

            total_hits = sum(int(row.get("hit_count") or 0) for row in rows)
            total_count = int(total_identifications.count or 0)

            return {
                "total_identifications": total_count,
                "total_cache_hits": total_hits,
                "cache_hit_rate": total_hits / max(total_count, 1),
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"total_identifications": 0, "total_cache_hits": 0, "cache_hit_rate": 0.0}

    async def get_available_filters(self) -> JSONDict:
        """Get all available filter options from the database"""
        try:
            # You were selecting only "id" before, but then reading traits/native_region.
            # That’s a real logic bug, not just typing.
            result = (
                self.client.table("species")
                .select("traits, native_region", count=cast(Any, "exact"))
                .execute()
            )

            rows = cast(List[JSONDict], result.data or [])

            colors_set: set[str] = set()
            countries_set: set[str] = set()

            for species in rows:
                traits = cast(JSONDict, species.get("traits") or {})
                color_primary = traits.get("color_primary") or []

                if isinstance(color_primary, str):
                    color_primary = [color_primary]
                if isinstance(color_primary, list):
                    colors_set.update(str(c) for c in color_primary)

                native_region = species.get("native_region") or []
                if isinstance(native_region, str):
                    native_region = [native_region]
                if isinstance(native_region, list):
                    countries_set.update(str(c) for c in native_region)

            colors_list: List[JSONDict] = []
            for color in sorted(colors_set):
                count = await self.count_by_color(color)
                colors_list.append({"value": color, "label": color.capitalize(), "count": count})

            countries_list: List[JSONDict] = []
            for country in sorted(countries_set):
                count = await self.count_by_country(country)
                countries_list.append({"value": country, "label": country, "count": count})

            return {"colors": colors_list, "countries": countries_list}

        except Exception as e:
            print(f"Error getting filters: {e}")
            return {"colors": [], "countries": []}

    async def count_by_color(self, color: str) -> int:
        """Count flowers with a specific color"""
        try:
            result = (
                self.client.table("species")
                .select("id", count=cast(Any, "exact"))
                .contains("traits", {"color_primary": [color]})
                .execute()
            )
            return int(result.count or 0)
        except Exception:
            return 0

    async def count_by_country(self, country: str) -> int:
        """Count flowers from a specific country/region"""
        try:
            result = (
                self.client.table("species")
                .select("id", count=cast(Any, "exact"))
                .contains("native_region", [country])
                .execute()
            )
            return int(result.count or 0)
        except Exception:
            return 0

