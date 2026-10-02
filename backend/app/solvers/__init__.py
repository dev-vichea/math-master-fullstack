"""
Solvers Module - Mathematical problem solving engine.

This module provides a clean, modular architecture for solving mathematical problems.
Each solver is specialized for a specific problem domain (algebra, calculus, etc.)
and provides both solution computation and step-by-step explanation generation.

Architecture:
- Base classes define the solver interface
- Domain-specific solvers (algebra, calculus) implement the interface
- Registry maps problem types to appropriate solvers
- Main solve() function orchestrates the solving process

Usage:
    from app.solvers import solve
    from app.parser import parse_math_text

    parsed = parse_math_text("2x + 5 = 15")
    result = solve(parsed, problem_type="linear_equation")
    print(result.answer)  # "5"
    print(result.steps)   # [SolutionStep(...), ...]
"""

from app.parser.math_parser.expression_parser import ParsedMath
from app.solvers.base import SolveResult
from app.solvers.registry import get_solver, list_supported_types


def solve(parsed: ParsedMath, problem_type: str) -> SolveResult:
    """
    Solve a mathematical problem using the appropriate solver.

    This is the main entry point for the solving engine. It:
    1. Finds the appropriate solver based on problem_type
    2. Delegates to that solver's solve() method
    3. Returns a SolveResult with answer, verification, and steps

    Args:
        parsed: ParsedMath object containing the mathematical expression/equation
        problem_type: Problem type string from classifier
                     (e.g., "linear_equation", "quadratic_equation", "calculus_limit")

    Returns:
        SolveResult containing:
        - answer: The solution as a string
        - variable: The variable being solved for (if applicable)
        - is_verified: Whether the solution was verified
        - steps: List of step-by-step solution steps
        - metadata: Additional information about the solution

    Raises:
        ValueError: If no solver can handle the problem type

    Examples:
        >>> from app.parser import parse_math_text
        >>> parsed = parse_math_text("2x + 5 = 15")
        >>> result = solve(parsed, "linear_equation")
        >>> result.answer
        '5'
        >>> result.is_verified
        True

        >>> parsed = parse_math_text("x^2 - 5x + 6 = 0")
        >>> result = solve(parsed, "quadratic_equation")
        >>> result.answer
        '2, 3'
    """
    # Find the appropriate solver
    solver = get_solver(problem_type)

    if solver is None:
        # No solver found for this problem type
        # Return a result indicating unsupported problem type
        from app.api.schemas.responses import SolutionStep

        return SolveResult(
            answer=None,
            variable=None,
            is_verified=False,
            steps=[
                SolutionStep(
                    order=1,
                    description_km=f"ប្រភេទបញ្ហា '{problem_type}' មិនទាន់គាំទ្រ",
                    description_en=f"Problem type '{problem_type}' not yet supported",
                    expression=str(parsed.raw_text),
                )
            ],
            metadata={
                "problem_type": problem_type,
                "error": "No solver registered for this problem type",
                "supported_types": list(list_supported_types().keys()),
            },
        )

    # Delegate to the solver
    try:
        result = solver.solve(parsed, problem_type)
        # Add problem_type to metadata if not already there
        if "problem_type" not in result.metadata:
            result.metadata["problem_type"] = problem_type
        return result
    except Exception as e:
        # Catch any unexpected errors during solving
        from app.api.schemas.responses import SolutionStep

        return SolveResult(
            answer=None,
            variable=str(parsed.symbols[0]) if parsed.symbols else None,
            is_verified=False,
            steps=[
                SolutionStep(
                    order=1,
                    description_km=f"កំហុសក្នុងការដោះស្រាយ៖ {str(e)}",
                    description_en=f"Error during solving: {str(e)}",
                    expression=str(parsed.raw_text),
                )
            ],
            metadata={
                "problem_type": problem_type,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )


__all__ = [
    "solve",
    "SolveResult",
    "get_solver",
    "list_supported_types",
]
