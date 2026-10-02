"""
Integrals Lessons and Chapter (Grade 12 Calculus - Cambodian BacII Curriculum).

Covers:
- Primitives (ព្រីមីទីវ):
  * Definition and verification: F'(x) = f(x)
  * Finding general primitives on interval I
  * Initial value problems (លក្ខខណ្ឌដើម F(x₀) = y₀)
- Indefinite Integrals (អាំងតេក្រាលមិនកំណត់):
  * Power rule: ∫ xⁿ dx = xⁿ⁺¹/(n+1) + C
  * Rational & radical powers: ∫ x⁻ⁿ dx, ∫ 1/√x dx = 2√x + C
  * Logarithmic form: ∫ 1/x dx = ln|x| + C, ∫ 1/(ax+b) dx = (1/a)ln|ax+b| + C
  * Exponential rules: ∫ eˣ dx = eˣ + C, ∫ eᵃˣ⁺ᵇ dx = (1/a)eᵃˣ⁺ᵇ + C
  * Trigonometric rules: ∫ sin x dx = -cos x + C, ∫ cos x dx = sin x + C,
    ∫ 1/cos²x dx = tan x + C, ∫ 1/sin²x dx = -cot x + C
  * Composite exponential form: ∫ u'(x) eᵘ⁽ˣ⁾ dx = eᵘ⁽ˣ⁾ + C
  * Integration by Parts (អាំងតេក្រាលដោយផ្នែក): ∫ u dv = uv - ∫ v du
  * Substitution Method (វិធីជំនួសអថេរ): u = g(x)
- Definite Integrals (អាំងតេក្រាលកំណត់):
  * Fundamental Theorem of Calculus: ∫ₐᵇ f(x) dx = [F(x)]ₐᵇ = F(b) - F(a)
"""

from __future__ import annotations

from typing import Any

import sympy
from sympy import Add, Eq, Integral, Mul, Pow, Symbol, exp, log, sin, cos, tan

from app.knowledge.explanation_templates.calculus import (
    template_derivative_step_by_step,
    template_limit_direct_substitution,
)
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
# 1. Methods: Primitives Verification & Initial Values
# ---------------------------------------------------------------------------

method_primitive_verification = Method(
    id="method_primitive_verification",
    rule_id="rule_primitive_definition",
    name_km="ផ្ទៀងផ្ទាត់ព្រីមីទីវ F'(x) = f(x)",
    name_en="Primitive / Antiderivative Verification",
    description_km="បង្ហាញថា F(x) ជាព្រីមីទីវនៃ f(x) ដោយគណនាដេរីវេ F'(x) រួចផ្ទៀងផ្ទាត់ថា F'(x) = f(x)។",
    description_en="Show F(x) is an antiderivative of f(x) by showing F'(x) = f(x).",
    applicability="Verification problems: Show that F(x) is a primitive of f(x).",
    examples=[
        CurriculumExample(
            id="ex_prim_verif_1",
            method_id="method_primitive_verification",
            problem_raw=r"F(x) = 3x^3 - 7x, f(x) = 9x^2 - 7",
            problem_latex=r"F(x) = 3x^3 - 7x, \quad f(x) = 9x^2 - 7",
            solution_latex=r"F'(x) = (3x^3 - 7x)' = 9x^2 - 7 = f(x)",
            explanation_summary_km="គណនាដេរីវេ F'(x) ឃើញស្មើ f(x) នាំឱ្យ F(x) ជាព្រីមីទីវនៃ f(x)។",
        ),
    ],
)

method_primitive_general = Method(
    id="method_primitive_general",
    rule_id="rule_primitive_definition",
    name_km="រកព្រីមីទីវទូទៅលើចន្លោះ I",
    name_en="General Antiderivative on Interval",
    description_km="រកព្រីមីទីវទូទៅ F(x) = ∫ f(x) dx = G(x) + c លើចន្លោះ I។",
    description_en="Find general primitive F(x) = ∫ f(x) dx + c on interval I.",
    applicability="Finding antiderivative F(x) on interval I.",
    examples=[],
)

