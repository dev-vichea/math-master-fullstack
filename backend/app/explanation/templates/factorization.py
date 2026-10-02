"""
Factorization Explanation Templates.

Implements lesson-aware pedagogical step generation for:
1. Common Factor Extraction: ka + kb = k(a + b)
2. Difference of Two Squares: a² - b² = (a - b)(a + b)
3. Quadratic Trinomial Factoring: x² + (p + q)x + pq = (x + p)(x + q)
4. General Algebraic Factoring (Grouping & Identities)

Every step explains "what is being done" (title) and "why" (rationale),
with formulas and verification.
"""

from __future__ import annotations

import sympy
from sympy import Add, Mul, Pow, Symbol, expand, factor, gcd, latex, sqrt

from app.api.schemas.responses import SolutionStep


def get_square_root_base(term: sympy.Expr) -> sympy.Expr | None:
    """Extracts clean square root base if term is a perfect square."""
    if term.is_Number:
        if term < 0:
            return None
        s = sqrt(term)
        return s if s.is_rational else None
    if isinstance(term, Symbol):
        return None
    if isinstance(term, Pow) and getattr(term.exp, "is_integer", False) and term.exp % 2 == 0:
        return term.base ** (term.exp // 2)
    if isinstance(term, Mul):
        num_part = 1
        var_parts = []
        for a in term.args:
            if a.is_Number:
                if a < 0:
                    return None
                num_part *= a
            elif isinstance(a, Pow) and getattr(a.exp, "is_integer", False) and a.exp % 2 == 0:
                var_parts.append(a.base ** (a.exp // 2))
            elif isinstance(a, Symbol):
                return None
            else:
                return None
        s_num = sqrt(num_part)
        if not s_num.is_rational:
            return None
        return Mul(s_num, *var_parts)
    return None


def generate_common_factor_explanation(
    expr: sympy.Expr,
    common_factor: sympy.Expr,
    quotient: sympy.Expr,
    prefix: str = "",
) -> list[SolutionStep]:
    """
    Step 1: Identify Greatest Common Factor (GCF)
    Step 2: Factor outside parentheses
    Step 3: Simplify remaining expression
    Step 4: Verify by expanding back
    """
    steps: list[SolutionStep] = []

    # Step 1: Identify common factor
    terms = expr.as_ordered_terms() if isinstance(expr, Add) else [expr]
    terms_latex = ", \\; ".join(latex(t) for t in terms)
    steps.append(
        SolutionStep(
            order=1,
            title_km="កំណត់កត្តារួមធំបំផុត (GCF)",
            title_en="Identify Greatest Common Factor (GCF)",
            rationale_km="ពិនិត្យតួនីមួយៗក្នុងកន្សោម ដើម្បីស្វែងរកកត្តារួមនៃមេគុណលេខ និងអថេរដែលមានស្វ័យគុណទាបបំផុត។",
            rationale_en="Inspect each term in the polynomial to find the common divisor of coefficients and variables with minimum power.",
            description_km=f"កំណត់កត្តារួមធំបំផុត (GCF) នៃតួទាំងអស់ [{terms_latex}] គឺ៖ {latex(common_factor)}",
            description_en=f"Identify greatest common factor (GCF) among all terms [{terms_latex}]: {latex(common_factor)}",
            expression=rf"\text{{GCF}}\left({terms_latex}\right) = {latex(common_factor)}",
            rule_formula=r"\text{GCF}(ka, kb) = k",
            is_verification=False,
            operation="identify_factor",
            transformation="find_common_factor",
        )
    )

    # Step 2: Factor it outside parentheses
    terms_divided = " + ".join(rf"\frac{{{latex(t)}}}{{{latex(common_factor)}}}" for t in terms)
    terms_divided_clean = terms_divided.replace("+ -", "- ")
    steps.append(
        SolutionStep(
            order=2,
            title_km="ទាញកត្តារួមចេញក្រៅវង់ក្រចក",
            title_en="Factor Out Common Term",
            rationale_km="អនុវត្តរូបមន្ត ka + kb = k(a + b) ដោយដាក់កត្តារួមនៅមុខវង់ក្រចក។",
            rationale_en="Apply formula ka + kb = k(a + b) by placing the greatest common factor outside parentheses.",
            description_km="ទាញកត្តារួមចេញក្រៅវង់ក្រចកតាមរូបមន្ត ka + kb = k(a + b)៖",
            description_en="Factor the common term outside parentheses using ka + kb = k(a + b):",
            expression=f"{prefix}= {latex(common_factor)}\\left({terms_divided_clean}\\right)",
            rule_formula=r"ka + kb = k(a + b)",
            is_verification=False,
            operation="factor",
            transformation="extract_common_factor",
        )
    )

    # Step 3: Simplify inside parentheses
    factored_latex = f"{latex(common_factor)}\\left({latex(quotient)}\\right)"
    steps.append(
        SolutionStep(
            order=3,
            title_km="សម្រួលកន្សោមក្នុងវង់ក្រចក",
            title_en="Simplify Remaining Expression",
            rationale_km="ចែកតួនីមួយៗនៃកន្សោមដើមនឹងកត្តារួម ដើម្បីទទួលបានកន្សោមផលចែកសាមញ្ញបំផុតក្នុងវង់ក្រចក។",
            rationale_en="Divide each original term by the common factor to produce the simplified quotient inside parentheses.",
            description_km="សម្រួលកន្សោមផលចែកដែលនៅសល់ក្នុងវង់ក្រចក៖",
            description_en="Simplify the quotient remaining inside the parentheses:",
            expression=f"{prefix}= {factored_latex}",
            rule_formula=None,
            is_verification=False,
            operation="simplify",
            transformation="simplify_parentheses",
        )
    )

    # Step 4: Verify result by expanding back
    expanded_back = expand(common_factor * quotient)
    steps.append(
        SolutionStep(
            order=4,
            title_km="ផ្ទៀងផ្ទាត់លទ្ធផលដោយគុណពន្លាតត្រឡប់ក្រោយ",
            title_en="Verify by Expanding Back",
            rationale_km="គុណពន្លាតកត្តាដែលទើបតែរកឃើញចូលក្នុងវង់ក្រចកវិញ ដើម្បីផ្ទៀងផ្ទាត់ថាតើស្មើនឹងកន្សោមដើមពិតឬមិនពិត។",
            rationale_en="Multiply the factored expression back out to confirm that it reproduces the original expression exactly.",
            description_km="ផ្ទៀងផ្ទាត់ចម្លើយដោយគុណពន្លាតត្រឡប់ក្រោយ (ស្មើនឹងកន្សោមដើម)៖",
            description_en="Verify by expanding back (matches the original expression):",
            expression=rf"{factored_latex} = {latex(expanded_back)} \quad \text{{(ត្រឹមត្រូវ / Verified)}}",
            rule_formula=r"k(a + b) = ka + kb",
            is_verification=True,
            operation="verify",
            transformation="expand_verification",
        )
    )

    return steps


def generate_diff_squares_explanation(
    expr: sympy.Expr,
    a: sympy.Expr,
    b: sympy.Expr,
    prefix: str = "",
) -> list[SolutionStep]:
    """
    Step 1: Identify difference of squares a² - b²
    Step 2: Identify terms a and b
    Step 3: Apply factoring identity a² - b² = (a - b)(a + b)
    Step 4: Verify result by expansion
    """
    steps: list[SolutionStep] = []

    # Step 1: Identify squares
    steps.append(
        SolutionStep(
            order=1,
            title_km="កំណត់ទម្រង់ផលសងការេ a² − b²",
            title_en="Identify Difference of Squares a² − b²",
            rationale_km="កត់សម្គាល់ថាកន្សោមមានពីរតួដែលជាផលដករវាងការេពេញពីរ។",
            rationale_en="Recognize that the expression consists of two terms separated by subtraction of perfect squares.",
            description_km="កំណត់ទម្រង់ផលសងការេ a² − b² នៃកន្សោមដើម៖",
            description_en="Identify the difference of squares structure a² − b² in the expression:",
            expression=f"{prefix}{latex(expr)} = \\left({latex(a)}\\right)^2 - \\left({latex(b)}\\right)^2",
            rule_formula=r"a^2 - b^2",
            is_verification=False,
            operation="identify_identity",
            transformation="rewrite_as_squares",
        )
    )

    # Step 2: Identify terms a and b
    steps.append(
        SolutionStep(
            order=2,
            title_km="កំណត់តម្លៃមូលដ្ឋាន a និង b",
            title_en="Identify Base Terms a and b",
            rationale_km="ទាញយកឫសការេនៃតួនីមួយៗដើម្បីកំណត់តម្លៃមូលដ្ឋាន a និង b។",
            rationale_en="Extract the square root of each term to determine the base components a and b.",
            description_km=f"កំណត់តម្លៃមូលដ្ឋាននៃតួនីមួយៗ៖ a = {latex(a)} និង b = {latex(b)}",
            description_en=f"Identify base terms: a = {latex(a)} and b = {latex(b)}",
            expression=rf"a = {latex(a)}, \quad b = {latex(b)}",
            rule_formula=r"a = \sqrt{a^2}, \; b = \sqrt{b^2}",
            is_verification=False,
            operation="extract_terms",
            transformation="base_identification",
        )
    )

    # Step 3: Apply identity
    factored_latex = f"\\left({latex(a)} - {latex(b)}\\right)\\left({latex(a)} + {latex(b)}\\right)"
    steps.append(
        SolutionStep(
            order=3,
            title_km="អនុវត្តរូបមន្តផលសងការេ",
            title_en="Apply Difference of Squares Identity",
            rationale_km="ជំនួសតម្លៃ a និង b ចូលក្នុងរូបមន្តផលគុណកត្តា a² − b² = (a − b)(a + b)។",
            rationale_en="Substitute base terms a and b into the difference of squares factoring formula.",
            description_km="អនុវត្តរូបមន្តផលសងការេ a² − b² = (a − b)(a + b)៖",
            description_en="Apply the identity a² − b² = (a − b)(a + b):",
            expression=f"{prefix}= {factored_latex}",
            rule_formula=r"a^2 - b^2 = (a - b)(a + b)",
            is_verification=False,
            operation="factor",
            transformation="apply_diff_squares",
        )
    )

    # Step 4: Verification
    expanded_back = expand((a - b) * (a + b))
    steps.append(
        SolutionStep(
            order=4,
            title_km="ផ្ទៀងផ្ទាត់ចម្លើយដោយគុណពន្លាត",
            title_en="Verify Result by Expansion",
            rationale_km="គុណពន្លាត (a - b)(a + b) = a² - b² ដើម្បីផ្ទៀងផ្ទាត់ភាពត្រឹមត្រូវនៃចម្លើយ។",
            rationale_en="Expand (a - b)(a + b) = a² - b² to verify algebraic correctness.",
            description_km="ផ្ទៀងផ្ទាត់ចម្លើយដោយគុណពន្លាតផលគុណកត្តាត្រឡប់មកវិញ៖",
            description_en="Verify the result by expanding the factored product back:",
            expression=rf"{factored_latex} = {latex(expanded_back)} \quad \text{{(ត្រឹមត្រូវ / Verified)}}",
            rule_formula=r"(a - b)(a + b) = a^2 - b^2",
            is_verification=True,
            operation="verify",
            transformation="expand_verification",
        )
    )

    return steps


def generate_trinomial_explanation(
    expr: sympy.Expr,
    b: sympy.Expr,
    c: sympy.Expr,
    p: sympy.Expr,
    q: sympy.Expr,
    symbol: sympy.Symbol,
    prefix: str = "",
) -> list[SolutionStep]:
    """
    Step 1: Identify coefficients of quadratic trinomial
    Step 2: Find two numbers p and q such that p + q = b and p * q = c
    Step 3: Write factored form (x + p)(x + q)
    Step 4: Verify result by expansion
    """
    steps: list[SolutionStep] = []
    sym_latex = latex(symbol)

    # Step 1: Identify coefficients
    steps.append(
        SolutionStep(
            order=1,
            title_km=f"កំណត់មេគុណនៃត្រីធាដឺក្រេទីពីរ {sym_latex}² + b{sym_latex} + c",
            title_en=f"Identify Coefficients of Quadratic Trinomial {sym_latex}² + b{sym_latex} + c",
            rationale_km="កត់សម្គាល់មេគុណ b (ផលបូក) និងតួលេខសេរី c (ផលគុណ)។",
            rationale_en="Identify coefficient b (sum of roots) and constant c (product of roots).",
            description_km=f"កំណត់មេគុណនៃត្រីធាដឺក្រេទីពីរ {sym_latex}² + b{sym_latex} + c ៖",
            description_en=f"Identify coefficients of the quadratic trinomial {sym_latex}² + b{sym_latex} + c:",
            expression=rf"b = {latex(b)}, \quad c = {latex(c)}",
            rule_formula=rf"{sym_latex}^2 + bx + c",
            is_verification=False,
            operation="identify_coefficients",
            transformation="identify_trinomial",
        )
    )

    # Step 2: Find p and q
    steps.append(
        SolutionStep(
            order=2,
            title_km="ស្វែងរកពីរចំនួន p និង q",
            title_en="Find Integers p and q",
            rationale_km="រកពីរចំនួនដែលបូកបញ្ចូលគ្នាស្មើ b និងគុណគ្នាស្មើ c។",
            rationale_en="Find two integers whose sum equals b and whose product equals c.",
            description_km=f"ស្វែងរកពីរចំនួន p និង q ដែលបំពេញ៖ p + q = {latex(b)} និង p × q = {latex(c)} ៖",
            description_en=f"Find two numbers p and q such that: p + q = {latex(b)} and p × q = {latex(c)}:",
            expression=rf"({latex(p)}) + ({latex(q)}) = {latex(b)}, \quad ({latex(p)}) \times ({latex(q)}) = {latex(c)} \implies p = {latex(p)}, \; q = {latex(q)}",
            rule_formula=r"p + q = b, \; p \times q = c",
            is_verification=False,
            operation="find_roots",
            transformation="sum_product_matching",
        )
    )

    # Step 3: Write factored form
    p_term = f"+ {latex(p)}" if p > 0 else f"- {latex(-p)}"
    q_term = f"+ {latex(q)}" if q > 0 else f"- {latex(-q)}"
    factored_latex = f"\\left({sym_latex} {p_term}\\right)\\left({sym_latex} {q_term}\\right)"
    steps.append(
        SolutionStep(
            order=3,
            title_km=f"សរសេរជាផលគុណកត្តា ({sym_latex} + p)({sym_latex} + q)",
            title_en=f"Write Factored Form ({sym_latex} + p)({sym_latex} + q)",
            rationale_km="ជំនួសតម្លៃ p និង q ចូលក្នុងទម្រង់ផលគុណកត្តា។",
            rationale_en="Substitute p and q into the factored binomial product structure.",
            description_km=f"សរសេរជាផលគុណកត្តា ({sym_latex} + p)({sym_latex} + q)៖",
            description_en=f"Write factored binomial product ({sym_latex} + p)({sym_latex} + q):",
            expression=f"{prefix}= {factored_latex}",
            rule_formula=r"x^2 + (p+q)x + pq = (x + p)(x + q)",
            is_verification=False,
            operation="factor",
            transformation="write_factored_trinomial",
        )
    )

    # Step 4: Verification
    expanded_back = expand((symbol + p) * (symbol + q))
    steps.append(
        SolutionStep(
            order=4,
            title_km="ផ្ទៀងផ្ទាត់ចម្លើយដោយគុណពន្លាត",
            title_en="Verify Result by Expansion",
            rationale_km="គុណពន្លាត (x + p)(x + q) = x² + (p+q)x + pq ដើម្បីផ្ទៀងផ្ទាត់។",
            rationale_en="Expand (x + p)(x + q) = x² + (p+q)x + pq to confirm equality with original trinomial.",
            description_km="ផ្ទៀងផ្ទាត់ចម្លើយដោយគុណពន្លាតត្រឡប់ក្រោយ៖",
            description_en="Verify the result by expanding the factored product back:",
            expression=rf"{factored_latex} = {latex(expanded_back)} \quad \text{{(ត្រឹមត្រូវ / Verified)}}",
            rule_formula=r"(x + p)(x + q) = x^2 + (p+q)x + pq",
            is_verification=True,
            operation="verify",
            transformation="expand_verification",
        )
    )

    return steps


def generate_general_factorization_explanation(
    expr: sympy.Expr,
    factored: sympy.Expr,
    prefix: str = "",
) -> list[SolutionStep]:
    """Fallback pedagogical explanation for general factorization."""
    steps: list[SolutionStep] = []

    steps.append(
        SolutionStep(
            order=1,
            title_km="កន្សោមដើមដែលត្រូវដាក់ជាផលគុណកត្តា",
            title_en="Original Expression to be Factored",
            rationale_km="កំណត់សម្គាល់កន្សោមពហុធាដើមដែលត្រូវបំប្លែងទៅជាផលគុណកត្តា។",
            rationale_en="Identify the polynomial expression to be factored into simpler algebraic components.",
            description_km="កន្សោមដើមដែលត្រូវដាក់ជាផលគុណកត្តា៖",
            description_en="Original expression to be factored:",
            expression=f"{prefix}{latex(expr)}",
            is_verification=False,
            operation="identify_expression",
            transformation="identify",
        )
    )

    steps.append(
        SolutionStep(
            order=2,
            title_km="បំបែកជាផលគុណកត្តា",
            title_en="Factor into Algebraic Product",
            rationale_km="បំបែកជាផលគុណកត្តាតាមរូបមន្តស្មើភាព និងការផ្ដុំតួសមស្រប។",
            rationale_en="Factor expression using algebraic identities and term grouping.",
            description_km="បំបែកជាផលគុណកត្តាតាមរូបមន្តស្មើភាព និងកត្តារួម៖",
            description_en="Factor into product using algebraic identities and grouping:",
            expression=f"{prefix}= {latex(factored)}",
            is_verification=False,
            operation="factor",
            transformation="factor_expression",
        )
    )

    steps.append(
        SolutionStep(
            order=3,
            title_km="ផ្ទៀងផ្ទាត់លទ្ធផលដោយគុណពន្លាត",
            title_en="Verify by Expansion",
            rationale_km="គុណពន្លាតផលគុណកត្តាត្រឡប់មកវិញ ដើម្បីផ្ទៀងផ្ទាត់ភាពស្មើគ្នានឹងកន្សោមដើម។",
            rationale_en="Expand factored form back to confirm equality with original expression.",
            description_km="ផ្ទៀងផ្ទាត់លទ្ធផលដោយគុណពន្លាត៖",
            description_en="Verify result by expanding:",
            expression=rf"{latex(factored)} = {latex(expand(factored))} \quad \text{{(ត្រឹមត្រូវ / Verified)}}",
            is_verification=True,
            operation="verify",
            transformation="expand_verification",
        )
    )

    return steps
