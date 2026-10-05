"""
Differential Equations Lessons and Chapter (Grade 12 BacII Mathematics).

Covers standard Cambodian curriculum for first-order differential equations:
1. Linear Homogeneous First-Order ODEs: y' + ay = 0 -> y = A * e^{-ax} (A in R)
2. Direct Integration ODEs: y' = f(x) -> y = int f(x) dx + C
3. Separable ODEs: y'/y = f(x) -> ln|y| = F(x) + C -> y = A * e^{F(x)}
4. Cauchy Initial Value Problems: y(x0) = y0 -> Determine constant A or C
5. Solution Verification: Show that y = f(x) satisfies F(x, y, y') = 0
"""

from __future__ import annotations

from typing import Any

from sympy import Derivative, Function, Symbol

from app.knowledge.models import (
    Chapter,
    Concept,
    CurriculumExample,
    ExplanationStepTemplate,
    ExplanationTemplate,
    Lesson,
    Method,
    RuleFormula,
    SubjectDomain,
)

# --- Template 1: Linear Homogeneous ODE (y' + ay = 0) ---
template_ode_linear_homogeneous = ExplanationTemplate(
    id="tmpl_ode_linear_homogeneous",
    method_id="method_ode_linear_homogeneous",
    name_km="ដោះស្រាយសមីការឌីផេរ៉ង់ស្យែលលីនេអ៊ែរលំដាប់ទី១ y' + ay = 0",
    name_en="Solve First-Order Linear Homogeneous ODE y' + ay = 0",
    verification_strategy="substitution",
    pedagogical_notes_km="សមីការមានទម្រង់ y' + ay = 0 ឬ dy/dx + ay = 0។ កំណត់មេគុណ a រួចសរសេរចម្លើយទូទៅតាមរូបមន្ត y = A e^{-ax} ដែល A ជាចំនួនថេរ។ ប្រសិនបើមានលក្ខខណ្ឌដើម y(x0) = y0 ត្រូវជំនួសដើម្បីរកតម្លៃ A។",
    pedagogical_notes_en="The equation has standard form y' + ay = 0. Identify coefficient a and apply general solution y = A * e^{-ax} where A is an arbitrary real constant.",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="standardize_ode",
            title_km="សរសេរសមីការក្នុងទម្រង់ស្តង់ដារ",
            title_en="Write in Standard Form",
            rationale_template_km="បំលែងសមីការឲ្យទៅជាទម្រង់ស្តង់ដារ y' + ay = 0។",
            rationale_template_en="Transform the equation to standard form y' + ay = 0.",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="identify_coefficient",
            title_km="កំណត់មេគុណ a",
            title_en="Identify Coefficient a",
            rationale_template_km="ទាញរកតម្លៃមេគុណ a ពីសមីការស្តង់ដារ។",
            rationale_template_en="Extract coefficient a from the standard equation.",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="state_general_solution",
            title_km="សរសេរចម្លើយទូទៅ",
            title_en="State General Solution",
            rationale_template_km="អនុវត្តរូបមន្តចម្លើយទូទៅ y = A \\cdot e^{-ax} ដែល A ជាចំនួនថេរ។",
            rationale_template_en="Apply the general solution formula y = A * e^{-ax} where A is an arbitrary constant.",
            rule_reference="y' + ay = 0 \\iff y = A e^{-ax}",
        ),
        ExplanationStepTemplate(
            order=4,
            action_type="apply_initial_condition",
            title_km="ជំនួសលក្ខខណ្ឌដើម (បើមាន)",
            title_en="Apply Initial Condition (if given)",
            rationale_template_km="ជំនួស x = x0 និង y(x0) = y0 ដើម្បីគណនាតម្លៃថេរ A។",
            rationale_template_en="Substitute x = x0 and y(x0) = y0 to solve for constant A.",
        ),
        ExplanationStepTemplate(
            order=5,
            action_type="conclude_particular_solution",
            title_km="សន្និដ្ឋានចម្លើយចុងក្រោយ",
            title_en="State Final Solution",
            rationale_template_km="សរសេរចម្លើយពិសេសដែលទទួលបានពីការជំនួសតម្លៃ A។",
            rationale_template_en="State the final particular solution.",
        ),
    ],
)

