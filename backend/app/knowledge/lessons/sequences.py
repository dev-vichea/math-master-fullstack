"""
Real Sequences Lessons and Chapter (Grade 12 BacII Focus).

Covers standard Cambodian Grade 12 BacII curriculum for Real Sequences (ស្វ៊ីតចំនួនពិត):
1. Convergence and Divergence of Sequences (ភាពរួម ឬរីកនៃស្វ៊ីត):
   - lim_{n -> +oo} U_n = L in R => (U_n) ជាស្វ៊ីតរួមខិតទៅរក L (Convergent)
   - lim_{n -> +oo} U_n = +-oo or does not exist => (U_n) ជាស្វ៊ីតរីក (Divergent)
2. Squeeze Theorem for Sequences (ទ្រឹស្តីបទញှៀប):
   - -1 <= sin(f(n)) <= 1, -1 <= cos(f(n)) <= 1, -1 <= (-1)^n <= 1
3. Limit Evaluation Techniques for Sequences:
   - Factoring highest power n^k in rational sequences
   - Conjugate multiplication for radical differences
   - Factorial simplification: (n+1)! = (n+1) n!
   - D'Alembert ratio limit: lim_{n -> +oo} U_{n+1} / U_n
4. Recurrence Sequences (ស្វ៊ីតកំណត់ដោយទំនាក់ទំនងដំណាល):
   - First-order linear recurrence: a_{n+1} = p * a_n + q
   - Fixed point equation: L = p * L + q => L = q / (1 - p)
   - Auxiliary geometric sequence: v_n = a_n - L with ratio p
   - Explicit general term: a_n = L + (a_1 - L) * p^{n-1}
   - Limit as n -> +oo and convergence analysis.
"""

from __future__ import annotations

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
# 1. Methods: Convergence and Divergence
# ---------------------------------------------------------------------------

method_sequence_convergence = Method(
    id="method_sequence_convergence",
    rule_id="rule_sequence_convergence",
    name_km="សិក្សាភាពរួម ឬរីកនៃស្វ៊ីត (Convergence & Divergence)",
    name_en="Sequence Convergence and Divergence",
    description_km="គណនាលីមីត \\lim_{n \\to +\\infty} U_n = L។ ប្រសិនបើ L ជាចំនួនពិតកំណត់ នោះ (U_n) ជាស្វ៊ីតរួម។ ប្រសិនបើ L = \\pm\\infty ឬគ្មានលីមីត នោះ (U_n) ជាស្វ៊ីតរីក។",
    description_en="Evaluate lim_{n -> +oo} U_n = L. If L is a finite real number, (U_n) converges to L. If L = +-oo or does not exist, (U_n) diverges.",
    applicability="General term U_n given, determining whether sequence converges or diverges.",
    examples=[
        CurriculumExample(
            id="ex_seq_conv_poly",
            method_id="method_sequence_convergence",
            problem_raw=r"U_n = 3n^2 + 5n + 1",
            problem_latex=r"U_n = 3n^2 + 5n + 1",
            solution_latex=r"\lim_{n \to +\infty} U_n = +\infty \implies (U_n) \text{ ជាស្វ៊ីតរីក}",
            explanation_summary_km=r"គណនា \lim_{n \to +\infty} (3n^2 + 5n + 1) = +\infty ។ ដូចនេះ (U_n) ជាស្វ៊ីតរីកខិតទៅរក +\infty ។",
        ),
        CurriculumExample(
            id="ex_seq_conv_rational",
            method_id="method_sequence_convergence",
            problem_raw=r"U_n = \frac{n^2 + n}{2n^2 + 5}",
            problem_latex=r"U_n = \frac{n^2 + n}{2n^2 + 5}",
            solution_latex=r"\lim_{n \to +\infty} U_n = \frac{1}{2} \implies (U_n) \text{ ជាស្វ៊ីតរួម}",
            explanation_summary_km=r"គណនា \lim_{n \to +\infty} \frac{n^2+n}{2n^2+5} = \frac{1}{2} ។ ដូចនេះ (U_n) ជាស្វ៊ីតរួមខិតទៅរក \frac{1}{2} ។",
        ),
    ],
)

