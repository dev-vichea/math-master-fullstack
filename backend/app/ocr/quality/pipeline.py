"""
Math OCR Quality Pipeline.

Orchestrates:
1. Image preprocessing variant generation (trimmed, contrast, binary)
2. Routing to formula vs text OCR providers
3. Multiple candidate generation
4. Normalization and validation
5. Candidate ranking and selection
6. Structured debug logging
"""

from __future__ import annotations

import logging
from typing import Any

from app.ocr.engines.base import BaseVisionEngine, VisionResult
from app.ocr.quality.models import CandidateStatus, MathOcrCandidate, OcrPipelineResult
from app.ocr.quality.preprocessor import generate_preprocessing_variants
from app.ocr.quality.ranker import rank_and_select_candidates
from app.ocr.quality.validator import validate_math_candidate

logger = logging.getLogger("app.ocr.quality.pipeline")


class MathOcrQualityPipeline:
    """End-to-end OCR Quality Pipeline ensuring no unverified garbage reaches the solver."""

    def __init__(self, formula_engine: BaseVisionEngine | None = None) -> None:
        self.formula_engine = formula_engine

    def process_image(self, image_bytes: bytes, max_variants: int = 3) -> OcrPipelineResult:
        """
        Runs the full OCR quality pipeline on raw image bytes.

        Steps:
        1. Preprocessing variants (original, trimmed, contrast, binary)
        2. Execute OCR on variants
        3. Normalize & validate each output into a MathOcrCandidate
        4. Rank candidates and pick the best one
        5. Record structured debug trace
        """
        debug_trace: list[dict[str, Any]] = []

        if not image_bytes:
            debug_trace.append({"step": "init", "error": "Empty image bytes"})
            return rank_and_select_candidates([], debug_trace=debug_trace)

        # 1. Generate preprocessing variants
        variants = generate_preprocessing_variants(image_bytes)
        debug_trace.append({
            "step": "preprocessing",
            "variants_generated": [v["variant_name"] for v in variants[:max_variants]],
        })

        candidates: list[MathOcrCandidate] = []

        # 2. Lazy load formula engine if needed
        engine = self.formula_engine
        if engine is None:
            from app.ocr.engines.pix2tex_engine import Pix2TexVisionEngine

            engine = Pix2TexVisionEngine()
            self.formula_engine = engine

        # 3. Run OCR on each variant
        for var_info in variants[:max_variants]:
            v_name = var_info["variant_name"]
            v_bytes = var_info["image_bytes"]
            v_bbox = var_info.get("bounding_box")

            try:
                res: VisionResult = engine.detect(v_bytes)
                raw_text = res.detected_text or ""
                conf = res.confidence or 0.85

                engine_name = getattr(engine, "name", "pix2tex")
                provider_str = "mock" if hasattr(engine_name, "_mock_name") or hasattr(engine_name, "mock") else str(engine_name)

                candidate = validate_math_candidate(
                    raw_ocr_text=raw_text,
                    confidence=conf,
                    source_provider=provider_str,
                    variant_name=v_name,
                    bounding_box=v_bbox,
                )
                candidates.append(candidate)

                debug_trace.append({
                    "step": "candidate_evaluated",
                    "variant": v_name,
                    "raw_text": raw_text,
                    "normalized": candidate.normalized_math_text,
                    "status": candidate.status.value,
                    "confidence": candidate.confidence,
                    "score": candidate.score,
                    "suspicious_tokens": candidate.suspicious_tokens,
                })

                # If first candidate is perfectly VERIFIED with high confidence, we can proceed
                if candidate.status == CandidateStatus.VERIFIED and candidate.confidence >= 0.90:
                    break

            except Exception as exc:
                logger.warning(f"Error processing variant '{v_name}': {exc}")
                debug_trace.append({
                    "step": "candidate_error",
                    "variant": v_name,
                    "error": str(exc),
                })

        # 4. Rank and select best candidate
        pipeline_result = rank_and_select_candidates(candidates, debug_trace=debug_trace)

        logger.info(
            f"MathOcrQualityPipeline: selected '{pipeline_result.selected_candidate.normalized_math_text}' "
            f"[status={pipeline_result.status.value}, score={pipeline_result.selected_candidate.score}, "
            f"variant={pipeline_result.selected_candidate.variant_name}]"
        )

        return pipeline_result
