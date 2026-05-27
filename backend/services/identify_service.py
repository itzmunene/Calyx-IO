import os
import time
from typing import Dict, Any

from fastapi import Request

from backend.models import IdentificationResponse
from backend.services.preprocess_service import process_upload
from backend.services.image_processing_service import prepare_image
from backend.services.trait_extractor import extract_traits
from backend.services.candidate_service import resolve_candidates

from backend.services.debug_image import (
    generate_debug_image,
    save_debug_image,
    build_debug_url,
)
from PIL import Image
import io


DEBUG = os.getenv("DEBUG", "false").lower() == "true"

DEBUG_IMAGE_DIR = "/tmp/calyx_debug"
os.makedirs(DEBUG_IMAGE_DIR, exist_ok=True)


async def identify_flower_service(*, image, use_cache, db, vision, request: Request) -> IdentificationResponse:
    start_time = time.time()

    processed = await process_upload(image)
    prepared = prepare_image(processed.pil_image)

    traits = await extract_traits(
        prepared.cropped_flower,
        image_metadata=processed.image_metadata
    )

    if processed.image_metadata:
        traits.update(processed.image_metadata)

    # =========================
    # 🔥 DEBUG IMAGE PIPELINE (SINGLE SOURCE OF TRUTH)
    # =========================

    debug_image_url = None

    if DEBUG:
        try:
            print("\n🧠 ================= DEBUG IMAGE PIPELINE =================")

            print("📍 Stage 1: Pose + Trait Overlay Rendering START")

            debug_img = generate_debug_image(
                img=prepared.cropped_flower,
                pose_data=traits,
                shape_data=traits,
            )

            print("✅ Stage 1 COMPLETE")

            print("💾 Stage 2: Saving debug image")

            filename = save_debug_image(debug_img)

            print(f"📁 Saved as: {filename}")

            print("🌐 Stage 3: Building debug URL")

            debug_image_url = build_debug_url(request, filename)

            print(f"🔗 DEBUG URL: {debug_image_url}")

            print("🧠 ================= END DEBUG PIPELINE =================\n")

        except Exception as e:
            print(f"❌ DEBUG IMAGE FAILED: {e}")

    # =========================
    # EMBEDDING
    # =========================
    try:
        embedding = await vision.get_embedding(prepared.cropped_flower)
    except Exception:
        embedding = None

    candidates, method, exact_match_found, resolved_traits = await resolve_candidates(
        db=db,
        traits=traits,
        embedding=embedding if embedding else []
    )

    response_time = int((time.time() - start_time) * 1000)

    # ❌ NO MATCH
    if not candidates:
        return IdentificationResponse(
            species_id=None,
            scientific_name="Unknown Flower",
            common_names=["Unknown Flower"],
            confidence=0.0,
            primary_image_url=None,
            debug_image_url=debug_image_url,  # ✅ WORKS NOW
            method=method,
            traits_extracted=resolved_traits,
            alternatives=[],
            response_time_ms=response_time,
        )

    # ✅ TOP MATCH
    top_match = candidates[0]

    return IdentificationResponse(
        species_id=top_match.get("id"),
        scientific_name=top_match.get("scientific_name", "Unknown Flower"),
        common_names=top_match.get("common_names", ["Unknown Flower"]),
        confidence=top_match.get("confidence", 0.0),
        primary_image_url=top_match.get("primary_image_url"),
        debug_image_url=debug_image_url,  # ✅ WORKS NOW
        method=method,
        traits_extracted=resolved_traits,
        alternatives=candidates[1:5],  # Include top 5 candidates as alternatives
        response_time_ms=response_time,
    )