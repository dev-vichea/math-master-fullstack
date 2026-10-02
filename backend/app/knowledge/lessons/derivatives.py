"""
Derivatives Lessons and Chapter (Grade 12 Differential Calculus).

Covers standard Cambodian curriculum for derivatives:
- Power Rule: (xⁿ)' = n*xⁿ⁻¹
- Radical / Chain Rule: (√u)' = u' / (2√u)
- Quotient Rule: (u/v)' = (u'v - uv') / v²
- Reciprocal / Power Rule: (1/uⁿ)' = -n*u' / uⁿ⁺¹
- Exponential Rule: (eᵘ)' = u'*eᵘ
- Sum and Difference Rule: (u ± v)' = u' ± v'
- Product Rule: (uv)' = u'v + uv'
"""

from __future__ import annotations

from app.knowledge.explanation_templates.calculus import template_derivative_step_by_step
from app.knowledge.models import (
    Chapter,
    Concept,
    CurriculumExample,
    Lesson,
    Method,
    RuleFormula,
    SubjectDomain,
)

# 1. Power Rule Method
method_power_rule = Method(
    id="method_derivative_power_rule",
    rule_id="rule_derivative_power_rule",
    name_km="វិធានដេរីវេស្វ័យគុណ xⁿ",
    name_en="Power Rule for Differentiation",
    description_km="ដេរីវេនៃ xⁿ គឺ n * xⁿ⁻¹។",
    description_en="Derivative of xⁿ is n * xⁿ⁻¹.",
    applicability="Power functions xⁿ where n is a real number.",
    template=template_derivative_step_by_step,
    examples=[
        CurriculumExample(
            id="ex_deriv_power",
            method_id="method_derivative_power_rule",
            problem_raw=r"\frac{d}{dx}(x^3)",
            problem_latex=r"\frac{d}{dx}(x^3)",
            solution_latex=r"3x^2",
            explanation_summary_km="ទម្លាក់ស្វ័យគុណ 3 មកមុខ រួចបន្ថយស្វ័យគុណ 1 បាន 3x²។",
        ),
    ],
)

rule_power_rule = RuleFormula(
    id="rule_derivative_power_rule",
    concept_id="concept_derivative_rules",
    name_km="រូបមន្តដេរីវេស្វ័យគុណ",
    name_en="Power Rule Identity",
    formula_latex=r"(x^n)' = n x^{n-1}",
    methods=[method_power_rule],
)

# 2. Radical Chain Rule Method (√u)' = u' / (2√u)
method_radical_chain = Method(
    id="method_derivative_radical_chain",
    rule_id="rule_derivative_radical_chain",
    name_km="វិធានដេរីវេរ៉ាឌីកាល់ (√u)'",
    name_en="Radical Chain Rule for Differentiation",
    description_km="ដេរីវេនៃ √u គឺ u' / (2√u)។",
    description_en="Derivative of √u is u' / (2√u).",
    applicability="Square root functions √(u(x)).",
    template=template_derivative_step_by_step,
    examples=[
        CurriculumExample(
            id="ex_deriv_radical",
            method_id="method_derivative_radical_chain",
            problem_raw=r"y = \sqrt{x^2 - 1}",
            problem_latex=r"y = \sqrt{x^2 - 1}",
            solution_latex=r"y' = \frac{x}{\sqrt{x^2 - 1}}",
            explanation_summary_km="អនុវត្ត (√u)' = u'/(2√u) ចំពោះ u = x² - 1 បាន y' = 2x/(2√(x²-1)) = x/√(x²-1)។",
        ),
    ],
)

rule_radical_chain = RuleFormula(
    id="rule_derivative_radical_chain",
    concept_id="concept_derivative_rules",
    name_km="រូបមន្តដេរីវេរ៉ាឌីកាល់",
    name_en="Radical Derivative Identity",
    formula_latex=r"(\sqrt{u})' = \frac{u'}{2\sqrt{u}}",
    methods=[method_radical_chain],
)

# 3. Quotient Rule Method (u/v)' = (u'v - uv') / v²
method_quotient_rule = Method(
    id="method_derivative_quotient_rule",
    rule_id="rule_derivative_quotient_rule",
    name_km="វិធានដេរីវេផលចែក (u/v)'",
    name_en="Quotient Rule for Differentiation",
    description_km="ដេរីវេនៃផលចែក u/v គឺ (u'v - uv') / v²។",
    description_en="Derivative of quotient u/v is (u'v - uv') / v².",
    applicability="Rational or fractional functions u(x)/v(x).",
    template=template_derivative_step_by_step,
    examples=[
        CurriculumExample(
            id="ex_deriv_quotient",
            method_id="method_derivative_quotient_rule",
            problem_raw=r"f(x) = \frac{e^x}{e^x + 3}",
            problem_latex=r"f(x) = \frac{e^x}{e^x + 3}",
            solution_latex=r"f'(x) = \frac{3e^x}{(e^x + 3)^2}",
            explanation_summary_km="អនុវត្ត (u/v)' = (u'v - uv')/v² រួចសម្រួលភាគយកបាន 3eˣ/(eˣ+3)²។",
        ),
    ],
)

