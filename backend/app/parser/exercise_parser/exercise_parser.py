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
    r"|[0-9\u17e0-\u17e9]+[\.៖:](?!\d)"
    r")[:៖.-]?\s*"
)

# Instructions in Khmer and English
_INSTRUCTION_RE = re.compile(
    r"(?i)(?:"
    r"(?:^\s*(?:[0-9\u17e0-\u17e9]{1,2}|[I|V|X]+)\s*[\.\)៖:]\s*)?"
    r"(?:"
    r"(?:Find|Calculate|Evaluate|Compute|Solve)\s+(?:each\s+of\s+)?(?:the\s+)?(?:following\s+)?(?:definite\s+|indefinite\s+)?integrals?(?:\s+of)?(?:\s+the\s+following)?"
    r"|(?:Find|Calculate|Evaluate|Compute)\s+(?:the\s+)?antiderivatives?(?:\s+of)?(?:\s+the\s+following)?(?:\s+functions?)?"
    r"|(?:ចូរ)?(?:គណនា|រក)(?:នូវ)?(?:តម្លៃ)?(?:នៃ)?អាំងតេក្រាល(?:មិនកំណត់|កំណត់)?(?:ខាងក្រោម)?(?:នេះ)?(?:ទាំងនេះ)?(?:ដូចខាងក្រោម)?"
    r"|(?:ចូរ)?(?:គណនា|រក)(?:នូវ)?(?:តម្លៃ)?ព្រីមីទីវ(?:នៃអនុគមន៍)?(?:ខាងក្រោម)?(?:នេះ)?(?:ទាំងនេះ)?(?:ដូចខាងក្រោម)?"
    r"|(?:Find|Calculate|Evaluate|Compute|Solve)\s+(?:each\s+of\s+)?(?:the\s+)?(?:following\s+)?limits?(?:\s+of)?(?:\s+the\s+following)?"
    r"|(?:Find|Calculate|Evaluate|Compute|Determine|Differentiate)\s+(?:each\s+of\s+)?(?:the\s+)?(?:following\s+)?derivatives?(?:\s+of)?(?:\s+the\s+following)?(?:\s+functions?)?"
    r"|(?:ចូរ)?(?:គណនា|រក)(?:នូវ)?(?:តម្លៃ)?(?:នៃ)?ដេរីវេ(?:នៃអនុគមន៍)?(?:ខាងក្រោម)?(?:នេះ)?(?:ទាំងនេះ)?(?:ដូចខាងក្រោម)?"
    r"|(?:ចូរ)?រកសមីការឌីផេរ៉ង់ស្យែល(?:\s*លីនេអ៊ែរ)?(?:\s*លំដាប់ទី\s*[១២12មួយពីរ]+)?(?:\s*អូម៉ូសែន)?(?:\s*ដែល)?\s*មាន(?:\s*អនុគមន៍)?(?:\s*[a-zA-Z]\s*)?ជាចម្លើយ"
    r"|(?:Find|Determine)\s+(?:the\s+)?(?:second[- ]order\s+|first[- ]order\s+)?(?:linear\s+)?(?:homogeneous\s+)?differential\s+equation(?:\s+which|\s+that)?\s+has\s+(?:function\s+)?[a-zA-Z]?\s+as\s+(?:a\s+)?solution"
    r"|(?:Solve|Find|Determine)\s+(?:the\s+)?(?:following\s+)?(?:first[- ]order\s+|second[- ]order\s+)?(?:linear\s+)?(?:homogeneous\s+)?differential\s+equations?(?:\s+according\s+to\s+given\s+conditions?)?"
    r"|(?:ចូរ)?ដោះស្រាយសមីការឌីផេរ៉ង់ស្យែល(?:\s*លីនេអ៊ែរ)?(?:\s*លំដាប់ទី\s*[១២12មួយពីរ]+)?(?:\s*អូម៉ូសែន)?(?:តាមលក្ខខណ្ឌដែលឲ្យ)?(?:ខាងក្រោម)?"
    r"|(?:ចូរ)?(?:ផ្ទៀងផ្ទាត់|បង្ហាញ)(?:ថា)?(?:អនុគមន៍)?(?:\s*[a-zA-Z]\s*)?(?:នីមួយៗ)?ជាចម្លើយ(?:នៃ)?សមីការឌីផេរ៉ង់ស្យែល(?:ដែលគេ(?:ឱ្យ|ឲ្យ)នៅខាងស្ដាំ|ខាងក្រោម)?"
    r"|(?:ចូរ)?បង្ហាញថាអនុគមន៍(?:នីមួយៗ)?ជាចម្លើយនៃសមីការឌីផេរ៉ង់ស្យែល(?:ខាងក្រោម)?"
    r"|(?:Verify|Show)\s+that\s+(?:each\s+)?(?:of\s+the\s+following\s+)?functions?(?:\s+[a-zA-Z])?\s+(?:is|are)\s+(?:a\s+)?solutions?\s+(?:to|of)\s+the\s+differential\s+equation(?:\s+given\s+on\s+the\s+right)?"
    r"|Show\s+that\s+(?:each\s+)?(?:of\s+the\s+following\s+)?functions?\s+(?:is|are)\s+(?:a\s+)?solutions?\s+(?:to|of)\s+the\s+differential\s+equation"
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
    r"|(?:ចូរ)?(?:កំណត់(?!លើ)|ផ្ទៀងផ្ទាត់|ទាញរក|ចាត់ថ្នាក់|បកស្រាយ|ផ្តល់ហេតុផល)"
    r"|(?:ចូរ)?សរសេរ\s*[a-zA-Z0-9_]*\s*ជាអនុគមន៍នៃ\s*[a-zA-Z0-9_]*"
    r"))[:៖\s]*"
)

