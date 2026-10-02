"""
Worksheet processing endpoints.

Provides end-to-end processing of math worksheet images:
- Upload image
- OCR extraction
- Exercise structure parsing
- Automatic problem solving
"""

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel, Field

from app.services.worksheet_service import WorksheetProcessor, get_worksheet_processor

router = APIRouter()


class WorksheetProcessResponse(BaseModel):
    """Response model for worksheet processing."""

    success: bool
    data: dict | None = None
    error: str | None = None


class WorksheetStatisticsResponse(BaseModel):
    """Response model for worksheet statistics only."""

    success: bool
    statistics: dict | None = None
    error: str | None = None


@router.post("/worksheets/process", response_model=WorksheetProcessResponse, tags=["worksheets"])
async def process_worksheet(
    image: UploadFile = File(..., description="Worksheet image (PNG, JPEG, etc.)"),
    processor: WorksheetProcessor = Depends(get_worksheet_processor),
) -> WorksheetProcessResponse:
    """
    Process a complete math worksheet image.

    This endpoint:
    1. Extracts text from the image using OCR
    2. Parses the exercise structure (instructions + problems)
    3. Solves each problem automatically
    4. Returns structured results with solutions

    Args:
        image: Uploaded image file containing the worksheet

    Returns:
        WorksheetProcessResponse containing:
        - ocr: OCR results (detected text, confidence, errors)
        - exercise: Parsed structure (instruction, sections, problems)
        - solutions: List of solved problems with steps
        - statistics: Problem counts, label distribution, etc.
        - validation: Structure validation results

    Example response:
        {
            "success": true,
            "data": {
                "ocr": {
                    "detected_text": "ចូរដាក់ជាកត្តាកត់\\nក. 3x² - 9x\\nខ. x³ + 8",
                    "confidence": 0.95,
                    "error": null
                },
                "exercise": {
                    "instruction": {
                        "text": "ចូរដាក់ជាកត្តាកត់",
                        "type": "factorize",
                        "normalized": "ចូរដាក់ជាកត្តាកត់"
                    },
                    "sections": [{
                        "title": null,
                        "instruction": "ចូរដាក់ជាកត្តាកត់",
                        "problems": [
                            {"label": "ក", "expression": "3x² - 9x"},
                            {"label": "ខ", "expression": "x³ + 8"}
                        ]
                    }]
                },
                "solutions": [
                    {
                        "label": "ក",
                        "expression": "3x² - 9x",
                        "problem_type": "factorization",
                        "answer": "3*x*(x - 3)",
                        "is_verified": true,
                        "steps": [...]
                    },
                    {
                        "label": "ខ",
                        "expression": "x³ + 8",
                        "problem_type": "factorization",
                        "answer": "(x + 2)*(x² - 2*x + 4)",
                        "is_verified": true,
                        "steps": [...]
                    }
                ],
                "statistics": {
                    "total_problems": 2,
                    "sections": 1,
                    "has_instruction": true,
                    "label_distribution": {"khmer_lower": 2}
                },
                "validation": {
                    "is_valid": true,
                    "errors": []
                }
            },
            "error": null
        }
    """
    try:
        # Read image bytes
        image_bytes = await image.read()

        # Process the worksheet
        result = processor.process_image(image_bytes)

        # Convert to dictionary
        data = result.to_dict()

        return WorksheetProcessResponse(success=True, data=data, error=None)

    except Exception as e:
        return WorksheetProcessResponse(success=False, data=None, error=f"Processing failed: {str(e)}")


