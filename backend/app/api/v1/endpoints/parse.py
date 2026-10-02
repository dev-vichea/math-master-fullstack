"""
POST /api/v1/math/parse — returns detected intent, normalized expression, and problem type
without solving. Allows the client UI to preview and let the user edit before submitting.
"""

from fastapi import APIRouter, Depends

from app.models.schemas import APIResponse, SolveRequest
from app.services.math_service import MathProcessingError, MathService, get_math_service

router = APIRouter()


@router.post("/math/parse", response_model=APIResponse, tags=["math"])
def parse_math(
    payload: SolveRequest,
    math_service: MathService = Depends(get_math_service),
) -> APIResponse:
    """
    Parses math input and returns detected intent, raw expression,
    normalized SymPy expression, and problem type without executing a solve.
    """
    try:
        parsed_data = math_service.parse_question(payload.question)
    except MathProcessingError as exc:
        return APIResponse(success=False, error=str(exc))

    return APIResponse(success=True, data=parsed_data)