# --- Template 2: Direct Integration ODE (y' = f(x)) ---
template_ode_direct_integration = ExplanationTemplate(
    id="tmpl_ode_direct_integration",
    method_id="method_ode_direct_integration",
    name_km="ដោះស្រាយសមីការឌីផេរ៉ង់ស្យែលតាមអាំងតេក្រាលផ្ទាល់ y' = f(x)",
    name_en="Solve Differential Equation by Direct Integration y' = f(x)",
    verification_strategy="differentiation",
    pedagogical_notes_km="សមីការ y' = f(x) នាំឲ្យ y = \\int f(x) dx + C។ គណនាព្រីមីទីវ ឬអាំងតេក្រាលមិនកំណត់ រួចរកតម្លៃ C តាមលក្ខខណ្ឌដើមបើមាន។",
    pedagogical_notes_en="Directly integrate both sides: y = int f(x) dx + C. Determine constant C using initial condition if provided.",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="express_as_integral",
            title_km="បម្លែងជាទម្រង់អាំងតេក្រាល",
            title_en="Express as Indefinite Integral",
            rationale_template_km="គេមាន y' = f(x) នាំឲ្យ y = \\int f(x)\\,dx។",
            rationale_template_en="Given y' = f(x), express y = int f(x) dx.",
            rule_reference="y' = f(x) \\implies y = \\int f(x)\\,dx",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="compute_integral",
            title_km="គណនាអាំងតេក្រាល",
            title_en="Compute Integral",
            rationale_template_km="អនុវត្តវិធានអាំងតេក្រាលស្វ័យគុណ អិចស្បូណង់ស្យែល ឬលោការីតលើកន្សោម f(x)។",
            rationale_template_en="Apply integration rules to determine the antiderivative.",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="solve_constant",
            title_km="គណនាតម្លៃថេរ C (បើមានលក្ខខណ្ឌដើម)",
            title_en="Solve for Constant C (if initial condition given)",
            rationale_template_km="ជំនួសតម្លៃ x = x0 និង y(x0) = y0 ចូលក្នុងចម្លើយទូទៅដើម្បីទាញរក C។",
            rationale_template_en="Substitute x = x0 and y(x0) = y0 to find constant C.",
        ),
        ExplanationStepTemplate(
            order=4,
            action_type="conclude_solution",
            title_km="សន្និដ្ឋានចម្លើយចុងក្រោយ",
            title_en="State Final Solution",
            rationale_template_km="សរសេរចម្លើយសម្រួលចុងក្រោយនៃសមីការឌីផេរ៉ង់ស្យែល។",
            rationale_template_en="State the final simplified solution.",
        ),
    ],
)