rule_quotient_rule = RuleFormula(
    id="rule_derivative_quotient_rule",
    concept_id="concept_derivative_rules",
    name_km="រូបមន្តដេរីវេផលចែក",
    name_en="Quotient Rule Identity",
    formula_latex=r"\left(\frac{u}{v}\right)' = \frac{u'v - uv'}{v^2}",
    methods=[method_quotient_rule],
)

# 4. Reciprocal Power Rule Method (1/uⁿ)' = -n*u' / uⁿ⁺¹
method_reciprocal_power = Method(
    id="method_derivative_reciprocal_power",
    rule_id="rule_derivative_reciprocal_power",
    name_km="វិធានដេរីវេចម្រាសស្វ័យគុណ (1/uⁿ)'",
    name_en="Reciprocal Power Rule for Differentiation",
    description_km="ដេរីវេនៃ 1/uⁿ គឺ -n*u' / uⁿ⁺¹។",
    description_en="Derivative of 1/uⁿ is -n*u' / uⁿ⁺¹.",
    applicability="Functions of the form 1/(u(x))ⁿ.",
    template=template_derivative_step_by_step,
    examples=[
        CurriculumExample(
            id="ex_deriv_reciprocal",
            method_id="method_derivative_reciprocal_power",
            problem_raw=r"y = \frac{1}{(x^2 + 3x + 1)^2}",
            problem_latex=r"y = \frac{1}{(x^2 + 3x + 1)^2}",
            solution_latex=r"y' = -\frac{2(2x + 3)}{(x^2 + 3x + 1)^3}",
            explanation_summary_km="អនុវត្ត (1/u²)' = -2u'/u³ ចំពោះ u = x² + 3x + 1 បាន y' = -2(2x+3)/(x²+3x+1)³។",
        ),
    ],
)

rule_reciprocal_power = RuleFormula(
    id="rule_derivative_reciprocal_power",
    concept_id="concept_derivative_rules",
    name_km="រូបមន្តដេរីវេចម្រាសស្វ័យគុណ",
    name_en="Reciprocal Power Rule Identity",
    formula_latex=r"\left(\frac{1}{u^n}\right)' = -\frac{n u'}{u^{n+1}}",
    methods=[method_reciprocal_power],
)

# 5. Exponential Rule Method (eᵘ)' = u' eᵘ
method_exponential = Method(
    id="method_derivative_exponential",
    rule_id="rule_derivative_exponential",
    name_km="វិធានដេរីវេអិចស្បូណង់ស្យែល (eᵘ)'",
    name_en="Exponential Rule for Differentiation",
    description_km="ដេរីវេនៃ eᵘ គឺ u' * eᵘ។",
    description_en="Derivative of eᵘ is u' * eᵘ.",
    applicability="Exponential functions e^(u(x)).",
    template=template_derivative_step_by_step,
    examples=[
        CurriculumExample(
            id="ex_deriv_exp",
            method_id="method_derivative_exponential",
            problem_raw=r"f(x) = e^x + 3 - \frac{e^x}{e^x + 3}",
            problem_latex=r"f(x) = e^x + 3 - \frac{e^x}{e^x + 3}",
            solution_latex=r"f'(x) = \frac{e^x(e^{2x} + 6e^x + 6)}{(e^x + 3)^2}",
            explanation_summary_km="គណនាដេរីវេផលបូក ដក និងផលចែកនៃអនុគមន៍អិចស្បូណង់ស្យែល រួចតម្រូវភាគបែងរួម។",
        ),
    ],
)

rule_exponential = RuleFormula(
    id="rule_derivative_exponential",
    concept_id="concept_derivative_rules",
    name_km="រូបមន្តដេរីវេអិចស្បូណង់ស្យែល",
    name_en="Exponential Derivative Identity",
    formula_latex=r"(e^u)' = u' e^u",
    methods=[method_exponential],
)

# 6. Sum and Difference Rule
method_sum_diff = Method(
    id="method_derivative_sum_diff",
    rule_id="rule_derivative_sum_diff",
    name_km="វិធានដេរីវេផលបូកនិងផលដក",
    name_en="Sum and Difference Rule",
    description_km="ដេរីវេនៃផលបូក ដក ស្មើនឹងផលបូក ដកនៃដេរីវេតួនិមួយៗ។",
    description_en="Derivative of sum or difference equals sum or difference of derivatives.",
    applicability="Sums and differences of differentiable functions.",
    template=template_derivative_step_by_step,
    examples=[],
)