method_sequence_squeeze = Method(
    id="method_sequence_squeeze",
    rule_id="rule_sequence_squeeze",
    name_km="ទ្រឹស្តីបទញှៀបសម្រាប់ស្វ៊ីត (Squeeze Theorem)",
    name_en="Squeeze Theorem for Sequences",
    description_km="ប្រើប្រាស់លក្ខណៈខ្នាតជាប់ព្រំដែនដូចជា -1 \\le \\sin \\theta \\le 1, -1 \\le \\cos \\theta \\le 1, -1 \\le (-1)^n \\le 1 ដើម្បីញှៀបស្វ៊ីតរវាងស្វ៊ីតពីរផ្សេងទៀត។",
    description_en="Use bounded bounds such as -1 <= sin <= 1, -1 <= cos <= 1, or -1 <= (-1)^n <= 1 to sandwich sequence between two convergent sequences.",
    applicability="Sequences with trigonometric functions sin(kn), cos(kn), or oscillating term (-1)^n.",
    examples=[
        CurriculumExample(
            id="ex_seq_squeeze_sin",
            method_id="method_sequence_squeeze",
            problem_raw=r"U_n = \frac{\sin 2n}{5^n}",
            problem_latex=r"U_n = \frac{\sin 2n}{5^n}",
            solution_latex=r"\lim_{n \to +\infty} U_n = 0",
            explanation_summary_km=r"គេមាន -1 \le \sin 2n \le 1 នាំឱ្យ -\frac{1}{5^n} \le U_n \le \frac{1}{5^n} ។ ដោយ \lim_{n \to +\infty} \frac{1}{5^n} = 0 នោះ \lim_{n \to +\infty} U_n = 0 ។",
        ),
    ],
)

# ---------------------------------------------------------------------------
# 2. Methods: Sequence Limit Evaluation Techniques
# ---------------------------------------------------------------------------

method_sequence_limit_rational = Method(
    id="method_sequence_limit_rational",
    rule_id="rule_sequence_limit_rational",
    name_km="គណនាលីមីតស្វ៊ីតសនិទាន (Rational Sequence Limit)",
    name_en="Rational Sequence Limit Evaluation",
    description_km="ដាក់ស្វ័យគុណធំបំផុត n^k នៃភាគយក និងភាគបែងជាកត្តារួចសម្រួល ឬប្រៀបធៀបដឺក្រេខ្ពស់បំផុត។",
    description_en="Factor highest power n^k in numerator and denominator and simplify.",
    applicability="Rational sequences P(n)/Q(n) as n -> +oo.",
    examples=[
        CurriculumExample(
            id="ex_seq_limit_rat",
            method_id="method_sequence_limit_rational",
            problem_raw=r"\lim_{n \to +\infty} \frac{n^2 + 3n - 1}{8n^2 - n + 1}",
            problem_latex=r"\lim_{n \to +\infty} \frac{n^2 + 3n - 1}{8n^2 - n + 1}",
            solution_latex=r"\frac{1}{8}",
            explanation_summary_km=r"សម្រួលស្វ័យគុណធំបំផុត \lim_{n \to +\infty} \frac{n^2}{8n^2} = \frac{1}{8} ។",
        ),
    ],
)

method_sequence_conjugate = Method(
    id="method_sequence_conjugate",
    rule_id="rule_sequence_conjugate",
    name_km="គុណកន្សោមឆ្លាស់បំបាត់រ៉ាឌីកាល់ (Conjugate Multiplication)",
    name_en="Radical Sequence Conjugate Multiplication",
    description_km="គុណនិងចែកនឹងកន្សោមឆ្លាស់ដើម្បីបំបាត់រ៉ាឌីកាល់នៃរាងមិនកំណត់ \\infty - \\infty។",
    description_en="Multiply and divide by conjugate to resolve indeterminate radical form oo - oo.",
    applicability="Radical sequence differences like sqrt(n+1) - sqrt(n).",
    examples=[
        CurriculumExample(
            id="ex_seq_conj_sqrt",
            method_id="method_sequence_conjugate",
            problem_raw=r"\lim_{n \to +\infty} (\sqrt{n+1} - \sqrt{n})",
            problem_latex=r"\lim_{n \to +\infty} (\sqrt{n+1} - \sqrt{n})",
            solution_latex=r"0",
            explanation_summary_km=r"គុណកន្សោមឆ្លាស់: \lim_{n \to +\infty} \frac{n+1 - n}{\sqrt{n+1} + \sqrt{n}} = \lim \frac{1}{\sqrt{n+1}+\sqrt{n}} = 0 ។",
        ),
    ],
)