# --- Template 3: Verification of ODE Solution ---
template_ode_verification = ExplanationTemplate(
    id="tmpl_ode_verification",
    method_id="method_ode_verification",
    name_km="បង្ហាញថាអនុគមន៍ជាចម្លើយនៃសមីការឌីផេរ៉ង់ស្យែល",
    name_en="Verify Function is a Solution to Differential Equation",
    verification_strategy="substitution",
    pedagogical_notes_km="គណនាដេរីវេ y' នៃអនុគមន៍ដែលឲ្យ រួចជំនួស y និង y' ចូលក្នុងអង្គខាងឆ្វេងនៃសមីការឌីផេរ៉ង់ស្យែល។ សម្រួលអង្គខាងឆ្វេងឲ្យឃើញស្មើអង្គខាងស្តាំ។",
    pedagogical_notes_en="Differentiate the given function y = f(x) to find y'. Substitute y and y' into the differential equation and verify both sides are equal.",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="compute_derivative",
            title_km="គណនាដេរីវេនៃអនុគមន៍ដែលឲ្យ",
            title_en="Compute Derivative of Given Function",
            rationale_template_km="គណនា y' = [f(x)]' តាមវិធានដេរីវេ។",
            rationale_template_en="Differentiate given function y = f(x) to obtain y'.",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="substitute_into_ode",
            title_km="ជំនួស y និង y' ចូលក្នុងសមីការឌីផេរ៉ង់ស្យែល",
            title_en="Substitute y and y' into Differential Equation",
            rationale_template_km="ជំនួសកន្សោម y និងដេរីវេ y' ចូលក្នុងអង្គខាងឆ្វេង (LHS) នៃសមីការ។",
            rationale_template_en="Substitute expressions for y and y' into the left-hand side of the ODE.",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="simplify_and_compare",
            title_km="សម្រួលកន្សោម និងប្រៀបធៀបជាមួយអង្គខាងស្តាំ",
            title_en="Simplify and Compare with RHS",
            rationale_template_km="ពន្លា និងសម្រួលតួសងខាងដើម្បីបង្ហាញថា LHS = RHS។",
            rationale_template_en="Simplify algebraic terms and verify LHS equals RHS.",
        ),
        ExplanationStepTemplate(
            order=4,
            action_type="conclude_verification",
            title_km="សន្និដ្ឋានការផ្ទៀងផ្ទាត់",
            title_en="Conclude Verification",
            rationale_template_km="សន្និដ្ឋានថាអនុគមន៍ពិតជាចម្លើយនៃសមីការឌីផេរ៉ង់ស្យែល។",
            rationale_template_en="Conclude that the function is indeed a solution to the ODE.",
        ),
    ],
)

# 1. Linear Homogeneous Method
method_linear_homogeneous = Method(
    id="method_ode_linear_homogeneous",
    rule_id="rule_ode_linear_homogeneous",
    name_km="វិធីដោះស្រាយសមីការលីនេអ៊ែរលំដាប់ទី១ y' + ay = 0",
    name_en="First-Order Linear Homogeneous ODE Method",
    description_km="រកមេគុណ a រួចជំនួសក្នុងរូបមន្តចម្លើយទូទៅ y = A e^{-ax}។",
    description_en="Identify coefficient a and use formula y = A * e^{-ax}.",
    applicability="First-order linear homogeneous equations y' + ay = 0 or Ay' + By = 0.",
    template=template_ode_linear_homogeneous,
    examples=[
        CurriculumExample(
            id="ex_ode_lin_1",
            method_id="method_ode_linear_homogeneous",
            problem_raw=r"\frac{dy}{dx} + 2y = 0",
            problem_latex=r"\frac{dy}{dx} + 2y = 0",
            solution_latex=r"y = A e^{-2x} \quad (A \in \mathbb{R})",
            explanation_summary_km="ដោយ a = 2 នោះចម្លើយទូទៅគឺ y = A e^{-2x} ដែល A ជាចំនួនថេរ។",
        ),
    ],
)

rule_linear_homogeneous = RuleFormula(
    id="rule_ode_linear_homogeneous",
    concept_id="concept_first_order_ode",
    name_km="រូបមន្តសមីការឌីផេរ៉ង់ស្យែល y' + ay = 0",
    name_en="First-Order Linear Homogeneous Formula",
    formula_latex=r"y' + ay = 0 \iff y = A e^{-ax} \quad (A \in \mathbb{R})",
    methods=[method_linear_homogeneous],
)

