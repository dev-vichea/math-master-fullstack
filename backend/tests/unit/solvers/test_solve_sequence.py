"""
Comprehensive unit and integration tests for Real Sequences (ស្វ៊ីតចំនួនពិត) - Cambodian Grade 12 BacII.

Covers all exercises from training/test_exercises/sequences/:
- Exercise 1: Sequence Convergence and Divergence (ក, ខ, គ, ឃ, ង, ច)
- Exercise 2: Sequence Limits at Infinity (ក, ខ, គ, ឃ, ង, ច)
- Exercise 3: Radicals and Factorials (ក, ខ, គ, ឃ)
- Exercise 4: D'Alembert Ratio and Dominance (ក, ខ)
- Exercise 5: First-Order Linear Recurrence Relations (ក, ខ, គ)
- Curriculum Knowledge Base and Metadata verification
- End-to-end Khmer question processing via math_service
"""

import pytest

from app.parser.math_parser.expression_parser import parse_math_text
from app.classifier.problem_classifier.classifier import classify_problem
from app.services.math_service import process_question
from app.solvers import solve


class TestExercise1SequenceConvergence:
    """Exercise 1: Determine whether sequence (U_n) converges or diverges."""

    def test_ex1_ka_polynomial_divergent(self):
        """1.ក: U_n = 3n^2 + 5n + 1 -> +oo (ស្វ៊ីតរីក)"""
        expr_str = r"U_n = 3n^2 + 5n + 1"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence"

        result = solve(parsed, "sequence")
        assert result.answer in ("oo", "+oo", "+\\infty")
        assert result.metadata.get("convergence") == "divergent"
        assert len(result.steps) >= 3
        step_descriptions = [s.description_km for s in result.steps]
        assert any("ស្វ៊ីតរីក" in d for d in step_descriptions)

    def test_ex1_kha_rational_convergent(self):
        """1.ខ: U_n = (n^2 + n) / (2n^2 + 5) -> 1/2 (ស្វ៊ីតរួម)"""
        expr_str = r"U_n = \frac{n^2 + n}{2n^2 + 5}"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence"

        result = solve(parsed, "sequence")
        assert result.answer == "1/2"
        assert result.metadata.get("convergence") == "convergent"
        step_descriptions = [s.description_km for s in result.steps]
        assert any("ស្វ៊ីតរួម" in d for d in step_descriptions)
        assert any("1/2" in d or r"\frac{1}{2}" in d for d in step_descriptions)

    def test_ex1_ko_trig_exponential_squeeze(self):
        """1.គ: U_n = sin(2n) / 5^n -> 0 (ស្វ៊ីតរួម)"""
        expr_str = r"U_n = \frac{\sin 2n}{5^n}"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence"

        result = solve(parsed, "sequence")
        assert result.answer == "0"
        assert result.metadata.get("convergence") == "convergent"
        step_descriptions = [s.description_km for s in result.steps]
        assert any("ទ្រឹស្តីបទញှៀប" in s.title_km or "ទ្រឹស្តីបទញှៀប" in s.description_km for s in result.steps)
        assert any("ស្វ៊ីតរួម" in d for d in step_descriptions)

    def test_ex1_kho_two_rationals_divergent(self):
        """1.ឃ: U_n = 2n/(n+3) + 3n^3/(n^2+5) -> +oo (ស្វ៊ីតរីក)"""
        expr_str = r"U_n = \frac{2n}{n+3} + \frac{3n^3}{n^2+5}"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence"

        result = solve(parsed, "sequence")
        assert result.answer in ("oo", "+oo", "+\\infty")
        assert result.metadata.get("convergence") == "divergent"
        step_descriptions = [s.description_km for s in result.steps]
        assert any("ស្វ៊ីតរីក" in d for d in step_descriptions)

    def test_ex1_ngo_rational_trig_squeeze(self):
        """1.ង: U_n = n*sin(n) / (n^2 + 1) -> 0 (ស្វ៊ីតរួម)"""
        expr_str = r"U_n = \frac{n \sin n}{n^2 + 1}"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence"

        result = solve(parsed, "sequence")
        assert result.answer == "0"
        assert result.metadata.get("convergence") == "convergent"
        step_descriptions = [s.description_km for s in result.steps]
        assert any("ស្វ៊ីតរួម" in d for d in step_descriptions)

    def test_ex1_cha_fraction_sqrt_convergent(self):
        """1.ច: U_n = 2 - 3/n + 4/sqrt(n) -> 2 (ស្វ៊ីតរួម)"""
        expr_str = r"U_n = 2 - \frac{3}{n} + \frac{4}{\sqrt{n}}"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence"

        result = solve(parsed, "sequence")
        assert result.answer == "2"
        assert result.metadata.get("convergence") == "convergent"
        step_descriptions = [s.description_km for s in result.steps]
        assert any("ស្វ៊ីតរួម" in d for d in step_descriptions)
        assert any("2" in d for d in step_descriptions)