method_sequence_factorial = Method(
    id="method_sequence_factorial",
    rule_id="rule_sequence_factorial",
    name_km="សម្រួលកន្សោមហ្វាក់តូរីយ៉ែល (Factorial Simplification)",
    name_en="Factorial Sequence Simplification",
    description_km="ប្រើប្រាស់រូបមន្ត (n+1)! = (n+1)n! ដើម្បីដាក់ n! ជាកត្តារួចសម្រួល។",
    description_en="Apply (n+1)! = (n+1)n! to factor out and cancel common factorials.",
    applicability="Sequence expressions involving factorials n!, (n+1)!.",
    examples=[
        CurriculumExample(
            id="ex_seq_factorial_simp",
            method_id="method_sequence_factorial",
            problem_raw=r"\lim_{n \to +\infty} \left(\frac{n!}{(n+1)! - n!} - \frac{2}{n} + 3\right)",
            problem_latex=r"\lim_{n \to +\infty} \left(\frac{n!}{(n+1)! - n!} - \frac{2}{n} + 3\right)",
            solution_latex=r"3",
            explanation_summary_km=r"(n+1)! - n! = n!(n+1-1) = n \cdot n! \implies \frac{n!}{n \cdot n!} = \frac{1}{n} \implies \lim (\frac{1}{n} - \frac{2}{n} + 3) = 3 ។",
        ),
    ],
)

method_sequence_ratio_dalembert = Method(
    id="method_sequence_ratio_dalembert",
    rule_id="rule_sequence_ratio",
    name_km="គណនាផលធៀបដាឡំប៊ែរ (D'Alembert Ratio Limit)",
    name_en="D'Alembert Ratio Limit Evaluation",
    description_km="គណនាផលធៀប \\lim_{n \\to +\\infty} \\frac{U_{n+1}}{U_n} ដើម្បីសិក្សាល្បឿនលូតលាស់នៃស្វ៊ីត។",
    description_en="Compute ratio limit lim_{n -> +oo} U_{n+1} / U_n to study growth rate and convergence.",
    applicability="Sequences with powers and factorials like n^k / a^n or a^n / n!.",
    examples=[
        CurriculumExample(
            id="ex_seq_ratio_un",
            method_id="method_sequence_ratio_dalembert",
            problem_raw=r"U_n = \frac{n^3}{2^n}",
            problem_latex=r"\lim_{n \to +\infty} \frac{U_{n+1}}{U_n}",
            solution_latex=r"\frac{1}{2}",
            explanation_summary_km=r"\frac{U_{n+1}}{U_n} = \frac{(n+1)^3}{2^{n+1}} \cdot \frac{2^n}{n^3} = \frac{1}{2}\left(1 + \frac{1}{n}\right)^3 \to \frac{1}{2} ។",
        ),
    ],
)

# ---------------------------------------------------------------------------
# 3. Methods: Recurrence Relations
# ---------------------------------------------------------------------------

