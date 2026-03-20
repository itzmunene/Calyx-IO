# backend/repositories/analytics_repository.py

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

    async def save_feedback(
        self,
        identification_id: str,
        is_correct: bool,
        correct_species_id: Optional[str],
        notes: Optional[str],
    ) -> None:
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
        try:
            total_identifications = self.client.table("identification_cache").select("id", count=cast(Any, "exact")).execute()
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
