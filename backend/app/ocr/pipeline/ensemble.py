"""
Multi-engine OCR ensemble with fallback and voting mechanisms.

Combines results from multiple OCR providers to improve accuracy and reliability.
Supports:
- Sequential fallback (try engines in order until success)
- Parallel voting (run multiple engines, select best result)
- Confidence-weighted selection
"""

from __future__ import annotations

from collections import Counter
from typing import Literal

from app.core.logging import get_logger
from app.ocr.engines.base import MathVisionEngine, VisionResult
from app.ocr.factory import create_vision_engine

logger = get_logger("app.ocr.extraction.ensemble")


class OCREnsemble:
    """
    Multi-engine OCR ensemble for improved accuracy through fallback and voting.

    Strategies:
    - 'fallback': Try engines sequentially until one succeeds
    - 'voting': Run all engines, select most common result
    - 'confidence': Run all engines, select highest confidence result
    - 'best_of_n': Run N engines, use voting among successful ones
    """

    def __init__(
        self,
        provider_names: list[str],
        strategy: Literal["fallback", "voting", "confidence", "best_of_n"] = "fallback",
        min_confidence: float = 0.5,
        timeout_seconds: float = 30.0,
    ):
        """
        Initialize OCR ensemble.

        Args:
            provider_names: List of OCR provider names (e.g., ["tesseract", "kiri", "gemini"])
            strategy: Ensemble strategy to use
            min_confidence: Minimum confidence threshold for accepting results
            timeout_seconds: Maximum time to wait for each engine
        """
        self.provider_names = provider_names
        self.strategy = strategy
        self.min_confidence = min_confidence
        self.timeout_seconds = timeout_seconds
        self.engines: list[MathVisionEngine] = []

        # Initialize engines
        for provider_name in provider_names:
            try:
                engine = create_vision_engine(provider_name)
                self.engines.append(engine)
                logger.info(f"Loaded OCR engine: {provider_name}")
            except Exception as e:
                logger.warning(f"Failed to load OCR engine {provider_name}: {e}")

    def detect(self, image_bytes: bytes) -> VisionResult:
        """
        Detect text using ensemble strategy.

        Args:
            image_bytes: Raw image bytes

        Returns:
            VisionResult with detected text and metadata
        """
        if not self.engines:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message="No OCR engines available in ensemble",
            )

        if self.strategy == "fallback":
            return self._fallback_detect(image_bytes)
        elif self.strategy == "voting":
            return self._voting_detect(image_bytes)
        elif self.strategy == "confidence":
            return self._confidence_detect(image_bytes)
        elif self.strategy == "best_of_n":
            return self._best_of_n_detect(image_bytes)
        else:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message=f"Unknown ensemble strategy: {self.strategy}",
            )

    def _fallback_detect(self, image_bytes: bytes) -> VisionResult:
        """
        Try engines sequentially until one succeeds.
        """
        last_error = None

        for i, engine in enumerate(self.engines):
            try:
                logger.debug(
                    f"Trying OCR engine {i + 1}/{len(self.engines)}: {self.provider_names[i]}"
                )
                result = engine.detect(image_bytes)

                # Check if result is successful
                if (
                    result.detected_text
                    and not result.error_message
                    and result.confidence >= self.min_confidence
                ):
                    logger.info(
                        f"OCR success with {self.provider_names[i]} "
                        f"(confidence: {result.confidence:.2f})"
                    )
                    return result

                last_error = result.error_message or "Low confidence"
                logger.debug(f"Engine {self.provider_names[i]} failed: {last_error}")

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Engine {self.provider_names[i]} raised exception: {e}")
                continue

        # All engines failed
        return VisionResult(
            detected_text=None,
            confidence=0.0,
            error_message=f"All OCR engines failed. Last error: {last_error}",
        )

    def _voting_detect(self, image_bytes: bytes) -> VisionResult:
        """
        Run all engines and select the most common result.
        """
        results: list[VisionResult] = []

        for i, engine in enumerate(self.engines):
            try:
                result = engine.detect(image_bytes)
                if result.detected_text and result.confidence >= self.min_confidence:
                    results.append(result)
                    logger.debug(
                        f"Engine {self.provider_names[i]}: '{result.detected_text}' "
                        f"(confidence: {result.confidence:.2f})"
                    )
            except Exception as e:
                logger.warning(f"Engine {self.provider_names[i]} failed: {e}")
                continue

        if not results:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message="No OCR engines produced valid results",
            )

        # Vote: find most common text
        text_votes = [r.detected_text for r in results if r.detected_text]

        if not text_votes:
            return results[0]  # Return first result if no valid text

        # Count votes
        vote_counter = Counter(text_votes)
        most_common_text, vote_count = vote_counter.most_common(1)[0]

        # Find result with most common text and highest confidence
        matching_results = [r for r in results if r.detected_text == most_common_text]
        best_result = max(matching_results, key=lambda r: r.confidence)

        # Boost confidence if multiple engines agree
        agreement_ratio = vote_count / len(text_votes)
        boosted_confidence = min(best_result.confidence * (1 + agreement_ratio * 0.2), 1.0)

        logger.info(
            f"Voting result: '{most_common_text}' "
            f"({vote_count}/{len(results)} engines agree, "
            f"confidence: {boosted_confidence:.2f})"
        )

        return VisionResult(
            detected_text=best_result.detected_text,
            confidence=boosted_confidence,
            error_message=None,
            exercise_metadata=best_result.exercise_metadata,
        )

    def _confidence_detect(self, image_bytes: bytes) -> VisionResult:
        """
        Run all engines and select the result with highest confidence.
        """
        results: list[VisionResult] = []

        for i, engine in enumerate(self.engines):
            try:
                result = engine.detect(image_bytes)
                if result.detected_text and result.confidence >= self.min_confidence:
                    results.append(result)
                    logger.debug(
                        f"Engine {self.provider_names[i]}: confidence {result.confidence:.2f}"
                    )
            except Exception as e:
                logger.warning(f"Engine {self.provider_names[i]} failed: {e}")
                continue

        if not results:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message="No OCR engines produced valid results",
            )

        # Select highest confidence result
        best_result = max(results, key=lambda r: r.confidence)

        logger.info(
            f"Best confidence result: '{best_result.detected_text}' "
            f"(confidence: {best_result.confidence:.2f})"
        )

        return best_result

    def _best_of_n_detect(self, image_bytes: bytes) -> VisionResult:
        """
        Run all engines, then use voting among successful ones.
        Combines confidence filtering with voting for robustness.
        """
        results: list[VisionResult] = []

        for i, engine in enumerate(self.engines):
            try:
                result = engine.detect(image_bytes)
                if result.detected_text and result.confidence >= self.min_confidence:
                    results.append(result)
            except Exception as e:
                logger.warning(f"Engine {self.provider_names[i]} failed: {e}")
                continue

        if not results:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message="No OCR engines produced valid results",
            )

        # If only one result, return it
        if len(results) == 1:
            return results[0]

        # Use voting among successful results
        text_votes = [r.detected_text for r in results if r.detected_text]
        vote_counter = Counter(text_votes)
        most_common_text, vote_count = vote_counter.most_common(1)[0]

        # Find best confidence among matching results
        matching_results = [r for r in results if r.detected_text == most_common_text]
        best_result = max(matching_results, key=lambda r: r.confidence)

        # Weighted confidence: base confidence + agreement bonus
        agreement_ratio = vote_count / len(results)
        final_confidence = min(best_result.confidence * 0.8 + agreement_ratio * 0.2, 1.0)

        logger.info(
            f"Best-of-{len(results)} result: '{most_common_text}' "
            f"(agreement: {vote_count}/{len(results)}, confidence: {final_confidence:.2f})"
        )

        return VisionResult(
            detected_text=best_result.detected_text,
            confidence=final_confidence,
            error_message=None,
            exercise_metadata=best_result.exercise_metadata,
        )


def create_ocr_ensemble(
    providers: list[str] | str | None = None,
    strategy: Literal["fallback", "voting", "confidence", "best_of_n"] = "fallback",
    min_confidence: float = 0.5,
) -> OCREnsemble:
    """
    Create an OCR ensemble from provider names.

    Args:
        providers: List of provider names, comma-separated string, or None for defaults
        strategy: Ensemble strategy
        min_confidence: Minimum confidence threshold

    Returns:
        Configured OCREnsemble

    Examples:
        >>> ensemble = create_ocr_ensemble(["kiri", "tesseract"], strategy="voting")
        >>> ensemble = create_ocr_ensemble("kiri,tesseract,gemini", strategy="confidence")
        >>> ensemble = create_ocr_ensemble()  # Uses default fallback: kiri -> tesseract
    """
    if providers is None:
        # Default: try Kiri first (native Khmer), fallback to Tesseract
        provider_list = ["kiri", "tesseract"]
    elif isinstance(providers, str):
        provider_list = [p.strip() for p in providers.split(",") if p.strip()]
    else:
        provider_list = providers

    return OCREnsemble(
        provider_names=provider_list,
        strategy=strategy,
        min_confidence=min_confidence,
    )
