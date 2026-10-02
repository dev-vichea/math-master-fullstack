"""
Mathematical solving engine.

DEPRECATED: Components have been moved to:
- app.classifier.problem_classifier (classification)
- app.solvers (solving logic - to be refactored)
- app.reasoning.steps (step generation)
- app.reasoning.operations (operation metadata)

Backward compatibility maintained for now.
"""

import warnings

from app.classifier.problem_classifier.classifier import classify_problem
from app.reasoning.operations.operations import OperationType, StepBuilder
from app.reasoning.steps.registry import get_step_generator

warnings.warn(
    "app.core.engine is deprecated. Components moved to app.classifier, app.solvers, and app.reasoning.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["classify_problem", "get_step_generator", "OperationType", "StepBuilder"]
