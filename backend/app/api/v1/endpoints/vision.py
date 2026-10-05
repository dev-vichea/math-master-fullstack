"""
Math Vision endpoint: Photo -> OCR -> Mathematical extraction -> Solver -> Steps.
"""

from __future__ import annotations

import re
from fastapi import APIRouter, Depends, File, UploadFile

from app.config import get_settings
from app.core.exceptions import MathProcessingError, VisionProcessingError
from app.core.logging import get_logger
from app.ocr.engines.base import BaseVisionEngine, VisionResult
from app.ocr.factory import create_vision_engine
from app.ocr.engines.stub import NotImplementedVisionEngine
from app.models.schemas import APIResponse
from app.services.math_service import MathService, get_math_service
from app.services.vision_service import VisionService

router = APIRouter()
logger = get_logger("app.api.vision")
settings = get_settings()

class HybridKhmerMathVisionEngine(BaseVisionEngine):
    """
    Intelligent vision engine that adapts to document content:
    - If Khmer characters or exercise instructions are detected, uses Kiri OCR with math radical normalization.
    - Otherwise uses the specialized LaTeX-OCR / pix2tex engine for pure formulas.
    """

    def __init__(self, formula_engine: BaseVisionEngine):
        self.formula_engine = formula_engine
        self._kiri: BaseVisionEngine | None = None

    def detect(self, image_bytes: bytes) -> VisionResult:
        if not image_bytes:
            return VisionResult(detected_text=None, confidence=0.0, error_message="Empty image")

        # 1. Prioritize formula_engine (e.g. specialized LaTeX-OCR / pix2tex) for mathematical formulas
        try:
            formula_res = self.formula_engine.detect(image_bytes)
            if formula_res.detected_text and not formula_res.error_message:
                return formula_res
        except Exception as exc:
            logger.warning(f"Formula engine failed: {exc}, attempting fallback to Kiri OCR")

        # 2. Fallback to Kiri OCR if formula engine did not succeed
        try:
            if self._kiri is None:
                from app.ocr.engines.kiri_ocr import KiriVisionEngine

                self._kiri = KiriVisionEngine()
            res = self._kiri.detect(image_bytes)
            if res.detected_text:
                clean = re.sub(r"([vV])\^?([0-9a-zA-Z]+)", r"\\sqrt{\2}", res.detected_text)
                clean = re.sub(r"--\s*", r"- ", clean)
                clean = re.sub(r"\+\+\s*", r"+ ", clean)
                return VisionResult(
                    detected_text=clean.strip(),
                    confidence=res.confidence or 0.92,
                    error_message=None,
                )
        except Exception as exc:
            logger.warning(f"Kiri OCR failed on fallback: {exc}")

        return VisionResult(
            detected_text=None,
            confidence=0.0,
            error_message="Could not recognize mathematical expression in image",
        )


# Module-level default vision engine (maintained for backwards compatibility with tests)
try:
    _raw_vision_engine: BaseVisionEngine = create_vision_engine(settings.vision_provider)
    _vision_engine: BaseVisionEngine = HybridKhmerMathVisionEngine(_raw_vision_engine)
except Exception as exc:
    logger.warning(
        f"Failed to initialize vision provider '{settings.vision_provider}': {exc}. "
        "Falling back to stub provider."
    )
    _vision_engine = NotImplementedVisionEngine()


def get_vision_engine() -> BaseVisionEngine:
    """Dependency provider for the vision OCR engine, defaulting to _vision_engine."""
    return _vision_engine


def get_vision_service(
    vision_engine: BaseVisionEngine = Depends(get_vision_engine),
    math_service: MathService = Depends(get_math_service),
) -> VisionService:
    """Dependency provider for VisionService with proper injection."""
    return VisionService(vision_engine=vision_engine, math_service=math_service)


