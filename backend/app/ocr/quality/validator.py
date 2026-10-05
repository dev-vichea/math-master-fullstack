"""
Math OCR Candidate Validator.

Checks mathematical syntax, delimiter balance, SymPy parseability,
and flags suspicious OCR artifacts. Assigns explicit statuses:
- VERIFIED
- NEEDS_REVIEW
- INVALID
"""

from __future__ import annotations

import re
from typing import Any

from app.classifier.problem_classifier.classifier import classify_problem
from app.ocr.quality.models import CandidateStatus, MathOcrCandidate
from app.ocr.quality.normalizer import safe_normalize_math
from app.parser.math_parser.expression_parser import ExpressionParseError, parse_math_text

# Disallowed / suspicious OCR artifacts that indicate noise or misrecognition
_SUSPICIOUS_TOKEN_PATTERNS = [
    re.compile(r"\\(?:star|dagger|ddagger|vdash|dashv|uparrow|downarrow|updownarrow)\b"),
    re.compile(r"\\(?:Psi|Omega|Theta|Phi)\^[^{]"),  # Isolated Greek uppercase noise
    re.compile(r"(?:\+\s*){2,}"),                   # ++
    re.compile(r"(?:-\s*){2,}"),                   # --
    re.compile(r"(?:\*\s*){2,}"),                  # **
    re.compile(r"(?:/\s*){2,}"),                   # //
    re.compile(r"==+"),                            # ==
    re.compile(r"\\frac(?!\s*\{)"),                # \frac without opening brace
    re.compile(r"\\sqrt(?!\s*[\{\[])"),            # \sqrt without brace/bracket
]


def check_delimiter_balance(text: str) -> tuple[bool, list[str]]:
    """Verify that all matching pairs of braces, brackets, and parentheses are balanced."""
    # Strip item labels like 'a)', 'b)', '1)', '2)', 'ក)', 'ខ)' at line/string start before balance check
    cleaned = re.sub(r"(?:^|(?<=[\n;]))\s*(?:\([a-zA-Z0-9\u1780-\u17d0]{1,2}\)|[a-zA-Z0-9\u1780-\u17d0]{1,2}[\)\.\:៖])\s*", " ", text)
    issues = []
    pairs = [("{", "}"), ("(", ")"), ("[", "]")]
    for open_char, close_char in pairs:
        open_count = cleaned.count(open_char)
        close_count = cleaned.count(close_char)
        if open_count != close_count:
            issues.append(
                f"Unbalanced delimiters '{open_char}' and '{close_char}': {open_count} open vs {close_count} close"
            )
    return len(issues) == 0, issues


