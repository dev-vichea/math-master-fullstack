"""
Step Generators — Generate step-by-step solutions for different problem types.

Each generator produces a sequence of steps showing the reasoning process
from problem to solution.

Subpackages:
- algebra/   — Linear, quadratic, polynomial, inequality, system, expansion, logarithm
- calculus/  — Derivative, integral, limit
"""

from app.reasoning.steps.base import StepGenerator
from app.reasoning.steps.registry import get_step_generator

__all__ = [
    "get_step_generator",
    "StepGenerator",
]
