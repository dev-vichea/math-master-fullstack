"""
Solution Builder - Orchestrates the complete problem-solving pipeline.

The ProblemBuilder orchestrates:
1. Text normalization
2. Intent detection
3. Expression extraction
4. Mathematical parsing
5. Problem classification
6. Characteristic detection

Output: Complete MathProblem object ready for solving
"""

from app.reasoning.solution_builder.problem_builder import ProblemBuilder

__all__ = ["ProblemBuilder"]
