"""
Math OCR Quality Pipeline.

Orchestrates:
1. Direct single-pass OCR execution
2. Normalization and mathematical validation
3. Structured debug logging

Enhanced to support region-based processing for selective formula OCR.
"""

from __future__ import annotations

import logging
from io import BytesIO
from typing import Any

from app.models.document import BoundingBox
from app.ocr.engines.base import BaseVisionEngine, VisionResult
from app.ocr.quality.models import CandidateStatus, MathOcrCandidate, OcrPipelineResult
from app.ocr.quality.validator import validate_math_candidate

logger = logging.getLogger("app.ocr.quality.pipeline")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL not available - region cropping will not work")


class MathOcrQualityPipeline:
    """
    End-to-end OCR Quality Pipeline ensuring no unverified garbage reaches the solver.
    
    Now supports region-based processing for selective formula OCR on cropped areas.
    """

    def __init__(self, formula_engine: BaseVisionEngine | None = None) -> None:
        self.formula_engine = formula_engine

    def process_image(self, image_bytes: bytes, max_variants: int = 3) -> OcrPipelineResult:
        """
        Process a complete image (backward compatible).
        
        Args:
            image_bytes: Full image bytes
            max_variants: Maximum preprocessing variants to try
            
        Returns:
            OcrPipelineResult with best candidate
        """
        return self.process_region(image_bytes, region_bbox=None, max_variants=max_variants)

    def process_region(
        self,
        image_bytes: bytes,
        region_bbox: BoundingBox | None = None,
        max_variants: int = 3,
    ) -> OcrPipelineResult:
        """
        Process image or image region through OCR quality pipeline.
        
        This method supports both:
        - Full image processing (region_bbox=None) - backward compatible
        - Region-based processing (region_bbox provided) - for selective formula OCR
        
        Steps:
        1. Crop region if bbox provided
        2. Direct single-pass OCR execution on image
        3. Normalize & validate output into a MathOcrCandidate
        4. Record structured debug trace
        
        Args:
            image_bytes: Full image or pre-cropped region bytes
            region_bbox: Optional bounding box to crop from image (normalized 0-1 coords)
            max_variants: Deprecated/legacy parameter (retained for backward compatibility)
            
        Returns:
            OcrPipelineResult with candidate result
        """
        debug_trace: list[dict[str, Any]] = []

        if not image_bytes:
            debug_trace.append({"step": "init", "error": "Empty image bytes"})
            empty_cand = MathOcrCandidate(
                raw_ocr_text="",
                normalized_math_text="",
                status=CandidateStatus.INVALID,
                confidence=0.0,
                source_provider="none",
                variant_name="original",
                score=-100.0,
                validation_issues=["Empty image bytes"],
                is_parseable=False,
            )
            return OcrPipelineResult(
                selected_candidate=empty_cand,
                all_candidates=[empty_cand],
                original_raw_text="",
                status=CandidateStatus.INVALID,
                confidence=0.0,
                debug_trace=debug_trace,
            )

        # Step 0: Crop region if bounding box provided
        processed_image_bytes = image_bytes
        if region_bbox is not None:
            try:
                processed_image_bytes = self._crop_region(image_bytes, region_bbox)
                debug_trace.append({
                    "step": "region_crop",
                    "bbox": region_bbox.to_dict(),
                    "cropped": True,
                })
            except Exception as exc:
                logger.warning(f"Failed to crop region: {exc}, using full image")
                debug_trace.append({
                    "step": "region_crop",
                    "error": str(exc),
                    "fallback": "full_image",
                })

        # 1. Lazy load formula engine if needed
        engine = self.formula_engine
        if engine is None:
            from app.ocr.engines.pix2tex_engine import Pix2TexVisionEngine

            engine = Pix2TexVisionEngine()
            self.formula_engine = engine

        # 2. Direct single-pass OCR execution (no multi-variant ranking step)
        try:
            res: VisionResult = engine.detect(processed_image_bytes)
            raw_text = res.detected_text or ""
            conf = res.confidence or 0.85

            engine_name = getattr(engine, "name", "pix2tex")
            provider_str = "mock" if hasattr(engine_name, "_mock_name") or hasattr(engine_name, "mock") else str(engine_name)

            candidate = validate_math_candidate(
                raw_ocr_text=raw_text,
                confidence=conf,
                source_provider=provider_str,
                variant_name="original",
                exercise_metadata=getattr(res, "exercise_metadata", None),
            )
        except Exception as exc:
            logger.warning(f"Error processing OCR: {exc}")
            debug_trace.append({"step": "candidate_error", "error": str(exc)})
            candidate = MathOcrCandidate(
                raw_ocr_text="",
                normalized_math_text="",
                status=CandidateStatus.INVALID,
                confidence=0.0,
                source_provider="error",
                variant_name="original",
                score=-10.0,
                validation_issues=[str(exc)],
                is_parseable=False,
            )

        debug_trace.append({
            "step": "candidate_evaluated",
            "variant": "original",
            "raw_text": candidate.raw_ocr_text,
            "normalized": candidate.normalized_math_text,
            "status": candidate.status.value,
            "confidence": candidate.confidence,
            "score": candidate.score,
            "suspicious_tokens": candidate.suspicious_tokens,
        })

        pipeline_result = OcrPipelineResult(
            selected_candidate=candidate,
            all_candidates=[candidate],
            original_raw_text=candidate.raw_ocr_text,
            status=candidate.status,
            confidence=candidate.confidence,
            debug_trace=debug_trace,
        )

        logger.info(
            f"MathOcrQualityPipeline: '{pipeline_result.selected_candidate.normalized_math_text}' "
            f"[status={pipeline_result.status.value}, score={pipeline_result.selected_candidate.score}]"
        )

        return pipeline_result

    def _crop_region(self, image_bytes: bytes, bbox: BoundingBox) -> bytes:
        """
        Crop a region from the image using normalized bounding box coordinates.
        
        Args:
            image_bytes: Full image bytes
            bbox: Bounding box with normalized coordinates (0.0-1.0)
            
        Returns:
            Cropped image bytes
            
        Raises:
            ImportError: If PIL is not available
            ValueError: If bounding box is invalid
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL required for region cropping")
        
        # Validate bbox
        if not (0 <= bbox.x <= 1 and 0 <= bbox.y <= 1):
            raise ValueError(f"Invalid bounding box coordinates: x={bbox.x}, y={bbox.y}")
        if not (0 < bbox.width <= 1 and 0 < bbox.height <= 1):
            raise ValueError(f"Invalid bounding box dimensions: width={bbox.width}, height={bbox.height}")
        
        # Load image
        image = Image.open(BytesIO(image_bytes))
        width, height = image.size
        
        # Convert normalized coordinates to pixel coordinates
        left = int(bbox.x * width)
        top = int(bbox.y * height)
        right = int((bbox.x + bbox.width) * width)
        bottom = int((bbox.y + bbox.height) * height)
        
        # Ensure coordinates are within image bounds
        left = max(0, min(left, width - 1))
        top = max(0, min(top, height - 1))
        right = max(left + 1, min(right, width))
        bottom = max(top + 1, min(bottom, height))
        
        # Crop image
        cropped = image.crop((left, top, right, bottom))
        
        # Convert back to bytes
        output = BytesIO()
        cropped.save(output, format=image.format or "PNG")
        return output.getvalue()
