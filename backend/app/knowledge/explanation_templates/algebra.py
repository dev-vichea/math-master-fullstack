"""
Algebra Explanation Templates.

Curriculum-aligned step templates for algebraic expansion and factorization.
"""

from __future__ import annotations

from app.knowledge.models import ExplanationStepTemplate, ExplanationTemplate

# --- Template: Expansion Distributive ---
template_expansion_distributive = ExplanationTemplate(
    id="tmpl_expansion_distributive",
    method_id="method_distributive_multiplication",
    name_km="ការពន្លាតតាមលក្ខណៈបំបែកនៃផលគុណ",
    name_en="Expansion via Distributive Property",
    verification_strategy="none",
    pedagogical_notes_km="គុណតួនីមួយៗនៃកត្តាទី១ ទៅលើកត្តាទី២ រួចពន្លាតនិងបង្រួមតួដូចគ្នា។",
    pedagogical_notes_en="Multiply each term of the first factor by the second factor, then expand and combine like terms.",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="identify_expression",
            title_km="កន្សោមដើម",
            title_en="Original Expression",
            rationale_template_km="កត់សម្គាល់កន្សោមដើមដែលជាផលគុណរវាងពហុធានិងពហុធា។",
            rationale_template_en="Identify the original expression as a product of polynomials.",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="apply_distributive",
            title_km="អនុវត្តលក្ខណៈបំបែកនៃផលគុណ",
            title_en="Apply Distributive Property",
            rationale_template_km="គុណតួនីមួយៗនៃកត្តាទី១ ជាមួយនឹងកត្តាទី២ តាមរូបមន្ត (A + B)C = AC + BC។",
            rationale_template_en="Multiply each term of the first factor by the second factor using (A + B)C = AC + BC.",
            rule_reference="(A + B)C = AC + BC",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="expand_terms",
            title_km="គុណពន្លាតតួនីមួយៗចូលក្នុងវង់ក្រចក",
            title_en="Multiply Terms Inside Parentheses",
            rationale_template_km="គុណមេគុណលេខ និងបូកស្វ័យគុណនៃអថេរដូចគ្នា ដើម្បីបំប្លែងទៅជាតួទោល។",
            rationale_template_en="Multiply coefficients and add exponents of identical variables into individual terms.",
        ),
        ExplanationStepTemplate(
            order=4,
            action_type="combine_like_terms",
            title_km="បង្រួមតួដូចគ្នា និងរៀបតាមស្វ័យគុណចុះ",
            title_en="Combine Like Terms",
            rationale_template_km="បូកដកតួដែលមានអថេរ និងស្វ័យគុណដូចគ្នា ដើម្បីទទួលបានទម្រង់ពហុធាសាមញ្ញបំផុត។",
            rationale_template_en="Add or subtract like terms to obtain the simplest polynomial form.",
        ),
    ],
)

# --- Template: Common Factor Extraction ---
template_fact_common_factor = ExplanationTemplate(
    id="tmpl_fact_common_factor",
    method_id="method_common_factor_extraction",
    name_km="ការដាក់ជាផលគុណកត្តាដោយទាញកត្តារួម",
    name_en="Factoring by Common Factor Extraction",
    verification_strategy="expand_to_verify",
    pedagogical_notes_km="ស្វែងរកតួចែករួមធំបំផុត (GCF) នៃមេគុណលេខ និងអថេរ រួចទាញចេញក្រៅវង់ក្រចក។",
    pedagogical_notes_en="Find the greatest common factor (GCF) of coefficients and variables, and extract outside parentheses.",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="identify_common_factor",
            title_km="កំណត់កត្តារួមធំបំផុត (GCF)",
            title_en="Identify Greatest Common Factor",
            rationale_template_km="ពិនិត្យតួនីមួយៗក្នុងកន្សោម ដើម្បីស្វែងរកកត្តារួមនៃមេគុណលេខ និងអថេរដែលមានស្វ័យគុណទាបបំផុត។",
            rationale_template_en="Inspect each term to find the common factor of numeric coefficients and variables with lowest exponent.",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="extract_factor",
            title_km="ទាញកត្តារួមចេញក្រៅវង់ក្រចក",
            title_en="Factor Out Common Term",
            rationale_template_km="អនុវត្តរូបមន្ត ka + kb = k(a + b) ដោយដាក់កត្តារួមនៅមុខវង់ក្រចក។",
            rationale_template_en="Apply formula ka + kb = k(a + b) by placing the common factor in front of parentheses.",
            rule_reference="ka + kb = k(a + b)",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="simplify_remainder",
            title_km="សម្រួលកន្សោមក្នុងវង់ក្រចក",
            title_en="Simplify Remaining Expression",
            rationale_template_km="ចែកតួនីមួយៗនៃកន្សោមដើមនឹងកត្តារួម ដើម្បីទទួលបានកន្សោមសាមញ្ញក្នុងវង់ក្រចក។",
            rationale_template_en="Divide each original term by the common factor to produce the simplified quotient inside parentheses.",
        ),
        ExplanationStepTemplate(
            order=4,
            action_type="verify_result",
            title_km="ផ្ទៀងផ្ទាត់លទ្ធផលដោយគុណពន្លាតត្រឡប់ក្រោយ",
            title_en="Verify by Expanding Back",
            rationale_template_km="គុណពន្លាតកត្តាដែលទើបតែរកឃើញចូលក្នុងវង់ក្រចកវិញ ដើម្បីផ្ទៀងផ្ទាត់ថាតើស្មើនឹងកន្សោមដើមពិតឬមិនពិត។",
            rationale_template_en="Multiply the extracted factor back inside parentheses to confirm equality with the original expression.",
            is_verification=True,
        ),
    ],
)

