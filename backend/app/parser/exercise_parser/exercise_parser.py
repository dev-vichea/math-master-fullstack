"""
Bilingual exercise parser for Khmer and English math problems.

Extracts structured components from raw exercise text or OCR output:
- Exercise headers (e.g., "លំហាត់ទី ១", "Exercise 2", "Problem 3")
- Instructions (e.g., "ដោះស្រាយសមីការ", "Solve for x", "គណនា", "Simplify")
- Target variable prompt isolation (prevents "Find x if 4x+10=30" from becoming "x4x")
- Sub-problem itemization (e.g., "ក. 2x + 4 = 12", "ខ) 3x - 9 = 0", "a) ...", "b) ...")
- Mathematical expression extraction
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.classifier.problem_classifier.intent_classifier import (
    MathIntent,
    RuleBasedIntentClassifier,
)
from app.ocr.normalization.ocr_postprocessor import sanitize_ocr_math_text
from app.parser.expression_parser.khmer_normalizer import normalize_khmer_text

_intent_classifier = RuleBasedIntentClassifier()

# Exercise headers in Khmer and English
_HEADER_RE = re.compile(
    r"(?i)^\s*(?:"
    r"(?:លំហាត់ទី|លំហាត់|សំណួរទី|សំណួរ|វិញ្ញាសាទី|វិញ្ញាសា)\s*(?:\([^)]*\))?"
    r"(?:\s*[:៖.-]?\s*[0-9\u17e0-\u17e9]+(?=\s*[:៖.-]|\s+[a-zA-Z\u1780-\u17ff]|$))?"
    r"|(?:Exercise|Problem|Question|Task|Practice|Example|Ex|Q)\.?"
    r"(?:\s*\([^)]*\))?"
    r"(?:\s*[:.-]?\s*[0-9\u17e0-\u17e9]+(?=\s*[:.-]|\s+[a-zA-Z\u1780-\u17ff]|$))?"
    r")[:៖.-]?\s*"
)

# Instructions in Khmer and English
_INSTRUCTION_RE = re.compile(
    r"(?i)(?:"
    r"(?:Find|Calculate|Evaluate|Compute|Solve)\s+(?:each\s+of\s+)?(?:the\s+)?(?:following\s+)?limits?(?:\s+of)?(?:\s+the\s+following)?"
    r"|(?:Find|Calculate|Evaluate|Compute|Determine|Differentiate)\s+(?:each\s+of\s+)?(?:the\s+)?(?:following\s+)?derivatives?(?:\s+of)?(?:\s+the\s+following)?(?:\s+functions?)?"
    r"|(?:ចូរ)?(?:គណនា|រក)(?:នូវ)?(?:តម្លៃ)?(?:នៃ)?ដេរីវេ(?:នៃអនុគមន៍)?(?:ខាងក្រោម)?(?:នេះ)?(?:ទាំងនេះ)?(?:ដូចខាងក្រោម)?"
    r"|Find\s+(?:the\s+)?value\s+of\s+[a-zA-Z]\s*(?:if|in|when|where|:)?"
    r"|Solve\s+for\s+[a-zA-Z]\s*(?:if|in|when|where|:)?"
    r"|Solve\s+the\s+(?:following\s+)?equation"
    r"|Find\s+[a-zA-Z]\s*(?:if|in|when|where|:)"
    r"|Calculate\s+(?:the\s+value\s+of\s+)?[a-zA-Z]?"
    r"|Evaluate\s*(?:the\s+expression|the\s+following)?"
    r"|Simplify\s*(?:the\s+expression|the\s+following)?"
    r"|Determine\s+(?:the\s+value\s+of\s+)?[a-zA-Z]?"
    r"|Prove\s+(?:that\s+)?|Show\s+that\s+|Verify\s+(?:that\s+)?|Deduce\s+(?:that\s+)?"
    r"|Express\s+[a-zA-Z0-9_]+\s+in\s+terms\s+of\s+[a-zA-Z0-9_]+"
    r"|Factor(?:ise)?\s*(?:the\s+expression|the\s+following)?"
    r"|Expand\s*(?:the\s+expression|the\s+following)?"
    r"|Sketch\s*(?:the\s+curve|the\s+graph|the\s+following)?"
    r"|Plot\s*(?:the\s+points|the\s+graph)?"
    r"|(?:ចូរ)?(?:គណនា|រក|ដោះស្រាយ)(?:នូវ)?(?:តម្លៃ)?(?:នៃ)?លីមីត(?:នៃអនុគមន៍)?(?:ខាងក្រោម)?(?:នេះ)?(?:ទាំងនេះ)?(?:ដូចខាងក្រោម)?"
    r"|(?:ចូរ)?(?:ស្រាយបំភ្លឺថា|បង្ហាញថា|បញ្ជាក់ថា)"
    r"|ដោះស្រាយសមីការ(?:ខាងក្រោម)?"
    r"|ចូរដោះស្រាយសមីការ(?:ខាងក្រោម)?"
    r"|ចូរដោះស្រាយ"
    r"|ដោះស្រាយ"
    r"|រកតម្លៃនៃ\s*[a-zA-Z]\s*(?:បើ|បើសិន|បើសិនជា|កាលណា|៖|:)?"
    r"|រកតម្លៃ\s*[a-zA-Z]?"
    r"|រក\s*[a-zA-Z]\s*(?:បើ|បើសិន|បើសិនជា|កាលណា|៖|:)"
    r"|ចូររកតម្លៃ(?:នៃ)?\s*[a-zA-Z]?"
    r"|គណនាតម្លៃនៃ\s*[a-zA-Z]?"
    r"|គណនាតម្លៃ"
    r"|គណនាកន្សោម(?:ខាងក្រោម)?"
    r"|គណនាប្រភាគ"
    r"|គណនា"
    r"|ចូរគណនា"
    r"|(?:ចូរ)?(?:សម្រួល|ធ្វើឲ្យសាមញ្ញ|បង្រួម)(?:នូវ)?(?:កន្សោម)?(?:ខាងក្រោម)?"
    r"|(?:ចូរ)?(?:ដាក់ជាផលគុណកត្តា|ពន្លាត)(?:នូវ)?(?:កន្សោម)?(?:ខាងក្រោម)?"
    r"|(?:ចូរ)?(?:កំណត់|ផ្ទៀងផ្ទាត់|ទាញរក|ចាត់ថ្នាក់|បកស្រាយ|ផ្តល់ហេតុផល)"
    r"|(?:ចូរ)?សរសេរ\s*[a-zA-Z0-9_]*\s*ជាអនុគមន៍នៃ\s*[a-zA-Z0-9_]*"
    r")[:៖\s]*"
)

# Sub-problem numbering (e.g. 'ក.', 'ក)', 'ខ.', 'a)', '1.', '(a)', '(1)', '\mathcal{Q}.')
_SUBITEM_RE = re.compile(
    r"(?i)(?:"
    r"(?:^|(?<=[\n,;៖:]))\s*\(([a-zA-Z]|[0-9]{1,2}|[\u1780-\u17a2]|[\u17e0-\u17e9]{1,2})\)\s*"
    r"|(?:^|(?<=[\n,;៖:]))\s*(?:[\\/](?:tilde|bar|hat|mathcal|mathbf|mathrm|text)\{([a-zA-Z0-9\u1780-\u17a2]+)\}|([ក-អ]|[a-zA-Z]|[0-9]{1,2}|[\u17e0-\u17e9]{1,2}))[\)៖:]\s*"
    r"|(?:^|(?<=[\n,;៖:\s]))\s*(?:[\\/](?:tilde|bar|hat|mathcal|mathbf|mathrm|text)\{([a-zA-Z0-9\u1780-\u17a2]+)\}|([ក-អ]|[a-zA-Z]|[0-9]{1,2}|[\u17e0-\u17e9]{1,2}))\.(?!\d)\s*"
    r")"
)

# Single isolated leading label prefix (e.g. 'ក.', '1.', '(a)', '\mathcal{Q}.')
_LEADING_LABEL_RE = re.compile(
    r"^\s*(?:"
    r"\([a-zA-Z0-9\u1780-\u17a2]{1,2}\)[\.៖:]?"
    r"|(?:[\\/](?:tilde|bar|hat|mathcal|mathbf|mathrm|text)\{[^{}]*(?:\{[^{}]*\})*\}|[ក-អ]|[a-zA-Z]|[0-9]{1,2}|[\u17e0-\u17e9]{1,2})[\)\.៖:](?!\d)"
    r")\s*"
)

# Mathematical expression regex
_EXPRESSION_RUN = re.compile(r"[0-9a-zA-Z.\+\-\*/\^=()\[\]\s<>=≤≥\\{}_]{3,}")
_MULTI_LETTER_WORD = re.compile(r"(?<!\\)\b[a-zA-Z]{2,}\b")

# Math function and LaTeX names that must never be stripped as prose words
_MATH_KEYWORDS = {
    "sin",
    "cos",
    "tan",
    "cot",
    "sec",
    "csc",
    "lim",
    "log",
    "ln",
    "exp",
    "det",
    "gcd",
    "lcm",
    "mod",
    "max",
    "min",
    "sqrt",
    "deg",
    "to",
    "rightarrow",
    "infty",
    "frac",
    "cdot",
    "times",
    "div",
    "pm",
    "mp",
    "int",
    "sum",
    "prod",
    "dx",
    "dy",
    "dt",
    "dz",
}


def _strip_non_math_words(text: str) -> str:
    """Strip English prose words while preserving recognized mathematical functions."""

    def _rep(m: re.Match) -> str:
        word = m.group(0)
        if word.lower() in _MATH_KEYWORDS:
            return word
        return " "

    return _MULTI_LETTER_WORD.sub(_rep, text)


@dataclass
class SubExercise:
    label: str
    raw_text: str
    expression: str
    intent: str


@dataclass
class ParsedExercise:
    original_text: str
    clean_text: str
    exercise_title: str | None
    instruction: str | None
    primary_expression: str | None
    detected_intent: str
    sub_exercises: list[SubExercise] = field(default_factory=list)


def _extract_single_math_expression(text: str) -> str | None:
    """Extract a single clean math expression string from text segment."""
    # First, strip common prompt clauses that contain target variable letters
    # e.g., "Find x if 4x + 10 = 30" -> " 4x + 10 = 30"
    cleaned = _INSTRUCTION_RE.sub(" ", text)

    # Strip multi-letter words (words in prose like 'solve', 'find', 'when') while preserving math functions
    cleaned = _strip_non_math_words(cleaned)

    # Remove leading sub-item label prefix if any remains at start of string
    cleaned = _LEADING_LABEL_RE.sub("", cleaned)

    # Clean LaTeX spacing tokens like \; \, \! \: \quad \qquad \hfill so they don't split candidate math runs
    cleaned = re.sub(r"\\+([;,!:])", " ", cleaned)
    cleaned = re.sub(r"\\(?:quad|qquad|hfill|vfill)", " ", cleaned)
    cleaned = re.sub(r"\\[\s]+", " ", cleaned)

    candidates = _EXPRESSION_RUN.findall(cleaned)
    if not candidates:
        return None

    # Prefer candidates containing digits
    with_digits = [c for c in candidates if re.search(r"\d", c)]
    pool = with_digits or candidates

    best = max(pool, key=len).strip()
    if "\\" in best or "{" in best:
        best = re.sub(r"\s+", " ", best).strip()
    else:
        best = re.sub(r"\s+", "", best)

    # Clean leading label prefix if any remained in best (e.g. \mathcal{Q}. or 2. or a. or (a))
    best = _LEADING_LABEL_RE.sub("", best)

    # Clean leading/trailing stray punctuation (preserve leading \ for LaTeX commands like \frac, \sqrt)
    best = best.strip(".:;=, ")
    while best.endswith("\\"):
        best = best[:-1].rstrip(".:;=, ")
    return best or None


def parse_exercise(raw_text: str) -> ParsedExercise:
    """
    Parse a math exercise in Khmer or English into structured components.
    """
    if not raw_text or not raw_text.strip():
        return ParsedExercise(
            original_text=raw_text,
            clean_text="",
            exercise_title=None,
            instruction=None,
            primary_expression=None,
            detected_intent=MathIntent.UNKNOWN.value,
            sub_exercises=[],
        )

    # 1. OCR sanitization + Khmer normalization
    pre_cleaned = raw_text.replace(r"\operatorname*{lim}", r"\lim").replace(
        r"\operatorname{lim}", r"\lim"
    )
    sanitized = sanitize_ocr_math_text(pre_cleaned)
    normalized = normalize_khmer_text(sanitized)

    # 2. Extract exercise header / title
    header_match = _HEADER_RE.search(normalized)
    exercise_title = header_match.group(0).strip(" \t\r\n:៖.-") if header_match else None
    remaining_text = _HEADER_RE.sub("", normalized, count=1) if header_match else normalized

    # 3. Extract instruction / intent phrasing
    inst_match = _INSTRUCTION_RE.search(remaining_text)
    instruction = inst_match.group(0).strip(" \t\r\n:៖.-") if inst_match else None
    body_text = _INSTRUCTION_RE.sub("", remaining_text, count=1) if inst_match else remaining_text

    # 4. Check for sub-problems (e.g., 'ក. 2x+1=5\nខ. 3x-2=7', or single 'ខ. \lim...')
    sub_matches = list(_SUBITEM_RE.finditer(body_text))
    sub_exercises: list[SubExercise] = []

    if len(sub_matches) >= 2:
        for i, match in enumerate(sub_matches):
            label = next((g for g in match.groups() if g is not None), "")
            start_idx = match.end()
            end_idx = sub_matches[i + 1].start() if i + 1 < len(sub_matches) else len(body_text)
            sub_raw = body_text[start_idx:end_idx].strip()
            sub_expr = _extract_single_math_expression(sub_raw)
            if sub_expr:
                sub_intent = _intent_classifier.classify(sub_raw)
                sub_exercises.append(
                    SubExercise(
                        label=label,
                        raw_text=sub_raw,
                        expression=sub_expr,
                        intent=sub_intent.value,
                    )
                )
    elif len(sub_matches) == 1:
        match = sub_matches[0]
        if match.start() <= 2:
            label = next((g for g in match.groups() if g is not None), "")
            sub_raw = body_text[match.end() :].strip()
            sub_expr = _extract_single_math_expression(sub_raw)
            if sub_expr:
                sub_intent = _intent_classifier.classify(sub_raw)
                sub_exercises.append(
                    SubExercise(
                        label=label,
                        raw_text=sub_raw,
                        expression=sub_expr,
                        intent=sub_intent.value,
                    )
                )
                body_text = sub_raw

    # 5. Determine primary expression
    if sub_exercises:
        primary_expr = sub_exercises[0].expression
    else:
        primary_expr = _extract_single_math_expression(body_text)

    # 6. Determine overall intent
    overall_intent = _intent_classifier.classify(normalized)
    if overall_intent == MathIntent.UNKNOWN and primary_expr:
        # If expression contains '=', default to solve_equation
        if "=" in primary_expr:
            overall_intent = MathIntent.SOLVE_EQUATION
        else:
            overall_intent = MathIntent.EVALUATE_EXPRESSION

    return ParsedExercise(
        original_text=raw_text,
        clean_text=normalized,
        exercise_title=exercise_title,
        instruction=instruction,
        primary_expression=primary_expr,
        detected_intent=overall_intent.value,
        sub_exercises=sub_exercises,
    )
