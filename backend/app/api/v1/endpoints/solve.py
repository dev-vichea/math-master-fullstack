from fastapi import APIRouter, Depends

from app.models.schemas import APIResponse, SolveRequest
from app.services.history_service import HistoryService, get_history_service
from app.services.math_service import MathProcessingError, MathService, get_math_service

router = APIRouter()


@router.post("/math/solve", response_model=APIResponse, tags=["math"])
async def solve_math(
    payload: SolveRequest,
    math_service: MathService = Depends(get_math_service),
    history_service: HistoryService = Depends(get_history_service),
) -> APIResponse:
    """
    Solves a math problem written in Khmer or English, stores it in history,
    and returns deterministic verified step-by-step solution.
    """
    try:
        data = math_service.process_question(payload.question)
    except MathProcessingError as exc:
        return APIResponse(success=False, data=None, error=str(exc))

    await history_service.save_entry(question=payload.question, data=data)
    return APIResponse(success=True, data=data, error=None)
