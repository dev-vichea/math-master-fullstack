"""
Natural Logarithm Lessons and Chapter (Grade 12 Calculus).

Covers standard Cambodian Grade 12 BacII curriculum for Logarithmic Functions:
- Properties and Evaluation of Natural Logarithm:
  * ln(e) = 1, ln(1) = 0
  * e^(ln a) = a (for a > 0)
  * ln(e^u) = u (for all u)
  * ln(a * b) = ln(a) + ln(b)
  * ln(a / b) = ln(a) - ln(b)
  * ln(a^n) = n * ln(a)
- Limits of Logarithmic Functions:
  * lim_{x -> +oo} (ln x) / x^n = 0 (n > 0)
  * lim_{x -> 0^+} x^n * ln(x) = 0 (n > 0)
  * lim_{x -> 0} ln(1 + x) / x = 1
  * lim_{x -> +oo} ln(x) = +oo, lim_{x -> 0^+} ln(x) = -oo
- Derivatives of Logarithmic Functions:
  * Basic Rule: (ln x)' = 1 / x
  * Composite / Chain Rule: (ln u)' = u' / u
  * Product & Quotient Rules involving ln(x)
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

# ---------------------------------------------------------------------------
# 1. Methods: Logarithm Properties & Evaluation
# ---------------------------------------------------------------------------

method_logarithm_property_exp = Method(
    id="method_logarithm_property_exp",
    rule_id="rule_logarithm_properties",
    name_km="រូបមន្តលក្ខណៈ e^{\\ln a} = a",
    name_en="Exponential of Natural Logarithm Property",
    description_km="ចំពោះ a > 0 យើងមាន e^{\\ln a} = a។",
    description_en="For any a > 0, e^{\\ln a} = a.",
    applicability="Expressions of the form e^{\\ln(a)}.",
    examples=[
        CurriculumExample(
            id="ex_log_exp_7",
            method_id="method_logarithm_property_exp",
            problem_raw=r"e^{\ln 7}",
            problem_latex=r"e^{\ln 7}",
            solution_latex=r"7",
            explanation_summary_km=r"អនុវត្តរូបមន្ត e^{\ln a} = a ចំពោះ a = 7 គេបាន e^{\ln 7} = 7។",
        ),
    ],
)

method_logarithm_property_log_exp = Method(
    id="method_logarithm_property_log_exp",
    rule_id="rule_logarithm_properties",
    name_km="រូបមន្តលក្ខណៈ \\ln(e^u) = u",
    name_en="Logarithm of Exponential Property",
    description_km="ចំពោះគ្រប់កន្សោម u យើងមាន \\ln(e^u) = u។",
    description_en="For any expression u, \\ln(e^u) = u.",
    applicability="Expressions of the form \\ln(e^u).",
    examples=[
        CurriculumExample(
            id="ex_log_exp_x_minus_2",
            method_id="method_logarithm_property_log_exp",
            problem_raw=r"\ln(e^{x-2})",
            problem_latex=r"\ln(e^{x-2})",
            solution_latex=r"x - 2",
            explanation_summary_km=r"អនុវត្តរូបមន្ត \ln(e^u) = u ចំពោះ u = x - 2 គេបាន \ln(e^{x-2}) = x - 2។",
        ),
    ],
)

rule_logarithm_properties = RuleFormula(
    id="rule_logarithm_properties",
    concept_id="concept_logarithm_properties",
    name_km="រូបមន្តលក្ខណៈនៃអនុគមន៍លោការីតនេពែ",
    name_en="Properties of Natural Logarithms",
    formula_latex=r"e^{\ln a} = a, \quad \ln(e^u) = u, \quad \ln(ab) = \ln a + \ln b",
    methods=[method_logarithm_property_exp, method_logarithm_property_log_exp],
)

# ---------------------------------------------------------------------------
# 2. Methods: Limits of Logarithmic Functions
# ---------------------------------------------------------------------------

method_limit_logarithm_infinity = Method(
    id="method_limit_logarithm_infinity",
    rule_id="rule_limit_logarithm_fundamental",
    name_km="លីមីតគ្រឹះលោការីតត្រង់អនន្ត \\lim_{x \\to +\\infty} \\frac{\\ln x}{x^n} = 0",
    name_en="Logarithmic Limit at Infinity",
    description_km="នៅពេល x ខិតជិត +\\infty កន្សោម (\\ln x)/x^n មានលីមីតស្មើ 0 (ចំពោះ n > 0)។",
    description_en="As x approaches +oo, (ln x) / x^n approaches 0 for any n > 0.",
    applicability="Limits at +oo of the form (ln x) / x^n or x^(-n) * ln(x).",
    examples=[
        CurriculumExample(
            id="ex_lim_log_inf_x5",
            method_id="method_limit_logarithm_infinity",
            problem_raw=r"\lim_{x \to +\infty} x^{-5} \ln x",
            problem_latex=r"\lim_{x \to +\infty} \frac{\ln x}{x^5}",
            solution_latex=r"0",
            explanation_summary_km=r"អនុវត្តរូបមន្តលីមីតគ្រឹះ \lim_{x \to +\infty} \frac{\ln x}{x^n} = 0 (n=5) គេបានលីមីតស្មើ 0។",
        ),
    ],
)

method_limit_logarithm_zero = Method(
    id="method_limit_logarithm_zero",
    rule_id="rule_limit_logarithm_fundamental",
    name_km="លីមីតគ្រឹះលោការីតត្រង់សូន្យ \\lim_{x \\to 0^+} x^n \\ln x = 0",
    name_en="Logarithmic Limit at Zero",
    description_km="នៅពេល x ខិតជិត 0 ខាងស្តាំ (x > 0) កន្សោម x^n * \\ln x មានលីមីតស្មើ 0 (ចំពោះ n > 0)។",
    description_en="As x approaches 0 from the right, x^n * ln(x) approaches 0 for any n > 0.",
    applicability="Limits at 0+ of the form x^n * ln(x).",
    examples=[
        CurriculumExample(
            id="ex_lim_log_zero_x",
            method_id="method_limit_logarithm_zero",
            problem_raw=r"\lim_{x \to 0^+} x \ln x",
            problem_latex=r"\lim_{x \to 0^+} x \ln x",
            solution_latex=r"0",
            explanation_summary_km=r"អនុវត្តរូបមន្តលីមីតគ្រឹះ \lim_{x \to 0^+} x^n \ln x = 0 (n=1) គេបានលីមីតស្មើ 0។",
        ),
    ],
)

rule_limit_logarithm_fundamental = RuleFormula(
    id="rule_limit_logarithm_fundamental",
    concept_id="concept_logarithm_limits",
    name_km="រូបមន្តលីមីតគ្រឹះនៃអនុគមន៍លោការីតនេពែ",
    name_en="Fundamental Limits of Natural Logarithm",
    formula_latex=r"\lim_{x \to +\infty} \frac{\ln x}{x^n} = 0, \quad \lim_{x \to 0^+} x^n \ln x = 0 \quad (n > 0)",
    methods=[method_limit_logarithm_infinity, method_limit_logarithm_zero],
)

# ---------------------------------------------------------------------------
# 3. Methods: Derivatives of Logarithmic Functions
# ---------------------------------------------------------------------------

method_derivative_logarithm_basic = Method(
    id="method_derivative_logarithm_basic",
    rule_id="rule_derivative_logarithm",
    name_km="រូបមន្តដេរីវេគ្រឹះ (\\ln x)' = \\frac{1}{x}",
    name_en="Basic Natural Logarithm Derivative Rule",
    description_km="ដេរីវេនៃអនុគមន៍ \\ln x ចំពោះ x > 0 គឺ 1/x។",
    description_en="Derivative of ln(x) is 1/x for x > 0.",
    applicability="Functions of the form y = ln(x).",
    template=template_derivative_step_by_step,
    examples=[
        CurriculumExample(
            id="ex_deriv_log_x",
            method_id="method_derivative_logarithm_basic",
            problem_raw=r"\frac{d}{dx}(\ln x)",
            problem_latex=r"(\ln x)'",
            solution_latex=r"\frac{1}{x}",
            explanation_summary_km=r"អនុវត្តរូបមន្ត (\ln x)' = \frac{1}{x}។",
        ),
    ],
)

method_derivative_logarithm_composite = Method(
    id="method_derivative_logarithm_composite",
    rule_id="rule_derivative_logarithm_composite",
    name_km="រូបមន្តដេរីវេអនុគមន៍បណ្តាក់ (\\ln u)' = \\frac{u'}{u}",
    name_en="Composite Chain Rule for Natural Logarithm",
    description_km="ដេរីវេនៃអនុគមន៍បណ្តាក់ \\ln u គឺ u'/u។",
    description_en="Derivative of composite function ln(u) is u'/u.",
    applicability="Composite functions of the form y = ln(u(x)).",
    template=template_derivative_step_by_step,
    examples=[
        CurriculumExample(
            id="ex_deriv_log_composite_sqrt",
            method_id="method_derivative_logarithm_composite",
            problem_raw=r"\ln(x + \sqrt{1 + x^2})",
            problem_latex=r"y = \ln(x + \sqrt{1 + x^2})",
            solution_latex=r"\frac{1}{\sqrt{1 + x^2}}",
            explanation_summary_km=r"អនុវត្តរូបមន្ត (\ln u)' = \frac{u'}{u} ចំពោះ u = x + \sqrt{1 + x^2} គេបាន y' = \frac{1}{\sqrt{1 + x^2}}។",
        ),
    ],
)

method_derivative_logarithm_product = Method(
    id="method_derivative_logarithm_product",
    rule_id="rule_derivative_logarithm",
    name_km="វិធានផលគុណជាមួយលោការីត (u \\cdot \\ln v)'",
    name_en="Product Rule with Logarithmic Factors",
    description_km="អនុវត្តវិធានផលគុណ (uv)' = u'v + uv' លើកន្សោមដែលមានកត្តាលោការីតនេពែ។",
    description_en="Apply product rule (uv)' = u'v + uv' to expressions with logarithmic factors.",
    applicability="Products of polynomials, radicals, or powers with ln(x).",
    template=template_derivative_step_by_step,
    examples=[
        CurriculumExample(
            id="ex_deriv_log_product_sqrt",
            method_id="method_derivative_logarithm_product",
            problem_raw=r"y = \sqrt{x} \ln x",
            problem_latex=r"y = \sqrt{x} \ln x",
            solution_latex=r"\frac{\ln x + 2}{2\sqrt{x}}",
            explanation_summary_km=r"អនុវត្តវិធានផលគុណ (uv)' = u'v + uv' ចំពោះ u = \sqrt{x}, v = \ln x គេបាន y' = \frac{\ln x + 2}{2\sqrt{x}}។",
        ),
    ],
)

rule_derivative_logarithm = RuleFormula(
    id="rule_derivative_logarithm",
    concept_id="concept_logarithm_derivatives",
    name_km="រូបមន្តដេរីវេនៃអនុគមន៍លោការីតនេពែ",
    name_en="Derivative Rule for Natural Logarithm",
    formula_latex=r"(\ln x)' = \frac{1}{x}",
    methods=[method_derivative_logarithm_basic, method_derivative_logarithm_product],
)

rule_derivative_logarithm_composite = RuleFormula(
    id="rule_derivative_logarithm_composite",
    concept_id="concept_logarithm_derivatives",
    name_km="រូបមន្តដេរីវេអនុគមន៍បណ្តាក់លោការីត",
    name_en="Chain Rule for Logarithmic Composite Functions",
    formula_latex=r"(\ln u)' = \frac{u'}{u}",
    methods=[method_derivative_logarithm_composite],
)

# ---------------------------------------------------------------------------
# 4. Concepts, Lesson, and Chapter
# ---------------------------------------------------------------------------

concept_logarithm_properties = Concept(
    id="concept_logarithm_properties",
    lesson_id="lesson_natural_logarithm",
    order=1,
    title_km="លោការីតនេពែនៃ e និងលក្ខណៈពិជគណិត",
    title_en="Natural Logarithm of e and Algebraic Properties",
    definition_km="និយមន័យលោការីតនេពែ និងលក្ខណៈគ្រឹះ៖ e^{\\ln a} = a, \\ln(e^u) = u, \\ln(ab) = \\ln a + \\ln b។",
    definition_en="Definition of natural logarithm and fundamental algebraic properties.",
    rules=[rule_logarithm_properties],
)

concept_logarithm_limits = Concept(
    id="concept_logarithm_limits",
    lesson_id="lesson_natural_logarithm",
    order=2,
    title_km="លីមីតនៃអនុគមន៍លោការីតនេពែ",
    title_en="Limits of Natural Logarithmic Functions",
    definition_km="លីមីតគ្រឹះនៃលោការីតនេពែត្រង់ +\\infty និងត្រង់ 0 ខាងស្តាំ។",
    definition_en="Fundamental limits of natural logarithm at +infinity and at 0+.",
    rules=[rule_limit_logarithm_fundamental],
)

concept_logarithm_derivatives = Concept(
    id="concept_logarithm_derivatives",
    lesson_id="lesson_natural_logarithm",
    order=3,
    title_km="ដេរីវេនៃអនុគមន៍លោការីតនេពែ",
    title_en="Derivatives of Natural Logarithmic Functions",
    definition_km="រូបមន្តដេរីវេគ្រឹះ (\\ln x)' = 1/x និងរូបមន្តដេរីវេអនុគមន៍បណ្តាក់ (\\ln u)' = u'/u។",
    definition_en="Standard and composite chain rules for natural logarithms.",
    rules=[rule_derivative_logarithm, rule_derivative_logarithm_composite],
)

lesson_natural_logarithm = Lesson(
    id="lesson_natural_logarithm",
    chapter_id="chapter_exponential_and_logarithmic_functions",
    order=2,
    title_km="មេរៀនទី២ : អនុគមន៍លោការីតនេពែ (Natural Logarithmic Functions)",
    title_en="Lesson 2: Natural Logarithmic Functions",
    description_km="លោការីតនេពែនៃ e លក្ខណៈពិជគណិត លីមីតគ្រឹះ និងដេរីវេនៃអនុគមន៍លោការីតនេពែ។",
    description_en="Natural logarithm of e, algebraic properties, fundamental limits, and derivatives.",
    concepts=[
        concept_logarithm_properties,
        concept_logarithm_limits,
        concept_logarithm_derivatives,
    ],
)

chapter_logarithms = Chapter(
    id="chapter_exponential_and_logarithmic_functions",
    domain=SubjectDomain.CALCULUS,
    order=4,
    title_km="ជំពូកទី៤ : អនុគមន៍អិចស្ប៉ូណង់ស្យែល និងអនុគមន៍លោការីត",
    title_en="Chapter 4: Exponential and Logarithmic Functions",
    grade_level=12,
    description_km="អនុគមន៍អិចស្ប៉ូណង់ស្យែល និងអនុគមន៍លោការីតនេពែ ព្រមទាំងអនុវត្តន៍ដេរីវេ និងលីមីត។",
    description_en="Exponential and logarithmic functions with their limits, derivatives, and applications.",
    lessons=[lesson_natural_logarithm],
)
