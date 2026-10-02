"""
Common types used across all solvers.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.api.schemas.responses import SolutionStep


@dataclass
class SolveResult:
    """
    Result of solving a mathematical problem.

    Attributes:
        answer: The final answer as a string (e.g., "5", "x = 2, 3", "No solution")
        variable: The variable being solved for (e.g., "x", "y"), None for expressions
        is_verified: Whether the solution was verified by substitution
        steps: List of step-by-step solution steps with bilingual descriptions
        metadata: Optional additional information about the solution
    """

    answer: str | None
    variable: str | None
    is_verified: bool
    steps: list[SolutionStep] = field(default_factory=list)
    metadata: dict[str, any] = field(default_factory=dict)
    lesson_info: dict[str, any] | None = None

    def __post_init__(self):
        """Ensure steps are valid SolutionStep instances."""
        if self.steps and not all(isinstance(step, SolutionStep) for step in self.steps):
            # Convert any dict steps to SolutionStep instances
            self.steps = [
                step if isinstance(step, SolutionStep) else SolutionStep(**step)
                for step in self.steps
            ]
