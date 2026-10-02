"""
Reasoning Layer - Step-by-step solution generation.

This module handles:
- Solution step generation (linear, quadratic, polynomial, etc.)
- Operation metadata tracking
- Solution building and orchestration
- Step-by-step reasoning logic

Refactored from app/core/engine/steps/ and app/core/ for better modularity.
"""

from app.reasoning.operations.operations import (
    OperationType,
    StepBuilder,
    TransformationType,
)
from app.reasoning.solution_builder.problem_builder import ProblemBuilder
from app.reasoning.steps.registry import StepGenerator, get_step_generator

__all__ = [
    "get_step_generator",
    "StepGenerator",
    "OperationType",
    "TransformationType",
    "StepBuilder",
    "ProblemBuilder",
]