method_primitive_initial_value = Method(
    id="method_primitive_initial_value",
    rule_id="rule_primitive_initial_value",
    name_km="រកព្រីមីទីវផ្ទៀងផ្ទាត់លក្ខខណ្ឌដើម F(x₀) = y₀",
    name_en="Particular Antiderivative with Initial Value",
    description_km="រកព្រីមីទីវទូទៅ F(x) = G(x) + c រួចជំនួស x = x₀ ស្មើ y₀ ដើម្បីរកតម្លៃចំនួនថេរ c។",
    description_en="Find particular primitive by solving for constant c using initial condition F(x₀) = y₀.",
    applicability="Problems with initial condition F(x₀) = y₀.",
    examples=[
        CurriculumExample(
            id="ex_prim_init_1",
            method_id="method_primitive_initial_value",
            problem_raw=r"f(x) = x^2 - x, F(0) = 1",
            problem_latex=r"f(x) = x^2 - x, \quad F(0) = 1",
            solution_latex=r"F(x) = \frac{x^3}{3} - \frac{x^2}{2} + 1",
            explanation_summary_km="រកព្រីមីទីវទូទៅ x³/3 - x²/2 + c រួចជំនួស F(0) = 1 រកឃើញ c = 1។",
        ),
    ],
)

rule_primitive_definition = RuleFormula(
    id="rule_primitive_definition",
    concept_id="concept_primitive_definition",
    name_km="និយមន័យព្រីមីទីវ",
    name_en="Definition of Antiderivative",
    formula_latex=r"F'(x) = f(x) \iff F(x) = \int f(x) \, dx + C",
    methods=[method_primitive_verification, method_primitive_general],
)

rule_primitive_initial_value = RuleFormula(
    id="rule_primitive_initial_value",
    concept_id="concept_primitive_definition",
    name_km="ព្រីមីទីវផ្ទៀងផ្ទាត់លក្ខខណ្ឌដើម",
    name_en="Antiderivative Initial Value Problem",
    formula_latex=r"F(x) = \int f(x) \, dx + c, \quad F(x_0) = y_0 \implies c = y_0 - G(x_0)",
    methods=[method_primitive_initial_value],
)

# ---------------------------------------------------------------------------
# 2. Methods: Indefinite Integral Rules
# ---------------------------------------------------------------------------

method_integral_power_rule = Method(
    id="method_integral_power_rule",
    rule_id="rule_integral_power_rule",
    name_km="រូបមន្តអាំងតេក្រាលស្វ័យគុណ",
    name_en="Power Rule for Integration",
    description_km="អាំងតេក្រាលនៃ xⁿ dx គឺ (xⁿ⁺¹)/(n+1) + C (ចំពោះ n ≠ -1)។",
    description_en="Integral of xⁿ dx is (xⁿ⁺¹)/(n+1) + C for n != -1.",
    applicability="Integrals of power expressions xⁿ and polynomials.",
    examples=[
        CurriculumExample(
            id="ex_integ_poly",
            method_id="method_integral_power_rule",
            problem_raw=r"\int (2x^3 - 5x^2 + 3x + 1) \, dx",
            problem_latex=r"\int (2x^3 - 5x^2 + 3x + 1) \, dx",
            solution_latex=r"\frac{x^4}{2} - \frac{5x^3}{3} + \frac{3x^2}{2} + x + C",
            explanation_summary_km="អនុវត្តវិធានស្វ័យគុណតួនិមួយៗ រួចបូកចំនួនថេរ C។",
        ),
    ],
)

method_integral_rational_power = Method(
    id="method_integral_rational_power",
    rule_id="rule_integral_rational_power",
    name_km="អាំងតេក្រាលស្វ័យគុណសនិទាន និងរ៉ាឌីកាល់",
    name_en="Rational and Radical Power Integration",
    description_km="បំប្លែងរ៉ាឌីកាល់ ឬភាគបែងជាស្វ័យគុណ xᵃ រួចអនុវត្តរូបមន្តស្វ័យគុណ។",
    description_en="Convert radicals or denominators to powers xᵃ and apply power rule.",
    applicability="Integrals of forms 1/√x, √x, P(x)/xⁿ, etc.",
    examples=[],
)

