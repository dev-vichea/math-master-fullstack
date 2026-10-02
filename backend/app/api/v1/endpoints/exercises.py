"""
Exercise analysis endpoints.

Provides REST API for processing complete math exercise documents
with instructions and multiple problems.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.exercise_service import ExerciseService

router = APIRouter()


class ExerciseTextRequest(BaseModel):
    """Request model for text-based exercise analysis."""

    text: str = Field(..., description="Exercise text with instructions and problems")
    language: str = Field(
        default="km",
        description="Language code (km for Khmer, en for English)",
        pattern="^(km|en)$",
    )


class ExerciseResponse(BaseModel):
    """Response model for exercise analysis."""

    success: bool = Field(..., description="Whether processing was successful")
    exercise: dict[str, Any] = Field(..., description="Structured exercise document")
    statistics: dict[str, Any] | None = Field(
        None, description="Exercise statistics"
    )
    validation: dict[str, Any] | None = Field(
        None, description="Validation results"
    )
    errors: list[str] = Field(default_factory=list, description="Error messages")
    warnings: list[str] = Field(default_factory=list, description="Warning messages")


class ExerciseValidationResponse(BaseModel):
    """Response model for exercise validation."""

    is_valid: bool = Field(..., description="Whether exercise structure is valid")
    errors: list[str] = Field(
        default_factory=list, description="Validation error messages"
    )


class ExerciseStatisticsResponse(BaseModel):
    """Response model for exercise statistics."""

    sections: int = Field(..., description="Number of sections")
    total_problems: int = Field(..., description="Total number of problems")
    problems_per_section: list[int] = Field(
        ..., description="Problems in each section"
    )
    instruction_types: list[str] = Field(..., description="Instruction types detected")
    problem_types: dict[str, int] = Field(
        ..., description="Distribution of problem types"
    )
    average_confidence: float = Field(..., description="Average confidence score")
    languages: list[str] = Field(..., description="Languages detected")


# Initialize service
exercise_service = ExerciseService()


@router.post(
    "/analyze",
    response_model=ExerciseResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze exercise text",
    description="""
Analyze a complete math exercise document with instructions and multiple problems.

The service will:
- Detect mathematical instructions (solve, factor, simplify, etc.)
- Extract numbered/lettered problems
- Classify problems using instruction context
- Build structured exercise document with sections

Supports both Khmer and English text with various label formats (a), b), ក., ខ., 1), 2), etc.)
    """,
)
def analyze_exercise(request: ExerciseTextRequest) -> ExerciseResponse:
    """
    Analyze exercise text and return structured document.

    Args:
        request: Exercise text and language

    Returns:
        ExerciseResponse with structured exercise, statistics, and validation

    Raises:
        HTTPException: If processing fails critically
    """
    try:
        # Process exercise text
        result = exercise_service.process_text(
            text=request.text, language=request.language
        )

        # Get statistics
        statistics = None
        if result.success and result.exercise:
            statistics = exercise_service.get_statistics(result.exercise)

        # Validate structure
        validation = None
        if result.success and result.exercise:
            is_valid, validation_errors = exercise_service.validate_exercise(
                result.exercise
            )
            validation = {"is_valid": is_valid, "errors": validation_errors}

        return ExerciseResponse(
            success=result.success,
            exercise=result.exercise.to_dict(),
            statistics=statistics,
            validation=validation,
            errors=result.errors,
            warnings=result.warnings,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process exercise: {str(e)}",
        )


@router.post(
    "/validate",
    response_model=ExerciseValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate exercise structure",
    description="""
Validate the structure of an exercise without full processing.

Checks for:
- Valid section structure
- Problem sequences (a, b, c or ក, ខ, គ)
- Required components (instructions, problems)
    """,
)
def validate_exercise(request: ExerciseTextRequest) -> ExerciseValidationResponse:
    """
    Validate exercise structure.

    Args:
        request: Exercise text and language

    Returns:
        ExerciseValidationResponse with validation results

    Raises:
        HTTPException: If validation fails critically
    """
    try:
        # Process exercise
        result = exercise_service.process_text(
            text=request.text, language=request.language
        )

        if not result.success:
            return ExerciseValidationResponse(
                is_valid=False, errors=result.errors + result.warnings
            )

        # Validate structure
        is_valid, errors = exercise_service.validate_exercise(result.exercise)

        return ExerciseValidationResponse(is_valid=is_valid, errors=errors)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate exercise: {str(e)}",
        )


@router.post(
    "/statistics",
    response_model=ExerciseStatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get exercise statistics",
    description="""
Get detailed statistics about an exercise document.

Returns:
- Number of sections and problems
- Distribution of instruction types
- Distribution of problem types
- Average confidence scores
- Detected languages
    """,
)
def get_exercise_statistics(
    request: ExerciseTextRequest,
) -> ExerciseStatisticsResponse:
    """
    Get statistics for exercise.

    Args:
        request: Exercise text and language

    Returns:
        ExerciseStatisticsResponse with detailed statistics

    Raises:
        HTTPException: If statistics generation fails
    """
    try:
        # Process exercise
        result = exercise_service.process_text(
            text=request.text, language=request.language
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process exercise: {', '.join(result.errors)}",
            )

        # Get statistics
        stats = exercise_service.get_statistics(result.exercise)

        return ExerciseStatisticsResponse(**stats)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate statistics: {str(e)}",
        )
