"""
Math Vision endpoint: Photo -> OCR -> Mathematical extraction -> Solver -> Steps.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from app.config import get_settings
from app.core.exceptions import MathProcessingError, VisionProcessingError
from app.core.logging import get_logger
from app.ocr.engines.base import BaseVisionEngine
from app.ocr.factory import create_vision_engine
from app.ocr.engines.stub import NotImplementedVisionEngine
from app.models.schemas import APIResponse
from app.services.math_service import MathService, get_math_service
from app.services.vision_service import VisionService

router = APIRouter()
logger = get_logger("app.api.vision")
settings = get_settings()

# Module-level default vision engine (maintained for backwards compatibility with tests)
try:
    _vision_engine: BaseVisionEngine = create_vision_engine(settings.vision_provider)
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
