"""
Tests for Lesson-Aware Step-by-Step Explanation System.

Validates:
1. Knowledge Base Curriculum Hierarchy (Chapter → Lesson → Concept → Rule → Method → Template → Examples)
2. Explanation Engine Method Identification
3. Pedagogical Step Generation (What & Why, formulas, verification)
4. Factorization (Common factor, Difference of squares, Trinomial)
5. Expansion (Distributive property)
6. End-to-End API Integration with lesson_info and enriched SolutionStep
"""

from __future__ import annotations

import sympy
from fastapi.testclient import TestClient

from app.explanation.engine import get_explanation_engine
from app.knowledge.registry import get_knowledge_registry
from app.main import app


def test_knowledge_base_curriculum_structure():
    """Verify the Grade 12 & Foundation curriculum hierarchy."""
    registry = get_knowledge_registry()
    chapters = registry.get_all_chapters()
    assert len(chapters) >= 2

    # Algebra Foundations Chapter
    chap_alg = registry.get_chapter("chapter_algebra_foundations")
    assert chap_alg is not None
    assert "ពិជគណិត" in chap_alg.title_km
    assert len(chap_alg.lessons) >= 2

    # Methods lookup
    methods = [
        "method_common_factor_extraction",
        "method_diff_squares",
        "method_trinomial_split",
        "method_distributive_multiplication",
        "method_limit_conjugate",
    ]
    for mid in methods:
        method = registry.get_method(mid)
        assert method is not None, f"Method {mid} not found"
        metadata = registry.get_metadata(mid)
        assert metadata is not None, f"Metadata for {mid} not found"
        meta_dict = metadata.to_dict()
        assert "chapter_km" in meta_dict
        assert "lesson_km" in meta_dict
        assert "method_km" in meta_dict
        assert "rule_formula" in meta_dict
        assert len(method.template.steps) >= 3


def test_factorization_common_factor_pedagogy():
    """Test 4-step common factor explanation: 3x^2 + 6x -> 3x(x + 2)."""
    engine = get_explanation_engine()
    x = sympy.Symbol("x")
    expr = 3 * x**2 + 6 * x

    steps, lesson_info = engine.generate_explanation(
        expr,
        problem_type="expression_factorization",
        raw_text="3x^2 + 6x",
    )

    assert lesson_info is not None
    assert lesson_info["method_id"] == "method_common_factor_extraction"
    assert "កត្តារួម" in lesson_info["method_km"]
    assert "ka + kb = k(a + b)" in lesson_info["rule_formula"]

    # 4 distinct pedagogical steps
    assert len(steps) == 4

    # Step 1: Identify GCF
    s1 = steps[0]
    assert s1.order == 1
    assert "GCF" in s1.title_en or "Common Factor" in s1.title_en
    assert s1.rationale_km is not None
    assert s1.is_verification is False

    # Step 2: Factor out
    s2 = steps[1]
    assert s2.order == 2
    assert "3 x" in s2.expression or "3x" in s2.expression
    assert s2.rule_formula == r"ka + kb = k(a + b)"

    # Step 3: Simplify quotient
    s3 = steps[2]
    assert s3.order == 3
    assert "x + 2" in s3.expression

    # Step 4: Verify by expansion
    s4 = steps[3]
    assert s4.order == 4
    assert s4.is_verification is True
    assert "Verified" in s4.expression or "ត្រឹមត្រូវ" in s4.expression


def test_factorization_difference_of_squares_pedagogy():
    """Test 4-step difference of squares explanation: x^2 - 9 -> (x - 3)(x + 3)."""
    engine = get_explanation_engine()
    x = sympy.Symbol("x")
    expr = x**2 - 9

    steps, lesson_info = engine.generate_explanation(
        expr,
        problem_type="expression_factorization",
        raw_text="x^2 - 9",
    )

    assert lesson_info is not None
    assert lesson_info["method_id"] == "method_diff_squares"
    assert "ផលសងការេ" in lesson_info["method_km"]

    # 4 distinct pedagogical steps
    assert len(steps) == 4

    # Step 1: Identify a^2 - b^2
    assert steps[0].order == 1
    assert "a^2 - b^2" in steps[0].rule_formula

    # Step 2: Extract base terms a and b
    assert steps[1].order == 2
    assert "a = x" in steps[1].expression and "b = 3" in steps[1].expression

    # Step 3: Apply identity
    assert steps[2].order == 3
    assert "x - 3" in steps[2].expression and "x + 3" in steps[2].expression

    # Step 4: Verify
    assert steps[3].order == 4
    assert steps[3].is_verification is True


