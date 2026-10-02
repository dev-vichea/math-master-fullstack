"""
Registry mapping problem_type -> StepGenerator.

To add support for a new topic later (quadratic, systems of equations,
calculus, ...): write a class implementing StepGenerator in its own file,
then add one line here. No other file needs to change.
"""

from __future__ import annotations

from app.reasoning.steps.base import StepGenerator
from app.reasoning.steps.calculus.derivative import DerivativeStepGenerator
from app.reasoning.steps.calculus.integral import IntegralStepGenerator
from app.reasoning.steps.calculus.limit import LimitStepGenerator
from app.reasoning.steps.algebra.expansion import ExpansionStepGenerator
from app.reasoning.steps.algebra.inequality import LinearInequalityStepGenerator
from app.reasoning.steps.algebra.linear import LinearStepGenerator
from app.reasoning.steps.algebra.logarithm import LogarithmStepGenerator
from app.reasoning.steps.algebra.polynomial import PolynomialStepGenerator
from app.reasoning.steps.algebra.quadratic import QuadraticStepGenerator
from app.reasoning.steps.algebra.sequence import SequenceStepGenerator
from app.reasoning.steps.algebra.system import SystemStepGenerator

_expansion_gen = ExpansionStepGenerator()
_logarithm_gen = LogarithmStepGenerator()
_integral_gen = IntegralStepGenerator()
_sequence_gen = SequenceStepGenerator()

_GENERATORS: dict[str, StepGenerator] = {
    "linear_equation": LinearStepGenerator(),
    "quadratic_equation": QuadraticStepGenerator(),
    "polynomial_equation": PolynomialStepGenerator(),
    "system_of_equations": SystemStepGenerator(),
    "linear_inequality": LinearInequalityStepGenerator(),
    "calculus_limit": LimitStepGenerator(),
    "calculus_derivative": DerivativeStepGenerator(),
    "calculus_integral": _integral_gen,
    "factored_expression": _expansion_gen,
    "expression_expansion": _expansion_gen,
    "polynomial_expansion": _expansion_gen,
    "logarithm_evaluation": _logarithm_gen,
    "logarithm_simplification": _logarithm_gen,
    "sequence": _sequence_gen,
    "sequence_convergence": _sequence_gen,
    "sequence_limit": _sequence_gen,
    "sequence_recurrence": _sequence_gen,
    "sequence_ratio": _sequence_gen,
    "real_sequence": _sequence_gen,
}



def get_step_generator(problem_type: str) -> StepGenerator | None:
    """Returns None when no dedicated generator is registered yet for this
    problem_type (e.g. quadratic_equation) — callers should fall back to a
    generic, still-verified-but-not-narrated answer in that case."""
    return _GENERATORS.get(problem_type)