# Sub-problem numbering (e.g. 'ក.', 'ក)', 'ខ.', 'a)', '1.', '(a)', '(1)', 'ឌ,', '\mathcal{Q}.')
_SUBITEM_RE = re.compile(
    r"(?i)(?:"
    r"(?:^|(?<=[\n,;៖:]))\s*\(([a-zA-Z]|[0-9]{1,2}|[\u1780-\u17a2]|[\u17e0-\u17e9]{1,2})\)\s*"
    r"|(?:^|(?<=[\n,;៖:]))\s*(?:[\\/](?:tilde|bar|hat|mathcal|mathbf|mathrm|text)\{([a-zA-Z0-9\u1780-\u17a2]+)\}|([ក-អ]|[a-zA-Z]|[0-9]{1,2}|[\u17e0-\u17e9]{1,2}))[\)៖:,]\s*"
    r"|(?:^|(?<=[\n,;៖:\s]))\s*(?:[\\/](?:tilde|bar|hat|mathcal|mathbf|mathrm|text)\{([a-zA-Z0-9\u1780-\u17a2]+)\}|([ក-អ]|[a-zA-Z]|[0-9]{1,2}|[\u17e0-\u17e9]{1,2}))\.(?!\d)\s*"
    r")"
)

# Single isolated leading label prefix (e.g. 'ក.', '1.', '(a)', 'ឌ,', '\mathcal{Q}.')
_LEADING_LABEL_RE = re.compile(
    r"^\s*(?:"
    r"\([a-zA-Z0-9\u1780-\u17a2]{1,2}\)[\.៖:,]?"
    r"|(?:[\\/](?:tilde|bar|hat|mathcal|mathbf|mathrm|text)\{[^{}]*(?:\{[^{}]*\})*\}|[ក-អ]|[a-zA-Z]|[0-9]{1,2}|[\u17e0-\u17e9]{1,2})[\)\.៖:,](?!\d)"
    r")\s*"
)

