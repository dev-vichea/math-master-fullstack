"""
Turn a plain-text math expression (already Khmer-normalized and extracted,
e.g. "2x+5=15") into a SymPy expression or equation.

This is the boundary between "text" and "math": everything after this point
in the pipeline works with SymPy objects, never strings, until the very end
when we render steps back out.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import sympy
from sympy import Derivative, Eq, Function, Limit, Symbol
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
    metadata: dict[str, Any] = field(default_factory=dict)


def _clean_latex_text(text: str) -> str:
    """Normalize LaTeX notation, strip trailing spacing artifacts and clean functions."""
    t = text.strip()
    # Normalize unicode integrals
    t = t.replace("∫", r"\int ").replace("∬", r"\iint ").replace("∭", r"\iiint ")
    t = t.replace("{(}", "(").replace("{)}", ")")
    t = t.replace("{[}", "[").replace("{]}", "]")
    t = re.sub(r"[។៕]", " ", t)
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

    # Ensure int without backslash has backslash if followed by bounds or space
    t = re.sub(r"(?<!\\)\bint(?=[_\{ ])", r"\\int", t)

    # Ensure integral single-char bounds have curly braces for latex2sympy2: \int_1^e -> \int_{1}^{e}
    t = re.sub(r"\\int_([a-zA-Z0-9])", lambda m: r"\int_{" + m.group(1) + r"}", t)
    t = re.sub(
        r"(\\int(?:_\{[^}]+\})?)\^([a-zA-Z0-9])(?![a-zA-Z0-9{])",
        lambda m: m.group(1) + r"^{" + m.group(2) + r"}",
        t,
    )

    # Ensure spacing before differential: e.g. 3xdx -> 3x dx
    t = re.sub(r"(?<=[0-9a-zA-Z\)\]\}])\s*(d[xyzut]\b)", r" \1", t)
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


def _standardize_symbols(expr: Any) -> Any:
    """Standardize symbols to plain unadorned Symbol objects without extraneous assumptions."""
    if not hasattr(expr, "free_symbols"):
        return expr
    subs_map = {}
    for s in expr.free_symbols:
        if s.name in ("e", r"\mathrm{e}"):
            subs_map[s] = sympy.E
        elif s.name in ("pi", r"\pi"):
            subs_map[s] = sympy.pi
        else:
            subs_map[s] = Symbol(s.name)
    return expr.subs(subs_map)


def _try_parse_differential_equation(raw_expression: str) -> ParsedMath | None:
    """
    Detect and parse first-order differential equations, including:
    - Direct integration: y' = f(x), xy' = 1
    - Cauchy initial value problems: y' = f(x), y(x0) = y0
    - First-order linear homogeneous ODEs: y' + ay = 0, dy/dx + 2y = 0
    - Separable ODEs: y'/y = cos(x), y'/tan(x) = 1
    - Solution verification: y = f(x), y' - y = 1 - x
    """
    text = raw_expression.strip()
    text = text.replace(r"\left", "").replace(r"\right", "")
    text = re.sub(r"\\nonumber\b", "", text)
    # Ensure fraction denominators have braces: \frac{u}y -> \frac{u}{y}
    text = re.sub(r"\\frac\s*\{([^}]+)\}\s*([a-zA-Z0-9])\b", r"\\frac{\1}{\2}", text)

    # Check if text contains differential equation markers or is an instruction to form ODE from solution
    form_ode_marker = bool(
        re.search(r"រកសមីការឌីផេរ៉ង់ស្យែល|find.*differential|form.*differential", text, re.IGNORECASE)
        and re.search(r"ជាចម្លើយ|as.*solution", text, re.IGNORECASE)
    )
    ode_marker = re.search(
        r"(?:y[\'’]{1,2}|y\s*\^\s*\{?\\+prime(?:\\+prime)?\}?|y[\"”\u201d]|\\frac\{\s*(?:\\mathrm\{d\}|d)\s*y?\s*\}\{\s*(?:\\mathrm\{d\}|d)\s*x\s*\}|\bdy/dx\b)",
        text,
    )
    if not ode_marker and not form_ode_marker:
        return None

    try:
        if form_ode_marker and not ode_marker:
            # Extract function definition: e.g. f(x) = ... or y = ...
            f_match = re.search(r"(?:[a-zA-Z](?:_[0-9a-zA-Z]+)?\s*\(\s*([a-zA-Z])\s*\)|y)\s*=\s*(.+)$", text)
            if f_match:
                var_str = f_match.group(1) or "x"
                rhs_raw = f_match.group(2).strip()
                var_sym = Symbol(var_str)
                if LATEX2SYMPY_AVAILABLE and latex2sympy is not None:
                    rhs_sp = _standardize_symbols(latex2sympy(_clean_latex_text(rhs_raw)))
                else:
                    rhs_sp = _standardize_symbols(parse_expr(rhs_raw, transformations=_TRANSFORMATIONS))
                fn_expr = Eq(Function("f")(var_sym), rhs_sp)
                return ParsedMath(
                    raw_text=raw_expression,
                    is_equation=True,
                    sympy_expr=fn_expr,
                    symbols=[var_sym],
                    metadata={
                        "is_differential_equation": True,
                        "is_form_ode": True,
                        "order": 2,
                        "function_rhs": rhs_sp,
                        "independent_var": var_sym,
                        "dependent_var": Symbol("y"),
                        "raw_ode_str": text,
                    },
                )

        # 1. Extract domain annotation (e.g. កំណត់លើ (-1, 1))
        dom_pat = re.compile(
            r"(?:\\text\{\s*)?កំណត់លើ(?:\s*\}|\s+)*(\([^\)]+\)|\[[^\]]+\])\s*\}?",
            re.UNICODE,
        )
        domain = None
        m_dom = dom_pat.search(text)
        if m_dom:
            domain = m_dom.group(1).strip()
            text = text[: m_dom.start()] + text[m_dom.end() :]
            text = text.strip()

        # 2. Extract initial conditions (e.g. , y(1) = 4 or , y'(0) = 2)
        ics_tuple = None
        ics_prime_tuple = None

        m_ic_prime = re.search(
            r"[,;]\s*\{?y\}?[\'’]\s*\((.*?)\)\s*=\s*([^,;]+)",
            text,
        )
        if m_ic_prime:
            x1_raw = m_ic_prime.group(1).strip()
            y1_raw = m_ic_prime.group(2).strip()
            text = text[: m_ic_prime.start()] + text[m_ic_prime.end() :]
            text = text.strip()
            if LATEX2SYMPY_AVAILABLE and latex2sympy is not None:
                x1_sp = _standardize_symbols(latex2sympy(_clean_latex_text(x1_raw)))
                y1_sp = _standardize_symbols(latex2sympy(_clean_latex_text(y1_raw)))
            else:
                x1_sp = _standardize_symbols(parse_expr(x1_raw, transformations=_TRANSFORMATIONS))
                y1_sp = _standardize_symbols(parse_expr(y1_raw, transformations=_TRANSFORMATIONS))
            ics_prime_tuple = (x1_sp, y1_sp)

        m_ics = re.search(
            r"[,;]\s*\{?y\}?\s*\((.*?)\)\s*=\s*([^,;]+)",
            text,
        )
        if m_ics:
            x0_raw = m_ics.group(1).strip()
            y0_raw = m_ics.group(2).strip()
            text = text[: m_ics.start()].strip()
            if LATEX2SYMPY_AVAILABLE and latex2sympy is not None:
                x0_sp = _standardize_symbols(latex2sympy(_clean_latex_text(x0_raw)))
                y0_sp = _standardize_symbols(latex2sympy(_clean_latex_text(y0_raw)))
            else:
                x0_sp = _standardize_symbols(parse_expr(x0_raw, transformations=_TRANSFORMATIONS))
                y0_sp = _standardize_symbols(parse_expr(y0_raw, transformations=_TRANSFORMATIONS))
            ics_tuple = (x0_sp, y0_sp)

        # 3. Check for verification pair: y = f(x) or f(x) = ... , F(x, y, y', y'') = 0
        is_verification = False
        verif_expr = None
        fn_var = None
        if "," in text:
            parts = [p.strip() for p in text.split(",") if p.strip()]
            if len(parts) == 2:
                p1, p2 = parts
                fn_lhs_pat = r"^\s*(?:y\s*(?:\([a-zA-Z]\))?|[a-zA-Z](?:_[0-9a-zA-Z]+)?\s*\([a-zA-Z]\))\s*=\s*"
                ode_pat = r"y[\'’\"]|y\s*\^\s*\{?\\+prime|\bdy/dx\b"
                if re.match(fn_lhs_pat, p1) and not re.search(ode_pat, p1) and re.search(ode_pat, p2):
                    is_verification = True
                    m_fn = re.search(r"^\s*(?:y|[a-zA-Z](?:_[0-9a-zA-Z]+)?)\s*\(\s*([a-zA-Z])\s*\)\s*=", p1)
                    if m_fn:
                        fn_var = Symbol(m_fn.group(1))
                    verif_raw = p1.split("=", 1)[1].strip()
                    if LATEX2SYMPY_AVAILABLE and latex2sympy is not None:
                        verif_expr = _standardize_symbols(latex2sympy(_clean_latex_text(verif_raw)))
                    else:
                        verif_expr = _standardize_symbols(parse_expr(verif_raw, transformations=_TRANSFORMATIONS))
                    text = p2
                elif re.match(fn_lhs_pat, p2) and not re.search(ode_pat, p2) and re.search(ode_pat, p1):
                    is_verification = True
                    m_fn = re.search(r"^\s*(?:y|[a-zA-Z](?:_[0-9a-zA-Z]+)?)\s*\(\s*([a-zA-Z])\s*\)\s*=", p2)
                    if m_fn:
                        fn_var = Symbol(m_fn.group(1))
                    verif_raw = p2.split("=", 1)[1].strip()
                    if LATEX2SYMPY_AVAILABLE and latex2sympy is not None:
                        verif_expr = _standardize_symbols(latex2sympy(_clean_latex_text(verif_raw)))
                    else:
                        verif_expr = _standardize_symbols(parse_expr(verif_raw, transformations=_TRANSFORMATIONS))
                    text = p1

        # 4. Standardize derivatives
        t = text
        t = re.sub(r"\\frac\{\s*(?:\\mathrm\{d\}|d)\s*y\s*\}\{\s*(?:\\mathrm\{d\}|d)\s*x\s*\}", "y'", t)
        t = re.sub(r"\\frac\{\s*(?:\\mathrm\{d\}|d)\s*\}\{\s*(?:\\mathrm\{d\}|d)\s*x\s*\}\s*y", "y'", t)
        t = t.replace("’", "'").replace("‘", "'")
        t = re.sub(r"y\^\{\\prime\s*\\prime\}|y\\prime\\prime", "y''", t)
        t = re.sub(r"y\^\{\\prime\}|y\\prime", "y'", t)

        # 5. Substitute derivatives with dummy symbols (w for y'', u for y')
        t_mod = re.sub(r"y\'\'|y[\"”\u201d]", "w", t)
        t_mod = re.sub(r"y\'", "u", t_mod)
        if "=" in t_mod:
            lhs_str, rhs_str = t_mod.split("=", 1)
            if LATEX2SYMPY_AVAILABLE and latex2sympy is not None:
                lhs_sp = _standardize_symbols(latex2sympy(_clean_latex_text(lhs_str.strip())))
                rhs_sp = _standardize_symbols(latex2sympy(_clean_latex_text(rhs_str.strip())))
            else:
                lhs_sp = _standardize_symbols(parse_expr(lhs_str.strip(), transformations=_TRANSFORMATIONS))
                rhs_sp = _standardize_symbols(parse_expr(rhs_str.strip(), transformations=_TRANSFORMATIONS))
        else:
            if LATEX2SYMPY_AVAILABLE and latex2sympy is not None:
                lhs_sp = _standardize_symbols(latex2sympy(_clean_latex_text(t_mod.strip())))
            else:
                lhs_sp = _standardize_symbols(parse_expr(t_mod.strip(), transformations=_TRANSFORMATIONS))
            rhs_sp = sympy.Integer(0)

        # 6. Identify independent variable (default: x)
        all_syms = set()
        if hasattr(lhs_sp, "free_symbols"):
            all_syms.update(lhs_sp.free_symbols)
        if hasattr(rhs_sp, "free_symbols"):
            all_syms.update(rhs_sp.free_symbols)
        var_syms = [s for s in all_syms if s.name not in ("w", "u", "y")]
        if var_syms:
            var = var_syms[0]
        elif fn_var is not None:
            var = fn_var
        elif is_verification and verif_expr is not None and getattr(verif_expr, "free_symbols", None):
            preferred = [s for s in verif_expr.free_symbols if s.name in ("x", "t", "s", "z", "u")]
            if preferred:
                var = preferred[0]
            else:
                lowercase = [s for s in verif_expr.free_symbols if s.name.islower() and s.name not in ("e", "i")]
                var = sorted(lowercase, key=lambda s: s.name)[0] if lowercase else Symbol("x")
        else:
            var = Symbol("x")

        y_fn = Function("y")(var)
        w_sym = Symbol("w")
        u_sym = Symbol("u")
        y_sym = Symbol("y")

        sub_map = {
            w_sym: Derivative(y_fn, (var, 2)),
            u_sym: Derivative(y_fn, var),
            y_sym: y_fn,
        }
        lhs = lhs_sp.subs(sub_map)
        rhs = rhs_sp.subs(sub_map)
        ode_eq = Eq(lhs, rhs)

        # 7. Metadata
        is_second_order = w_sym in getattr(lhs_sp, "free_symbols", set()) or w_sym in getattr(rhs_sp, "free_symbols", set())
        cauchy_val = (ics_tuple, ics_prime_tuple) if ics_prime_tuple is not None else ics_tuple
        meta = {
            "is_differential_equation": True,
            "order": 2 if is_second_order else 1,
            "independent_var": var,
            "dependent_var": Symbol("y"),
            "initial_condition": ics_tuple,
            "initial_condition_prime": ics_prime_tuple,
            "cauchy": cauchy_val,
            "domain": domain,
            "is_verification": is_verification,
            "verification_func": verif_expr,
            "function_rhs": verif_expr,
            "differential_eq": ode_eq,
            "raw_ode_str": text,
        }

        symbols = [var, Symbol("y")]
        return ParsedMath(
            raw_text=raw_expression,
            is_equation=True,
            sympy_expr=ode_eq,
            symbols=symbols,
            metadata=meta,
        )
    except Exception:
        return None


def parse_math_text(raw_expression: str) -> ParsedMath:
    r"""
    Parse text such as '2x+5=15', '3*(4+2)', or LaTeX '\frac{2x+5}{3}=15'
    into a SymPy Eq or Expr.

    Supports:
    - Standard algebraic notation
    - Implicit multiplication ('2x' -> '2*x')
    - Caret exponentiation ('x^2' -> 'x**2')
    - LaTeX math via latex2sympy2 ('\frac{a}{b}', '\sqrt{x}', '\le', etc.)
    - Differential equations and initial value problems
    """
    text = raw_expression.strip()

    # 0. Check for differential equations first
    ode_parsed = _try_parse_differential_equation(text)
    if ode_parsed is not None:
        return ode_parsed

    # Clean LaTeX environments like cases, aligned, array
    cleaned_cases = re.sub(r"\\begin\{[^\}]*\}(?:\{[^\}]*\})?", "", text)
    cleaned_cases = re.sub(r"\\end\{[^\}]*\}", "", cleaned_cases).strip()
    if cleaned_cases != text:
        text = cleaned_cases

    if text.count("=") > 1:
        parts = [
            p.strip()
            for p in re.split(r"\\\\|[,;\n]|\s*\\(?:quad|qquad)\s*|\s*\\text\{\s*(?:and|និង)\s*\}\s*", text)
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

    # Normalize unicode integrals and strip Khmer punctuation
    text = text.replace("∫", r"\int ").replace("∬", r"\iint ").replace("∭", r"\iiint ")
    text = re.sub(r"[។៕]", " ", text).strip()

    # If the expression does not contain '=' or '\int', but ends with differential 'd[xyzut]',
    # prepend '\int ' so it is parsed as an integral rather than implicit multiplication (e.g. 3*d*x**2)
    if "=" not in text and r"\int" not in text and re.search(r"(?:^|[\s+\-*/\(\[\{])d[xyzut]\b\s*$", text):
        text = r"\int " + text

    # If the expression uses LaTeX notation, attempt LaTeX parsing first
    is_latex = (
        "\\" in text
        or ("{" in text and "}" in text)
        or "lim" in text.lower()
        or r"\int" in text
        or "int_" in text
    )

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