@router.post("/worksheets/statistics", response_model=WorksheetStatisticsResponse, tags=["worksheets"])
async def get_worksheet_statistics(
    image: UploadFile = File(..., description="Worksheet image (PNG, JPEG, etc.)"),
    processor: WorksheetProcessor = Depends(get_worksheet_processor),
) -> WorksheetStatisticsResponse:
    """
    Extract statistics from a worksheet image without solving problems.

    This is a lighter-weight endpoint that:
    1. Runs OCR on the image
    2. Parses the exercise structure
    3. Returns statistics only (no solving)

    Useful for:
    - Quick validation of worksheet structure
    - Checking problem counts before processing
    - Testing OCR quality

    Args:
        image: Uploaded image file containing the worksheet

    Returns:
        Statistics including:
        - total_problems: Number of problems found
        - sections: Number of sections
        - has_instruction: Whether instruction was detected
        - label_distribution: Count of each label type
        - instruction_types: Distribution of instruction types

    Example response:
        {
            "success": true,
            "statistics": {
                "total_problems": 10,
                "sections": 2,
                "has_instruction": true,
                "label_distribution": {
                    "khmer_lower": 5,
                    "arabic": 5
                },
                "instruction_types": {
                    "factorize": 1
                }
            },
            "error": null
        }
    """
    try:
        # Read image bytes
        image_bytes = await image.read()

        # Run OCR only
        ocr_result = processor.vision_engine.detect(image_bytes)

        if ocr_result.error_message or not ocr_result.detected_text:
            return WorksheetStatisticsResponse(
                success=False, statistics=None, error=ocr_result.error_message or "OCR failed"
            )

        # Parse structure (no solving)
        processing_result = processor.exercise_service.process_text(ocr_result.detected_text)

        # Get statistics
        statistics = processor.exercise_service.get_statistics(processing_result.exercise)

        return WorksheetStatisticsResponse(success=True, statistics=statistics, error=None)

    except Exception as e:
        return WorksheetStatisticsResponse(success=False, statistics=None, error=f"Statistics failed: {str(e)}")


@router.post("/worksheets/validate", response_model=WorksheetProcessResponse, tags=["worksheets"])
async def validate_worksheet(
    image: UploadFile = File(..., description="Worksheet image (PNG, JPEG, etc.)"),
    processor: WorksheetProcessor = Depends(get_worksheet_processor),
) -> WorksheetProcessResponse:
    """
    Validate worksheet structure without solving problems.

    This endpoint:
    1. Runs OCR on the image
    2. Parses the exercise structure
    3. Validates structure (checks for issues)
    4. Returns validation results (no solving)

    Useful for:
    - Pre-flight validation before processing
    - Checking if worksheet is well-formed
    - Debugging OCR/parsing issues

    Args:
        image: Uploaded image file containing the worksheet

    Returns:
        Validation results including:
        - exercise structure
        - validation errors (if any)
        - statistics

    Example response:
        {
            "success": true,
            "data": {
                "exercise": {...},
                "validation": {
                    "is_valid": false,
                    "errors": [
                        "Problem 'ក' has empty expression",
                        "Section 0 has no problems"
                    ]
                },
                "statistics": {...}
            },
            "error": null
        }
    """
    try:
        # Read image bytes
        image_bytes = await image.read()

        # Run OCR
        ocr_result = processor.vision_engine.detect(image_bytes)

        if ocr_result.error_message or not ocr_result.detected_text:
            return WorksheetProcessResponse(
                success=False,
                data=None,
                error=ocr_result.error_message or "OCR failed",
            )

        # Parse structure
        processing_result = processor.exercise_service.process_text(ocr_result.detected_text)
        exercise = processing_result.exercise

        # Validate
        is_valid, validation_errors = processor.exercise_service.validate_exercise(exercise)

        # Get statistics
        statistics = processor.exercise_service.get_statistics(exercise)

        # Build response (no solutions)
        data = {
            "exercise": {
                "instruction": {
                    "text": exercise.instruction.text if exercise.instruction else None,
                    "type": exercise.instruction.type.value if exercise.instruction else None,
                    "normalized": exercise.instruction.normalized_text if exercise.instruction else None,
                }
                if exercise.instruction
                else None,
                "sections": [
                    {
                        "title": section.title,
                        "instruction": section.instruction.text if section.instruction else None,
                        "problems": [
                            {
                                "label": problem.label.text if problem.label else None,
                                "expression": problem.expression,
                            }
                            for problem in section.problems
                        ],
                    }
                    for section in exercise.sections
                ],
            },
            "validation": {
                "is_valid": is_valid,
                "errors": validation_errors,
            },
            "statistics": statistics,
        }

        return WorksheetProcessResponse(success=True, data=data, error=None)

    except Exception as e:
        return WorksheetProcessResponse(success=False, data=None, error=f"Validation failed: {str(e)}")
