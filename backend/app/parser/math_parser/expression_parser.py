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
    t = t.replace("{(}", "(").replace("{)}", ")")
    t = t.replace("{[}", "[").replace("{]}", "]")
    t = re.sub(r"\\underline\{\s*\{*\s*=\s*\}*\s*\}", "=", t)
    t = re.sub(r"([+\-=])\{\s*(\\frac\{[^{}]*\}\{[^{}]*\})\s*\}", r"\1\2", t)
    # Strip leading label prefix like \mathcal{Q}. or 2. or a. or (a) before a formula
    t = re.sub(
        r"^\s*(?:"
        r"\([a-zA-Z0-9\u1780-\u17a2]{1,2}\)[\.៖:]?"
        r"|(?:[\\/](?:tilde|bar|hat|mathcal|mathbf|mathrm|text)\{[^{}]*(?:\{[^{}]*\})*\}|[ក-អ]|[a-zA-Z]|[0-9]{1,2}|[\u17e0-\u17e9]{1,2})[\)\.៖:](?!\d)"
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

    # Normalize +\infty to \infty in limit targets
    t = re.sub(
        r"(?:->|\\\\rightarrow|\\rightarrow|\\\\to|\\to|\bto\b)\s*\+\s*(?:\\)?infty",
        r"\\to \\infty",
        t,
    )
    # Normalize one-sided targets like 0^+ or 0^- or 0^{+}
    t = re.sub(
        r"(?:->|\\\\rightarrow|\\rightarrow|\\\\to|\\to|\bto\b)\s*([0-9a-zA-Z]+)\^\{?[+\-]\}?",
        r"\\to \1",
        t,
    )
    # Convert ASCII limits like 'lim x->0 expr', 'lim_{x->0} expr', 'limit x->0' to '\lim_{x \to 0} expr'
    ascii_lim_pat = re.compile(
        r"(?i)(?:\\\\|\\|/)*lim(?:it)?\s*(?:_\{?|\s+)\s*([a-zA-Z])\s*(?:->|\\\\rightarrow|\\rightarrow|\\\\to|\\to|\bto\b)\s*([+\-]?\s*(?:\\[a-zA-Z]+|[0-9a-zA-Z]+))\}?"
    )
    t = ascii_lim_pat.sub(lambda m: rf"\lim_{{{m.group(1)} \to {m.group(2).strip()}}} ", t)

    # Ensure math functions in LaTeX have leading backslash if missing
    func_pat = re.compile(r"(?<![\\\\a-zA-Z])(sin|cos|tan|cot|sec|csc|ln|log|exp)\b")
    t = func_pat.sub(lambda m: "\\" + m.group(1), t)

    # Ensure lim_{ has leading backslash if missing
    if "lim_{" in t and r"\lim_{" not in t:
        t = t.replace("lim_{", r"\lim_{")

    # Ensure integral single-char bounds have curly braces for latex2sympy2: \int_1^e -> \int_{1}^{e}
    t = re.sub(r"\\int_([a-zA-Z0-9])", lambda m: r"\int_{" + m.group(1) + r"}", t)
    t = re.sub(
        r"(\\int(?:_\{[^}]+\})?)\^([a-zA-Z0-9])(?![a-zA-Z0-9{])",
        lambda m: m.group(1) + r"^{" + m.group(2) + r"}",
        t,
    )
    return t


def _extract_symbols(expr: sympy.Expr | Eq) -> list[Symbol]:
    """Extract all active variables including bound variables in limits/integrals."""
    symbols = set(expr.free_symbols)
    if isinstance(expr, (tuple, list, sympy.Tuple)):
        for item in expr:
            symbols.update(_extract_symbols(item))
        return sorted(symbols, key=lambda s: s.name)
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
        parts = [
            p.strip()
            for p in re.split(r"[,;\n]|\s*\\(?:quad|qquad)\s*|\s*\\text\{\s*(?:and|និង)\s*\}\s*", text)
            if p.strip()
        ]
        if len(parts) > 1 and all(p.count("=") == 1 for p in parts):
            sub_results = [_parse_latex(p) for p in parts]
            return sympy.Tuple(*[r[0] for r in sub_results]), True
        raise ExpressionParseError(f"Expression contains multiple equals signs: {text!r}")


    has_inequality = bool(
        re.search(r"(?:<=|>=|≤|≥|<|>|\\(?:le|ge|leq|geq)(?![a-zA-Z]))", text)
    )

    def _normalize_parsed_expr(ex: Any) -> Any:
        if hasattr(ex, "free_symbols"):
            e_syms = [s for s in ex.free_symbols if s.name in ("e", r"\mathrm{e}")]
            if e_syms:
                ex = ex.subs({s: sympy.E for s in e_syms})
        ex = ex.replace(
            lambda a: isinstance(a, sympy.log) and len(a.args) == 2 and a.args[1] == sympy.E,
            lambda a: sympy.log(a.args[0]),
        )
        return ex

    if "=" in text and not has_inequality:
        lhs_text, rhs_text = text.split("=", 1)
        lhs_clean = lhs_text.strip()
        m_func = re.match(
            r"^\s*([a-zA-Z])\s*(?:\\left)?\(\s*([a-zA-Z])\s*(?:\\right)?\)\s*$", lhs_clean
        )
        if m_func:
            lhs = sympy.Function(m_func.group(1))(Symbol(m_func.group(2)))
        else:
            lhs = latex2sympy(lhs_clean)
        rhs = latex2sympy(rhs_text.strip())

        res_eq = Eq(lhs, rhs)
        res_eq = _normalize_parsed_expr(res_eq)
        return res_eq, True
    else:
        expr = latex2sympy(text.strip())
        if isinstance(expr, (list, tuple)):
            expr = expr[0]
        expr = _normalize_parsed_expr(expr)
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
        parts = [
            p.strip()
            for p in re.split(r"[,;\n]|\s*\\(?:quad|qquad)\s*|\s*\\text\{\s*(?:and|និង)\s*\}\s*", text)
            if p.strip()
        ]
        if len(parts) > 1 and all(p.count("=") == 1 for p in parts):
            try:
                sub_parsed = [parse_math_text(p) for p in parts]
                composite_expr = sympy.Tuple(*[p.sympy_expr for p in sub_parsed])
                all_symbols = sorted(
                    set().union(*[p.symbols for p in sub_parsed]),
                    key=lambda s: s.name,
                )
                return ParsedMath(
                    raw_text=raw_expression,
                    is_equation=True,
                    sympy_expr=composite_expr,
                    symbols=all_symbols,
                )
            except Exception:
                pass
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
            lhs_clean = lhs_text.strip()
            m_func = re.match(
                r"^\s*([a-zA-Z])\s*(?:\\left)?\(\s*([a-zA-Z])\s*(?:\\right)?\)\s*$", lhs_clean
            )
            if m_func:
                lhs = sympy.Function(m_func.group(1))(Symbol(m_func.group(2)))
            else:
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

    if hasattr(expr, "free_symbols"):
        e_syms = [s for s in expr.free_symbols if s.name in ("e", r"\mathrm{e}")]
        if e_syms:
            expr = expr.subs({s: sympy.E for s in e_syms})

    symbols = _extract_symbols(expr)
    return ParsedMath(
        raw_text=raw_expression,
        is_equation=is_equation,
        sympy_expr=expr,
        symbols=symbols,
    )
