"""
Mathpix OCR integration for mathematical handwriting recognition.

Mathpix specializes in converting images of math equations (handwritten or
printed) into LaTeX and text. It's excellent for mathematical notation but
requires a paid API subscription.

Setup:
1. Sign up at https://mathpix.com/
2. Get your APP_ID and APP_KEY from the dashboard
3. Set environment variables:
   MATHPIX_APP_ID=your_app_id
   MATHPIX_APP_KEY=your_app_key
4. Install: pip install requests

Documentation: https://docs.mathpix.com/
"""

from __future__ import annotations

import base64
import os

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from app.ocr.extraction.base import MathVisionEngine, VisionResult


class MathpixVisionEngine(MathVisionEngine):
    """
    OCR using Mathpix API for math handwriting recognition.

    Pros:
    - Best-in-class for mathematical notation
    - Handles complex equations, matrices, fractions
    - Supports Khmer numerals
    - Fast response time

    Cons:
    - Paid service (free tier: 1000 requests/month)
    - Requires internet connection
    - External dependency
    """

    API_URL = "https://api.mathpix.com/v3/text"

    def __init__(self, app_id: str | None = None, app_key: str | None = None):
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "requests library required for Mathpix. Install with: pip install requests"
            )

        self.app_id = app_id or os.getenv("MATHPIX_APP_ID")
        self.app_key = app_key or os.getenv("MATHPIX_APP_KEY")

        if not self.app_id or not self.app_key:
            raise ValueError(
                "Mathpix credentials not found. Set MATHPIX_APP_ID and "
                "MATHPIX_APP_KEY environment variables or pass them to constructor."
            )

    def detect(self, image_bytes: bytes) -> VisionResult:
        """
        Send image to Mathpix API and get back detected math text.
        """
        try:
            # Encode image as base64
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            # Prepare request
            headers = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "Content-Type": "application/json",
            }

            payload = {
                "src": f"data:image/jpeg;base64,{image_base64}",
                "formats": ["text", "latex_simplified"],
                "data_options": {"include_asciimath": True, "include_latex": True},
            }

            # Make API request
            response = requests.post(self.API_URL, json=payload, headers=headers, timeout=30)

            if response.status_code != 200:
                return VisionResult(
                    detected_text=None,
                    confidence=0.0,
                    error_message=f"Mathpix API error: {response.status_code} - {response.text}",
                )

            result = response.json()

            # Extract text (prefer simplified text over LaTeX for our parser)
            detected_text = result.get("text", "")
            confidence = result.get("confidence", 0.0)

            # If no text detected
            if not detected_text:
                return VisionResult(
                    detected_text=None,
                    confidence=0.0,
                    error_message="No mathematical text detected in image",
                )

            return VisionResult(
                detected_text=detected_text, confidence=confidence, error_message=None
            )

        except requests.RequestException as e:
            return VisionResult(
                detected_text=None, confidence=0.0, error_message=f"Network error: {str(e)}"
            )
        except Exception as e:
            return VisionResult(
                detected_text=None, confidence=0.0, error_message=f"Unexpected error: {str(e)}"
            )