@router.post("/math/ocr", response_model=APIResponse, tags=["vision"])
async def vision_ocr(
    image: UploadFile = File(...),
    vision_engine: BaseVisionEngine = Depends(get_vision_engine),
) -> APIResponse:
    """
    Fast OCR endpoint with quality validation: image -> validated LaTeX math without solving.
    """
    image_bytes = await image.read()
    try:
        from app.ocr.quality import MathOcrQualityPipeline
        from app.parser.exercise_parser.exercise_parser import parse_exercise

        pipeline = MathOcrQualityPipeline(formula_engine=vision_engine)
        pipeline_res = pipeline.process_image(image_bytes)
        candidate = pipeline_res.selected_candidate

        parsed_ex = parse_exercise(candidate.normalized_math_text or candidate.raw_ocr_text)
        instruction = parsed_ex.instruction
        exercise_title = parsed_ex.exercise_title
        sub_exercises = [
            {
                "label": s.label,
                "raw_text": s.raw_text,
                "expression": s.expression,
                "intent": s.intent,
            }
            for s in parsed_ex.sub_exercises
        ]

        return APIResponse(
            success=True,
            data={
                "detected_text": candidate.raw_ocr_text,
                "expression": candidate.normalized_math_text,
                "status": candidate.status.value,
                "confidence": candidate.confidence,
                "score": candidate.score,
                "suspicious_tokens": candidate.suspicious_tokens,
                "validation_issues": candidate.validation_issues,
                "detected_prefix": candidate.detected_prefix,
                "detected_suffix": candidate.detected_suffix,
                "exercise_title": exercise_title,
                "instruction": instruction,
                "sub_exercises": sub_exercises,
                "candidates": [
                    {
                        "raw_text": c.raw_ocr_text,
                        "normalized": c.normalized_math_text,
                        "status": c.status.value,
                        "confidence": c.confidence,
                        "score": c.score,
                        "variant": c.variant_name,
                    }
                    for c in pipeline_res.all_candidates
                ],
            },
            error=None,
        )
    except Exception as exc:
        logger.error(f"OCR detection error: {exc}", exc_info=True)
        return APIResponse(success=False, data=None, error=f"OCR failed: {str(exc)}")


@router.post("/math/vision", response_model=APIResponse, tags=["vision"])
async def vision_solve(
    image: UploadFile = File(...),
    vision_service: VisionService = Depends(get_vision_service),
) -> APIResponse:
    """
    Math Vision endpoint: photo -> OCR -> solve -> step-by-step solution.

    This endpoint processes a single math problem from an image and returns
    the solved result. For images with multiple sub-exercises, use /math/vision/batch.
    """
    image_bytes = await image.read()

    try:
        data = vision_service.process_image(image_bytes)
        return APIResponse(success=True, data=data, error=None)
    except VisionProcessingError as exc:
        return APIResponse(success=False, data=None, error=exc.message)
    except MathProcessingError as exc:
        return APIResponse(success=False, data=exc.details, error=exc.message)


@router.post("/math/vision/batch", response_model=APIResponse, tags=["vision"])
async def vision_solve_batch(
    image: UploadFile = File(...),
    vision_service: VisionService = Depends(get_vision_service),
) -> APIResponse:
    """
    Batch Math Vision endpoint: photo -> OCR -> parse multi-exercise -> structured problems.

    This endpoint handles images containing multiple sub-exercises (e.g., Exercise 1: a) b) c))
    and returns a structured MultiProblemSet with:
    - Exercise title and instruction
    - Individual MathProblem objects for each sub-exercise
    - Confidence scores and warnings for each problem
    - Overall batch metadata

    Use this endpoint when you expect multiple problems in one image.
    Each problem can then be solved individually via POST /math/solve.
    """
    image_bytes = await image.read()

    try:
        problem_set = vision_service.process_image_batch(image_bytes)

        return APIResponse(
            success=True,
            data=problem_set.to_dict(),
            error=None,
        )
    except VisionProcessingError as exc:
        logger.error(f"Vision processing error in batch mode: {exc}")
        return APIResponse(success=False, data=None, error=exc.message)
    except Exception as exc:
        logger.error(f"Unexpected error in batch vision processing: {exc}", exc_info=True)
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to process image batch: {str(exc)}",
        )
