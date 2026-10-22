"""
LaTeX-OCR (pix2tex) vision engine for mathematical formula recognition.

Uses Lukas Blecher's LaTeX-OCR (ViT + ResNet encoder-decoder) to transcribe
cropped images of mathematical equations directly into LaTeX code.
"""

from __future__ import annotations

from io import BytesIO
import re
from typing import Any

from PIL import Image

from app.ocr.engines.base import MathVisionEngine, VisionResult


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

    # Strip style switches
    t = re.sub(r"\\(?:textstyle|displaystyle)\s*", "", t)
    t = _unwrap_outer_braces(t)

    # Normalize tilde spaces, spacing commands and equivalence symbols
    t = t.replace("~", " ")
    t = t.replace("{(}", "(").replace("{)}", ")")
    t = t.replace("{[}", "[").replace("{]}", "]")
    t = re.sub(r"([+\-=])\{\s*(\\frac\{[^{}]*\}\{[^{}]*\})\s*\}", r"\1\2", t)
    t = re.sub(r"\\(?:quad|qquad|hfill|vfill)", " ", t)
    t = re.sub(r"\\underline\{\s*\{*\s*=\s*\}*\s*\}", "=", t)
    t = re.sub(r"\\(?:equiv|doteq|simeq|cong|sim)\b", "=", t)
    t = t.replace(r"\equiv", "=").replace(r"\doteq", "=").replace(r"\sim", "=")

    # Normalize common handwriting OCR artifact for \sqrt{x} after \lim or standalone
    t = re.sub(r"\bijD\b", r"\\sqrt{x}", t)

    # Normalize liIm typos from OCR before array parsing
    t = re.sub(r"\\(?:mathrm|operatorname\*?|mathbf)\{liIm\}", lambda m: r"\lim", t)
    t = t.replace(r"\operatorname*{lim}", r"\lim").replace(r"\operatorname{lim}", r"\lim")
    t = re.sub(r"\\(?:operatorname\*?|mathrm)\s*\{\s*[I1l]n\s*\}", r"\\ln", t)
    t = re.sub(r"\{[I1l]n\}", r"\\ln", t)
    t = re.sub(r"\b[I1]n\b", r"\\ln", t)

    # Unwrap multi-row arrays (e.g. limit formula in row 1 and approach arrow in row 2)
    array_match = re.search(
        r"\\begin\{(?:array|matrix)\}(?:\{[^}]*\})?(.*?)(?:\\end\{(?:array|matrix)\}|$)",
        t,
        re.DOTALL,
    )
    if array_match:
        prefix = t[:array_match.start()].strip()
        end_pos = array_match.end()
        suffix = t[end_pos:].strip() if "\\end{" in t[array_match.start():] else ""
        content = array_match.group(1).strip()

        # Check if array is hallucinated noise from non-math text:
        is_hallucinated = bool(re.search(r"\\(?:hat|vec|otimes|iiint|mathbb\{[A-Z]\}|mathfrak|stackrel|zeta)\b|Dillijj", content))
        if prefix and ("=" in prefix or "\\int" in prefix or "\\lim" in prefix or "y'" in prefix or "y^" in prefix) and is_hallucinated:
            # Check for interval in array content (e.g. \left(-1\,,1\right))
            m_int = re.search(r"([(\[])\s*([-+]?\d+)\s*(?:\\+,+|[,;])+\s*([-+]?\d+)\s*(?:\\right)?\s*([)\]])", content)
            if m_int:
                int_str = f"{m_int.group(1)}{m_int.group(2)}, {m_int.group(3)}{m_int.group(4)}"
                t = f"{prefix} , x \\in {int_str}"
            else:
                t = prefix
        else:
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
                inner = row0_text
            elif len(rows) == 1:
                row0_cells = [_unwrap_outer_braces(c) for c in rows[0].split("&")]
                inner = " ".join(row0_cells)
            else:
                inner = content

            parts = [p for p in [prefix, inner, suffix] if p]
            t = " ".join(parts)

    # Normalize pipe or \mid or \vert right before a digit into 1 (e.g. |5 -> 15)
    t = re.sub(r"(?:\\mid|\\vert|\|)\s*(?=\d)", "1", t)

    # Unwrap font switches (\mathbf, \mathrm, \mathit, \text, \boldsymbol, \bf, \rm)
    t = re.sub(r"([0-9a-zA-Z])\s*\\times\s*(?=\\mathrm\{[dD]\}|[dD]|\bI|\bk|\\mathbf\{[dDIk]\})", r"\g<1>x ", t)
    t = re.sub(r"\\(?:mathbf|mathrm|mathit|text|boldsymbol)\{([^{}]+)\}", r"\1", t)
    t = re.sub(r"\{\\(?:bf|rm)\s+([^{}]+)\}", r"\1", t)
    t = re.sub(r"\\(?:bf|rm)\s+([a-zA-Z0-9]+)", r"\1", t)
    t = re.sub(r"\\(?:bf|rm)\b", "", t)

    # Repair differential misrecognitions: \vert x, |x, Ix, kx, \mathrm{d}X, dX, \dim\times, \ln x -> dx
    t = re.sub(r"([0-9a-zA-Z])\s*\\times\s*(?=\\dim)", r"\g<1>x ", t)
    t = re.sub(r"\\dim\s*\\times\b", "dx", t)
    t = re.sub(r"\\dim\s*([xX])\b", r"d\1", t)
    t = re.sub(r"(\\int.*?(?:[0-9a-zA-Z\)\]\}]))\s*\\ln\s*([xX])\b", r"\1 d\2", t)
    t = re.sub(r"(?:\\vert|\|)\s*(?:\\(?:mathbf|mathrm|bf)\s*)?([xX])\b", r"d\1", t)
    t = re.sub(r"\b[Ik]\s*([xX])\b", r"d\1", t)
    t = re.sub(r"\b[dD]\s*([xX])\b", r"d\1", t)
    t = re.sub(r"\b[dD]\s*X\b", "dx", t)
    t = re.sub(r"\\mathrm\{[dD]\}\s*([xX])\b", r"d\1", t)
    t = re.sub(r"\\mathrm\{\s*d\s*\}", "d", t)

    # Normalize \times recognized as variable x
    t = re.sub(r"\\times(?=[\^_])", "x", t)
    t = re.sub(r"(\\int(?:_\{[^}]*\}\^\{[^}]*\}|_[0-9a-zA-Z]\^[0-9a-zA-Z])?\s*)\\times\b", r"\1x", t)
    t = re.sub(r"([(\[{])\s*\\times\b", r"\1x", t)
    t = re.sub(r"\\times\s*(?=\\mathrm\{[dD]\}|[dD]|\bI|\bk|\\dim|\b[dD][xyzut])", "x ", t)

    # Hallucinated integral symbol when OCR misreads label + bounds:
    # e.g. {\tilde{\mathbb{N}}}_{0}^{2}, \Phi_{0}^{2}, \Phi_{0}|_{0}^{2}, \mathbf{\hat{n}}_{n}^{2}, \mathfrak{A}_{1}^{2}
    t = re.sub(r"^\\Phi_{0}\|(?=_{)", "", t)
    t = re.sub(
        r"^(?:\{?\\(?:tilde|hat|bar)\{\\(?:mathbb|mathbf|mathrm)\{[A-Z]\}\}\}?|\\(?:Phi|Psi|Omega|Theta|Xi|Gamma)|\\mathbf\{\\hat\{[a-z]\}\}|{\\mathfrak\{[A-Za-z]\}}|[A-Za-z])_\{?([0-9a-zA-Z])\}?\^\{?([0-9a-zA-Z])\}?(?=.*(?:\\mathrm\{d\}|d[xyzut]|\b[Ik]x))",
        lambda m: rf"\int_{{{m.group(1)}}}^{{{m.group(2)}}}",
        t,
    )
    # Fix lower bound OCR typos: n, a, o, O -> 0 when upper bound is a positive digit
    t = re.sub(r"(\\int_)\{?[naoO]\}?(\^\{?[1-9]\}?)", r"\g<1>{0}\2", t)

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
        r"^\s*(?:\\mathbf\{\\partial\}|\\partial|\\mid|\\cdot|\\circ|\\O(?![a-zA-Z])(?:_\{\s*\\cdot\s*\}\^\{\s*\\circ\s*\}|_\{\\cdot\}|\^\{\\circ\})?|\\bullet|[\s;.,|:_~])+\s*",
        "",
        t,
    )
    # Normalize LaTeX spacing tokens like \; \, \! \: \quad \qquad \hfill \vfill
    t = re.sub(r"\\+([;,!:])", " ", t)
    t = re.sub(r"\\(?:quad|qquad|hfill|vfill)", " ", t)
    # Normalize derivative primes misread as asterisks or exponents (e.g. y^* r -> y'', {y}^{\prime +} -> y'' + y, y^{r} -> y'')
    t = re.sub(r"(?<=[0-9a-zA-Z])\s*\\(?:beta|theta)\s*,?", ", ", t)
    t = re.sub(r"\\beta\s*,?", ", ", t)
    def _fix_second_deriv_term(m):
        g1 = m.group(1)
        g2 = m.group(2)
        return f"{g1}'' + {g2}" if g2 else f"{g1}''"
    t = re.sub(r"\{?([yY])\}?\s*\^\s*\{?\s*(?:\\prime\s*\\prime|\\prime\s*[*r]|[*r]\s*\\prime|\'\s*\'|\*\s*\*|\\prime\s*\,?\s*\\dagger|\\prime\s*\,?\s*\+)\s*\}?\s*(?:\\mp|\+|\s*x\s*)?\s*\{?([yY])\}?", _fix_second_deriv_term, t)
    t = re.sub(r"=\s*\{\s*\\?\s*([0-9a-zA-Z]+)\s*\}", r"= \1", t)
    t = re.sub(r"([yY])\^\{?\s*(?:\\prime\s*[*r]|[*r]\s*\\prime)\s*\}?", r"\1''", t)
    t = re.sub(r"([yY])\^\{?r\}?\s*(?=\()", r"\1'", t)
    t = re.sub(r"([yY])\^\{?r\}?", r"\1''", t)
    t = re.sub(r"([yY])\^\{?\*\}?\s*r\b", r"\1''", t)
    t = re.sub(r"([yY])\^\{?\*\}?", r"\1'", t)
    t = re.sub(r"\{?([yY])\}?\s*\^\s*\{?\\(?:dagger|dag)\s*([+\-])\s*([0-9a-zA-Z]+)\s*\}?", r"\1' \2 \3", t)
    t = re.sub(r"\{?([yY])\}?\s*\^\s*\{?\\(?:dagger|dag)\}?", r"\1'", t)
    # Fix slashed zero 0 misread as \theta in initial conditions: y(\theta) -> y(0), y'(\theta) -> y'(0)
    t = re.sub(r"([yY](?:\'|\^\{?\\prime\}?)?\s*\()\s*\\theta\s*(\))", r"\g<1>0\2", t)

    # Fix rogue degree symbol / prime confusion in initial conditions or derivatives: y^{\circ} -> y', 0^{\circ} -> 0
    t = re.sub(r"([yY])\^\{?\\circ\}?", r"\1'", t)
    t = re.sub(r"\{\s*\{?0\}?\^\{?\\circ\}?\s*\}|0\^\{?\\circ\}?", "0", t)

    # Fix OCR parentheses misread as equals in initial conditions: y=0=-2 -> y(0)=-2, y=0)=-2 -> y(0)=-2, y0)=-2 -> y(0)=-2
    t = re.sub(r"([,;]\s*\{?[yY]\}?)\s*[=(]\s*(\d+)\s*[\)]?\s*=\s*([-+]?\d+)", r"\1(\2) = \3", t)
    t = re.sub(r"([,;]\s*\{?[yY]\}?)\s*(\d+)\)\s*=\s*([-+]?\d+)", r"\1(\2) = \3", t)

    # Normalize operatorname or font commands wrapping variables: \operatorname{y} -> y, \mathrm{y} -> y
    t = re.sub(r"\\(?:mathrm|operatorname\*?|mathbf)\s*\{\s*([a-zA-Z])\s*\}", r"\1", t)
    t = re.sub(r"\\operatorname\*?\s*", "", t)

    # Insert missing comma before initial condition y: e.g. = 3 y'(0) -> = 3, y'(0)
    t = re.sub(r"(?<=\d|\))\s+(?=[yY](?:'|\^\{?\\prime\}?|\())", ", ", t)

    # Normalize duplicate prime in initial conditions (e.g. , y'(0)=1 , y'(0)=3 -> , y(0)=1 , y'(0)=3)
    t = re.sub(r"([,;]\s*\{?y\}?)'(?=\s*(?:\\left)?\s*\(.*?\)\s*=\s*[^,;]+[,;]\s*\{?y\}?['’])", r"\1", t)
    # Normalize double prime in initial condition (e.g. , y''(0)=3 -> , y'(0)=3)
    t = re.sub(r"([,;]\s*\{?y\}?)(?:''|\^\{\\prime\s*\\prime\}?)(?=\s*(?:\\left)?\s*\()", r"\1'", t)

    # Fix accidental duplicate prime in 1st order linear ODE: ay' + by' = 0 -> ay' + by = 0
    t = re.sub(r"([0-9a-zA-Z\\]*y(?:\'|\^\{?\\prime\}?))(\s*[-+]\s*[0-9a-zA-Z\\]*y)(?:\'|\^\{?\\prime\}?)(?=\s*=)", r"\1\2", t)

    # Auto-close trailing unclosed square root brace (e.g. \sqrt{2 -> \sqrt{2})
    t = re.sub(r"(\\sqrt\{[0-9a-zA-Z]+)$", r"\1}", t)

    # Strip trailing punctuation, Khmer full stops (ฯ), and OCR noise letters like dangling 'i', 'v', 'I', \vdash after formula
    t = re.sub(r"(?<=\d|\)|\})\s*[\s,;.]*(?:\\vdash|\\uparrow|[iIvV|\\~ฯ])+$", "", t)
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
    # Strip style switches (textstyle, displaystyle, boldmath)
    t = re.sub(r"\\(?:textstyle|displaystyle|boldmath)\s*", "", t)
    # Strip leading bullets or punctuation before math
    t = re.sub(r"^(?:\\cdot|\\bullet|\\mid|\||\s)+", "", t)
    # Fix missing variable in limit arrow: \lim_{\to 0} -> \lim_{x\to 0}, \lim_{\rightarrow 0} -> \lim_{x\to 0}
    t = re.sub(r"(\\lim_\{?)\s*\\(?:rightarrow|to|->)\s*", r"\g<1>x\\to ", t)

    # Collapse duplicate adjacent \lim expressions: e.g. \lim_{x\to+\infty} \lim_{...} -> \lim_{x\to+\infty}
    t = re.sub(r"(\\lim(?:_\{[^}]*\})?)\s*\\lim(?:_\{[^}]*\})?", r"\1", t)

    # Normalize Omega or mega before subscript approach arrow to \lim: \Omega_{x\to...} -> \lim_{x\to...}
    t = re.sub(r"(?:\\cdot\s*)?(?:\\mathbf\{\\Omega\}|\\Omega)_(?=\{?[a-zA-Z]\s*(?:\\to|\\rightarrow|->))", r"\\lim_", t)
    t = re.sub(r"\bmega_(?=\{?[a-zA-Z]\s*(?:\\to|\\rightarrow|->))", r"\\lim_", t)

    # Strip hallucinated non-math symbol clusters preceding \lim or \int (e.g. \widehat{r}\Omega... \lim_{x\to 2})
    m_op = re.search(r"\\(?:operatorname\*?\s*\{?\\?lim\}?|\\mathrm\s*\{?\\?lim\}?|lim)(?=[^a-zA-Z]|$)|\\int\b", t)
    if m_op and m_op.start() > 0:
        head = t[:m_op.start()].strip()
        m_lbl = re.search(r"(\([0-9a-zA-Z\u1780-\u17a2]{1,2}\)|(?:\b|^)[0-9a-zA-Z\u1780-\u17a2]{1,2}[\.\)៖:។])", head)
        if m_lbl:
            t = f"{m_lbl.group(1)} {t[m_op.start():].strip()}"
        elif not any(eq in head for eq in ["=", "<", ">", "\\le", "\\ge"]):
            t = t[m_op.start():].strip()

    # Fix \ln(\lim x) -> \ln(\ln x), \lim x -> x
    t = re.sub(r"(\\ln\s*\(\s*)\\lim\s*x\b", r"\g<1>\\ln x", t)
    t = re.sub(r"\\lim\s*x\b", "x", t)

    # Normalize un-backslashed or operatorname trig and log functions: {tan} -> \tan, {sin} -> \sin, \operatorname{tan} -> \tan
    t = re.sub(r"\{?\b(sin|cos|tan|cot|arcsin|arccos|arctan|ln|log|exp)\b\}?", r"\\\1 ", t)
    t = re.sub(r"\\(?:operatorname\*?|mathrm)\s*\{\s*(sin|cos|tan|cot|arcsin|arccos|arctan|ln|log|exp)\s*\}", r"\\\1", t)
    t = re.sub(r"\\+(sin|cos|tan|cot|arcsin|arccos|arctan|ln|log|exp)\b", r"\\\1", t)
    t = re.sub(r"\\ln([a-zA-Z])", r"\\ln \1", t)

    # Normalize OCR misreadings of parameter 'b' as \mathcal{D} or \partial in algebraic limits like x(a - \mathcal{D})
    t = re.sub(r"(?<=[a-zA-Z\s\-+,])\\(?:mathcal\{D\}|partial)(?=[a-zA-Z0-9\s\-+,)\}]|\\(?:neq|ne|le|ge|=|<|>)|$)", "b", t)
    t = re.sub(r"\\neq\s*([a-zA-Z0-9])", r"\\neq \1", t)
    # Fix uppercase A before - \d+ x in limit polynomial -> 4 (e.g. A - 3x - x^2 -> 4 - 3x - x^2)
    t = re.sub(r"(?<=[(\[])\s*A\s*(?=[-]\s*\d+\s*[a-zA-Z])", "4", t)
    # Normalize OCR confusion of digit 6 as Greek \delta or \sigma in trig arguments (e.g. \cos \delta x -> \cos 6x)
    t = re.sub(r"\\(cos|sin|tan)\s*\\(?:delta|sigma)(?![a-zA-Z])\s*([a-zA-Z0-9\(])", r"\\\1 6\2", t)

    # Normalize unbalanced floor/ceiling brackets to standard brackets
    if r"\rfloor" in t and r"\lfloor" not in t:
        t = t.replace(r"\rfloor", "]")
    if r"\rceil" in t and r"\lceil" not in t:
        t = t.replace(r"\rceil", "]")
    if r"\lfloor" in t and r"\rfloor" not in t:
        t = t.replace(r"\lfloor", "[")

    # Clean LaTeX spacing tokens like \; \, \! \: \quad and escaped spaces '\ ' before trailing noise cleanup
    t = re.sub(r"\\[;,!:]", " ", t)
    t = re.sub(r"\\[\s]+", " ", t)

    # Strip trailing overset annotations like {\overset{\textrm{t a}}{x}}
    t = re.sub(r"\{?\s*\\overset\b.*$", "", t)

    # Strip trailing text/font commands (e.g. \mathrm{{\scriptsize eqprit}})
    t = re.sub(r"\s*\\(?:mathrm|text|mathit|mathbf|textbf|scriptsize|footnotesize|tiny)\b.*$", "", t)

    # Strip trailing OCR noise annotations (e.g. \cdot, ^{\infty}, \stackrel..., \vdash, \uparrow, speckles)
    t = re.sub(r"\s*(?:\\leftarrow|\\rightarrow|\\leftrightarrow|\\stackrel\{[^{}]*\}\{[^{}]*\}|\\stackrel\{[^{}]*\}|[a-zA-Z]_\{?1\}?|\bc_1\b|\{*\}_\{?1\}?)\s*$", "", t)
    t = re.sub(r"(?<=[0-9a-zA-Z\)\]\}])\s*(?:\^\{?\\infty\}?|\\cdot|\\bullet|\\vdash|\\uparrow|\\downarrow|[iIvV|\\~ฯ.,;])+\s*$", "", t)
    t = re.sub(r"[\s\\]*(?:\\cdot|\\bullet|[.។,;])+\s*$", "", t)

    # Clean spaces inside trig functions from OCR (e.g. 's i n' or 'c o s' or 't a n')
    t = t.replace("s i n", r"\sin").replace("c o s", r"\cos").replace("t a n", r"\tan")
    # Normalize Greek letter chi to x when used as variable
    t = re.sub(r"\\chi\b", "x", t)
    # Remove rogue aleph, kappa, or noisy superscript artifacts from OCR
    t = re.sub(r"\^\{?\\(aleph|kappa)\}?", "^", t)
    # Normalize \times recognized as variable x (e.g. 12\times=25 -> 12x=25)
    t = re.sub(r"(?<=\d)\\times(?=[=+\-*/<>]|\s|$)", "x", t)
    # Normalize radical index OCR notations: {}^{3}\sqrt{...} or 3\sqrt{...} -> \sqrt[3]{...}
    t = t.replace(r"{}\bar{\Lambda}", r"\sqrt").replace(r"\bar{\Lambda}", r"\sqrt")
    t = t.replace(r"{}\bar{\Delta}", r"\sqrt").replace(r"\bar{\Delta}", r"\sqrt")
    t = re.sub(r"\{\}\^\{?(\d+)\}?\s*\\sqrt\s*\{", r"\\sqrt[\1]{", t)
    t = re.sub(r"(\\lim(?:_\{[^}]*\})?)\s*([2-9])\s*\{\s*\\sqrt\s*(\{.*?\})\s*\}", r"\1 \\sqrt[\2]\3", t)
    t = re.sub(r"(\\lim(?:_\{[^}]*\})?)\s*([2-9])\s*\\sqrt\s*\{", r"\1 \\sqrt[\2]{", t)
    if "lim_{" in t and r"\lim_{" not in t:
        t = t.replace("lim_{", r"\lim_{")

    # Normalize handwriting OCR artifacts (e.g. kappa/chi to x, \mathcal{X} to x, \vert\kappax to \ln x)
    t = re.sub(r"(\\lim_\{?)\\(?:kappa|chi)\b", r"\g<1>x", t)
    t = re.sub(r"\\mathcal\{[xX]\}", "x", t)
    t = re.sub(r"_\{\s*-\s*\}|_-\b", " - ", t)
    t = re.sub(r"(?<=[=+\-*/\s])\\vert(?=[=+\-*/\s]|$)", "1", t)
    t = t.replace(r"\vert\kappax", r"\ln x").replace(r"\mp", "x")
    t = re.sub(r"\\(?:vert|mid|\|)\s*(?:\\(?:kappa|chi)\s*)?x(?=[\s\)/]|$)", r"\\ln x", t)
    # Unwrap redundant wrapper braces around \frac e.g. '{\frac{...}{...}}' -> '\frac{...}{...}'
    # Preserve braces if preceded by \sqrt or \sqrt[...] (where braces enclose the radicand)
    t = re.sub(r"(?<!\\sqrt)(?<!\\sqrt\[\d\])\{\s*(\\frac\{[^{}]*\}\{[^{}]*\})\s*\}", r"\1", t)

    # Strip trailing noise after differential at end of expression (e.g. ~v, \Psi, \{)
    t = re.sub(r"(d[xyzut])\s*[^0-9a-zA-Z+\-*/=^()\[\]{}]+.*$", r"\1", t)
    while t.startswith("{") and t.count("{") > t.count("}"):
        t = t[1:].strip()
    while t.endswith("}") and t.count("}") > t.count("{"):
        t = t[:-1].strip()
    while t.endswith("{") and t.count("{") > t.count("}"):
        t = t[:-1].strip()
    while t.count(r"\}") > t.count(r"\{"):
        idx = t.rfind(r"\}")
        t = t[:idx] + t[idx + 2 :]
    while t.endswith(("{", "\\", "|", "~")) or (t.endswith("}") and t.count("}") > t.count("{")):
        t = t[:-1].strip()
    t = _unwrap_outer_braces(t)
    t = re.sub(r"(?<=[0-9a-zA-Z\)\]\}])\s*(d[xyzut]\b)", r" \1", t)

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

    def __init__(self, model_instance: Any | None = None, weights_path: str | Any | None = None):
        import os
        from pathlib import Path

        self._model = model_instance
        self.weights_path = weights_path or os.getenv("PIX2TEX_WEIGHTS_PATH")
        if self.weights_path is None:
            candidate = (
                Path(__file__).resolve().parent.parent.parent.parent
                / "training"
                / "pix2tex"
                / "models"
                / "weights.pth"
            )
            if candidate.exists():
                self.weights_path = str(candidate)

    @property
    def model(self) -> Any:
        """Lazy load model weights so app startup remains fast."""
        if self._model is None:
            from pathlib import Path
            from munch import Munch
            from pix2tex.cli import LatexOCR

            if self.weights_path and Path(self.weights_path).exists():
                args = Munch({
                    "config": "settings/config.yaml",
                    "checkpoint": str(self.weights_path),
                    "no_cuda": True,
                    "no_resize": False,
                    "pad": True,
                })
                self._model = LatexOCR(arguments=args)
            else:
                self._model = LatexOCR()
            if hasattr(self._model, "args"):
                self._model.args.temperature = 0.00001
        return self._model

    @staticmethod
    def _detect_label_gap(img: Image.Image) -> int | None:
        """
        Detect vertical blank gap in the left 45% of an image that separates
        an exercise label (e.g. 'ក.', '1.', '(a)', 'គ.') from the mathematical formula.
        Uses connected components analysis and column ink profiles for robust splitting.
        """
        try:
            import cv2
            import numpy as np

            gray = np.array(img.convert("L"))
            h, w = gray.shape
            binary = ((gray < 200) * 255).astype(np.uint8)
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary)
            comps = []
            for i in range(1, num_labels):
                x, y, cw, ch, area = stats[i]
                if area > 8:
                    comps.append((x, y, cw, ch, area))
            if not comps:
                return None
            comps.sort(key=lambda c: c[0])

            # Filter comps for candidate label c0: must be a substantive stroke, not tiny dust
            valid_label_comps = [c for c in comps if c[4] >= 20 and c[3] >= 10]
            if not valid_label_comps:
                return None
            c0 = valid_label_comps[0]
            if c0[0] > w * 0.45:
                return None

            # If c0 is very tall relative to image height (e.g. integral spanning top to bottom),
            # it is not an exercise label
            if c0[3] > h * 0.55 and c0[2] < 20:
                return None

            # Check for Label + Dot: e.g. 'ក.', 'គ.', '1.'
            if len(comps) >= 2:
                for dot_idx in range(1, min(4, len(comps))):
                    dot = comps[dot_idx]
                    # Dot is small (width <= 14, height <= 14, area <= 80)
                    # and lies reasonably close to the label component (within 25px)
                    if (
                        dot[0] > c0[0]
                        and dot[0] <= c0[0] + c0[2] + 25
                        and dot[2] <= 14
                        and dot[3] <= 14
                        and dot[4] <= 80
                        and (dot[1] + dot[3] >= c0[1] + c0[3] * 0.6)
                    ):
                        # Found label dot! Look for start of math expression after dot
                        math_start = None
                        for m_idx in range(dot_idx + 1, len(comps)):
                            if comps[m_idx][0] > dot[0] + dot[2]:
                                math_start = comps[m_idx][0]
                                break
                        if math_start is not None and math_start > dot[0] + dot[2]:
                            split_x = dot[0] + dot[2] + (math_start - (dot[0] + dot[2])) // 2
                            return int(split_x)
                        elif dot[0] + dot[2] < w * 0.5:
                            return int(dot[0] + dot[2] + 2)

            # Fallback 1: check for distinct gap >= 28px after a compact left component
            if len(comps) >= 2:
                c1 = comps[1]
                gap = c1[0] - (c0[0] + c0[2])
                if gap >= 28 and c0[2] <= 45 and c0[3] <= h * 0.6:
                    return int(c0[0] + c0[2] + gap // 2)

            # Fallback 2: Column projection
            col_counts = np.sum(binary > 0, axis=0)
            ink_cols = np.where(col_counts > 1)[0]
            if len(ink_cols) > 0:
                first_x = ink_cols[0]
                max_search = min(first_x + 90, int(w * 0.45))
                for x in range(first_x + 18, max_search):
                    if col_counts[x] <= 1 and np.max(col_counts[x : min(x + 15, w)]) >= 15:
                        ink_left = np.sum(col_counts[first_x:x])
                        if 30 <= ink_left <= 1500:
                            return int(x)
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
            r"^(\([a-zA-Z0-9\u1780-\u17a2]{1,2}\)|[a-zA-Z0-9\u1780-\u17a2]{1,2}[\.\)៖:។])\s*$",
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
                        clean_txt = txt.strip()
                        if clean_txt.startswith("ក"):
                            return "ក."
                        return clean_txt
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
            eval_img = img
            if split_x:
                raw_label = self._extract_label(img.crop((0, 0, split_x, img.height)))
                if self._is_valid_prefix(raw_label):
                    label_text = raw_label
                    f_crop = img.crop((split_x, 0, img.width, img.height))
                    raw_latex = self.model(f_crop)
                    eval_img = f_crop
                else:
                    raw_latex = self.model(img)
            else:
                raw_latex = self.model(img)

            latex_code = clean_pix2tex_output(raw_latex)

            # If formula failed, has noise artifacts in cleaned code, or small image with missing operator, retry
            has_valid_op = bool(re.search(r"\\lim|\\int|\\sum|=", latex_code))
            noise_in_code = bool(re.search(r"\\(?:uparrow|downarrow|vdots|sim|dot\{1\}|mathbf\{\\Omega\})|ijD", latex_code))
            has_noise = (
                not latex_code
                or noise_in_code
                or (not has_valid_op and eval_img.height < 155)
            )
            if has_noise:
                # Retry 1: Multi-scale ladder for small crops (scales 1.8, 2.2, 2.5)
                if eval_img.height < 170:
                    for scale in [1.8, 2.2, 2.5]:
                        try:
                            scaled_w = int(eval_img.width * scale)
                            scaled_h = int(eval_img.height * scale)
                            scaled_img = eval_img.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
                            scaled_raw = self.model(scaled_img)
                            scaled_code = clean_pix2tex_output(scaled_raw)
                            scaled_has_op = bool(re.search(r"\\lim|\\int|\\sum|=", scaled_code))
                            scaled_has_noise = bool(re.search(r"\\(?:uparrow|downarrow|dot\{1\}|verti)", scaled_raw))
                            if scaled_code and (scaled_has_op or not has_valid_op) and not scaled_has_noise:
                                latex_code = scaled_code
                                has_valid_op = scaled_has_op
                                if has_valid_op:
                                    break
                        except Exception:
                            pass

                # Retry 2: Morphological thresholding
                if not has_valid_op or "\\uparrow" in latex_code or "\\downarrow" in latex_code:
                    try:
                        import cv2
                        import numpy as np

                        im = np.array(eval_img.convert("RGB"))
                        gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
                        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                        if np.mean(thresh == 255) < 0.5:
                            thresh = cv2.bitwise_not(thresh)
                        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                        cleaned_np = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
                        cleaned_img = Image.fromarray(cleaned_np)
                        denoised_raw = self.model(cleaned_img)
                        denoised_code = clean_pix2tex_output(denoised_raw)
                        denoised_has_op = bool(re.search(r"\\lim|\\int|\\sum|=", denoised_code))
                        denoised_has_noise = bool(re.search(r"\\(?:uparrow|downarrow|dot\{1\})", denoised_raw))
                        if denoised_code and (denoised_has_op or not has_valid_op) and not denoised_has_noise:
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

            from app.ocr.normalization.condition_extractor import extract_condition_and_math
            from app.parser.exercise_parser.exercise_parser import parse_exercise

            formula_only, ext_cond = extract_condition_and_math(latex_code)
            parsed_ex = parse_exercise(formula_only or latex_code)
            clean_expr = parsed_ex.primary_expression or formula_only or latex_code

            cond_dict = (
                {
                    "raw_condition": ext_cond.raw_condition,
                    "condition_type": ext_cond.condition_type,
                    "normalized_condition": ext_cond.normalized_condition,
                    "interval": ext_cond.interval,
                }
                if ext_cond
                else None
            )

            # Check if Tesseract finds Khmer condition (e.g. កំណត់លើ (-1, 1))
            if not cond_dict:
                try:
                    import pytesseract
                    tess_text = pytesseract.image_to_string(img, lang="eng+khm").strip()
                    _, tess_cond = extract_condition_and_math(tess_text)
                    if tess_cond:
                        cond_dict = {
                            "raw_condition": tess_cond.raw_condition,
                            "condition_type": tess_cond.condition_type,
                            "normalized_condition": tess_cond.normalized_condition,
                            "interval": tess_cond.interval,
                        }
                except Exception:
                    pass

            return VisionResult(
                detected_text=latex_code,
                confidence=0.95,
                error_message=None,
                exercise_metadata={
                    "exercise_title": parsed_ex.exercise_title,
                    "instruction": parsed_ex.instruction,
                    "primary_expression": clean_expr,
                    "condition": cond_dict,
                    "detected_intent": parsed_ex.detected_intent,
                    "sub_exercises": [
                        {
                            "label": s.label,
                            "raw_text": s.raw_text,
                            "expression": s.expression,
                            "intent": s.intent,
                            "condition": s.condition,
                            "condition_type": s.condition_type,
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
