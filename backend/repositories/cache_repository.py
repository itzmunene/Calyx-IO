# backend/repositories/cache_repository.py
import os
from typing import Any, Dict, List, Optional, cast

import numpy as np
from supabase import Client, create_client

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
        return self._connected


    async def get_cached_identification(self, image_hash: str) -> Optional[JSONDict]:
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
            self.client.table("identification_cache").update({"hit_count": current + 1}).eq("id", cache_id).execute()
        except Exception as e:
            print(f"Error incrementing cache hit: {e}")