def validate_math_candidate(
    raw_ocr_text: str,
    confidence: float = 0.85,
    source_provider: str = "pix2tex",
    variant_name: str = "original",
    bounding_box: tuple[int, int, int, int] | None = None,
    exercise_metadata: dict[str, Any] | None = None,
) -> MathOcrCandidate:
    """
    Validates a raw OCR result, normalizes it, tests SymPy parseability,
    checks for artifacts/prefixes, and returns a fully scored MathOcrCandidate.
    """
    if not raw_ocr_text or not raw_ocr_text.strip():
        return MathOcrCandidate(
            raw_ocr_text=raw_ocr_text or "",
            normalized_math_text="",
            status=CandidateStatus.INVALID,
            confidence=0.0,
            source_provider=source_provider,
            variant_name=variant_name,
            score=-10.0,
            validation_issues=["Empty OCR text"],
            is_parseable=False,
            exercise_metadata=exercise_metadata,
        )

    # 1. Deterministic safe normalization
    norm_text, norm_warnings, prefix, suffix = safe_normalize_math(raw_ocr_text)

    # Extract target math expression if part of a full exercise text with sub-exercises
    target_math = None
    if exercise_metadata and exercise_metadata.get("primary_expression"):
        target_math = exercise_metadata["primary_expression"]
    elif any(k in raw_ocr_text for k in ("លំហាត់", "Exercise", "Exercise:", "ក.", "ក)", "a)", "1.")):
        try:
            from app.parser.exercise_parser.exercise_parser import parse_exercise
            parsed_ex = parse_exercise(raw_ocr_text)
            if parsed_ex.sub_exercises or (parsed_ex.exercise_title and parsed_ex.primary_expression):
                target_math = parsed_ex.primary_expression
                if not exercise_metadata:
                    exercise_metadata = {
                        "exercise_title": parsed_ex.exercise_title,
                        "instruction": parsed_ex.instruction,
                        "primary_expression": parsed_ex.primary_expression,
                        "sub_exercises": [
                            {
                                "label": sub.label,
                                "raw_text": sub.raw_text,
                                "expression": sub.expression,
                                "intent": sub.intent,
                            }
                            for sub in parsed_ex.sub_exercises
                        ],
                    }
        except Exception:
            pass

    suspicious_tokens: list[str] = []
    validation_issues: list[str] = list(norm_warnings)

    if prefix:
        suspicious_tokens.append(f"prefix:{prefix}")
    if suffix:
        suspicious_tokens.append(f"suffix:{suffix}")

    # 2. Check for known OCR artifact tokens in raw and normalized text
    for pattern in _SUSPICIOUS_TOKEN_PATTERNS:
        matches = pattern.findall(raw_ocr_text)
        if matches:
            suspicious_tokens.extend(matches)
            validation_issues.append(f"Contains suspicious OCR token(s): {matches}")

    # 3. Delimiter balance check
    balanced, delim_issues = check_delimiter_balance(target_math or norm_text)
    if not balanced:
        validation_issues.extend(delim_issues)

    # 4. Mathematical structure check
    eval_text = target_math or norm_text
    has_letters = bool(re.search(r"[a-zA-Z]", eval_text))
    has_digits = bool(re.search(r"\d", eval_text))
    has_operators = any(c in eval_text for c in "=+-*/\\^")
    if not (has_letters or has_digits) or not has_operators:
        validation_issues.append("Lacks recognized mathematical structure (variables, digits, or operators)")

    # 5. SymPy parseability test
    is_parseable = False
    problem_type: str | None = None
    math_to_parse = target_math or norm_text
    if balanced and math_to_parse:
        try:
            parsed = parse_math_text(math_to_parse)
            is_parseable = True
            problem_type = classify_problem(parsed)
        except (ExpressionParseError, Exception) as exc:
            validation_issues.append(f"SymPy parse error: {str(exc)}")
            is_parseable = False

    # 6. Determine explicit status
    if not is_parseable or not balanced or not math_to_parse:
        status = CandidateStatus.INVALID
    elif suspicious_tokens or confidence < 0.70 or validation_issues:
        status = CandidateStatus.NEEDS_REVIEW
    else:
        status = CandidateStatus.VERIFIED

    # 7. Compute composite ranking score
    # Baseline from confidence
    score = confidence

    if status == CandidateStatus.VERIFIED:
        score += 2.0
    elif status == CandidateStatus.NEEDS_REVIEW:
        score += 1.0
    else:
        score -= 5.0

    if is_parseable:
        score += 1.5

    # Penalize suspicious tokens and warnings
    score -= len(suspicious_tokens) * 0.5
    score -= len(validation_issues) * 0.2

    # Prefer non-empty normalized text
    if len(norm_text) > 3:
        score += 0.2

    return MathOcrCandidate(
        raw_ocr_text=raw_ocr_text,
        normalized_math_text=target_math or norm_text,
        status=status,
        confidence=confidence,
        source_provider=source_provider,
        variant_name=variant_name,
        score=round(score, 3),
        bounding_box=bounding_box,
        suspicious_tokens=suspicious_tokens,
        validation_issues=validation_issues,
        detected_prefix=prefix,
        detected_suffix=suffix,
        is_parseable=is_parseable,
        problem_type=problem_type,
        exercise_metadata=exercise_metadata,
    )
