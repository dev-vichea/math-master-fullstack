"""
API Schemas - Pydantic models for API requests and responses.

This defines the API contract between backend and frontend.
Keep these stable - add fields rather than removing/renaming.
"""

from app.api.schemas.requests import SolveRequest
from app.api.schemas.responses import (
    APIResponse,
    HealthResponse,
    SolutionStep,
    SolveData,
)

__all__ = [
    # Requests
    "SolveRequest",
    # Responses
    "SolutionStep",
    "SolveData",
    "APIResponse",
    "HealthResponse",
]