# --- Template: Difference of Squares ---
template_fact_diff_squares = ExplanationTemplate(
    id="tmpl_fact_diff_squares",
    method_id="method_diff_squares",
    name_km="ការដាក់ជាផលគុណកត្តាតាមរូបមន្តផលសងការេ",
    name_en="Factoring Difference of Squares",
    verification_strategy="expand_to_verify",
    pedagogical_notes_km="បំប្លែងកន្សោមទៅជាទម្រង់ a² - b² រួចសរសេរជា (a - b)(a + b)។",
    pedagogical_notes_en="Transform expression into a² - b² and rewrite as (a - b)(a + b).",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="identify_squares",
            title_km="កំណត់ទម្រង់ផលសងការេ a² − b²",
            title_en="Identify Difference of Squares a² − b²",
            rationale_template_km="កត់សម្គាល់ថាកន្សោមមានពីរតួដែលជាផលដករវាងការេពេញពីរ។",
            rationale_template_en="Recognize that the expression consists of two terms separated by a subtraction of perfect squares.",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="extract_terms_a_b",
            title_km="កំណត់តម្លៃ a និង b",
            title_en="Identify Terms a and b",
            rationale_template_km="ទាញយកឫសការេនៃតួនីមួយៗដើម្បីកំណត់តម្លៃមូលដ្ឋាន a និង b។",
            rationale_template_en="Extract the square root of each term to identify the base values of a and b.",
            rule_reference="a = \\sqrt{a^2}, \\; b = \\sqrt{b^2}",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="apply_identity",
            title_km="អនុវត្តរូបមន្ត a² − b² = (a − b)(a + b)",
            title_en="Apply Identity a² − b² = (a − b)(a + b)",
            rationale_template_km="ជំនួសតម្លៃ a និង b ចូលក្នុងរូបមន្តផលគុណកត្តា។",
            rationale_template_en="Substitute a and b into the difference of squares factoring formula.",
            rule_reference="a^2 - b^2 = (a - b)(a + b)",
        ),
        ExplanationStepTemplate(
            order=4,
            action_type="verify_result",
            title_km="ផ្ទៀងផ្ទាត់ចម្លើយដោយគុណពន្លាត",
            title_en="Verify by Expansion",
            rationale_template_km="គុណពន្លាត (a - b)(a + b) = a² - b² ដើម្បីផ្ទៀងផ្ទាត់ភាពត្រឹមត្រូវនៃចម្លើយ។",
            rationale_template_en="Expand (a - b)(a + b) = a² - b² to verify mathematical correctness.",
            is_verification=True,
        ),
    ],
)

# --- Template: Quadratic Trinomial Split ---
template_fact_trinomial = ExplanationTemplate(
    id="tmpl_fact_trinomial",
    method_id="method_trinomial_split",
    name_km="ការដាក់ជាផលគុណកត្តាត្រីធាដឺក្រេទីពីរ x² + bx + c",
    name_en="Factoring Quadratic Trinomials x² + bx + c",
    verification_strategy="expand_to_verify",
    pedagogical_notes_km="ស្វែងរកពីរចំនួន p និង q ដែល p + q = b និង p * q = c រួចសរសេរជា (x + p)(x + q)។",
    pedagogical_notes_en="Find two numbers p and q such that p + q = b and p * q = c, then factor as (x + p)(x + q).",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="identify_coefficients",
            title_km="កំណត់មេគុណនៃត្រីធា x² + bx + c",
            title_en="Identify Coefficients of x² + bx + c",
            rationale_template_km="កត់សម្គាល់មេគុណ b (ផលបូក) និងតួលេខសេរី c (ផលគុណ)។",
            rationale_template_en="Identify coefficient b (sum) and constant c (product).",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="find_sum_product_numbers",
            title_km="ស្វែងរកពីរចំនួន p និង q",
            title_en="Find Integers p and q",
            rationale_template_km="រកពីរចំនួនដែលបូកបញ្ចូលគ្នាស្មើ b និងគុណគ្នាស្មើ c។",
            rationale_template_en="Find two integers with sum equal to b and product equal to c.",
            rule_reference="p + q = b, \\; p \\times q = c",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="write_factored_form",
            title_km="សរសេរជាផលគុណកត្តា (x + p)(x + q)",
            title_en="Write Factored Form (x + p)(x + q)",
            rationale_template_km="ជំនួសតម្លៃ p និង q ចូលក្នុងទម្រង់ផលគុណកត្តា។",
            rationale_template_en="Substitute p and q into the factored binomial product form.",
            rule_reference="x^2 + (p+q)x + pq = (x + p)(x + q)",
        ),
        ExplanationStepTemplate(
            order=4,
            action_type="verify_result",
            title_km="ផ្ទៀងផ្ទាត់ចម្លើយដោយគុណពន្លាត",
            title_en="Verify by Expansion",
            rationale_template_km="គុណពន្លាត (x + p)(x + q) = x² + (p+q)x + pq ដើម្បីផ្ទៀងផ្ទាត់។",
            rationale_template_en="Expand (x + p)(x + q) = x² + (p+q)x + pq to verify correctness.",
            is_verification=True,
        ),
    ],
)
