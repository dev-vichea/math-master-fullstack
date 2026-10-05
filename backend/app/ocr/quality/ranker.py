"""
Math OCR Candidate Ranker.

Ranks candidates generated across preprocessing variants, prioritizing
verified syntax and SymPy parseability over raw engine confidence.
"""

from __future__ import annotations

from typing import Any

from app.ocr.quality.models import CandidateStatus, MathOcrCandidate, OcrPipelineResult


def rank_and_select_candidates(
    candidates: list[MathOcrCandidate],
    debug_trace: list[dict[str, Any]] | None = None,
) -> OcrPipelineResult:
    """
    Ranks candidates and selects the optimal verified or cleanest candidate.

    Ranking Order:
    1. Status: VERIFIED > NEEDS_REVIEW > INVALID
    2. SymPy Parseability: True > False
    3. Composite score (includes penalty for suspicious artifacts)
    4. Confidence score
    """
    trace = debug_trace or []

    if not candidates:
        fallback = MathOcrCandidate(
            raw_ocr_text="",
            normalized_math_text="",
            status=CandidateStatus.INVALID,
            confidence=0.0,
            source_provider="none",
            variant_name="none",
            score=-100.0,
            validation_issues=["No candidates provided"],
            is_parseable=False,
        )
        return OcrPipelineResult(
            selected_candidate=fallback,
            all_candidates=[],
            original_raw_text="",
            status=CandidateStatus.INVALID,
            confidence=0.0,
            debug_trace=trace,
        )

    # Sort descending by:
    # 1. Status priority (VERIFIED = 2, NEEDS_REVIEW = 1, INVALID = 0)
    # 2. is_parseable (True = 1, False = 0)
    # 3. score (float)
    # 4. confidence (float)
    def status_key(c: MathOcrCandidate) -> int:
        if c.status == CandidateStatus.VERIFIED:
            return 2
        if c.status == CandidateStatus.NEEDS_REVIEW:
            return 1
        return 0

    sorted_candidates = sorted(
        candidates,
        key=lambda c: (status_key(c), int(c.is_parseable), c.score, c.confidence),
        reverse=True,
    )

    selected = sorted_candidates[0]

    trace.append({
        "step": "ranking_and_selection",
        "total_candidates": len(sorted_candidates),
        "selected_status": selected.status.value,
        "selected_score": selected.score,
        "selected_normalized": selected.normalized_math_text,
        "selected_provider": selected.source_provider,
        "selected_variant": selected.variant_name,
    })

    return OcrPipelineResult(
        selected_candidate=selected,
        all_candidates=sorted_candidates,
        original_raw_text=selected.raw_ocr_text,
        status=selected.status,
        confidence=selected.confidence,
        debug_trace=trace,
    )
