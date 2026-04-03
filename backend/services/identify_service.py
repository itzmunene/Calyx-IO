import os
import time
from typing import Any, Dict, List, Tuple

from fastapi import HTTPException

from backend.models import IdentificationResponse
from backend.services.preprocess_service import process_upload
from backend.services.image_processing_service import prepare_image
from backend.services.trait_extractor import extract_traits
from backend.services.candidate_service import resolve_candidates

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

async def identify_flower_service(*, image, use_cache, db, vision) -> IdentificationResponse:
    start_time = time.time()

    processed = await process_upload(image)
    prepared = prepare_image(processed.pil_image)
    low_quality = prepared.blur_score < 15

    if DEBUG:
        print("\n=== IDENTIFY DEBUG ===")
        print(f"Original size: {processed.pil_image.size}")
        print(f"Working size: {prepared.working.size}")
        print(f"Cropped size: {prepared.cropped_flower.size}")
        print(f"Blur score: {prepared.blur_score:.2f}")

    if DEBUG:
        prepared.cropped_flower.save(f"/tmp/calyx_{processed.image_hash}.jpg")

    if low_quality:
        print("Low quality image, continuing anyway.")

    traits = extract_traits(prepared.cropped_flower)

    if DEBUG:
        print("Pose traits:", traits.get("pose_traits", {}))
        print("Color traits:", traits.get("color_traits", {}))
        print("Shape traits:", traits.get("shape_traits", {}))
        print("Reproductive traits:", traits.get("reproductive_traits", {}))
        print("=====================\n")

    # ✅ CACHE
    if use_cache:
        cached = await db.get_cached_identification(processed.image_hash)
        if cached:
            await db.increment_cache_hit(cached["id"])
            return IdentificationResponse(
                **cached,
                response_time_ms=int((time.time() - start_time) * 1000),
                method="cache_hit",
            )

    # ✅ EMBEDDING
    try:
        embedding = await vision.get_embedding(prepared.cropped_flower)
    except Exception as exc:
        print(f"Embedding failed: {exc}")
        embedding = None

    # ✅ CANDIDATES
    candidates, method, exact_match_found, resolved_traits = await resolve_candidates(
        db=db,
        traits=traits,
        embedding = embedding if embedding is not None else []
    )

    
    response_time = int((time.time() - start_time) * 1000)

    # ❌ NO CANDIDATES AT ALL
    if not candidates:
        return IdentificationResponse(
            species_id=None, # type: ignore
            scientific_name="Unknown Flower",
            common_names=["Unknown Flower"],
            confidence=0.0,
            primary_image_url=None,
            method=method,
            traits_extracted=resolved_traits,
            alternatives=[],
            response_time_ms=response_time,
        )

    # ✅ SAFE TOP MATCH
    top_match = candidates[0]

    MIN_CONFIDENCE = 0.25

    # 🔶 SHORTLIST MODE (NO EXACT MATCH)
    if not exact_match_found or top_match.get("trait_score", 0.0) < MIN_CONFIDENCE:
        return IdentificationResponse(
            species_id=top_match.get("id"), # pyright: ignore[reportArgumentType]
            scientific_name=top_match.get("scientific_name", "Unknown"),
            common_names=top_match.get("common_names", ["Unknown"]),
            confidence=top_match.get("trait_score", 0.0),
            primary_image_url=top_match.get("primary_image_url"),
            method=method,
            traits_extracted=resolved_traits,
            alternatives=candidates[1:6], 
            response_time_ms=response_time,
        )

    # ✅ EXACT MATCH → CACHE IT
    await db.cache_identification(
        image_hash=processed.image_hash,
        species_id=top_match.get("id"),
        confidence=top_match.get("trait_score", 0.0),
        traits=resolved_traits,
        method=method,
    )

    return IdentificationResponse(
        species_id=top_match.get("id"), # type: ignore
        scientific_name=top_match["scientific_name"],
        common_names=top_match["common_names"],
        confidence=top_match.get("trait_score", 0.0),
        primary_image_url=top_match.get("primary_image_url"),
        method=method,
        traits_extracted=resolved_traits,
        alternatives=candidates[1:6],
        response_time_ms=response_time,
    )