# 2. Direct Integration Method
method_direct_integration = Method(
    id="method_ode_direct_integration",
    rule_id="rule_ode_direct_integration",
    name_km="វិធីដោះស្រាយដោយអាំងតេក្រាលផ្ទាល់ y' = f(x)",
    name_en="Direct Integration Method",
    description_km="ធ្វើអាំងតេក្រាលសងខាង y = int f(x) dx + C។",
    description_en="Integrate both sides y = int f(x) dx + C.",
    applicability="Differential equations of the form y' = f(x) or g(x)y' = f(x).",
    template=template_ode_direct_integration,
    examples=[
        CurriculumExample(
            id="ex_ode_dir_1",
            method_id="method_ode_direct_integration",
            problem_raw="y' = 2x^2 - x + 1",
            problem_latex="y' = 2x^2 - x + 1",
            solution_latex=r"y = \frac{2}{3}x^3 - \frac{1}{2}x^2 + x + C",
            explanation_summary_km=r"គេមាន y = \int (2x^2 - x + 1) dx = \frac{2}{3}x^3 - \frac{1}{2}x^2 + x + C។",
        ),
    ],
)

rule_direct_integration = RuleFormula(
    id="rule_ode_direct_integration",
    concept_id="concept_first_order_ode",
    name_km="រូបមន្តអាំងតេក្រាលផ្ទាល់",
    name_en="Direct Integration Formula",
    formula_latex=r"y' = f(x) \implies y = \int f(x)\,dx + C",
    methods=[method_direct_integration],
)

# 3. Verification Method
method_verification = Method(
    id="method_ode_verification",
    rule_id="rule_ode_verification",
    name_km="វិធីផ្ទៀងផ្ទាត់ចម្លើយសមីការឌីផេរ៉ង់ស្យែល",
    name_en="ODE Solution Verification Method",
    description_km="គណនា y' រួចជំនួស y និង y' ចូលសមីការដើម្បីផ្ទៀងផ្ទាត់ LHS = RHS។",
    description_en="Differentiate y = f(x) and substitute into ODE to verify equality.",
    applicability="Problems asking to show that a given function satisfies a differential equation.",
    template=template_ode_verification,
    examples=[
        CurriculumExample(
            id="ex_ode_verif_1",
            method_id="method_ode_verification",
            problem_raw="y = x + e^x , y' - y = 1 - x",
            problem_latex="y = x + e^x , y' - y = 1 - x",
            solution_latex=r"\text{ពិត}",
            explanation_summary_km="y' = 1 + e^x នាំឲ្យ y' - y = (1 + e^x) - (x + e^x) = 1 - x ពិត។",
        ),
    ],
)

rule_verification = RuleFormula(
    id="rule_ode_verification",
    concept_id="concept_ode_verification",
    name_km="វិធានផ្ទៀងផ្ទាត់ចម្លើយសមីការឌីផេរ៉ង់ស្យែល",
    name_en="ODE Verification Rule",
    formula_latex=r"F(x, y, y') = 0 \text{ with } y = f(x), y' = f'(x)",
    methods=[method_verification],
)