method_sequence_recurrence_linear = Method(
    id="method_sequence_recurrence_linear",
    rule_id="rule_sequence_recurrence_linear",
    name_km="ដោះស្រាយស្វ៊ីតដំណាលលីនេអ៊ែរ a_{n+1} = p a_n + q",
    name_en="First-Order Linear Recurrence Sequence",
    description_km="រកតម្លៃថេរ L = pL + q \iff L = \frac{q}{1-p} រួចបង្កើតស្វ៊ីតជំនួយ v_n = a_n - L ជាស្វ៊ីតធរណីមាត្រដើម្បីទាញរកតួទូទៅ a_n និងលីមីត។",
    description_en="Solve fixed point L = pL + q => L = q / (1 - p). Define auxiliary geometric sequence v_n = a_n - L to find general term a_n and limit.",
    applicability="First-order linear recurrence relations a_{n+1} = p * a_n + q with initial term a_1.",
    examples=[
        CurriculumExample(
            id="ex_seq_rec_half",
            method_id="method_sequence_recurrence_linear",
            problem_raw=r"a_1 = 2, a_{n+1} = \frac{1}{2}a_n + 3",
            problem_latex=r"a_1 = 2, a_{n+1} = \frac{1}{2}a_n + 3",
            solution_latex=r"a_n = 6 - 4\left(\frac{1}{2}\right)^{n-1}, \lim_{n \to +\infty} a_n = 6",
            explanation_summary_km=r"L = \frac{1}{2}L + 3 \implies L = 6; v_n = a_n - 6 \implies v_{n+1} = \frac{1}{2}v_n; v_1 = -4 \implies a_n = 6 - 4(\frac{1}{2})^{n-1} \implies \lim a_n = 6 ។",
        ),
        CurriculumExample(
            id="ex_seq_rec_divergent",
            method_id="method_sequence_recurrence_linear",
            problem_raw=r"a_1 = 3, a_{n+1} = 2a_n - 5",
            problem_latex=r"a_1 = 3, a_{n+1} = 2a_n - 5",
            solution_latex=r"a_n = 5 - 2^n, \lim_{n \to +\infty} a_n = -\infty",
            explanation_summary_km=r"L = 2L - 5 \implies L = 5; v_n = a_n - 5 \implies v_1 = -2; a_n = 5 - 2^n \implies \lim a_n = -\infty (ស្វ៊ីតរីក) ។",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Rules and Concepts
# ---------------------------------------------------------------------------

rule_sequence_convergence = RuleFormula(
    id="rule_sequence_convergence",
    concept_id="concept_sequence_convergence",
    name_km="និយមន័យភាពរួម និងភាពរីកនៃស្វ៊ីត",
    name_en="Sequence Convergence and Divergence Definition",
    formula_latex=r"\lim_{n \to +\infty} U_n = L \in \mathbb{R} \implies (U_n) \text{ រួម}; \quad \lim_{n \to +\infty} U_n = \pm\infty \implies (U_n) \text{ រីក}",
    description_km="ស្វ៊ីត (U_n) ហៅថាជាស្វ៊ីតរួម កាលណាវាមានលីមីតជាចំនួនពិត L កាលណា n ខិតជិត +oo។ បើគ្មានលីមីត ឬលីមីតស្មើ +-oo ហៅថាជាស្វ៊ីតរីក។",
    description_en="A sequence (U_n) is convergent if lim_{n -> +oo} U_n = L in R. If limit is infinite or does not exist, it is divergent.",
    methods=[method_sequence_convergence],
)

rule_sequence_squeeze = RuleFormula(
    id="rule_sequence_squeeze",
    concept_id="concept_sequence_convergence",
    name_km="ទ្រឹស្តីបទញှៀបនៃស្វ៊ីត",
    name_en="Squeeze Theorem for Sequences",
    formula_latex=r"V_n \le U_n \le W_n \quad \text{and} \quad \lim_{n \to +\infty} V_n = \lim_{n \to +\infty} W_n = L \implies \lim_{n \to +\infty} U_n = L",
    description_km="ប្រសិនបើ V_n \le U_n \le W_n ហើយ V_n, W_n មានលីមីតស្មើគ្នា L នោះ U_n ក៏មានលីមីតស្មើ L ដែរ។",
    description_en="If V_n <= U_n <= W_n and both V_n, W_n approach L, then U_n also approaches L.",
    methods=[method_sequence_squeeze],
)

concept_sequence_convergence = Concept(
    id="concept_sequence_convergence",
    lesson_id="lesson_sequence_limits",
    order=1,
    title_km="ភាពរួម និងភាពរីកនៃស្វ៊ីត (Convergence & Divergence)",
    title_en="Sequence Convergence and Divergence",
    definition_km="ការសិក្សាអំពីអាកប្បកិរិយារបស់តួស្វ៊ីតកាលណា n កើនឡើងដល់អនន្ត +oo។",
    definition_en="Study of the asymptotic behavior of sequence terms as n approaches infinity.",
    rules=[rule_sequence_convergence, rule_sequence_squeeze],
)

rule_sequence_limit_rational = RuleFormula(
    id="rule_sequence_limit_rational",
    concept_id="concept_sequence_limits_calc",
    name_km="លីមីតស្វ៊ីតសនិទាន",
    name_en="Rational Sequence Limits",
    formula_latex=r"\lim_{n \to +\infty} \frac{a_p n^p + \dots}{b_q n^q + \dots} = \lim_{n \to +\infty} \frac{a_p n^p}{b_q n^q}",
    description_km="លីមីតស្វ៊ីតសនិទានកាលណា n -> +oo ស្មើនឹងលីមីតនៃផលធៀបតួដែលមានដឺក្រេខ្ពស់បំផុត។",
    description_en="At infinity, the limit of a rational sequence equals the limit of the ratio of leading terms.",
    methods=[method_sequence_limit_rational],
)

rule_sequence_conjugate = RuleFormula(
    id="rule_sequence_conjugate",
    concept_id="concept_sequence_limits_calc",
    name_km="កន្សោមឆ្លាស់នៃស្វ៊ីតរ៉ាឌីកាល់",
    name_en="Radical Sequence Conjugate",
    formula_latex=r"\sqrt{A} - \sqrt{B} = \frac{A - B}{\sqrt{A} + \sqrt{B}}",
    description_km="គុណកន្សោមឆ្លាស់ដើម្បីបំបាត់រាងមិនកំណត់ oo - oo។",
    description_en="Conjugate multiplication to eliminate radical indeterminate differences.",
    methods=[method_sequence_conjugate],
)

rule_sequence_factorial = RuleFormula(
    id="rule_sequence_factorial",
    concept_id="concept_sequence_limits_calc",
    name_km="រូបមន្តហ្វាក់តូរីយ៉ែល",
    name_en="Factorial Identity",
    formula_latex=r"(n+1)! = (n+1)n!",
    description_km="បំបែក (n+1)! = (n+1)n! ដើម្បីសម្រួលកត្តាហ្វាក់តូរីយ៉ែលរួម។",
    description_en="Expand (n+1)! = (n+1)n! to factor out and simplify factorial expressions.",
    methods=[method_sequence_factorial],
)

rule_sequence_ratio = RuleFormula(
    id="rule_sequence_ratio",
    concept_id="concept_sequence_limits_calc",
    name_km="ផលធៀបដាឡំប៊ែរ",
    name_en="D'Alembert Ratio",
    formula_latex=r"\lim_{n \to +\infty} \frac{U_{n+1}}{U_n}",
    description_km="ផលធៀបរវាងពីរតួតគ្នានៃស្វ៊ីតកាលណា n -> +oo។",
    description_en="Ratio between consecutive sequence terms as n approaches infinity.",
    methods=[method_sequence_ratio_dalembert],
)

concept_sequence_limits_calc = Concept(
    id="concept_sequence_limits_calc",
    lesson_id="lesson_sequence_limits",
    order=2,
    title_km="វិធីសាស្ត្រគណនាលីមីតស្វ៊ីត (Sequence Limit Methods)",
    title_en="Sequence Limit Calculation Methods",
    definition_km="បណ្តាវិធីសាស្ត្រគណនាលីមីតនៃស្វ៊ីតកាលណា n -> +oo (ដឺក្រេខ្ពស់ កន្សោមឆ្លាស់ ហ្វាក់តូរីយ៉ែល ផលធៀប)។",
    definition_en="Methods for evaluating sequence limits at infinity including leading term factoring, conjugates, factorials, and ratios.",
    rules=[rule_sequence_limit_rational, rule_sequence_conjugate, rule_sequence_factorial, rule_sequence_ratio],
)

rule_sequence_recurrence_linear = RuleFormula(
    id="rule_sequence_recurrence_linear",
    concept_id="concept_sequence_recurrence_linear",
    name_km="រូបមន្តស្វ៊ីតដំណាលលីនេអ៊ែរ a_{n+1} = p a_n + q",
    name_en="First-Order Linear Recurrence Formula",
    formula_latex=r"L = \frac{q}{1-p}, \quad v_n = a_n - L \implies a_n = L + (a_1 - L)p^{n-1}",
    description_km="ស្វ៊ីតជំនួយ v_n = a_n - L ជាស្វ៊ីតធរណីមាត្រមានរ៉ាស្យុង p និងតួទីមួយ v_1 = a_1 - L។",
    description_en="Auxiliary sequence v_n = a_n - L is geometric with common ratio p and initial term v_1 = a_1 - L.",
    methods=[method_sequence_recurrence_linear],
)

concept_sequence_recurrence_linear = Concept(
    id="concept_sequence_recurrence_linear",
    lesson_id="lesson_sequence_recurrence",
    order=1,
    title_km="ស្វ៊ីតដំណាលលីនេអ៊ែរ (Linear Recurrence Sequences)",
    title_en="Linear Recurrence Sequences",
    definition_km="ស្វ៊ីតដែលកំណត់ដោយទំនាក់ទំនង a_{n+1} = p a_n + q និងស្គាល់តួទីមួយ a_1។",
    definition_en="Sequences defined by recurrence relation a_{n+1} = p * a_n + q with given initial term a_1.",
    rules=[rule_sequence_recurrence_linear],
)

# ---------------------------------------------------------------------------
# Lessons and Chapter
# ---------------------------------------------------------------------------

lesson_sequence_limits = Lesson(
    id="lesson_sequence_limits",
    chapter_id="chapter_sequences",
    order=1,
    title_km="លីមីតនៃស្វ៊ីតចំនួនពិត និងភាពរួម ឬរីក (Sequence Limits & Convergence)",
    title_en="Limits of Real Sequences and Convergence",
    description_km="ការគណនាលីមីតនៃស្វ៊ីតចំនួនពិត និងការសិក្សាភាពរួម ឬរីកនៃស្វ៊ីតស្របតាមកម្មវិធីថ្នាក់ទី១២ បាក់ឌុប។",
    description_en="Evaluating real sequence limits and analyzing convergence or divergence for Grade 12 BacII.",
    concepts=[concept_sequence_convergence, concept_sequence_limits_calc],
)

lesson_sequence_recurrence = Lesson(
    id="lesson_sequence_recurrence",
    chapter_id="chapter_sequences",
    order=2,
    title_km="ស្វ៊ីតកំណត់ដោយទំនាក់ទំនងដំណាល (Recurrence Sequences)",
    title_en="Sequences Defined by Recurrence Relations",
    description_km="ការរកតួទូទៅ និងលីមីតនៃស្វ៊ីតដំណាល a_{n+1} = p a_n + q ដោយប្រើស្វ៊ីតជំនួយធរណីមាត្រ។",
    description_en="Finding explicit general terms and limits of recurrence sequences a_{n+1} = p * a_n + q using auxiliary geometric sequences.",
    concepts=[concept_sequence_recurrence_linear],
)

chapter_sequences = Chapter(
    id="chapter_sequences",
    domain=SubjectDomain.ALGEBRA,
    order=5,
    title_km="ជំពូក៖ ស្វ៊ីតចំនួនពិត (Real Sequences)",
    title_en="Chapter: Real Sequences",
    grade_level=12,
    description_km="ស្វ៊ីតចំនួនពិត លីមីតនៃស្វ៊ីត ភាពរួមឬរីក និងស្វ៊ីតដំណាល។",
    description_en="Real sequences, sequence limits, convergence and divergence, and recurrence relations.",
    lessons=[lesson_sequence_limits, lesson_sequence_recurrence],
)