# Mathematical expression regex
_EXPRESSION_RUN = re.compile(r"[0-9a-zA-Z.\+\-\*/\^=()\[\]\s<>=≤≥\\{}_'’|,]{3,}")
_MULTI_LETTER_WORD = re.compile(r"(?<!\\)\b[a-zA-Z]{2,}\b(?![_^\'’\"])")

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
    "cases",
    "begin",
    "end",
    "aligned",
    "array",
    "matrix",
}


_COMMON_PROSE_WORDS = {
    "find", "solve", "evaluate", "calculate", "compute", "determine", "simplify",
    "prove", "show", "verify", "deduce", "express", "factor", "factorise",
    "expand", "sketch", "plot", "each", "the", "following", "functions", "function",
    "equation", "equations", "which", "that", "has", "have", "solution", "solutions",
    "value", "values", "if", "in", "when", "where", "with", "and", "or", "for", "from",
    "at", "by", "as", "given", "is", "are", "then", "let", "suppose", "assume",
    "problem", "exercise", "question", "task", "practice", "example",
}


def _strip_non_math_words(text: str) -> str:
    """Strip English prose words while preserving recognized mathematical functions and variable products (e.g. xy, ab)."""

    def _rep(m: re.Match) -> str:
        word = m.group(0).lower()
        if word in _MATH_KEYWORDS:
            return m.group(0)
        if word in _COMMON_PROSE_WORDS or len(word) >= 4:
            return " "
        return m.group(0)

    return _MULTI_LETTER_WORD.sub(_rep, text)


def _is_valid_math_expression(text: str | None) -> bool:
    """
    Autonomously validate whether a text string contains a solvable mathematical expression,
    equation, or operation rather than prose, solitary punctuation, or lone variable symbols.
    """
    if not text:
        return False
    clean = text.strip()
    if not clean:
        return False

    # Solitary punctuation, slashes, or arithmetic operators cannot be a math problem
    if clean in {"/", "\\", "+", "-", "*", "=", "^", ":", ";", ",", ".", "!", "?", "(", ")", "[", "]"}:
        return False

    # Must contain alphanumeric characters
    if not re.search(r"[0-9a-zA-Z\u1780-\u17ff]", clean):
        return False

    # A single isolated Latin letter (like 'f', 'x', 'y') is a variable or function label, not a complete problem
    if re.fullmatch(r"[a-zA-Z]", clean):
        return False

    # If there are NO digits in the expression:
    has_digits = bool(re.search(r"\d", clean))
    if not has_digits:
        # A purely symbolic math expression MUST contain recognized math operations or relations:
        # e.g., equations ('='), inequalities ('<', '>'), derivatives ('y\'', 'dy/dx'),
        # algebraic operators ('+', '-', '*', '/', '^'), or LaTeX math commands (\frac, \sqrt, \int, \lim, etc.)
        has_math_operator = bool(
            re.search(
                r"[=+\-*/\^<>≤≥]|\\(?:frac|sqrt|int|lim|sum|prod|sin|cos|tan|cot|ln|log|exp|cdot|times|pm|mp)\b|y[\'’\"]",
                clean,
            )
        )
        if not has_math_operator:
            return False

    # Ensure operators have operands and are not just stray syntax (e.g. "x /" or "/ x" or "+ -")
    if re.fullmatch(r"[\s+\-*/^=<>]+", clean):
        return False

    # If it contains Khmer characters without equations or recognized math structures, it's prose
    has_khmer = bool(re.search(r"[\u1780-\u17ff]", clean))
    if has_khmer and "=" not in clean and r"\int" not in clean and r"\lim" not in clean:
        if not re.search(r"\d+\s*[\+\-\*/\^]\s*\d+", clean):
            return False

    return True


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


