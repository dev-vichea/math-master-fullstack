"""
API Request Schemas - Pydantic models for incoming requests.
"""

from typing import Literal

from pydantic import BaseModel, Field


class SolveRequest(BaseModel):
    """Request to solve a mathematical problem."""

    language: Literal["km", "en"] = Field(
        default="km",
        description="Language of the input question.",
    )
    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Raw math question, e.g. 'ដោះស្រាយ 2x + 5 = 15'. Maximum 500 characters.",
    )