method_integral_exponential = Method(
    id="method_integral_exponential",
    rule_id="rule_integral_exponential",
    name_km="រូបមន្តអាំងតេក្រាលអិចស្ប៉ូណង់ស្យែល",
    name_en="Exponential Integration Rule",
    description_km="អាំងតេក្រាលនៃ eᵃˣ⁺ᵇ dx គឺ (1/a)eᵃˣ⁺ᵇ + C។",
    description_en="Integral of eᵃˣ⁺ᵇ dx is (1/a)eᵃˣ⁺ᵇ + C.",
    applicability="Exponential expressions of the form e^(ax+b).",
    examples=[],
)

method_integral_trigonometric = Method(
    id="method_integral_trigonometric",
    rule_id="rule_integral_trigonometric",
    name_km="រូបមន្តអាំងតេក្រាលត្រីកោណមាត្រ",
    name_en="Trigonometric Integration Rules",
    description_km="∫ sin x dx = -cos x + C, ∫ cos x dx = sin x + C, ∫ 1/cos²x dx = tan x + C, ∫ 1/sin²x dx = -cot x + C។",
    description_en="Standard trigonometric integrals for sin, cos, sec², and csc².",
    applicability="Integrals involving trigonometric functions.",
    examples=[],
)

method_integral_logarithmic = Method(
    id="method_integral_logarithmic",
    rule_id="rule_integral_logarithmic",
    name_km="រូបមន្តអាំងតេក្រាលនាំទៅរកលោការីតនេពែ",
    name_en="Logarithmic Form Integration",
    description_km="អាំងតេក្រាលនៃ (1/x) dx គឺ ln|x| + C និង ∫ u'/u dx = ln|u| + C។",
    description_en="Integral of 1/x dx is ln|x| + C and ∫ u'/u dx is ln|u| + C.",
    applicability="Integrals of the form 1/x, 1/(ax+b), or u'(x)/u(x).",
    examples=[],
)

rule_integral_power_rule = RuleFormula(
    id="rule_integral_power_rule",
    concept_id="concept_indefinite_integral",
    name_km="រូបមន្តអាំងតេក្រាលស្វ័យគុណ",
    name_en="Indefinite Integral Power Rule",
    formula_latex=r"\int x^n \, dx = \frac{x^{n+1}}{n+1} + C \quad (n \neq -1)",
    methods=[method_integral_power_rule],
)

rule_integral_rational_power = RuleFormula(
    id="rule_integral_rational_power",
    concept_id="concept_indefinite_integral",
    name_km="រូបមន្តអាំងតេក្រាលស្វ័យគុណសនិទាន",
    name_en="Rational Power Integration Rule",
    formula_latex=r"\int \frac{1}{\sqrt{x}} \, dx = 2\sqrt{x} + C, \quad \int x^{-n} \, dx = -\frac{1}{(n-1)x^{n-1}} + C",
    methods=[method_integral_rational_power],
)

rule_integral_exponential = RuleFormula(
    id="rule_integral_exponential",
    concept_id="concept_indefinite_integral",
    name_km="រូបមន្តអាំងតេក្រាលអិចស្ប៉ូណង់ស្យែល",
    name_en="Exponential Integration Formula",
    formula_latex=r"\int e^{ax+b} \, dx = \frac{1}{a}e^{ax+b} + C",
    methods=[method_integral_exponential],
)

rule_integral_trigonometric = RuleFormula(
    id="rule_integral_trigonometric",
    concept_id="concept_indefinite_integral",
    name_km="រូបមន្តអាំងតេក្រាលត្រីកោណមាត្រ",
    name_en="Trigonometric Integration Formulas",
    formula_latex=r"\int \sin x \, dx = -\cos x + C, \quad \int \cos x \, dx = \sin x + C, \quad \int \frac{1}{\cos^2 x} \, dx = \tan x + C",
    methods=[method_integral_trigonometric],
)