def clean_math_only(text: str | None) -> str:
    """
    Ensure the mathematical expression contains strictly minimal math only:
    - Strips all Khmer characters ([\\u1780-\\u17FF\\u19E0-\\u19FF]) and punctuation
    - Strips exercise headers, instructions, and labels (e.g. 1., a), ឌ,, ឃ.)
    - Strips LaTeX \\text{...} wrappers containing prose
    - Cleans OCR dash artifacts (e.g. ---, - - -) and stray delimiters
    - Strips leading / trailing stray punctuation
    """
    if not text:
        return ""

    s = text.strip()
    # 1. Unwrap outer environments like \\begin{aligned} ... \\end{aligned} or \\begin{gathered}
    s = re.sub(r"^\s*\\begin\{(?:aligned|gathered)\}\s*(?:&|\s)*", "", s)
    s = re.sub(r"\s*\\end\{(?:aligned|gathered)\}\s*$", "", s)
    s = re.sub(r"^&+\s*", "", s)

    # 2. Strip instructions and headers
    s = _HEADER_RE.sub(" ", s)
    s = _INSTRUCTION_RE.sub(" ", s)

    # 3. Strip any LaTeX text commands containing Khmer or prose words
    s = re.sub(r"\\(?:text|mathrm|mathbf|textbf|textit)\{[^{}]*[\u1780-\u17ff][^{}]*\}", " ", s)
    s = re.sub(r"\\(?:text|mathrm|mathbf|textbf|textit)\{\s*\}", " ", s)

    # 4. Strip ALL Khmer characters and Khmer punctuation
    s = re.sub(r"[\u1780-\u17FF\u19E0-\u19FF\u17D4-\u17DA]", " ", s)

    # 5. Clean LaTeX spacing tokens
    s = re.sub(r"\\+([;,!:])", " ", s)
    s = re.sub(r"\\(?:quad|qquad|hfill|vfill|thickspace|medspace|thinspace)\b", " ", s)

    # 6. Strip leading labels e.g. '1.', 'a)', 'A.', 'ឃ.', 'ឌ,'
    s = re.sub(
        r"^\s*(?:\([a-zA-Z0-9]{1,2}\)[\.៖:,]?|[a-zA-Z0-9]{1,2}[\)\.៖:,](?!\d))\s*",
        "",
        s,
    )
    s = re.sub(r"^\s*(?:[\\/](?:tilde|bar|hat|mathcal|mathbf|mathrm|text)\{[^{}]*\}[\)\.៖:,]?)\s*", "", s)

    # 7. Clean repeated OCR dashes (e.g. - - - or ---)
    s = re.sub(r"(?:-\s*){2,}", " ", s)

    # 8. Clean leading line breaks and alignment tokens left over from empty text lines
    s = re.sub(r"^(?:\\\\|&|\s)+", "", s)

    # 9. Clean solitary leading punctuation like , = or : = or .
    s = re.sub(r"^[\s,;:.]+", "", s)
    if s.startswith("=") and not re.search(r"^[a-zA-Z]\s*=", s):
        s = s.lstrip("= \t")
    s = re.sub(r"^[\s,;:.]+", "", s)

    # 10. Clean trailing OCR noise (stray dots, commas, solitary 'i' at end)
    s = re.sub(r"[\s,;:.|~]+$", "", s)
    s = re.sub(r"(?<=\d|\)|\]|\})\s+i\s*$", "", s)

    return re.sub(r"\s+", " ", s).strip()


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
    cleaned = re.sub(r"(?<!\\)\\[ \t]+", " ", cleaned)

    candidates = _EXPRESSION_RUN.findall(cleaned)
    if not candidates:
        return None

    # Check if verification sentence with multiple equations (e.g. y = f(x) and ODE)
    if any(k in text for k in ("ជាចម្លើយនៃសមីការ", "ជាចម្លើយ", "is a solution to", "is a solution of", "solution of the differential equation")):
        eq_runs = [c.strip() for c in candidates if "=" in c and len(c.strip()) >= 3]
        if len(eq_runs) >= 2:
            return f"{eq_runs[0]} , {eq_runs[1]}"

    # Prefer candidates containing digits
    with_digits = [c for c in candidates if re.search(r"\d", c)]
    pool = with_digits or candidates

    best = max(pool, key=len).strip()
    has_differential = bool(re.search(r"\b(d[xyzut])\b", best))
    if "\\" in best or "{" in best or has_differential:
        best = re.sub(r"\s+", " ", best).strip()
        if has_differential:
            best = re.sub(r"(?<=[0-9a-zA-Z\)\]\}])\s*(d[xyzut]\b)", r" \1", best)
    else:
        best = re.sub(r"\s+", "", best)

    # Clean leading label prefix if any remained in best (e.g. \mathcal{Q}. or 2. or a. or (a))
    best = _LEADING_LABEL_RE.sub("", best)

    # Clean leading/trailing stray punctuation (preserve leading \ for LaTeX commands like \frac, \sqrt)
    # Also strip Khmer punctuation marks '។' (\u17d4) and '៕' (\u17d5)
    # Do not strip '==' which is invalid mathematical syntax
    if not (best.endswith("==") or best.startswith("==")):
        if best.endswith("=") and not best.endswith("=="):
            best = best[:-1].rstrip()
        best = best.strip(".:;, \u17d4\u17d5")
    while best.endswith("\\"):
        best = best[:-1].rstrip(".:;, \u17d4\u17d5")

    if not _is_valid_math_expression(best):
        return None

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

    # 1. OCR sanitization + LaTeX text unwrapping + Khmer normalization
    pre_cleaned = raw_text.replace(r"\operatorname*{lim}", r"\lim").replace(
        r"\operatorname{lim}", r"\lim"
    )
    # Unwrap LaTeX text commands (e.g. \text{គណនា } -> គណនា)
    _latex_text_re = r"\\(?:text|mathrm|mathbf|textbf|textit)\{([^{}]+)\}"
    pre_cleaned = re.sub(_latex_text_re, r" \1 ", pre_cleaned)
    pre_cleaned = re.sub(_latex_text_re, r" \1 ", pre_cleaned)

    # Unwrap multi-line environments (\begin{gathered}, \begin{aligned}, etc.)
    pre_cleaned = re.sub(r"\\(?:begin|end)\{(?:gathered|aligned|matrix|array|cases)\}(?:\{[^}]*\})?", " ", pre_cleaned)
    # Strip LaTeX alignment tokens (&) and spacing commands (\quad, \qquad)
    pre_cleaned = re.sub(r"\\(?:quad|qquad|thickspace|medspace|thinspace)\b", " ", pre_cleaned)
    pre_cleaned = pre_cleaned.replace("&", " ")

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
            if sub_expr and _is_valid_math_expression(sub_expr):
                sub_intent = _intent_classifier.classify(sub_raw)
                sub_exercises.append(
                    SubExercise(
                        label=label,
                        raw_text=sub_raw,
                        expression=sub_expr,
                        intent=sub_intent.value,
                    )
                )
            elif not sub_exercises and not instruction:
                # If the first sub-item has no valid math expression, it was an instruction header!
                instruction = sub_raw.strip(" \t\r\n:៖.-")
    elif len(sub_matches) == 1:
        match = sub_matches[0]
        label = next((g for g in match.groups() if g is not None), "")
        prefix_text = body_text[: match.start()].strip(" \t\r\n:៖.-")
        if prefix_text and not instruction:
            instruction = prefix_text
        sub_raw = body_text[match.end() :].strip()
        sub_expr = _extract_single_math_expression(sub_raw)
        if sub_expr and _is_valid_math_expression(sub_expr):
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
        elif not instruction:
            instruction = sub_raw.strip(" \t\r\n:៖.-")

    # 5. Determine primary expression
    if sub_exercises:
        for s in sub_exercises:
            s.expression = clean_math_only(s.expression)
        primary_expr = sub_exercises[0].expression
    else:
        candidate_primary = _extract_single_math_expression(body_text)
        primary_expr = candidate_primary if _is_valid_math_expression(candidate_primary) else None

    if primary_expr:
        primary_expr = clean_math_only(primary_expr)

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
