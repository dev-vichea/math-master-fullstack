"""
Math Parser - Convert text expressions to SymPy objects.

Handles:
- Implicit multiplication (2x → 2*x)
- Power notation (x^2 → x**2)
- Fractions (1/2)
- Functions (sin, cos, sqrt, etc.)
- Equations (2x + 5 = 15)
"""

from app.parser.math_parser.expression_parser import ParsedMath, parse_math_text

__all__ = ["parse_math_text", "ParsedMath"]
