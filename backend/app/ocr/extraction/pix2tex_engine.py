"""
LaTeX-OCR (pix2tex) vision engine for mathematical formula recognition.

Uses Lukas Blecher's LaTeX-OCR (ViT + ResNet encoder-decoder) to transcribe
cropped images of mathematical equations directly into LaTeX code.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

from PIL import Image

from app.ocr.extraction.base import MathVisionEngine, VisionResult


def _unwrap_outer_braces(s: str) -> str:
    """Unwrap matching outer braces like '{{...}}' -> '...'."""
    res = s.strip()
    while res.startswith("{") and res.endswith("}"):
        depth = 0
        matches_whole = True
        for i, ch in enumerate(res):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0 and i < len(res) - 1:
                    matches_whole = False
                    break
        if matches_whole:
            res = res[1:-1].strip()
        else:
            break
    return res


def clean_pix2tex_output(latex_code: str) -> str:
    """Clean and normalize raw LaTeX output from pix2tex."""
    import re

    t = (latex_code or "").strip()

    # Normalize tilde spaces, spacing commands and equivalence symbols
    t = t.replace("~", " ")
    t = t.replace("{(}", "(").replace("{)}", ")")
    t = t.replace("{[}", "[").replace("{]}", "]")
    t = re.sub(r"([+\-=])\{\s*(\\frac\{[^{}]*\}\{[^{}]*\})\s*\}", r"\1\2", t)
    t = re.sub(r"\\(?:quad|qquad|hfill|vfill)", " ", t)
    t = re.sub(r"\\underline\{\s*\{*\s*=\s*\}*\s*\}", "=", t)
    t = re.sub(r"\\(?:equiv|doteq|simeq|cong)\b", "=", t)
    t = t.replace(r"\equiv", "=").replace(r"\doteq", "=")

    # Normalize liIm typos from OCR before array parsing
    t = re.sub(r"\\(?:mathrm|operatorname\*?|mathbf)\{liIm\}", lambda m: r"\lim", t)
    t = re.sub(r"\bliIm\b", lambda m: r"\lim", t)
    t = t.replace(r"\operatorname*{lim}", r"\lim").replace(r"\operatorname{lim}", r"\lim")

    # Unwrap multi-row arrays (e.g. limit formula in row 1 and approach arrow in row 2)
    array_match = re.search(
        r"\\begin\{(?:array|matrix)\}(?:\{[^}]*\})?(.*?)\\end\{(?:array|matrix)\}",
        t,
        re.DOTALL,
    )
    if array_match:
        content = array_match.group(1).strip()
        rows = [r.strip() for r in re.split(r"\\\\|\\cr", content) if r.strip()]
        if len(rows) >= 2:
            arrow_match = None
            for r in rows[1:]:
                m_arrow = re.search(r"([a-zA-Z]\s*(?:\\rightarrow|\\to|->)\s*[\w\.\-]+)", r)
                if m_arrow:
                    arrow_raw = m_arrow.group(1)
                    arrow_clean = re.sub(r"\\rightarrow|->", r"\\to", arrow_raw).replace(" ", "")
                    arrow_match = arrow_clean
                    break

            row0_cells = [_unwrap_outer_braces(c) for c in rows[0].split("&")]
            row0_text = " ".join(row0_cells)
            row0_text = re.sub(r"\\(?:mathrm|operatorname\*?|mathbf)\{liIm\}", lambda m: r"\lim", row0_text)
            row0_text = re.sub(r"\bliIm\b", lambda m: r"\lim", row0_text)

            if arrow_match:
                if r"\lim" in row0_text:
                    row0_text = re.sub(
                        r"\\lim(?:_\{?[a-zA-Z0-9]*\}?)?",
                        lambda m: r"\lim_{" + arrow_match + r"}",
                        row0_text,
                    )
                else:
                    row0_text = r"\lim_{" + arrow_match + r"} " + row0_text
            t = row0_text
        elif len(rows) == 1:
            row0_cells = [_unwrap_outer_braces(c) for c in rows[0].split("&")]
            t = " ".join(row0_cells)

    # Normalize pipe or \mid or \vert right before a digit into 1 (e.g. |5 -> 15)
    t = re.sub(r"(?:\\mid|\\vert|\|)\s*(?=\d)", "1", t)
    # Strip leading label artifacts like \mathcal{Q}. or 2. or a. or (a) before a formula
    t = re.sub(
        r"^\s*(?:"
        r"\([a-zA-Z0-9\u1780-\u17a2]{1,2}\)[\.៖:]?"
        r"|(?:[\\/](?:tilde|bar|hat|mathcal|mathbf|mathrm|text)\{[^{}]*(?:\{[^{}]*\})*\}|[ក-អ]|[a-zA-Z]|[0-9]{1,2}|[\u17e0-\u17e9]{1,2})[\)\.៖:](?!\d)"
        r")\s*",
        "",
        t,
    )
    # Strip leading OCR bullet/symbol noise before math
    t = re.sub(
        r"^\s*(?:\\mathbf\{\\partial\}|\\partial|\\mid|\\cdot|\\circ|\\O(?:_\{\s*\\cdot\s*\}\^\{\s*\\circ\s*\}|_\{\\cdot\}|\^\{\\circ\})?|\\bullet|[\s;.,|:_~])+\s*",
        "",
        t,
    )
    # Normalize LaTeX spacing tokens like \; \, \! \: \quad \qquad \hfill \vfill
    t = re.sub(r"\\+([;,!:])", " ", t)
    t = re.sub(r"\\(?:quad|qquad|hfill|vfill)", " ", t)
    # Strip trailing LaTeX punctuation like ;, .
    t = re.sub(r"[\s;.,]+$", "", t)
    # Normalize delimiter sizings like \Biggr), \Bigg], \biggr} into standard brackets
    t = re.sub(r"\\(?:Bigg[lr]?|bigg[lr]?|Big[lr]?|big[lr]?)\s*([()[\]{}|])", r"\1", t)
    t = re.sub(r"\\(?:Bigg[lr]?|bigg[lr]?|Big[lr]?|big[lr]?)", "", t)
    # Normalize hallucinated gradient symbol to variable
    t = re.sub(r"\\mathbf\{\\nabla\}|\\nabla", "x", t)
    # Clean OCR noise dots (ddots, cdots, vdots)
    t = re.sub(r"\\(ddots|cdots|vdots)", "", t)
    t = re.sub(r"_\{[\s\.\!]*\}", "", t)
    t = re.sub(r"_[\.\!]", "", t)
    # Clean spaces inside trig functions from OCR (e.g. 's i n' or 'c o s' or 't a n')
    t = t.replace("s i n", r"\sin").replace("c o s", r"\cos").replace("t a n", r"\tan")
    # Normalize Greek letter chi to x when used as variable
    t = re.sub(r"\\chi\b", "x", t)
    # Remove rogue aleph, kappa, or noisy superscript artifacts from OCR
    t = re.sub(r"\^\{?\\(aleph|kappa)\}?", "^", t)
    # Clean escaped spaces like '\ 15' or '\ '
    t = re.sub(r"\\[\s]+", " ", t)
    # Normalize \times recognized as variable x (e.g. 12\times=25 -> 12x=25)
    t = re.sub(r"(?<=\d)\\times(?=[=+\-*/<>]|\s|$)", "x", t)
    # Normalize radical index OCR notations: {}^{3}\sqrt{...} or 3\sqrt{...} -> \sqrt[3]{...}
    t = re.sub(r"\{\}\^\{?(\d+)\}?\s*\\sqrt\s*\{", r"\\sqrt[\1]{", t)
    t = re.sub(r"(\\lim(?:_\{[^}]*\})?)\s*([2-9])\s*\{\s*\\sqrt\s*(\{.*?\})\s*\}", r"\1 \\sqrt[\2]\3", t)
    t = re.sub(r"(\\lim(?:_\{[^}]*\})?)\s*([2-9])\s*\\sqrt\s*\{", r"\1 \\sqrt[\2]{", t)
    if "lim_{" in t and r"\lim_{" not in t:
        t = t.replace("lim_{", r"\lim_{")
    # Unwrap redundant wrapper braces around \frac e.g. '{\frac{...}{...}}' -> '\frac{...}{...}'
    # Preserve braces if preceded by \sqrt or \sqrt[...] (where braces enclose the radicand)
    t = re.sub(r"(?<!\\sqrt)(?<!\\sqrt\[\d\])\{\s*(\\frac\{[^{}]*\}\{[^{}]*\})\s*\}", r"\1", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


class Pix2TexVisionEngine(MathVisionEngine):
    """
    Formula OCR using pix2tex (LaTeX-OCR).

    Pros:
    - Open-source, runs offline
    - Converts mathematical notation directly into LaTeX code
    - Excellent for fractions, integrals, limits, exponents, roots

    Cons:
    - Designed specifically for isolated math formulas, not prose or Khmer words
    """

    def __init__(self, model_instance: Any | None = None):
        self._model = model_instance

    @property
    def model(self) -> Any:
        """Lazy load model weights so app startup remains fast."""
        if self._model is None:
            from pix2tex.cli import LatexOCR

            self._model = LatexOCR()
        return self._model

    @staticmethod
    def _detect_label_gap(img: Image.Image) -> int | None:
        """
        Detect vertical blank gap in the left 35% of an image that separates
        an exercise label (e.g. 'ក.', '1.', '(a)') from the mathematical formula.
        """
        try:
            import numpy as np

            gray = np.array(img.convert("L"))
            h, w = gray.shape
            binary = gray < 200
            col_counts = np.sum(binary, axis=0)

            max_search_x = int(w * 0.45)
            gap_start = None
            for x in range(5, max_search_x):
                if col_counts[x] <= 1:
                    if gap_start is None:
                        gap_start = x
                else:
                    if gap_start is not None:
                        gap_len = x - gap_start
                        if gap_len >= 10:
                            ink_left = np.sum(col_counts[:gap_start])
                            if ink_left > 30:
                                return gap_start + gap_len // 2
                        gap_start = None
        except Exception:
            pass
        return None

    @staticmethod
    def _is_valid_prefix(txt: str | None) -> bool:
        """Check if extracted prefix is valid Khmer text or an exercise label."""
        if not txt:
            return False
        t = txt.strip()
        known_keywords = (
            "យើងមាន",
            "គេមាន",
            "គណនា",
            "រក",
            "ចូរ",
            "លំហាត់",
            "បង្ហាញថា",
            "ដោះស្រាយ",
            "សន្មត",
            "កំណត់",
            "អនុវត្ត",
        )
        if any(kw in t for kw in known_keywords):
            return True

        import re

        if re.match(
            r"^(\([a-zA-Z0-9\u1780-\u17a2]{1,2}\)|[a-zA-Z0-9\u1780-\u17a2]{1,2}[\.\)៖:])\s*$",
            t,
        ):
            return True
        return False

    @staticmethod
    def _extract_label(crop: Image.Image) -> str | None:
        """Extract label text from the isolated left margin using Tesseract."""
        try:
            from PIL import ImageOps
            import pytesseract

            padded = ImageOps.expand(crop, border=20, fill="white")
            for lang in ["khm", "eng"]:
                try:
                    txt = pytesseract.image_to_string(padded, lang=lang, config="--psm 6").strip()
                    if txt:
                        if txt.startswith("ក"):
                            return "ក."
                        return txt
                except Exception:
                    pass
        except Exception:
            pass
        return None

    @staticmethod
    def _detect_header_split(img: Image.Image) -> int | None:
        """
        Detect horizontal blank gap in the top 55% of an image that separates
        a header instruction (e.g. 'គណនាដេរីវេនៃអនុគមន៍ខាងក្រោម ៈ') from the mathematical formula below it.
        """
        try:
            import numpy as np

            gray = np.array(img.convert("L"))
            h, w = gray.shape
            binary = gray < 200
            row_counts = np.sum(binary, axis=1)

            max_search_y = int(h * 0.65)
            gap_start = None
            for y in range(15, max_search_y):
                if row_counts[y] <= 2:
                    if gap_start is None:
                        gap_start = y
                else:
                    if gap_start is not None:
                        gap_len = y - gap_start
                        if gap_len >= 12:
                            ink_above = np.sum(row_counts[:gap_start])
                            if ink_above > 40:
                                return gap_start + gap_len // 2
                        gap_start = None

            if gap_start is not None:
                gap_len = max_search_y - gap_start
                if gap_len >= 12 and np.sum(row_counts[:gap_start]) > 40:
                    return gap_start + gap_len // 2
        except Exception:
            pass
        return None

    @staticmethod
    def _extract_header_text(crop: Image.Image) -> str | None:
        """Extract header instruction text using Tesseract."""
        try:
            from PIL import ImageOps
            import pytesseract

            padded = ImageOps.expand(crop, border=20, fill="white")
            for lang in ["khm", "khm+eng"]:
                try:
                    txt = pytesseract.image_to_string(padded, lang=lang).strip()
                    if txt:
                        txt = " ".join(txt.split())
                        if any("\u1780" <= c <= "\u17ff" for c in txt):
                            return txt
                except Exception:
                    pass
        except Exception:
            pass
        return None

    def detect(self, image_bytes: bytes) -> VisionResult:
        if not image_bytes:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message="Image data is empty",
            )

        try:
            img = Image.open(BytesIO(image_bytes))
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)

            header_text = None
            header_y = self._detect_header_split(img)
            if header_y:
                header_crop = img.crop((0, 0, img.width, header_y))
                header_text = self._extract_header_text(header_crop)
                img = img.crop((0, header_y, img.width, img.height))

            split_x = self._detect_label_gap(img)
            label_text = None
            if split_x:
                raw_label = self._extract_label(img.crop((0, 0, split_x, img.height)))
                if self._is_valid_prefix(raw_label):
                    label_text = raw_label
                    f_crop = img.crop((split_x, 0, img.width, img.height))
                    if f_crop.height < 150:
                        scale = 1.2
                        f_crop = f_crop.resize(
                            (int(f_crop.width * scale), int(f_crop.height * scale)),
                            Image.Resampling.LANCZOS,
                        )
                    f_padded = ImageOps.expand(f_crop, border=(20, 20, 20, 20), fill="white")
                    raw_latex = self.model(f_padded)
                else:
                    f_padded = ImageOps.expand(img, border=(20, 20, 20, 20), fill="white")
                    raw_latex = self.model(f_padded)
            else:
                f_padded = ImageOps.expand(img, border=(20, 20, 20, 20), fill="white")
                raw_latex = self.model(f_padded)

            latex_code = clean_pix2tex_output(raw_latex)

            # If raw formula failed or has noise artifacts,
            # apply morphological noise reduction on thresholded image and re-run.
            should_denoise = (
                not latex_code
                or "\\vdots" in raw_latex
                or "\\ddots" in raw_latex
                or "\\mathrm{liIm}" in raw_latex
            )
            if should_denoise:
                try:
                    import cv2
                    import numpy as np

                    im = np.array(img.convert("RGB"))
                    gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
                    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    if np.mean(thresh == 255) < 0.5:
                        thresh = cv2.bitwise_not(thresh)
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                    cleaned_np = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
                    cleaned_img = Image.fromarray(cleaned_np)
                    denoised_raw = self.model(cleaned_img)
                    denoised_code = clean_pix2tex_output(denoised_raw)
                    if denoised_code and ("\\begin{array}" not in denoised_raw or not latex_code):
                        latex_code = denoised_code
                except Exception:
                    pass

            if label_text and latex_code and not latex_code.startswith(label_text):
                latex_code = f"{label_text} {latex_code}"

            if header_text and latex_code:
                latex_code = f"{header_text} {latex_code}"

            if not latex_code:
                return VisionResult(
                    detected_text=None,
                    confidence=0.0,
                    error_message="No formula detected by LaTeX-OCR",
                )

            from app.parser.exercise_parser.exercise_parser import parse_exercise

            parsed_ex = parse_exercise(latex_code)
            clean_expr = parsed_ex.primary_expression or latex_code

            return VisionResult(
                detected_text=latex_code,
                confidence=0.95,
                error_message=None,
                exercise_metadata={
                    "exercise_title": parsed_ex.exercise_title,
                    "instruction": parsed_ex.instruction,
                    "primary_expression": clean_expr,
                    "sub_exercises": [
                        {
                            "label": s.label,
                            "raw_text": s.raw_text,
                            "expression": s.expression,
                            "intent": s.intent,
                        }
                        for s in parsed_ex.sub_exercises
                    ],
                },
            )

        except Exception as e:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message=f"LaTeX-OCR (pix2tex) error: {str(e)}",
            )
