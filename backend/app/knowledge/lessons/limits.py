"""
Limits of Functions Lessons and Chapter (Grade 12 BacII Focus).
"""

from __future__ import annotations

from app.knowledge.methods.conjugate import method_limit_conjugate
from app.knowledge.methods.factorization import method_limit_factor_cancel
from app.knowledge.methods.substitution import method_limit_direct_substitution
from app.knowledge.models import (
    Chapter,
    Concept,
    Lesson,
    RuleFormula,
    SubjectDomain,
)

# Rule 1: Direct Substitution for Continuous Functions
rule_limit_direct_substitution = RuleFormula(
    id="rule_limit_direct_substitution",
    concept_id="concept_continuous_limits",
    name_km="លក្ខណៈជំនួសតម្លៃផ្ទាល់សម្រាប់អនុគមន៍ជាប់",
    name_en="Direct Substitution for Continuous Functions",
    formula_latex=r"\lim_{x \to c} f(x) = f(c)",
    description_km="ប្រសិនបើ f ជាអនុគមន៍កំណត់ និងជាប់ត្រង់ c នោះលីមីតស្មើនឹងតម្លៃអនុគមន៍ត្រង់ c។",
    description_en="If f is defined and continuous at point c, the limit equals the function value f(c).",
    methods=[method_limit_direct_substitution],
)

# Concept 1: Continuous Function Limits
concept_continuous_limits = Concept(
    id="concept_continuous_limits",
    lesson_id="lesson_limits_evaluation",
    order=1,
    title_km="លីមីតនៃអនុគមន៍ជាប់ (Direct Substitution)",
    title_en="Limits of Continuous Functions",
    definition_km="ការគណនាលីមីតដោយជំនួសអថេរផ្ទាល់ត្រង់ចំណុចខិតជិត ដែលអនុគមន៍មានតម្លៃកំណត់ជាក់លាក់។",
    definition_en="Evaluating limits by direct evaluation at points where the function is well-defined and continuous.",
    rules=[rule_limit_direct_substitution],
)

# Rule 2: Conjugate Rationalization for [0/0] Radicals
rule_conjugate = RuleFormula(
    id="rule_conjugate_rationalization",
    concept_id="concept_indeterminate_forms",
    name_km="កន្សោមឆ្លាស់នៃរ៉ាឌីកាល់",
    name_en="Radical Conjugate Identity",
    formula_latex=r"(\sqrt{A} - B)(\sqrt{A} + B) = A - B^2",
    description_km="គុណកន្សោមឆ្លាស់ដើម្បីបំបាត់រ៉ាឌីកាល់ និងសម្រួលកត្តាសូន្យ (x - c)។",
    description_en="Multiply by conjugate to eliminate radicals and cancel indeterminate zero factors.",
    methods=[method_limit_conjugate],
)

# Rule 3: Factorization and Cancellation for [0/0]
rule_limit_factorization = RuleFormula(
    id="rule_limit_factorization",
    concept_id="concept_indeterminate_forms",
    name_km="ការដាក់ជាផលគុណកត្តាសម្រួលកត្តាសូន្យ",
    name_en="Factorization and Zero Factor Cancellation",
    formula_latex=r"\lim_{x \to c} \frac{(x - c)P(x)}{(x - c)Q(x)} = \lim_{x \to c} \frac{P(x)}{Q(x)}",
    description_km="សម្រួលកត្តាសូន្យរួម (x - c) នៃរាងមិនកំណត់ 0/0។",
    description_en="Cancel common factor (x - c) responsible for vanishing numerator and denominator.",
    methods=[method_limit_factor_cancel],
)

# Concept 2: Indeterminate Forms
concept_indeterminate_forms = Concept(
    id="concept_indeterminate_forms",
    lesson_id="lesson_limits_evaluation",
    order=2,
    title_km="លីមីតរាងមិនកំណត់ [0/0]",
    title_en="Indeterminate Form [0/0]",
    definition_km="លីមីតនៃផលធៀបអនុគមន៍ដែលភាគយកនិងភាគបែងខិតជិតសូន្យដំណាលគ្នា។",
    definition_en="Limits of quotients where both numerator and denominator approach zero.",
    rules=[rule_conjugate, rule_limit_factorization],
)

lesson_limits = Lesson(
    id="lesson_limits_evaluation",
    chapter_id="chapter_calculus_limits",
    order=1,
    title_km="លីមីតនៃអនុគមន៍ (Limits of Functions)",
    title_en="Limits of Functions",
    description_km="ការគណនាលីមីត និងការលុបរាងមិនកំណត់ 0/0, ∞/∞ ស្របតាមកម្មវិធីបាក់ឌុប។",
    description_en="Limit evaluation and indeterminate form resolution for Grade 12 BacII.",
    concepts=[concept_continuous_limits, concept_indeterminate_forms],
)

chapter_limits = Chapter(
    id="chapter_calculus_limits",
    domain=SubjectDomain.CALCULUS,
    order=1,
    title_km="ជំពូកទី១ : លីមីតនៃអនុគមន៍ (Limits)",
    title_en="Chapter 1: Limits of Functions",
    grade_level=12,
    description_km="លីមីតនៃអនុគមន៍ និងភាពជាប់នៃអនុគមន៍។",
    description_en="Limits and continuity of functions.",
    lessons=[lesson_limits],
)