# 4. Second-Order Linear Homogeneous Method (ay'' + by' + cy = 0)
template_ode_second_order_homogeneous = ExplanationTemplate(
    id="tmpl_ode_second_order_homogeneous",
    method_id="method_ode_second_order_homogeneous",
    name_km="ដោះស្រាយសមីការឌីផេរ៉ង់ស្យែលលីនេអ៊ែរលំដាប់ទីពីរ អូម៉ូសែន ay'' + by' + cy = 0",
    name_en="Solve Second-Order Linear Homogeneous ODE ay'' + by' + cy = 0",
    verification_strategy="characteristic_equation",
    pedagogical_notes_km="សមីការមានទម្រង់ ay'' + by' + cy = 0។ សរសេរសមីការសម្គាល់ ar^2 + br + c = 0 រួចគណនាឌីស្គ្រីមីណង់ Delta = b^2 - 4ac។ បើ Delta > 0 សមីការសម្គាល់មានឫសពីរផ្សេងគ្នា r1, r2 នាំឲ្យ y = C1 e^{r1 x} + C2 e^{r2 x}។ បើ Delta = 0 សមីការសម្គាល់មានឫសឌុប r0 = -b/(2a) នាំឲ្យ y = (C1 x + C2) e^{r0 x}។ បើ Delta < 0 សមីការសម្គាល់មានឫសកុំផ្លិចឆ្លាស់ r = alpha +/- i*beta នាំឲ្យ y = e^{alpha x}(C1 cos(beta x) + C2 sin(beta x))។",
    pedagogical_notes_en="Solve the characteristic equation ar^2 + br + c = 0 via discriminant Delta = b^2 - 4ac. Distinct real roots give y = C1 e^{r1 x} + C2 e^{r2 x}; repeated root gives y = (C1 x + C2) e^{r0 x}; complex roots give y = e^{alpha x}(C1 cos(beta x) + C2 sin(beta x)).",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="characteristic_equation",
            title_km="សរសេរសមីការសម្គាល់",
            title_en="Write Characteristic Equation",
            rationale_template_km="សរសេរសមីការសម្គាល់ ar^2 + br + c = 0 នៃសមីការឌីផេរ៉ង់ស្យែល។",
            rationale_template_en="Form the characteristic equation ar^2 + br + c = 0 from the ODE coefficients.",
            rule_reference="ay'' + by' + cy = 0 \\iff ar^2 + br + c = 0",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="solve_roots",
            title_km="គណនាឌីស្គ្រីមីណង់ និងរកឫសនៃសមីការសម្គាល់",
            title_en="Compute Discriminant and Solve for Roots",
            rationale_template_km="គណនា Delta = b^2 - 4ac និងទាញរកឫស r នៃសមីការសម្គាល់។",
            rationale_template_en="Calculate Delta = b^2 - 4ac and determine the roots r of the characteristic equation.",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="state_general_solution",
            title_km="សរសេរចម្លើយទូទៅ",
            title_en="State General Solution",
            rationale_template_km="សរសេររូបមន្តចម្លើយទូទៅស្របតាមសញ្ញានៃ Delta។",
            rationale_template_en="State the general solution formula corresponding to the sign of Delta.",
        ),
        ExplanationStepTemplate(
            order=4,
            action_type="apply_initial_conditions",
            title_km="ជំនួសលក្ខខណ្ឌដើម (បើមាន)",
            title_en="Apply Initial Conditions (if given)",
            rationale_template_km="ជំនួស y(x0) = y0 និង y'(x0) = y'0 ដើម្បីទាញរកតម្លៃថេរ C1 និង C2។",
            rationale_template_en="Substitute initial conditions to determine arbitrary constants.",
        ),
        ExplanationStepTemplate(
            order=5,
            action_type="conclude_solution",
            title_km="សន្និដ្ឋានចម្លើយចុងក្រោយ",
            title_en="State Final Solution",
            rationale_template_km="សរសេរចម្លើយសម្រួលចុងក្រោយនៃសមីការឌីផេរ៉ង់ស្យែល។",
            rationale_template_en="State the final simplified solution.",
        ),
    ],
)

method_second_order_homogeneous = Method(
    id="method_ode_second_order_homogeneous",
    rule_id="rule_ode_second_order_homogeneous",
    name_km="វិធីដោះស្រាយសមីការលីនេអ៊ែរលំដាប់ទីពីរ ay'' + by' + cy = 0",
    name_en="Second-Order Linear Homogeneous ODE Method",
    description_km="ដោះស្រាយតាមសមីការសម្គាល់ ar^2 + br + c = 0 និងឌីស្គ្រីមីណង់ Delta។",
    description_en="Solve via characteristic equation ar^2 + br + c = 0 and discriminant Delta.",
    applicability="Second-order linear homogeneous equations ay'' + by' + cy = 0 with constant coefficients.",
    template=template_ode_second_order_homogeneous,
    examples=[
        CurriculumExample(
            id="ex_ode_sec_1",
            method_id="method_ode_second_order_homogeneous",
            problem_raw="y'' + 4y' + 4y = 0",
            problem_latex="y'' + 4y' + 4y = 0",
            solution_latex=r"y = (C_1 x + C_2) e^{-2x} \quad (C_1, C_2 \in \mathbb{R})",
            explanation_summary_km="សមីការសម្គាល់ r^2 + 4r + 4 = 0 មានឫសឌុប r0 = -2 នាំឲ្យ y = (C1 x + C2) e^{-2x}។",
        ),
    ],
)

