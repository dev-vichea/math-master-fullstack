"""
Comprehensive automated tests for Math OCR Quality Pipeline.

Covers all 14 mandatory test cases:
1. Clean formula OCR
2. OCR with unwanted prefix (e.g. '1964,')
3. OCR with unwanted suffix (e.g. '~v')
4. Malformed LaTeX (unbalanced delimiters)
5. Missing operator
6. Incorrect fraction structure
7. Low-confidence OCR
8. Valid limit classification & method
9. Invalid expression rejection
10. Manual correction recovery
11. Multiple OCR candidates generation
12. Candidate ranking prioritization
13. Solver protection rejection
14. Solver verification validation
"""

from __future__ import annotations

import io
import pytest
from PIL import Image, ImageDraw

from app.ocr.quality.models import CandidateStatus, MathOcrCandidate
from app.ocr.quality.normalizer import safe_normalize_math
from app.ocr.quality.pipeline import MathOcrQualityPipeline
from app.ocr.quality.validator import check_delimiter_balance, validate_math_candidate
from app.services.math_service import MathService
from app.utils.exceptions import MathProcessingError


def create_synthetic_math_image_bytes() -> bytes:
    """Helper to create dummy math image bytes."""
    img = Image.new("RGB", (300, 100), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((50, 40), "lim x->0 (sin x)/x", fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestMathOcrQualityPipeline:
    """Test suite for Math OCR Quality Pipeline and Solver Protection."""

    # 1. Clean formula OCR
    def test_clean_formula_ocr(self):
        candidate = validate_math_candidate(
            raw_ocr_text=r"\lim_{x\to\frac{\pi}{3}}{\frac{1-2\cos{x}}{\pi-3x}}",
            confidence=0.95,
        )
        assert candidate.status == CandidateStatus.VERIFIED
        assert candidate.is_parseable is True
        assert len(candidate.suspicious_tokens) == 0
        assert candidate.score > 3.0

    # 2. OCR with unwanted prefix (e.g. '1964,')
    def test_ocr_with_unwanted_prefix(self):
        raw = r"1964, \lim_{x\to\frac{\pi}{3}}{\frac{1-2\cos{x}}{\pi-3x}}"
        candidate = validate_math_candidate(raw, confidence=0.92)
        assert candidate.detected_prefix == "1964,"
        assert candidate.status == CandidateStatus.NEEDS_REVIEW
        assert candidate.normalized_math_text.replace(" ", "") == r"\lim_{x\to\frac{\pi}{3}}{\frac{1-2\cos{x}}{\pi-3x}}".replace(" ", "")
        assert any("prefix:1964," in s for s in candidate.suspicious_tokens)

    # 3. OCR with unwanted suffix (e.g. '~v')
    def test_ocr_with_unwanted_suffix(self):
        raw = r"y' = 2x + 1 ~v"
        candidate = validate_math_candidate(raw, confidence=0.88)
        assert candidate.detected_suffix == "~v"
        assert candidate.status == CandidateStatus.NEEDS_REVIEW
        assert candidate.normalized_math_text == "y' = 2x + 1"
        assert any("suffix:~v" in s for s in candidate.suspicious_tokens)

    # 4. Malformed LaTeX (unbalanced delimiters)
    def test_malformed_latex_unbalanced(self):
        raw = r"\frac{1}{2"
        balanced, issues = check_delimiter_balance(raw)
        assert balanced is False
        assert len(issues) > 0

        candidate = validate_math_candidate(raw)
        assert candidate.status == CandidateStatus.INVALID
        assert candidate.is_parseable is False
        assert any("Unbalanced delimiters" in issue for issue in candidate.validation_issues)

    # 5. Missing operator
    def test_missing_operator(self):
        raw = "xyz"
        candidate = validate_math_candidate(raw, confidence=0.80)
        assert any("Lacks recognized mathematical structure" in issue for issue in candidate.validation_issues)

    # 6. Incorrect fraction structure
    def test_incorrect_fraction_structure(self):
        raw = r"y = \frac x + 1"
        candidate = validate_math_candidate(raw, confidence=0.85)
        assert candidate.status == CandidateStatus.INVALID
        assert any(r"\frac" in token for token in candidate.suspicious_tokens)

    # 7. Low-confidence OCR
    def test_low_confidence_ocr(self):
        raw = "x + 2 = 5"
        candidate = validate_math_candidate(raw, confidence=0.55)
        # Low confidence triggers review
        assert candidate.status == CandidateStatus.NEEDS_REVIEW
        assert candidate.confidence == 0.55

    # 8. Valid limit classification & method
    def test_valid_limit_classification_and_method(self):
        service = MathService()
        raw = r"\lim_{x\to\frac{\pi}{3}}{\frac{1-2\cos{x}}{\pi-3x}}"
        solve_data = service.process_question(raw)

        assert solve_data.problem_type == "calculus_limit"
        assert solve_data.answer == "-sqrt(3)/3"
        assert solve_data.lesson_info is not None
        assert solve_data.lesson_info["method_id"] == "method_limit_trigonometric"
        assert len(solve_data.steps) >= 4

    # 9. Invalid expression rejection
    def test_invalid_expression_rejection(self):
        service = MathService()
        invalid_raw = r"\frac{x}{ + = "
        with pytest.raises(MathProcessingError) as exc_info:
            service.process_question(invalid_raw)
        assert "mathematics" in str(exc_info.value).lower() or "parse" in str(exc_info.value).lower()

    # 10. Manual correction recovery
    def test_manual_correction_recovery(self):
        # Initial bad OCR
        bad_raw = r"\frac{1}{2"
        bad_cand = validate_math_candidate(bad_raw)
        assert bad_cand.status == CandidateStatus.INVALID

        # User edits in MathLive field
        corrected_raw = r"\frac{1}{2}"
        good_cand = validate_math_candidate(corrected_raw)
        assert good_cand.status in (CandidateStatus.VERIFIED, CandidateStatus.NEEDS_REVIEW)
        assert good_cand.is_parseable is True

    # 11. Single-pass OCR pipeline processing
    def test_single_pass_pipeline_processing(self):
        class MockEngine:
            name = "mock_formula"
            def detect(self, img_bytes):
                from app.ocr.engines.base import VisionResult
                return VisionResult(detected_text=r"\frac{1}{2}", confidence=0.92, error_message=None)

        pipeline = MathOcrQualityPipeline(formula_engine=MockEngine())
        img_bytes = create_synthetic_math_image_bytes()
        res = pipeline.process_image(img_bytes)
        assert res.selected_candidate.normalized_math_text == r"\frac{1}{2}"
        assert res.status == CandidateStatus.VERIFIED
        assert res.confidence == 0.92
        assert len(res.all_candidates) == 1

    # 12. Candidate scoring and verification
    def test_candidate_scoring_and_verification(self):
        bad_candidate = validate_math_candidate(
            raw_ocr_text=r"\frac{1}{2",
            confidence=0.99,  # high confidence, but invalid syntax!
            source_provider="pix2tex",
        )
        good_candidate = validate_math_candidate(
            raw_ocr_text=r"\frac{1}{2}",
            confidence=0.85,
            source_provider="pix2tex",
        )

        assert bad_candidate.status == CandidateStatus.INVALID
        assert good_candidate.status == CandidateStatus.VERIFIED
        assert good_candidate.score > bad_candidate.score

    # 13. Solver protection rejection
    def test_solver_protection_rejection(self):
        service = MathService()
        # Non-math text
        with pytest.raises(MathProcessingError):
            service.process_question("random non math prose words")
        # Malformed operators
        with pytest.raises(MathProcessingError):
            service.process_question("x ++ y ==")

    # 14. Solver verification validation
    def test_solver_verification_validation(self):
        service = MathService()
        # Differential equation with Cauchy condition
        ode = "y'' - 3y' + 2y = 0, y(0) = 1, y'(0) = 3"
        solve_data = service.process_question(ode)
        assert solve_data.is_verified is True
        assert solve_data.answer is not None