def test_factorization_trinomial_split_pedagogy():
    """Test 4-step quadratic trinomial factoring: x^2 - 5x + 6 -> (x - 2)(x - 3)."""
    engine = get_explanation_engine()
    x = sympy.Symbol("x")
    expr = x**2 - 5 * x + 6

    steps, lesson_info = engine.generate_explanation(
        expr,
        problem_type="expression_factorization",
        raw_text="x^2 - 5x + 6",
    )

    assert lesson_info is not None
    assert lesson_info["method_id"] == "method_trinomial_split"
    assert "ផលបូក-ផលគុណ" in lesson_info["method_km"]

    # 4 distinct pedagogical steps
    assert len(steps) == 4

    # Step 1: Identify b and c
    assert steps[0].order == 1
    assert "b = -5" in steps[0].expression and "c = 6" in steps[0].expression

    # Step 2: Find p and q
    assert steps[1].order == 2
    assert "p = -2" in steps[1].expression or "p = -3" in steps[1].expression

    # Step 3: Factored form
    assert steps[2].order == 3
    assert "x - 2" in steps[2].expression and "x - 3" in steps[2].expression

    # Step 4: Verify
    assert steps[3].order == 4
    assert steps[3].is_verification is True


def test_expansion_distributive_pedagogy():
    """Test 4-step distributive expansion: (k + 4)(k^2 - 4k + 1)."""
    engine = get_explanation_engine()
    k = sympy.Symbol("k")
    expr = (k + 4) * (k**2 - 4 * k + 1)

    steps, lesson_info = engine.generate_explanation(
        expr,
        problem_type="factored_expression",
        raw_text="A = (k + 4)(k^2 - 4k + 1)",
    )

    assert lesson_info is not None
    assert lesson_info["method_id"] == "method_distributive_multiplication"
    assert "លក្ខណៈបំបែក" in lesson_info["rule_name_km"]

    assert len(steps) == 4
    assert steps[0].title_km == "កន្សោមដើម"
    assert steps[1].title_km == "អនុវត្តលក្ខណៈបំបែកនៃផលគុណ"
    assert steps[2].title_km == "គុណពន្លាតតួនីមួយៗចូលក្នុងវង់ក្រចក"
    expr_clean = steps[3].expression.replace("{", "").replace("}", "")
    assert "k^3 - 15 k + 4" in expr_clean or "k^3 - 15*k + 4" in expr_clean


def test_api_factorization_end_to_end():
    """Test end-to-end API response contains lesson_info and enriched steps."""
    with TestClient(app) as client:
        # Common Factor problem
        res = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ដាក់ជាផលគុណកត្តា 3x^2 + 6x"},
        )
        assert res.status_code == 200
        json_data = res.json()
        assert json_data["success"] is True
        data = json_data["data"]

        # Verify lesson info
        assert "lesson_info" in data
        assert data["lesson_info"] is not None
        assert data["lesson_info"]["method_id"] == "method_common_factor_extraction"
        assert "ពិជគណិត" in data["lesson_info"]["chapter_km"]
        assert "កត្តារួម" in data["lesson_info"]["lesson_km"] or "កត្តារួម" in data["lesson_info"]["concept_km"]

        # Verify steps have pedagogical annotations
        steps = data["steps"]
        assert len(steps) == 4
        for step in steps:
            assert step["title_km"] is not None
            assert step["title_en"] is not None
            assert step["rationale_km"] is not None
            assert step["rationale_en"] is not None
            assert "expression" in step

        # Verify verification step
        assert steps[-1]["is_verification"] is True


def test_api_difference_of_squares_end_to_end():
    """Test API response for difference of squares x^2 - 16."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ដាក់ជាផលគុណកត្តា x^2 - 16"},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["lesson_info"]["method_id"] == "method_diff_squares"
        assert len(data["steps"]) == 4
        assert data["steps"][-1]["is_verification"] is True
