"""
Pluggable interface: each problem type (linear, quadratic, ...) gets its own
StepGenerator. Adding support for a new math topic later means writing one
new class and registering it in `registry.py` — nothing else in the API or
engine layer changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import sympy

from app.models.schemas import SolutionStep


class StepGenerator(ABC):
    problem_type: str

    @abstractmethod
    def generate(self, eq: sympy.Eq, symbol: sympy.Symbol) -> list[SolutionStep]: ...