rule_second_order_homogeneous = RuleFormula(
    id="rule_ode_second_order_homogeneous",
    concept_id="concept_second_order_ode",
    name_km="រូបមន្តសមីការឌីផេរ៉ង់ស្យែលលំដាប់ទីពីរ ay'' + by' + cy = 0",
    name_en="Second-Order Linear Homogeneous Formula",
    formula_latex=r"ay'' + by' + cy = 0 \iff ar^2 + br + c = 0",
    methods=[method_second_order_homogeneous],
)

# 5. Form Differential Equation from Solution Method
template_ode_form_from_solution = ExplanationTemplate(
    id="tmpl_ode_form_from_solution",
    method_id="method_ode_form_from_solution",
    name_km="រកសមីការឌីផេរ៉ង់ស្យែលលំដាប់ទីពីរដែលមានអនុគមន៍ f ជាចម្លើយ",
    name_en="Find Second-Order ODE Having Function f as Solution",
    verification_strategy="substitution",
    pedagogical_notes_km="គណនាដេរីវេទីមួយ f'(x) និងដេរីវេទីពីរ f''(x)។ ដោយ f ជាចម្លើយនៃសមីការ y'' + ay' + by = 0 នោះ f''(x) + af'(x) + bf(x) = 0។ ទាញរកតម្លៃមេគុណ a និង b រួចសរសេរសមីការឌីផេរ៉ង់ស្យែល។",
    pedagogical_notes_en="Compute f'(x) and f''(x). Since f satisfies y'' + ay' + by = 0, equate f''(x) + a*f'(x) + b*f(x) = 0 to solve for coefficients a and b, then state the differential equation.",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="compute_derivatives",
            title_km="គណនាដេរីវេទីមួយ និងទីពីរ",
            title_en="Compute First and Second Derivatives",
            rationale_template_km="គណនា f'(x) និង f''(x) តាមវិធានដេរីវេ។",
            rationale_template_en="Differentiate f(x) twice to find f'(x) and f''(x).",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="substitute_into_general_form",
            title_km="ជំនួសក្នុងទម្រង់សមីការឌីផេរ៉ង់ស្យែល",
            title_en="Substitute into General ODE Form",
            rationale_template_km="សមីការឌីផេរ៉ង់ស្យែលលីនេអ៊ែរលំដាប់ទីពីរអូម៉ូសែនមានទម្រង់ y'' + ay' + by = 0 នាំឲ្យ f''(x) + af'(x) + bf(x) = 0។",
            rationale_template_en="Substitute f(x), f'(x), and f''(x) into y'' + ay' + by = 0.",
            rule_reference="y'' + ay' + by = 0 \\implies f''(x) + af'(x) + bf(x) = 0",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="solve_coefficients",
            title_km="កំណត់តម្លៃមេគុណ a និង b",
            title_en="Solve for Coefficients a and b",
            rationale_template_km="ដោះស្រាយសមីការ ឬប្រព័ន្ធសមីការដើម្បីទាញរកតម្លៃ a និង b។",
            rationale_template_en="Equate coefficients or solve system of equations to determine a and b.",
        ),
        ExplanationStepTemplate(
            order=4,
            action_type="conclude_equation",
            title_km="សន្និដ្ឋានសមីការឌីផេរ៉ង់ស្យែល",
            title_en="Conclude Differential Equation",
            rationale_template_km="ជំនួសតម្លៃ a និង b ចូលក្នុងទម្រង់ y'' + ay' + by = 0 ដើម្បីទទួលបានសមីការចុងក្រោយ។",
            rationale_template_en="State the resulting second-order differential equation.",
        ),
    ],
)

