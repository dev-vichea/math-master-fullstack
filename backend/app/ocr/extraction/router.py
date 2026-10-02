"""
Intelligent OCR routing based on image analysis and content detection.

Analyzes image characteristics to automatically select the best OCR engine:
- Detects Khmer script presence → routes to Kiri OCR or Gemini
- Detects complex math notation → routes to Mathpix or Gemini
- Detects handwriting vs. print → routes to appropriate engine
- Detects image quality issues → applies preprocessing
"""

from __future__ import annotations

import io
from typing import Any, Literal

import cv2
import numpy as np
from PIL import Image

from app.core.logging import get_logger
from app.ocr.extraction.base import MathVisionEngine, VisionResult
from app.ocr.extraction.factory import create_vision_engine

logger = get_logger("app.ocr.extraction.router")


class ImageAnalyzer:
    """Analyzes image characteristics for intelligent OCR routing."""

    @staticmethod
    def analyze(image_bytes: bytes) -> dict[str, Any]:
        """
        Analyze image to determine optimal OCR strategy.

        Returns dict with:
        - has_khmer_script: bool (presence of Khmer characters)
        - has_complex_math: bool (fractions, radicals, matrices)
        - is_handwritten: bool (vs. printed text)
        - quality_score: float (0-1, image quality)
        - text_density: float (0-1, amount of text vs. white space)
        - recommended_engine: str (suggested OCR provider)
        """
        try:
            # Load image
            pil_img = Image.open(io.BytesIO(image_bytes))
            img_array = np.array(pil_img)

            # Convert to grayscale for analysis
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array

            # Detect image characteristics
            has_khmer = ImageAnalyzer._detect_khmer_script(gray)
            has_complex_math = ImageAnalyzer._detect_complex_math(gray)
            is_handwritten = ImageAnalyzer._detect_handwriting(gray)
            quality_score = ImageAnalyzer._calculate_quality_score(gray)
            text_density = ImageAnalyzer._calculate_text_density(gray)

            # Recommend engine based on analysis
            recommended_engine = ImageAnalyzer._recommend_engine(
                has_khmer=has_khmer,
                has_complex_math=has_complex_math,
                is_handwritten=is_handwritten,
                quality_score=quality_score,
            )

            return {
                "has_khmer_script": has_khmer,
                "has_complex_math": has_complex_math,
                "is_handwritten": is_handwritten,
                "quality_score": quality_score,
                "text_density": text_density,
                "recommended_engine": recommended_engine,
            }

        except Exception as e:
            logger.warning(f"Image analysis failed: {e}")
            return {
                "has_khmer_script": False,
                "has_complex_math": False,
                "is_handwritten": False,
                "quality_score": 0.5,
                "text_density": 0.5,
                "recommended_engine": "tesseract",
            }

    @staticmethod
    def _detect_khmer_script(gray: np.ndarray) -> bool:
        """
        Detect presence of Khmer script using contour analysis.

        Khmer script has distinctive characteristics:
        - Complex shapes with multiple connected components
        - Subscript characters (choengs)
        - Vowel diacritics above/below consonants
        """
        try:
            # Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
            )

            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                return False

            # Khmer characters tend to have:
            # 1. Complex shapes (high perimeter-to-area ratio)
            # 2. Multiple small components nearby (diacritics)
            complex_contours = 0

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 20:  # Too small
                    continue

                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:
                    continue

                # Complexity ratio (higher for Khmer)
                complexity = perimeter**2 / (4 * np.pi * area) if area > 0 else 0

                if complexity > 2.5:  # Khmer threshold
                    complex_contours += 1

            # If more than 20% of contours are complex, likely Khmer
            khmer_ratio = complex_contours / max(len(contours), 1)
            return khmer_ratio > 0.2

        except Exception:
            return False

    @staticmethod
    def _detect_complex_math(gray: np.ndarray) -> bool:
        """
        Detect complex mathematical notation (fractions, radicals, matrices).

        Complex math has:
        - Horizontal lines (fraction bars)
        - Multi-level structures (superscripts, subscripts)
        - Special symbols (√, ∫, ∑)
        """
        try:
            # Detect horizontal lines (fraction bars)
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(
                edges, 1, np.pi / 180, threshold=50, minLineLength=30, maxLineGap=10
            )

            if lines is None:
                return False

            # Count horizontal lines
            horizontal_lines = 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
                if angle < 10 or angle > 170:  # Nearly horizontal
                    horizontal_lines += 1

            # Detect multi-level text (superscripts/subscripts)
            # Find connected components at different vertical positions
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                return horizontal_lines > 2

            # Get vertical positions of text
            y_positions = []
            for contour in contours:
                _, y, _, h = cv2.boundingRect(contour)
                y_positions.append(y + h / 2)

            # Check for multiple text levels (indicates superscripts/subscripts)
            if y_positions:
                y_std = np.std(y_positions)
                height_avg = gray.shape[0] / 10  # Expected text height
                has_multilevel = y_std > height_avg * 0.5
            else:
                has_multilevel = False

            # Complex math if horizontal lines or multi-level structure
            return horizontal_lines > 2 or has_multilevel

        except Exception:
            return False

    @staticmethod
    def _detect_handwriting(gray: np.ndarray) -> bool:
        """
        Detect if text is handwritten vs. printed.

        Handwriting characteristics:
        - More irregular edges
        - Variable stroke width
        - Less uniform spacing
        """
        try:
            # Calculate edge variance (handwriting has more irregular edges)
            edges = cv2.Canny(gray, 50, 150)

            # Analyze stroke width variation
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # Calculate horizontal projection (spacing uniformity)
            horizontal_proj = np.sum(binary, axis=1)

            # Handwriting has more variation in projection
            if len(horizontal_proj) > 0:
                proj_std = np.std(horizontal_proj)
                proj_mean = (
                    np.mean(horizontal_proj[horizontal_proj > 0])
                    if np.any(horizontal_proj > 0)
                    else 1
                )
                variation_coef = proj_std / proj_mean if proj_mean > 0 else 0

                # High variation suggests handwriting
                return variation_coef > 0.6

            return False

        except Exception:
            return False

    @staticmethod
    def _calculate_quality_score(gray: np.ndarray) -> float:
        """
        Calculate image quality score (0-1).

        Factors:
        - Contrast
        - Sharpness (Laplacian variance)
        - Noise level
        """
        try:
            # Contrast (standard deviation of pixel intensities)
            contrast = np.std(gray) / 128.0  # Normalize to 0-1
            contrast = min(contrast, 1.0)

            # Sharpness (Laplacian variance)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var() / 1000.0  # Normalize
            sharpness = min(sharpness, 1.0)

            # Overall quality (weighted average)
            quality = 0.6 * contrast + 0.4 * sharpness

            return float(quality)

        except Exception:
            return 0.5

    @staticmethod
    def _calculate_text_density(gray: np.ndarray) -> float:
        """
        Calculate text density (ratio of text pixels to total).
        """
        try:
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            text_pixels = np.sum(binary > 0)
            total_pixels = binary.size

            density = text_pixels / total_pixels if total_pixels > 0 else 0
            return float(density)

        except Exception:
            return 0.5

    @staticmethod
    def _recommend_engine(
        has_khmer: bool,
        has_complex_math: bool,
        is_handwritten: bool,
        quality_score: float,
    ) -> str:
        """
        Recommend the best OCR engine based on image characteristics.

        Priority rules:
        1. Khmer + complex math → Gemini (best for both)
        2. Khmer only → Kiri OCR (native Khmer support)
        3. Complex math only → Mathpix (specialized for math)
        4. Handwritten → Gemini or Google Vision
        5. Low quality → Ensemble with voting
        6. Default → Tesseract (fast and free)
        """
        # Khmer content detected
        if has_khmer:
            if has_complex_math:
                return "gemini"  # Best for Khmer + complex math
            else:
                return "kiri"  # Native Khmer OCR

        # Complex math without Khmer
        if has_complex_math:
            if is_handwritten:
                return "gemini"  # Better for handwritten math
            else:
                return "mathpix"  # Best for printed complex math

        # Handwritten content
        if is_handwritten:
            return "gemini"  # Better handwriting recognition

        # Low quality image - use ensemble for robustness
        if quality_score < 0.4:
            return "ensemble:voting:tesseract,kiri"

        # Default: fast and free
        return "tesseract"


