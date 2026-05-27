import math
from typing import Any, Dict, List, Tuple

JSONDict = Dict[str, Any]

WEIGHTS = {
    "color": 2.0,
    "shape": 3.0,
    "pose": 1.5,
}

probability = 0.0
trait_score = 0.0
color_finish = None
flower_size = "unknown"

def _safe_set(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, list):
        return {str(v).strip().lower() for v in value if str(v).strip()}
    return {str(value).strip().lower()}

def softmax(scores: List[float]) -> List[float]:
    exp_scores = [math.exp(s) for s in scores]
    total = sum(exp_scores)
    return [s / total for s in exp_scores]

def _flatten_traits_for_db(traits: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "petal_count": traits.get("petal_count"),
        "petal_shape_outer": traits.get("petal_shape_outer"),
        "petal_shape_inner": traits.get("petal_shape_inner"),
        "petal_overlap": traits.get("petal_overlap"),
        "petal_margin": traits.get("petal_margin"),
        "bloom_openness": traits.get("bloom_openness"),
    }

def _score_overlap(extracted: set[str], candidate: set[str], weight: float) -> float:
    if not extracted or not candidate:
        return 0.0

    overlap = len(extracted & candidate)
    if overlap == 0:
        return 0.0

    return min(overlap * weight, weight)

def _apply_confidence(score: float, confidence: float | None, threshold: float = 0.4) -> float:
    if confidence is None:
        return score
    if confidence < threshold:
        return score * 0.3
    return score * confidence

def _score_color_traits(extracted: Dict[str, Any], candidate_traits: Dict[str, Any]) -> float:
    score = 0.0

    confidence = extracted.get("petal_color_confidence") or extracted.get("color_confidence")

    petal_primary = _safe_set(extracted.get("petal_color_primary"))
    petal_secondary = _safe_set(extracted.get("petal_color_secondary"))
    fallback_primary = _safe_set(extracted.get("color_primary"))
    candidate_colors = _safe_set(candidate_traits.get("color_primary"))

    score += _score_overlap(petal_primary, candidate_colors, 0.25)
    score += _score_overlap(petal_secondary, candidate_colors, 0.10)

    if extracted.get("color_blending") == candidate_traits.get("color_blending"):
        score += 0.12

    # fallback boost
    if score == 0.0:
        score += 0.10  # don't zero out candidates completely

    return _apply_confidence(score, confidence)


def _score_shape_traits(extracted: Dict[str, Any], candidate_traits: Dict[str, Any]) -> float:
    score = 0.0

    # 👇 copy to avoid mutation
    extracted = dict(extracted)

    if extracted.get("petal_overlap") in ["moderate", "layered"]:
        extracted["petal_count"] = None

    extracted_size = extracted.get("flower_size")
    candidate_size = candidate_traits.get("flower_size")
    if extracted_size and candidate_size and str(extracted_size).lower() == str(candidate_size).lower():
        score += 0.12

    extracted_petal_count = extracted.get("petal_count")
    candidate_petal_count = candidate_traits.get("petal_count")
    if extracted_petal_count is not None and candidate_petal_count is not None:
        try:
            diff = abs(int(extracted_petal_count) - int(candidate_petal_count))
            if diff == 0:
                score += 0.18
            elif diff <= 2:
                score += 0.12 # tolerant match
            elif diff <= 4:
                score += 0.05 # weak tolerance
        except Exception:
            pass
    
    extracted_open = extracted.get("bloom_openness")
    candidate_open = candidate_traits.get("bloom_openness")
    if extracted_open and candidate_open:
        if extracted_open == candidate_open:
            score += 0.08
        elif extracted_open == "partially_open" and candidate_open == "open":
            score += 0.05 # partial credit for partially vs fully open

    extracted_overlap = extracted.get("petal_overlap")
    candidate_overlap = candidate_traits.get("petal_overlap")
    if extracted_overlap and candidate_overlap:
        if extracted_overlap == candidate_overlap:
            score += 0.16
        elif extracted_overlap == "moderate" and candidate_overlap in ["moderate", "separate"]:
            score += 0.10 # partial credit for moderate vs layered

    outer_shape = extracted.get("petal_shape_outer")
    candidate_outer = candidate_traits.get("petal_shape_outer")
    if outer_shape and candidate_outer:
        if outer_shape == candidate_outer:
            score += 0.10

    inner_shape = extracted.get("petal_shape_inner")
    candidate_inner = candidate_traits.get("petal_shape_inner")
    if inner_shape and candidate_inner:
        if inner_shape == candidate_inner:
            score += 0.12

    extracted_margin = extracted.get("petal_margin")
    candidate_margin = candidate_traits.get("petal_margin")
    if extracted_margin and candidate_margin and str(extracted_margin).lower() == str(candidate_margin).lower():
        score += 0.05

    return score


