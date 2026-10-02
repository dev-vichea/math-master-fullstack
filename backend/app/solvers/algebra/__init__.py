"""
Algebra Solvers - Equation and inequality solvers.

Includes:
- Linear equations (ax + b = c)
- Quadratic equations (ax² + bx + c = 0)
- Polynomial equations (degree > 2)
- Systems of equations
- Linear inequalities (ax + b < c)
- Polynomial inequalities
"""

from app.solvers.algebra.equation_solver import EquationSolver
from app.solvers.algebra.inequality_solver import InequalitySolver
from app.solvers.algebra.sequence_solver import SequenceSolver
from app.solvers.algebra.system_solver import SystemSolver

__all__ = [
    "EquationSolver",
    "InequalitySolver",
    "SequenceSolver",
    "SystemSolver",
]

