import time
from typing import Any, Dict, List, Tuple

from fastapi import HTTPException

from backend.models import IdentificationResponse
from backend.services.preprocess_service import process_upload
from backend.services.image_processing_service import prepare_image
from backend.services.trait_extractor import extract_traits
from backend.services.candidate_service import resolve_candidates


async def identify_flower_service(*, image, use_cache, db, vision) -> IdentificationResponse:
    start_time = time.time()

    processed = await process_upload(image)
    prepared = prepare_image(processed.pil_image)

    print("\n=== IDENTIFY DEBUG ===")
    print(f"Original size: {processed.pil_image.size}")
    print(f"Working size: {prepared.working.size}")
    print(f"Cropped size: {prepared.cropped_flower.size}")
    print(f"Blur score: {prepared.blur_score:.2f}")

    prepared.cropped_flower.save("/tmp/calyx_last_crop.jpg")

    if prepared.blur_score < 20:
        raise HTTPException(
            status_code=400,
            detail="Image looks too blurry. Try a clearer photo with the flower centred.",
        )

    traits = extract_traits(prepared.cropped_flower)

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
    candidates, method, exact_match_found = await resolve_candidates(
        db=db,
        traits=traits,
        embedding=embedding, # type: ignore
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
            traits_extracted=traits,
            alternatives=[],
            response_time_ms=response_time,
        )

    # ✅ SAFE TOP MATCH
    top_match = candidates[0]

    # 🔶 SHORTLIST MODE (NO EXACT MATCH)
    if not exact_match_found:
        return IdentificationResponse(
            species_id=top_match.get("id"), # pyright: ignore[reportArgumentType]
            scientific_name=top_match.get("scientific_name", "Unknown"),
            common_names=top_match.get("common_names", ["Unknown"]),
            confidence=top_match.get("confidence", 0.0),
            primary_image_url=top_match.get("primary_image_url"),
            method=method,
            traits_extracted=traits,
            alternatives=candidates[:20],  # 🔥 TOP 20 shortlist
            response_time_ms=response_time,
        )

    # ✅ EXACT MATCH → CACHE IT
    await db.cache_identification(
        image_hash=processed.image_hash,
        species_id=top_match["id"],
        confidence=top_match["confidence"],
        traits=traits,
        method=method,
    )

    return IdentificationResponse(
        species_id=top_match["id"],
        scientific_name=top_match["scientific_name"],
        common_names=top_match["common_names"],
        confidence=top_match["confidence"],
        primary_image_url=top_match.get("primary_image_url"),
        method=method,
        traits_extracted=traits,
        alternatives=candidates[1:4],
        response_time_ms=response_time,
    )