rule_integral_logarithmic = RuleFormula(
    id="rule_integral_logarithmic",
    concept_id="concept_indefinite_integral",
    name_km="រូបមន្តអាំងតេក្រាលលោការីតនេពែ",
    name_en="Logarithmic Integration Formula",
    formula_latex=r"\int \frac{1}{x} \, dx = \ln|x| + C, \quad \int \frac{u'}{u} \, dx = \ln|u| + C",
    methods=[method_integral_logarithmic],
)

# ---------------------------------------------------------------------------
# 3. Methods: Techniques (Composite exp form, Substitution, By Parts)
# ---------------------------------------------------------------------------

method_integral_exp_composite = Method(
    id="method_integral_exp_composite",
    rule_id="rule_integral_exp_composite",
    name_km="អាំងតេក្រាលទម្រង់ \\int u'(x) e^{u(x)} dx = e^{u(x)} + C",
    name_en="Composite Exponential Integration Form",
    description_km="នៅពេលកន្សោមមានទម្រង់ u'(x) * e^{u(x)} អាំងតេក្រាលរបស់វាគឺ e^{u(x)} + C។",
    description_en="When expression is of form u'(x) * e^{u(x)}, integral is e^{u(x)} + C.",
    applicability="Integrals of the form u'(x) * e^(u(x)) or k * u'(x) * e^(u(x)).",
    examples=[
        CurriculumExample(
            id="ex_integ_comp_exp_1",
            method_id="method_integral_exp_composite",
            problem_raw=r"\int 2x e^{x^2} \, dx",
            problem_latex=r"\int 2x e^{x^2} \, dx",
            solution_latex=r"e^{x^2} + C",
            explanation_summary_km="ដោយសារ (x²)' = 2x នោះតាមរូបមន្ត ∫ u' eᵘ dx = eᵘ + C គេបាន e^(x²) + C។",
        ),
    ],
)

method_integral_substitution = Method(
    id="method_integral_substitution",
    rule_id="rule_integral_substitution",
    name_km="វិធីជំនួសអថេរ (Method of Substitution)",
    name_en="Method of Substitution",
    description_km="តាង u = g(x) នាំឱ្យ du = g'(x) dx រួចបំប្លែងអាំងតេក្រាលជាអថេរ u។",
    description_en="Substitute u = g(x), du = g'(x) dx to transform integral into simpler u-integral.",
    applicability="Integrals where integrand contains composite function and its derivative.",
    examples=[],
)

method_integral_by_parts = Method(
    id="method_integral_by_parts",
    rule_id="rule_integral_by_parts",
    name_km="វិធីអាំងតេក្រាលដោយផ្នែក \\int u \\, dv = uv - \\int v \\, du",
    name_en="Integration by Parts",
    description_km="ជ្រើសរើស u តាមលំដាប់ LIATE (Log, InvTrig, Alg, Trig, Exp) និង dv = v' dx រួចអនុវត្តរូបមន្ត ∫ u dv = uv - ∫ v du។",
    description_en="Apply integration by parts formula ∫ u dv = uv - ∫ v du using LIATE rule.",
    applicability="Products of polynomials and exponentials, logarithms, or trigonometric functions.",
    examples=[
        CurriculumExample(
            id="ex_integ_by_parts_1",
            method_id="method_integral_by_parts",
            problem_raw=r"\int x e^{-x} \, dx",
            problem_latex=r"\int x e^{-x} \, dx",
            solution_latex=r"-(x + 1)e^{-x} + C",
            explanation_summary_km="តាង u = x => du = dx, dv = e⁻ˣ dx => v = -e⁻ˣ។ គេបាន -x e⁻ˣ - ∫ (-e⁻ˣ) dx = -(x+1)e⁻ˣ + C។",
        ),
    ],
)