method_form_from_solution = Method(
    id="method_ode_form_from_solution",
    rule_id="rule_ode_form_from_solution",
    name_km="វិធីរកសមីការឌីផេរ៉ង់ស្យែលពីអនុគមន៍ចម្លើយ",
    name_en="Form ODE from Given Solution Method",
    description_km="គណនា f', f'' រួចកំណត់មេគុណ a, b នៃ y'' + ay' + by = 0។",
    description_en="Compute f', f'' and solve for coefficients a, b in y'' + ay' + by = 0.",
    applicability="Problems asking to find the differential equation that has a given function f as a solution.",
    template=template_ode_form_from_solution,
    examples=[
        CurriculumExample(
            id="ex_ode_form_1",
            method_id="method_ode_form_from_solution",
            problem_raw=r"f(x) = (x + 1)e^{-2x}",
            problem_latex=r"f(x) = (x + 1)e^{-2x}",
            solution_latex=r"y'' + 4y' + 4y = 0",
            explanation_summary_km=r"f'(x) = (-2x - 1)e^{-2x}, f''(x) = 4x e^{-2x} នាំឲ្យ a = 4, b = 4 ដូចនេះ y'' + 4y' + 4y = 0។",
        ),
    ],
)

rule_form_from_solution = RuleFormula(
    id="rule_ode_form_from_solution",
    concept_id="concept_second_order_ode",
    name_km="វិធានរកសមីការឌីផេរ៉ង់ស្យែលពីចម្លើយ",
    name_en="Form ODE from Solution Rule",
    formula_latex=r"y'' + ay' + by = 0 \iff f''(x) + af'(x) + bf(x) = 0",
    methods=[method_form_from_solution],
)

# Concepts
concept_first_order_ode = Concept(
    id="concept_first_order_ode",
    lesson_id="lesson_differentials_first_form",
    order=1,
    title_km="សមីការឌីផេរ៉ង់ស្យែលលំដាប់ទី១",
    title_en="First-Order Differential Equations",
    definition_km="សមីការដែលមានទំនាក់ទំនងរវាងអថេរឯករាជ្យ x អនុគមន៍ y និងដេរីវេទី១ y'។",
    definition_en="Equations relating an independent variable x, function y, and first derivative y'.",
    rules=[rule_linear_homogeneous, rule_direct_integration],
)

concept_ode_verification = Concept(
    id="concept_ode_verification",
    lesson_id="lesson_differentials_first_form",
    order=2,
    title_km="ការផ្ទៀងផ្ទាត់ចម្លើយសមីការឌីផេរ៉ង់ស្យែល",
    title_en="Verification of Differential Equation Solutions",
    definition_km="បង្ហាញថាអនុគមន៍ដែលបានកំណត់ផ្ទៀងផ្ទាត់សមីការឌីផេរ៉ង់ស្យែល។",
    definition_en="Demonstrating that a given function satisfies a differential equation.",
    rules=[rule_verification],
)

concept_second_order_ode = Concept(
    id="concept_second_order_ode",
    lesson_id="lesson_differentials_second_form",
    order=1,
    title_km="សមីការឌីផេរ៉ង់ស្យែលលំដាប់ទី២",
    title_en="Second-Order Differential Equations",
    definition_km="សមីការដែលមានទំនាក់ទំនងរវាងអថេរឯករាជ្យ x អនុគមន៍ y ដេរីវេទី១ y' និងដេរីវេទី២ y''។",
    definition_en="Equations relating independent variable x, function y, first derivative y', and second derivative y''.",
    rules=[rule_second_order_homogeneous, rule_form_from_solution],
)

