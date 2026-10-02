"""
Unified normalization pipeline combining all text preprocessing steps.

This module creates a single pipeline that processes text from raw input
(OCR or typed) through all normalization stages while tracking:
- What transformations were applied
- Confidence at each stage
- Warnings about ambiguous cases
"""

from __future__ import annotations

from functools import lru_cache

from app.core.khmer.digits import khmer_digits_to_arabic
from app.core.khmer.normalizer import convert_percentages_to_decimals, normalize_khmer_text
from app.ocr.normalization.ocr_postprocessor import sanitize_ocr_math_text
from app.models.problem import NormalizationResult, NormalizationStep


class NormalizationPipeline:
    """
    Unified pipeline for text normalization with tracking.

    Combines Khmer normalization and OCR postprocessing into a single
    pipeline with confidence tracking and transformation logging.
    """

    def __init__(
        self,
        apply_khmer_normalization: bool = True,
        apply_ocr_postprocessing: bool = True,
        apply_percentage_conversion: bool = True,
        track_transformations: bool = True,
    ):
        """
        Initialize normalization pipeline.

        Args:
            apply_khmer_normalization: Enable Khmer-specific processing
            apply_ocr_postprocessing: Enable OCR error correction
            apply_percentage_conversion: Convert percentages to decimals
            track_transformations: Log all transformations (slower but useful for debugging)
        """
        self.apply_khmer_normalization = apply_khmer_normalization
        self.apply_ocr_postprocessing = apply_ocr_postprocessing
        self.apply_percentage_conversion = apply_percentage_conversion
        self.track_transformations = track_transformations

    def normalize(
        self,
        text: str,
        is_from_ocr: bool = False,
    ) -> NormalizationResult:
        """
        Normalize text through the complete pipeline.

        Args:
            text: Raw input text
            is_from_ocr: Whether text came from OCR (affects confidence)

        Returns:
            NormalizationResult with normalized text and metadata
        """
        result = NormalizationResult(
            original_text=text,
            normalized_text=text,
            steps_applied=[],
            confidence=1.0,
        )

        # Start with lower confidence for OCR input
        if is_from_ocr:
            result.confidence = 0.9

        current_text = text

        # Stage 1: Khmer digit conversion
        if self.apply_khmer_normalization:
            before = current_text
            current_text = khmer_digits_to_arabic(current_text)
            if current_text != before:
                result.add_transformation(NormalizationStep.KHMER_DIGITS, before, current_text)

        # Stage 2: Khmer text normalization (punctuation, etc.)
        if self.apply_khmer_normalization:
            before = current_text
            current_text = normalize_khmer_text(current_text)
            if current_text != before:
                result.add_transformation(NormalizationStep.KHMER_PUNCTUATION, before, current_text)

        # Stage 3: Percentage conversion (before OCR processing)
        if self.apply_percentage_conversion and "%" in current_text:
            before = current_text
            try:
                current_text = convert_percentages_to_decimals(current_text)
                if current_text != before:
                    result.add_transformation(
                        NormalizationStep.PERCENTAGE_CONVERSION, before, current_text
                    )
            except Exception as e:
                result.add_warning(f"Percentage conversion failed: {e}")

        # Stage 4: OCR postprocessing (comprehensive math text cleaning)
        if self.apply_ocr_postprocessing:
            before = current_text
            try:
                current_text = sanitize_ocr_math_text(current_text)
                if current_text != before:
                    # This applies multiple transformations, so add a combined entry
                    result.add_transformation(
                        NormalizationStep.OCR_ERROR_CORRECTION, before, current_text
                    )
            except Exception as e:
                result.add_warning(f"OCR postprocessing failed: {e}")
                # Reduce confidence on failure
                result.confidence *= 0.8

        # Stage 5: Final cleanup
        before = current_text
        current_text = current_text.strip()
        if current_text != before:
            result.add_transformation(NormalizationStep.WHITESPACE_CLEANUP, before, current_text)

        # Validate result
        if not current_text:
            result.add_warning("Normalization resulted in empty text")
            result.confidence = 0.0

        # Check for common issues
        if len(current_text) < 2:
            result.add_warning("Normalized text is very short")

        # Detect if normalization changed text significantly
        if len(current_text) < len(text) * 0.5:
            result.add_warning("Normalization reduced text length by >50%")

        result.normalized_text = current_text
        return result

    def normalize_batch(
        self,
        texts: list[str],
        is_from_ocr: bool = False,
    ) -> list[NormalizationResult]:
        """
        Normalize multiple texts efficiently.

        Args:
            texts: List of raw input texts
            is_from_ocr: Whether texts came from OCR

        Returns:
            List of NormalizationResult objects
        """
        return [self.normalize(text, is_from_ocr) for text in texts]


# Singleton instance
_default_pipeline: NormalizationPipeline | None = None


@lru_cache(maxsize=4)
def create_normalization_pipeline(
    apply_khmer_normalization: bool = True,
    apply_ocr_postprocessing: bool = True,
    apply_percentage_conversion: bool = True,
) -> NormalizationPipeline:
    """
    Create a normalization pipeline with specified settings.

    Cached for performance - same settings return same instance.
    """
    return NormalizationPipeline(
        apply_khmer_normalization=apply_khmer_normalization,
        apply_ocr_postprocessing=apply_ocr_postprocessing,
        apply_percentage_conversion=apply_percentage_conversion,
    )


def get_default_pipeline() -> NormalizationPipeline:
    """Get the default normalization pipeline."""
    global _default_pipeline
    if _default_pipeline is None:
        _default_pipeline = NormalizationPipeline()
    return _default_pipeline


def normalize_text(
    text: str,
    is_from_ocr: bool = False,
) -> NormalizationResult:
    """
    Convenience function to normalize text with default pipeline.

    This is a simpler API for common use cases.

    Args:
        text: Raw input text
        is_from_ocr: Whether text came from OCR

    Returns:
        NormalizationResult with normalized text and metadata
    """
    pipeline = get_default_pipeline()
    return pipeline.normalize(text, is_from_ocr)


# Backward compatibility function
def normalize_for_math(text: str) -> str:
    """
    Backward compatible function that returns only normalized text.

    This matches the signature of existing normalize_khmer_text()
    for drop-in replacement.
    """
    result = normalize_text(text, is_from_ocr=False)
    return result.normalized_text