rule_integral_exp_composite = RuleFormula(
    id="rule_integral_exp_composite",
    concept_id="concept_integral_techniques",
    name_km="រូបមន្តអាំងតេក្រាលទម្រង់ u' eᵘ",
    name_en="Composite Exponential Integration Formula",
    formula_latex=r"\int u'(x) e^{u(x)} \, dx = e^{u(x)} + C",
    methods=[method_integral_exp_composite],
)

rule_integral_substitution = RuleFormula(
    id="rule_integral_substitution",
    concept_id="concept_integral_techniques",
    name_km="រូបមន្តវិធីជំនួសអថេរ",
    name_en="Substitution Rule Formula",
    formula_latex=r"\int f(g(x)) g'(x) \, dx = \int f(u) \, du \quad (u = g(x))",
    methods=[method_integral_substitution],
)

rule_integral_by_parts = RuleFormula(
    id="rule_integral_by_parts",
    concept_id="concept_integral_techniques",
    name_km="រូបមន្តអាំងតេក្រាលដោយផ្នែក",
    name_en="Integration by Parts Formula",
    formula_latex=r"\int u \, dv = uv - \int v \, du",
    methods=[method_integral_by_parts],
)

# ---------------------------------------------------------------------------
# 4. Methods: Definite Integrals
# ---------------------------------------------------------------------------

method_integral_definite = Method(
    id="method_integral_definite",
    rule_id="rule_definite_fundamental",
    name_km="អាំងតេក្រាលកំណត់ \\int_a^b f(x) dx = [F(x)]_a^b = F(b) - F(a)",
    name_en="Fundamental Theorem of Definite Integrals",
    description_km="គណនាព្រីមីទីវ F(x) រួចជំនួសគោលលើ b និងគោលក្រោម a តាមរូបមន្ត [F(x)]ₐᵇ = F(b) - F(a)។",
    description_en="Evaluate antiderivative F(x) between bounds a and b: F(b) - F(a).",
    applicability="Definite integrals with lower bound a and upper bound b.",
    examples=[],
)

rule_definite_fundamental = RuleFormula(
    id="rule_definite_fundamental",
    concept_id="concept_definite_integral",
    name_km="ទ្រឹស្តីបទគ្រឹះនៃគណិតវិភាគសម្រាប់អាំងតេក្រាលកំណត់",
    name_en="Fundamental Theorem of Calculus for Definite Integrals",
    formula_latex=r"\int_a^b f(x) \, dx = \left[F(x)\right]_a^b = F(b) - F(a)",
    methods=[method_integral_definite],
)

# ---------------------------------------------------------------------------
# Concepts & Lessons Aggregation
# ---------------------------------------------------------------------------

concept_primitive_definition = Concept(
    id="concept_primitive_definition",
    lesson_id="lesson_primitives_indefinite",
    order=1,
    title_km="និយមន័យព្រីមីទីវ (Antiderivatives / Primitives)",
    title_en="Primitives and Antiderivatives",
    definition_km="អនុគមន៍ F ហៅថាជាព្រីមីទីវនៃ f លើចន្លោះ I លុះត្រាតែ F'(x) = f(x) ចំពោះគ្រប់ x ក្នុង I។",
    definition_en="A function F is an antiderivative of f on I if F'(x) = f(x) for all x in I.",
    rules=[rule_primitive_definition, rule_primitive_initial_value],
)

concept_indefinite_integral = Concept(
    id="concept_indefinite_integral",
    lesson_id="lesson_primitives_indefinite",
    order=2,
    title_km="អាំងតេក្រាលមិនកំណត់ និងរូបមន្តគ្រឹះ (Indefinite Integrals)",
    title_en="Indefinite Integrals & Basic Rules",
    definition_km="សំណុំនៃគ្រប់ព្រីមីទីវនៃ f ហៅថាអាំងតេក្រាលមិនកំណត់ តាងដោយ ∫ f(x) dx = F(x) + C។",
    definition_en="The set of all antiderivatives of f is the indefinite integral ∫ f(x) dx = F(x) + C.",
    rules=[
        rule_integral_power_rule,
        rule_integral_rational_power,
        rule_integral_exponential,
        rule_integral_trigonometric,
        rule_integral_logarithmic,
    ],
)

