"""
Turn a plain-text math expression (already Khmer-normalized and extracted,
e.g. "2x+5=15") into a SymPy expression or equation.

This is the boundary between "text" and "math": everything after this point
in the pipeline works with SymPy objects, never strings, until the very end
when we render steps back out.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import sympy
from sympy import Eq, Limit, Symbol
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

_TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

try:
    from latex2sympy2 import latex2sympy

    LATEX2SYMPY_AVAILABLE = True
except ImportError:
    latex2sympy = None  # type: ignore[assignment]
    LATEX2SYMPY_AVAILABLE = False


class ExpressionParseError(Exception):
    """Raised when the given text cannot be parsed as math at all."""


@dataclass
class ParsedMath:
    raw_text: str
    is_equation: bool
    sympy_expr: sympy.Expr | Eq
    symbols: list[Symbol]


def _clean_latex_text(text: str) -> str:
    """Normalize LaTeX notation, strip trailing spacing artifacts and clean functions."""
    t = text.strip()
    # Strip leading label prefix like \mathcal{Q}. or 2. or a. or (a) before a formula
    t = re.sub(
        r"^\s*(?:"
        r"\([a-zA-Z0-9\u1780-\u17a2]{1,2}\)[\.៖:]?"
        r"|(?:[\\/](?:mathcal|mathbf|mathrm|text)\{[a-zA-Z0-9\u1780-\u17a2]+\}|[ក-អ]|[a-zA-Z]|[0-9]{1,2}|[\u17e0-\u17e9]{1,2})[\)\.៖:](?!\d)"
        r")\s*",
        "",
        t,
    )
    # Strip trailing punctuation, LaTeX space tokens like \; \, \! \quad and backslashes
    t = re.sub(r"(\\[;,!]|\\quad|\\qquad|[\s;.,\\])+$", "", t)
    while t.endswith("\\"):
        t = t[:-1].strip()
    # Normalize \operatorname*{lim} or \operatorname{lim}
    t = t.replace(r"\operatorname*{lim}", r"\lim").replace(r"\operatorname{lim}", r"\lim")
    # Clean spaces inside trig functions from OCR (e.g. 's i n' or 'c o s' or 't a n')
    t = t.replace("s i n", r"\sin").replace("c o s", r"\cos").replace("t a n", r"\tan")
    t = (
        t.replace(r"\\sin", r"\sin")
        .replace(r"\\cos", r"\cos")
        .replace(r"\\tan", r"\tan")
        .replace(r"\\lim", r"\lim")
    )

    # Convert sqrt(...) to \sqrt{...}
    t = re.sub(r"(?:\\)?sqrt\(([^)]+)\)", r"\\sqrt{\1}", t)

    # Convert ASCII limits like 'lim x->0 expr', 'lim_{x->0} expr', 'limit x->0' to '\lim_{x \to 0} expr'
    ascii_lim_pat = re.compile(
        r"(?i)(?:\\\\|\\|/)*lim(?:it)?\s*(?:_\{?|\s+)\s*([a-zA-Z])\s*(?:->|\\\\rightarrow|\\rightarrow|\\\\to|\\to|\bto\b)\s*([0-9+\-a-zA-Z]+|\\[a-zA-Z]+)\}?"
    )
    t = ascii_lim_pat.sub(lambda m: rf"\lim_{{{m.group(1)} \to {m.group(2)}}} ", t)

    # Ensure math functions in LaTeX have leading backslash if missing
    func_pat = re.compile(r"(?<![\\\\a-zA-Z])(sin|cos|tan|cot|sec|csc|ln|log|exp)\b")
    t = func_pat.sub(lambda m: "\\" + m.group(1), t)

    # Ensure lim_{ has leading backslash if missing
    if "lim_{" in t and r"\lim_{" not in t:
        t = t.replace("lim_{", r"\lim_{")
    return t


def _extract_symbols(expr: sympy.Expr | Eq) -> list[Symbol]:
    """Extract all active variables including bound variables in limits/integrals."""
    symbols = set(expr.free_symbols)
    if isinstance(expr, Limit):
        if len(expr.args) > 1 and isinstance(expr.args[1], Symbol):
            symbols.add(expr.args[1])
    elif isinstance(expr, Eq):
        for side in (expr.lhs, expr.rhs):
            if isinstance(side, Limit):
                if len(side.args) > 1 and isinstance(side.args[1], Symbol):
                    symbols.add(side.args[1])
    return sorted(symbols, key=lambda s: s.name)


def _parse_latex(text: str) -> tuple[sympy.Expr | Eq, bool]:
    """Parse a LaTeX math string into a SymPy Expr or Eq using latex2sympy2."""
    if not LATEX2SYMPY_AVAILABLE or latex2sympy is None:
        raise ExpressionParseError("latex2sympy2 is required for LaTeX expressions.")

    text = _clean_latex_text(text)

    if text.count("=") > 1:
        raise ExpressionParseError(f"Expression contains multiple equals signs: {text!r}")

    has_inequality = any(
        op in text for op in ["<", ">", r"\le", r"\ge", r"\leq", r"\geq", "≤", "≥"]
    )

    if "=" in text and not has_inequality:
        lhs_text, rhs_text = text.split("=", 1)
        lhs = latex2sympy(lhs_text.strip())
        rhs = latex2sympy(rhs_text.strip())
        return Eq(lhs, rhs), True
    else:
        expr = latex2sympy(text.strip())
        if isinstance(expr, (list, tuple)):
            expr = expr[0]
        return expr, isinstance(expr, Eq)


def parse_math_text(raw_expression: str) -> ParsedMath:
    r"""
    Parse text such as '2x+5=15', '3*(4+2)', or LaTeX '\frac{2x+5}{3}=15'
    into a SymPy Eq or Expr.

    Supports:
    - Standard algebraic notation
    - Implicit multiplication ('2x' -> '2*x')
    - Caret exponentiation ('x^2' -> 'x**2')
    - LaTeX math via latex2sympy2 ('\frac{a}{b}', '\sqrt{x}', '\le', etc.)
    """
    text = raw_expression.strip()

    if text.count("=") > 1:
        raise ExpressionParseError(f"Expression contains multiple equals signs: {raw_expression!r}")

    # If the expression uses LaTeX notation, attempt LaTeX parsing first
    is_latex = "\\" in text or ("{" in text and "}" in text) or "lim" in text.lower()
    if is_latex and LATEX2SYMPY_AVAILABLE:
        try:
            expr, is_equation = _parse_latex(text)
            symbols = _extract_symbols(expr)
            return ParsedMath(
                raw_text=raw_expression,
                is_equation=is_equation,
                sympy_expr=expr,
                symbols=symbols,
            )
        except Exception:
            pass

    # Standard SymPy parser
    try:
        if "=" in text:
            lhs_text, rhs_text = text.split("=", 1)
            lhs = parse_expr(lhs_text, transformations=_TRANSFORMATIONS)
            rhs = parse_expr(rhs_text, transformations=_TRANSFORMATIONS)
            expr = Eq(lhs, rhs)
            is_equation = True
        else:
            expr = parse_expr(text, transformations=_TRANSFORMATIONS)
            is_equation = False
    except Exception as exc:  # sympy raises several different error types
        # If standard parser failed, try latex2sympy as fallback
        if LATEX2SYMPY_AVAILABLE:
            try:
                expr, is_equation = _parse_latex(text)
                symbols = _extract_symbols(expr)
                return ParsedMath(
                    raw_text=raw_expression,
                    is_equation=is_equation,
                    sympy_expr=expr,
                    symbols=symbols,
                )
            except Exception:
                pass
        raise ExpressionParseError(f"Could not parse expression: {raw_expression!r}") from exc

    symbols = _extract_symbols(expr)
    return ParsedMath(
        raw_text=raw_expression,
        is_equation=is_equation,
        sympy_expr=expr,
        symbols=symbols,
    )
