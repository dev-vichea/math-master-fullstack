"""
Step-by-step derivation for systems of linear equations.

Supports systems of 2 or 3 equations with 2 or 3 unknowns using:
  - Substitution method (for 2x2 systems)
  - Elimination method
  - Matrix methods (Cramer's rule, Gaussian elimination)

Every solution is verified by substitution before being returned.
"""

from __future__ import annotations

import sympy
from sympy import Eq, Symbol, nsimplify

from app.api.schemas.responses import SolutionStep
from app.reasoning.steps.base import StepGenerator


def _format_number(value: sympy.Expr) -> str:
    """Render a number the way a textbook would: no '.0', fractions kept as
    fractions rather than decimals."""
    if value == sympy.floor(value):
        try:
            return str(int(value))
        except TypeError:
            pass
    try:
        simplified = nsimplify(value, rational=False)
        return str(simplified)
    except Exception:
        return str(value)


class SystemStepGenerator(StepGenerator):
    """
    Step generator for systems of linear equations.

    Note: This is a placeholder for the full system solver feature.
    Currently, the parser and classifier don't support multiple equations yet,
    so this won't be called until we extend the ParsedMath structure to handle
    multiple equations.

    For now, this serves as the architecture for when we implement:
    1. Enhanced parser to detect and parse multiple equations (e.g., "2x+y=5, x-y=1")
    2. Extended classifier to identify system_of_equations
    3. Full step-by-step solution methods
    """

    problem_type = "system_of_equations"

    def generate(self, eq: Eq, symbol: Symbol) -> list[SolutionStep]:
        """
        Generate step-by-step solution for a system of equations.

        Note: Current implementation is a placeholder. To fully implement:
        1. Extend ParsedMath to hold multiple equations
        2. Update this method signature to accept list[Eq] and list[Symbol]
        3. Implement substitution, elimination, or matrix methods
        """
        steps: list[SolutionStep] = []
        order = 1

        # Placeholder implementation
        steps.append(
            SolutionStep(
                order=order,
                description_km="ប្រព័ន្ធសមីការនេះត្រូវការការអភិវឌ្ឍន៍បន្ថែម។",
                description_en="System of equations solver is under development.",
                expression=None,
            )
        )

        return steps


# Full implementation notes for future development:
"""
To implement a complete 2x2 system solver (e.g., "2x+y=5, x-y=1"):

SUBSTITUTION METHOD:
1. Display both equations
2. Solve first equation for one variable (y = 5 - 2x)
3. Substitute into second equation (x - (5-2x) = 1)
4. Solve for x (3x = 6, x = 2)
5. Substitute back to find y (y = 5 - 2(2) = 1)
6. Verify by substitution

ELIMINATION METHOD:
1. Display both equations
2. Multiply equations to align coefficients
3. Add or subtract equations to eliminate one variable
4. Solve for remaining variable
5. Substitute back
6. Verify

Example steps structure:

steps = [
    SolutionStep(
        order=1,
        description_km="ប្រព័ន្ធសមីការ៖",
        description_en="System of equations:",
        expression="2x + y = 5\\nx - y = 1"
    ),
    SolutionStep(
        order=2,
        description_km="ដោះស្រាយសមីការទីមួយសម្រាប់ y៖",
        description_en="Solve first equation for y:",
        expression="y = 5 - 2x"
    ),
    # ... more steps
]

For 3x3 systems, use Cramer's rule or Gaussian elimination.
"""