def _score_pose_traits(extracted: Dict[str, Any], candidate: JSONDict) -> float:
    candidate_traits = candidate.get("traits") or candidate
    score = 0.0

    extracted_flow = extracted.get("petal_flow")
    candidate_flow = candidate_traits.get("petal_flow")
    if extracted_flow and candidate_flow and str(extracted_flow).lower() == str(candidate_flow).lower():
        score += 0.12

    return score


def _score_reproductive_traits(extracted: Dict[str, Any], candidate: JSONDict) -> float:
    candidate_traits = candidate.get("traits") or candidate
    score = 0.0

    extracted_morphology = extracted.get("centre_morphology")
    candidate_morphology = candidate_traits.get("centre_morphology")
    if extracted_morphology and candidate_morphology:
        if str(extracted_morphology).lower() == str(candidate_morphology).lower():
            score += 0.4  # 🔥 dominant signal
        else:
            score -= 0.3  # ❗ penalty for mismatch

    for key, weight in [
        ("stamen_visible", 0.08),
        ("anther_visible", 0.08),
        ("stigma_visible", 0.06),
    ]:
        if key in extracted and key in candidate_traits:
            if bool(extracted[key]) == bool(candidate_traits[key]):
                score += weight

    return score


def score_candidate(candidate: JSONDict, traits: Dict[str, Any]) -> float:
    candidate_traits = candidate.get("traits") or candidate

    score = 0.0

    # ✅ ONLY SHAPE + POSE ACTIVE

    score += _score_shape_traits(traits, candidate_traits) * WEIGHTS["shape"]
    score += _score_pose_traits(traits, candidate) * WEIGHTS["pose"]

    return score


def rank_candidates(candidates: List[JSONDict], traits: Dict[str, Any]) -> List[JSONDict]:
    ranked: List[JSONDict] = []

    # 🔥 FIRST compute scores
    for candidate in candidates:
        candidate_copy = dict(candidate)

        score = score_candidate(candidate, traits)

        candidate_copy["trait_score"] = score
        candidate_copy["confidence"] = max(min(score, 1.0), 0.0)

        ranked.append(candidate_copy)

    # 🔥 SORT FIRST
    ranked.sort(key=lambda c: c.get("trait_score", 0.0), reverse=True)

    # 🔥 THEN compute softmax
    scores = [c["trait_score"] for c in ranked]
    probs = softmax(scores)

    for i, c in enumerate(ranked):
        c["probability"] = round(probs[i], 4)

    return ranked


async def resolve_candidates(
    db,
    traits: Dict[str, Any],
    embedding: List[float],
) -> Tuple[List[JSONDict], str, bool, Dict[str, Any]]:

    print("\n================ TRAIT PIPELINE DEBUG ================")

    # 🔥 RAW EXTRACTED TRAITS
    print("\n[EXTRACTED TRAITS]")
    for k, v in traits.items():
        print(f"{k}: {v}")

    # 🔥 FLATTENED FOR DB
    flat_traits = _flatten_traits_for_db(traits)

    print("\n[DB SEARCH TRAITS]")
    for k, v in flat_traits.items():
        print(f"{k}: {v}")

    print("=====================================================\n")

    # 1. Trait search
    candidates = await db.rpc(
        "search_by_traits",
        {"input_traits": flat_traits}
    )

    if not candidates:
        print("[NO TRAIT MATCHES] → falling back to embedding")

        if embedding:
            fallback = await db.rpc(
                "search_by_embedding",
                {"query_embedding": embedding}
            )
            return fallback[:20], "vector_shortlist", False, traits

        return [], "no_match", False, traits

    print(f"[CANDIDATES FOUND]: {len(candidates)}")

    # 🔥 PRINT RAW DB TRAITS
    for i, c in enumerate(candidates[:5]):
        print(f"\n[DB CANDIDATE {i+1}] {c.get('scientific_name')}")
        for k in flat_traits.keys():
            print(f"  {k}: {c.get(k)}")

    if len(candidates) == 1:
        return candidates, "trait_exact", True, traits

    # 🔍 Rank
    ranked = rank_candidates(candidates, traits)

    print("\n================ SCORING =================")

    for i, c in enumerate(ranked[:5]):
        print(f"\n[RANK {i+1}] {c.get('scientific_name')}")
        print(f"Score: {c.get('trait_score'):.4f}")
        print(f"Confidence: {c.get('confidence'):.4f}")

    print("=========================================\n")

    if embedding:
        refined = await db.refine_with_embedding(ranked, embedding)

        if refined:
            if len(refined) == 1:
                return refined, "trait_elimination", True, traits
            return refined[:20], "trait_shortlist", False, traits

    return ranked[:20], "trait_shortlist", False, traits