# Lessons
lesson_first_order_ode = Lesson(
    id="lesson_differentials_first_form",
    chapter_id="chapter_differential_equations",
    order=1,
    title_km="សមីការឌីផេរ៉ង់ស្យែលលំដាប់ទី១ (ទម្រង់ទី១)",
    title_en="First-Order Differential Equations (First Form)",
    description_km="មេរៀនសមីការឌីផេរ៉ង់ស្យែលលំដាប់ទី១ សម្រាប់ថ្នាក់ទី១២ បាក់ឌុប រួមមានសមីការ y' + ay = 0 សមីការ y' = f(x) ចំណោទកូស៊ី និងការផ្ទៀងផ្ទាត់ចម្លើយ។",
    description_en="Grade 12 BacII lesson on first-order differential equations: linear homogeneous y' + ay = 0, direct integration y' = f(x), Cauchy initial value problems, and solution verification.",
    concepts=[concept_first_order_ode, concept_ode_verification],
)

lesson_second_order_ode = Lesson(
    id="lesson_differentials_second_form",
    chapter_id="chapter_differential_equations",
    order=2,
    title_km="សមីការឌីផេរ៉ង់ស្យែលលំដាប់ទី២ (ទម្រង់ទី២)",
    title_en="Second-Order Differential Equations (Second Form)",
    description_km="មេរៀនសមីការឌីផេរ៉ង់ស្យែលលំដាប់ទី២ សម្រាប់ថ្នាក់ទី១២ បាក់ឌុប រួមមានសមីការ ay'' + by' + cy = 0 សមីការសម្គាល់ ចំណោទកូស៊ី និងការបង្កើតសមីការពីអនុគមន៍ចម្លើយ។",
    description_en="Grade 12 BacII lesson on second-order differential equations: linear homogeneous ay'' + by' + cy = 0, characteristic equations, Cauchy problems, and forming ODEs from given solutions.",
    concepts=[concept_second_order_ode],
)

# Chapter
chapter_differential_equations = Chapter(
    id="chapter_differential_equations",
    domain=SubjectDomain.CALCULUS,
    order=4,
    title_km="ជំពូក៖ សមីការឌីផេរ៉ង់ស្យែល",
    title_en="Chapter: Differential Equations",
    description_km="ជំពូកសមីការឌីផេរ៉ង់ស្យែល កម្មវិធីសិក្សាគណិតវិទ្យាថ្នាក់ទី១២ នៃក្រសួងអប់រំ យុវជន និងកីឡា (BacII)។",
    description_en="Chapter on Differential Equations for Grade 12 National Curriculum (MoEYS BacII).",
    grade_level=12,
    lessons=[lesson_first_order_ode, lesson_second_order_ode],
)


def detect_differential_method(parsed: Any) -> Method:
    """Detect which differential equation method applies based on parsed expression and metadata."""
    meta = getattr(parsed, "metadata", {}) or {}
    if meta.get("is_form_ode"):
        return method_form_from_solution
    if meta.get("is_verification"):
        return method_verification

    expr = getattr(parsed, "sympy_expr", None)
    if expr is not None and hasattr(expr, "lhs") and hasattr(expr, "rhs"):
        lhs = expr.lhs
        rhs = expr.rhs
        diff = lhs - rhs
        # Check if second order (contains Derivative of order 2)
        var = meta.get("independent_var") or Symbol("x")
        y_fn = Function("y")(var)
        d2y = Derivative(y_fn, (var, 2))
        if diff.has(d2y) or "Derivative(y" in str(diff) and ", 2)" in str(diff):
            return method_second_order_homogeneous

        # Check if linear homogeneous (y' + ay = 0)
        dy = Derivative(y_fn, var)
        if diff.has(dy) and diff.has(y_fn):
            return method_linear_homogeneous

    if meta.get("order") == 2:
        return method_second_order_homogeneous

    return method_direct_integration