concept_integral_techniques = Concept(
    id="concept_integral_techniques",
    lesson_id="lesson_primitives_indefinite",
    order=3,
    title_km="វិធីសាស្ត្រគណនាអាំងតេក្រាល (Integration Techniques)",
    title_en="Integration Techniques",
    definition_km="វិធីសាស្ត្រគណនាអាំងតេក្រាលដោយផ្នែក ∫ u dv = uv - ∫ v du និងវិធីជំនួសអថេរ។",
    definition_en="Integration techniques including integration by parts and substitution.",
    rules=[
        rule_integral_by_parts,
        rule_integral_exp_composite,
        rule_integral_substitution,
    ],
)

concept_definite_integral = Concept(
    id="concept_definite_integral",
    lesson_id="lesson_definite_integrals",
    order=4,
    title_km="អាំងតេក្រាលកំណត់ (Definite Integrals)",
    title_en="Definite Integrals",
    definition_km="អាំងតេក្រាលកំណត់ពី a ទៅ b នៃ f(x) dx គឺ F(b) - F(a)។",
    definition_en="Definite integral from a to b of f(x) dx is F(b) - F(a).",
    rules=[rule_definite_fundamental],
)

lesson_primitives_indefinite = Lesson(
    id="lesson_primitives_indefinite",
    chapter_id="chapter_calculus_integrals",
    order=1,
    title_km="មេរៀនទី១ : ព្រីមីទីវ និងអាំងតេក្រាលមិនកំណត់ (Primitives & Indefinite Integrals)",
    title_en="Lesson 1: Primitives and Indefinite Integrals",
    description_km="និយមន័យព្រីមីទីវ រូបមន្តគ្រឹះ វិធីអាំងតេក្រាលដោយផ្នែក និងជំនួសអថេរ។",
    description_en="Primitives, basic formulas, integration by parts, and substitution.",
    concepts=[
        concept_primitive_definition,
        concept_indefinite_integral,
        concept_integral_techniques,
    ],
)

lesson_definite_integrals = Lesson(
    id="lesson_definite_integrals",
    chapter_id="chapter_calculus_integrals",
    order=2,
    title_km="មេរៀនទី២ : អាំងតេក្រាលកំណត់ (Definite Integrals)",
    title_en="Lesson 2: Definite Integrals",
    description_km="ទ្រឹស្តីបទគ្រឹះនៃគណិតវិភាគ លក្ខណៈអាំងតេក្រាលកំណត់ និងការគណនាតម្លៃ។",
    description_en="Fundamental theorem of calculus, definite integral properties, and evaluation.",
    concepts=[concept_definite_integral],
)

lesson_integrals = lesson_primitives_indefinite

chapter_integrals = Chapter(
    id="chapter_calculus_integrals",
    domain=SubjectDomain.CALCULUS,
    order=5,
    title_km="ជំពូកទី៥ : អាំងតេក្រាល (Integrals)",
    title_en="Chapter 5: Integrals",
    grade_level=12,
    description_km="ព្រីមីទីវ អាំងតេក្រាលមិនកំណត់ និងអាំងតេក្រាលកំណត់នៃអនុគមន៍។",
    description_en="Primitives, indefinite integrals, and definite integrals.",
    lessons=[lesson_primitives_indefinite, lesson_definite_integrals],
)


# ---------------------------------------------------------------------------
# Method Detection Logic
# ---------------------------------------------------------------------------