rule_sum_diff = RuleFormula(
    id="rule_derivative_sum_diff",
    concept_id="concept_derivative_rules",
    name_km="រូបមន្តដេរីវេផលបូក ដក",
    name_en="Sum and Difference Identity",
    formula_latex=r"(u \pm v)' = u' \pm v'",
    methods=[method_sum_diff],
)

# Concept & Lesson Aggregation
concept_derivative_rules = Concept(
    id="concept_derivative_rules",
    lesson_id="lesson_derivatives_computation",
    order=1,
    title_km="វិធានដេរីវេគ្រឹះ (Basic Differentiation Rules)",
    title_en="Basic Differentiation Rules",
    definition_km="វិធានសម្រាប់គណនាដេរីវេនៃអនុគមន៍ស្វ័យគុណ ផលបូក ផលចែក រ៉ាឌីកាល់ និងអិចស្បូណង់ស្យែល។",
    definition_en="Standard rules for computing derivatives of power, sum, quotient, radical, and exponential functions.",
    rules=[
        rule_power_rule,
        rule_radical_chain,
        rule_quotient_rule,
        rule_reciprocal_power,
        rule_exponential,
        rule_sum_diff,
    ],
)

lesson_derivatives = Lesson(
    id="lesson_derivatives_computation",
    chapter_id="chapter_calculus_derivatives",
    order=1,
    title_km="ដេរីវេនៃអនុគមន៍ (Derivatives of Functions)",
    title_en="Derivatives of Functions",
    description_km="និយមន័យដេរីវេ រូបមន្តគ្រឹះ ផលចែក រ៉ាឌីកាល់ អិចស្បូណង់ស្យែល និងការសម្រួលចម្លើយ។",
    description_en="Derivative definitions, standard formulas, quotient, radical, exponential, and simplification.",
    concepts=[concept_derivative_rules],
)

chapter_derivatives = Chapter(
    id="chapter_calculus_derivatives",
    domain=SubjectDomain.CALCULUS,
    order=4,
    title_km="ជំពូកទី៣ : ដេរីវេ និងអនុវត្តន៍ (Derivatives)",
    title_en="Chapter 3: Derivatives and Applications",
    grade_level=12,
    description_km="ដេរីវេនៃអនុគមន៍ និងការសិក្សាអថេរភាពនៃអនុគមន៍។",
    description_en="Derivatives and function behavior studies.",
    lessons=[lesson_derivatives],
)


def detect_derivative_method(expr: Any, var: Any = None) -> str:
    """Determine the primary curriculum method ID for differentiating a given expression."""
    import sympy
    from sympy import Add, Mul, Pow, Symbol, exp, log
    if hasattr(expr, "rhs") and hasattr(expr, "lhs"):
        expr = expr.rhs if expr.rhs != 0 else expr.lhs

    if var is None:
        symbols = list(expr.free_symbols) if hasattr(expr, "free_symbols") else []
        var = symbols[0] if symbols else Symbol("x")

    # 1. Natural Logarithm if outer expression is log(...)
    if isinstance(expr, log):
        return (
            "method_derivative_logarithm_basic"
            if expr.args and expr.args[0] == var
            else "method_derivative_logarithm_composite"
        )

    # 2. Exponential Rules
    if expr.has(exp):
        return "method_derivative_exponential"

    # 3. Reciprocal power rule: 1 / u^n
    num, den = expr.as_numer_denom()
    if num == 1 and den != 1 and den.has(var):
        return "method_derivative_reciprocal_power"

    # 4. General Quotient Rule: num / den where den depends on var
    if den != 1 and den.has(var):
        return "method_derivative_quotient_rule"

    # 5. Natural Logarithm Rules (Product / Sum / Composite)
    if expr.has(log):
        if isinstance(expr, Mul):
            return "method_derivative_logarithm_product"
        elif isinstance(expr, Add):
            return "method_derivative_sum_diff"
        return "method_derivative_logarithm_composite"

    # 6. Radical chain rule: contains sqrt(...) or (u)**(1/2) with inner polynomial/expression
    has_sqrt = any(
        isinstance(p, Pow) and p.exp == sympy.Rational(1, 2)
        for p in expr.atoms(Pow)
    )
    if has_sqrt:
        return "method_derivative_radical_chain"

    # 7. Sum / Difference
    if isinstance(expr, Add):
        return "method_derivative_sum_diff"

    # 8. Default to Power Rule
    return "method_derivative_power_rule"

