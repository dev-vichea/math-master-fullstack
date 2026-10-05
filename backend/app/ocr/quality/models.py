"""
Data models for the Math OCR Quality Pipeline.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class CandidateStatus(str, Enum):
    """Explicit verification status for math OCR candidates."""
    VERIFIED = "VERIFIED"          # Valid math syntax, passes parser, high confidence, no suspicious tokens
    NEEDS_REVIEW = "NEEDS_REVIEW"  # Suspicious prefix/suffix, low confidence, or unusual structure
    INVALID = "INVALID"            # Unparseable garbage, unbalanced delimiters, or empty


class MathOcrCandidate(BaseModel):
    """A single candidate output from an OCR provider + preprocessing variant."""
    raw_ocr_text: str = Field(..., description="Raw string returned by the OCR engine")
    normalized_math_text: str = Field(..., description="Deterministically normalized math expression")
    status: CandidateStatus = Field(default=CandidateStatus.NEEDS_REVIEW, description="Validation status")
    confidence: float = Field(default=0.0, description="Confidence score [0.0 - 1.0]")
    source_provider: str = Field(default="pix2tex", description="Name of OCR provider")
    variant_name: str = Field(default="original", description="Preprocessing variant name")
    score: float = Field(default=0.0, description="Overall ranking score")
    bounding_box: tuple[int, int, int, int] | None = Field(default=None, description="(x, y, w, h) of ink region")
    suspicious_tokens: list[str] = Field(default_factory=list, description="Suspicious or stripped tokens (e.g. '1964,')")
    validation_issues: list[str] = Field(default_factory=list, description="Any detected structural or syntax warnings")
    detected_prefix: str | None = Field(default=None, description="Extracted non-math prefix (e.g. '1964,')")
    detected_suffix: str | None = Field(default=None, description="Extracted non-math suffix")
    is_parseable: bool = Field(default=False, description="Whether SymPy can successfully parse the expression")
    problem_type: str | None = Field(default=None, description="Detected math classification if parseable")


class OcrPipelineResult(BaseModel):
    """Complete result from running the OCR Quality Pipeline."""
    selected_candidate: MathOcrCandidate = Field(..., description="The highest-ranking candidate")
    all_candidates: list[MathOcrCandidate] = Field(default_factory=list, description="All evaluated candidates")
    original_raw_text: str = Field(default="", description="Original raw text of best candidate")
    status: CandidateStatus = Field(..., description="Final pipeline status (from selected candidate)")
    confidence: float = Field(default=0.0, description="Confidence score of selected candidate")
    debug_trace: list[dict[str, Any]] = Field(default_factory=list, description="Structured debug logging trace")