class TestExercise2SequenceLimits:
    """Exercise 2: Compute sequence limits at infinity."""

    def test_ex2_ka_rational_same_degree(self):
        """2.ក: lim_{n->+oo} (n^2 + 3n - 1) / (8n^2 - n + 1) = 1/8"""
        expr_str = r"\lim_{n \to +\infty} \frac{n^2 + 3n - 1}{8n^2 - n + 1}"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_limit"

        result = solve(parsed, "sequence_limit")
        assert result.answer == "1/8"
        assert result.is_verified is True
        assert len(result.steps) >= 2

    def test_ex2_kha_rational_higher_numerator(self):
        """2.ខ: lim_{n->+oo} (5n^3 + n^2 - n) / (n^2 + n - 1) = +oo"""
        expr_str = r"\lim_{n \to +\infty} \frac{5n^3 + n^2 - n}{n^2 + n - 1}"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_limit"

        result = solve(parsed, "sequence_limit")
        assert result.answer in ("oo", "+oo", "+\\infty")

    def test_ex2_ko_oscillating_negative_one(self):
        """2.គ: lim_{n->+oo} (5n^3 + (-1)^n) / (n + (-1)^n) = +oo"""
        expr_str = r"\lim_{n \to +\infty} \frac{5n^3 + (-1)^n}{n + (-1)^n}"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_limit"

        result = solve(parsed, "sequence_limit")
        assert result.answer in ("oo", "+oo", "+\\infty")

    def test_ex2_kho_trig_bounded_powers(self):
        """2.ឃ: lim_{n->+oo} (n^2 + sin n) / (5n^2 + cos pi n) = 1/5"""
        expr_str = r"\lim_{n \to +\infty} \frac{n^2 + \sin n}{5n^2 + \cos \pi n}"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_limit"

        result = solve(parsed, "sequence_limit")
        assert result.answer == "1/5"

    def test_ex2_ngo_n_squared_minus_cos(self):
        """2.ង: lim_{n->+oo} (n^2 - cos^2 pi n) = +oo"""
        expr_str = r"\lim_{n \to +\infty} (n^2 - \cos^2 \pi n)"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_limit"

        result = solve(parsed, "sequence_limit")
        assert result.answer in ("oo", "+oo", "+\\infty")

    def test_ex2_cha_negative_leading_oscillating(self):
        """2.ច: lim_{n->+oo} [-5n^3 + (-1)^n n^3] = -oo"""
        expr_str = r"\lim_{n \to +\infty} [-5n^3 + (-1)^n n^3]"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_limit"

        result = solve(parsed, "sequence_limit")
        assert result.answer in ("-oo", "-\\infty")


class TestExercise3RadicalFactorialLimits:
    """Exercise 3: Radicals and factorials."""

    def test_ex3_ka_sqrt_difference_conjugate(self):
        """3.ក: lim_{n->+oo} (sqrt(n+1) - sqrt(n)) = 0"""
        expr_str = r"\lim_{n \to +\infty} (\sqrt{n+1} - \sqrt{n})"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_limit"

        result = solve(parsed, "sequence_limit")
        assert result.answer == "0"
        assert result.metadata.get("method_id") == "method_sequence_conjugate"

    def test_ex3_kha_sqrt_product_conjugate(self):
        """3.ខ: lim_{n->+oo} sqrt(n)(sqrt(n-3) - sqrt(n)) = -3/2"""
        expr_str = r"\lim_{n \to +\infty} \sqrt{n}(\sqrt{n-3} - \sqrt{n})"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_limit"

        result = solve(parsed, "sequence_limit")
        assert result.answer == "-3/2"

    def test_ex3_ko_sqrt_conjugate_standard(self):
        """3.គ: lim_{n->+oo} (sqrt(n^2+1) - n) = 0"""
        expr_str = r"\lim_{n \to +\infty} (\sqrt{n^2+1} - n)"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_limit"

        result = solve(parsed, "sequence_limit")
        assert result.answer == "0"

    def test_ex3_kho_factorial_simplification(self):
        """3.ឃ: lim_{n->+oo} (n! / ((n+1)! - n!) - 2/n + 3) = 3"""
        expr_str = r"\lim_{n \to +\infty} (\frac{n!}{(n+1)! - n!} - \frac{2}{n} + 3)"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_limit"

        result = solve(parsed, "sequence_limit")
        assert result.answer == "3"
        assert result.metadata.get("method_id") == "method_sequence_factorial"
        step_descriptions = [s.description_km for s in result.steps]
        assert any("ហ្វាក់តូរីយ៉ែល" in d for d in step_descriptions)