class IntelligentOCRRouter(MathVisionEngine):
    """
    Intelligent OCR router that analyzes images and selects optimal engine.

    Can operate in two modes:
    - 'auto': Analyze image and route to best engine
    - 'fallback': Try recommended engine, fallback to ensemble if fails
    """

    def __init__(
        self,
        mode: Literal["auto", "fallback"] = "auto",
        fallback_strategy: Literal["voting", "confidence"] = "voting",
    ):
        """
        Initialize intelligent router.

        Args:
            mode: 'auto' for single best engine, 'fallback' for ensemble fallback
            fallback_strategy: Strategy to use if primary engine fails
        """
        self.mode = mode
        self.fallback_strategy = fallback_strategy
        self.analyzer = ImageAnalyzer()

    def detect(self, image_bytes: bytes) -> VisionResult:
        """
        Analyze image and route to optimal OCR engine.
        """
        # Analyze image characteristics
        analysis = self.analyzer.analyze(image_bytes)

        logger.info(
            f"Image analysis: Khmer={analysis['has_khmer_script']}, "
            f"Complex math={analysis['has_complex_math']}, "
            f"Handwritten={analysis['is_handwritten']}, "
            f"Quality={analysis['quality_score']:.2f}, "
            f"Recommended={analysis['recommended_engine']}"
        )

        # Route to recommended engine
        recommended = analysis["recommended_engine"]

        try:
            primary_engine = create_vision_engine(recommended)
            result = primary_engine.detect(image_bytes)

            # Check if result is acceptable
            if result.detected_text and result.confidence >= 0.5:
                logger.info(f"Primary engine {recommended} succeeded")
                return result

            # Primary failed, use fallback if enabled
            if self.mode == "fallback":
                logger.warning(f"Primary engine {recommended} failed, trying fallback")
                return self._fallback_detect(image_bytes, analysis)
            else:
                return result

        except Exception as e:
            logger.error(f"Primary engine {recommended} raised exception: {e}")

            if self.mode == "fallback":
                return self._fallback_detect(image_bytes, analysis)
            else:
                return VisionResult(
                    detected_text=None,
                    confidence=0.0,
                    error_message=f"OCR routing failed: {e}",
                )

    def _fallback_detect(self, image_bytes: bytes, analysis: dict[str, Any]) -> VisionResult:
        """
        Fallback detection using ensemble of multiple engines.
        """
        # Build fallback provider list based on analysis
        providers = []

        if analysis["has_khmer_script"]:
            providers.extend(["kiri", "gemini"])

        if analysis["has_complex_math"]:
            providers.extend(["mathpix", "gemini"])

        if not providers:
            providers = ["tesseract", "kiri"]

        # Remove duplicates while preserving order
        seen = set()
        unique_providers = []
        for p in providers:
            if p not in seen:
                seen.add(p)
                unique_providers.append(p)

        # Create ensemble
        try:
            from app.ocr.extraction.ensemble import create_ocr_ensemble

            ensemble = create_ocr_ensemble(
                unique_providers,
                strategy=self.fallback_strategy,
                min_confidence=0.4,
            )

            logger.info(f"Fallback to ensemble with providers: {unique_providers}")
            return ensemble.detect(image_bytes)

        except Exception as e:
            logger.error(f"Fallback ensemble failed: {e}")
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message=f"All OCR attempts failed: {e}",
            )


def create_intelligent_router(
    mode: Literal["auto", "fallback"] = "fallback",
) -> IntelligentOCRRouter:
    """
    Create an intelligent OCR router.

    Args:
        mode: 'auto' for best single engine, 'fallback' for ensemble backup

    Returns:
        Configured IntelligentOCRRouter

    Example:
        >>> router = create_intelligent_router(mode="fallback")
        >>> result = router.detect(image_bytes)
    """
    return IntelligentOCRRouter(mode=mode)