def detect_integral_method(expr: Any, var: Any = None) -> str:
    """Determine the primary curriculum method ID for integrating a given expression."""
    if isinstance(expr, Integral):
        # 1. Definite Integral
        if expr.limits and len(expr.limits[0]) == 3:
            return "method_integral_definite"

        integrand = expr.args[0]
        if expr.limits:
            limit_tuple = expr.limits[0]
            var = limit_tuple[0] if isinstance(limit_tuple, (tuple, list, sympy.Tuple)) else limit_tuple
        else:
            symbols = list(integrand.free_symbols) if hasattr(integrand, "free_symbols") else []
            var = symbols[0] if symbols else Symbol("x")
    else:
        integrand = expr
        if var is None:
            symbols = list(expr.free_symbols) if hasattr(expr, "free_symbols") else []
            var = symbols[0] if symbols else Symbol("x")

    # 1. Simplify denominator cancellation if rational expression
    num, den = integrand.as_numer_denom()
    if den != 1 and den.has(var):
        canceled = sympy.cancel(integrand)
        if canceled.as_numer_denom()[1] == 1 or canceled != integrand:
            if not canceled.has(log) and not integrand.has(log):
                integrand = canceled

    # 2. Expand quadratic powers (e.g. (1 - e^x)^2, (e^x +- e^-x)^2, (2x-3)^2)
    if isinstance(integrand, Pow) and integrand.exp == 2:
        if integrand.has(exp) or integrand.is_polynomial(var):
            integrand = sympy.expand(integrand)

    # 3. Composite Exponential: k * u'(x) * exp(u(x)) with non-linear u
    if integrand.has(exp):
        exp_atoms = [e for e in integrand.atoms(exp) if e.has(var)]
        if len(exp_atoms) == 1:
            exp_term = exp_atoms[0]
            inner_u = exp_term.args[0]
            deriv_u = sympy.diff(inner_u, var)
            if deriv_u != 0:
                coeff = sympy.simplify((integrand / exp_term) / deriv_u)
                if coeff.is_number and coeff != 0:
                    if not (inner_u.is_polynomial(var) and sympy.degree(inner_u, var) == 1):
                        return "method_integral_exp_composite"

    # 4. Integration by Parts:
    # A. Explicit logarithm in integrand (e.g. x ln x, ln(x)/x^2)
    if integrand.has(log):
        return "method_integral_by_parts"

    # B. Product of polynomial P(x) (deg >= 1) with exp, trig, or composite power
    if isinstance(integrand, Mul):
        args = list(integrand.args)
        pow_composite = [a for a in args if isinstance(a, Pow) and a.base != var and a.base.has(var)]
        poly_terms = [
            a
            for a in args
            if a.is_polynomial(var) and a not in pow_composite and sympy.degree(a, var) >= 1
        ]
        if poly_terms:
            if pow_composite:
                return "method_integral_by_parts"
            if integrand.has(exp):
                exp_atoms = [e for e in integrand.atoms(exp) if e.has(var)]
                if len(exp_atoms) == 1:
                    inner_u = exp_atoms[0].args[0]
                    if inner_u.is_polynomial(var) and sympy.degree(inner_u, var) == 1:
                        return "method_integral_by_parts"
            if any(integrand.has(fn) for fn in (sin, cos)):
                return "method_integral_by_parts"

    # 5. Trigonometric Integrals
    if any(integrand.has(fn) for fn in (sin, cos, tan)):
        return "method_integral_trigonometric"

    # 6. Logarithmic: u'/u, 1/x, or 1/(ax+b)
    num, den = integrand.as_numer_denom()
    if den != 1 and den.has(var):
        if num == 1 or num.is_number:
            if den == var:
                return "method_integral_logarithmic"
            if den.is_polynomial(var) and sympy.degree(den, var) == 1:
                return "method_integral_logarithmic"
        deriv_den = sympy.diff(den, var)
        if deriv_den != 0:
            ratio = sympy.simplify(num / deriv_den)
            if ratio.is_number and ratio != 0:
                return "method_integral_logarithmic"

    # 7. Pure Exponential: e^(ax+b)
    if integrand.has(exp):
        return "method_integral_exponential"

    # 8. Fractional powers & Radicals / Rational denominators
    if den != 1 and den.has(var):
        return "method_integral_rational_power"

    has_fractional_pow = any(
        isinstance(p, Pow) and p.exp.is_Rational and p.exp.q != 1
        for p in integrand.atoms(Pow)
    )
    if has_fractional_pow:
        return "method_integral_rational_power"

    # 9. Default to Power Rule
    return "method_integral_power_rule"