class TestExercise4SequenceRatio:
    """Exercise 4: Ratio limits and dominance."""

    def test_ex4_ka_dalembert_ratio_powers(self):
        """4.ក1: U_n = n^3 / 2^n -> lim U_{n+1}/U_n = 1/2"""
        from sympy import Symbol, simplify, Limit, oo
        n = Symbol("n", positive=True)
        u_n = n**3 / 2**n
        u_np1 = (n + 1)**3 / 2**(n + 1)
        ratio = simplify(u_np1 / u_n)
        lim_val = Limit(ratio, n, oo).doit()
        assert str(lim_val) == "1/2"

    def test_ex4_ka_dalembert_ratio_factorial(self):
        """4.ក2: V_n = 2^n / n! -> lim V_{n+1}/V_n = 0"""
        from sympy import Symbol, factorial, simplify, Limit, oo
        n = Symbol("n", positive=True)
        v_n = 2**n / factorial(n)
        v_np1 = 2**(n + 1) / factorial(n + 1)
        ratio = simplify(v_np1 / v_n)
        lim_val = Limit(ratio, n, oo).doit()
        assert str(lim_val) == "0"

    def test_ex4_kha_factorial_dominance(self):
        """4.ខ: lim_{n->+oo} (2^n + n^3) / (n! + n^3) = 0"""
        expr_str = r"\lim_{n \to +\infty} \frac{2^n + n^3}{n! + n^3}"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_limit"

        result = solve(parsed, "sequence_limit")
        assert result.answer == "0"


class TestExercise5RecurrenceSequences:
    """Exercise 5: First-order linear recurrence relations a_{n+1} = p * a_n + q."""

    def test_ex5_ka_convergent_fraction_ratio(self):
        """5.ក: a_1 = 2, a_{n+1} = (1/2) a_n + 3 -> lim = 6 (ស្វ៊ីតរួម)"""
        expr_str = r"a_1 = 2, a_{n+1} = \frac{1}{2}a_n + 3"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_recurrence"

        result = solve(parsed, "sequence_recurrence")
        assert result.answer == "6"
        assert result.metadata.get("convergence") == "convergent"
        assert result.metadata.get("fixed_point") == "6"
        assert len(result.steps) == 4
        assert result.steps[0].title_km == "កំណត់តម្លៃថេរ L"
        assert result.steps[1].title_km == "សិក្សាស្វ៊ីតជំនួយ (v_n)"
        assert result.steps[2].title_km == "រកតួទូទៅនៃស្វ៊ីត"
        assert result.steps[3].title_km == "គណនាលីមីត និងសន្និដ្ឋាន"
        assert "ស្វ៊ីតរួម" in result.steps[3].description_km

    def test_ex5_kha_divergent_ratio_two(self):
        """5.ខ: a_1 = 3, a_{n+1} = 2 a_n - 5 -> lim = -oo (ស្វ៊ីតរីក)"""
        expr_str = r"a_1 = 3, a_{n+1} = 2a_n - 5"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_recurrence"

        result = solve(parsed, "sequence_recurrence")
        assert result.answer in ("-oo", "-\\infty")
        assert result.metadata.get("convergence") == "divergent"
        assert result.metadata.get("fixed_point") == "5"
        assert "ស្វ៊ីតរីក" in result.steps[3].description_km

    def test_ex5_ko_convergent_fraction_third(self):
        """5.គ: a_1 = 1, a_{n+1} = (1/3) a_n + 4/3 -> lim = 2 (ស្វ៊ីតរួម)"""
        expr_str = r"a_1 = 1, a_{n+1} = \frac{1}{3}a_n + \frac{4}{3}"
        parsed = parse_math_text(expr_str)
        assert classify_problem(parsed) == "sequence_recurrence"

        result = solve(parsed, "sequence_recurrence")
        assert result.answer == "2"
        assert result.metadata.get("convergence") == "convergent"
        assert result.metadata.get("fixed_point") == "2"
        assert "ស្វ៊ីតរួម" in result.steps[3].description_km


class TestSequenceCurriculumAndPipeline:
    """Test curriculum registry metadata and end-to-end question processing."""

    def test_curriculum_registry_contains_sequences(self):
        from app.knowledge.registry import get_knowledge_registry
        reg = get_knowledge_registry()
        chap = reg.get_chapter("chapter_sequences")
        assert chap is not None
        assert "ស្វ៊ីតចំនួនពិត" in chap.title_km
        assert len(chap.lessons) == 2

    def test_process_question_convergence_pipeline(self):
        q = "តើស្វ៊ីត U_n = 3n^2 + 5n + 1 ជាស្វ៊ីតរួម ឬរីក ?"
        data = process_question(q)
        assert data.problem_type in ("sequence", "sequence_convergence")
        assert data.answer in ("oo", "+oo", "+\\infty")
        assert len(data.steps) >= 3

    def test_process_question_limit_pipeline(self):
        q = r"គណនាលីមីតនៃស្វ៊ីត \lim_{n \to +\infty} \frac{n^2 + 3n - 1}{8n^2 - n + 1}"
        data = process_question(q)
        assert data.problem_type == "sequence_limit"
        assert data.answer == "1/8"
        assert len(data.steps) >= 2

    def test_process_question_recurrence_pipeline(self):
        q = r"គណនាលីមីតនៃស្វ៊ីត (a_n) ដែលស្គាល់តួ a_1 = 2, a_{n+1} = \frac{1}{2}a_n + 3"
        data = process_question(q)
        assert data.problem_type == "sequence_recurrence"
        assert data.answer == "6"
        assert len(data.steps) == 4
