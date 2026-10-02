"""
Google Cloud Vision API integration for OCR.

Google Cloud Vision is a general-purpose OCR that works well for printed
text and has good support for Khmer language. It's less specialized for
math notation compared to Mathpix, but more affordable and supports more
languages.

Setup:
1. Create a Google Cloud project
2. Enable Cloud Vision API
3. Create a service account and download JSON key
4. Set environment variable:
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
5. Install: pip install google-cloud-vision

Documentation: https://cloud.google.com/vision/docs
"""

from __future__ import annotations

import os

try:
    from google.cloud import vision

    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False

from app.ocr.engines.base import MathVisionEngine, VisionResult


class GoogleVisionEngine(MathVisionEngine):
    """
    OCR using Google Cloud Vision API.

    Pros:
    - Excellent Khmer language support
    - Good for printed and typed math
    - Affordable pricing (free tier: 1000 requests/month)
    - Reliable and fast

    Cons:
    - Less accurate for complex handwritten math
    - May struggle with mathematical notation
    - Requires Google Cloud account
    """

    def __init__(self, credentials_path: str | None = None):
        if not GOOGLE_VISION_AVAILABLE:
            raise ImportError(
                "google-cloud-vision library required. "
                "Install with: pip install google-cloud-vision"
            )

        # Set credentials if provided
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        # Verify credentials are set
        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            raise ValueError(
                "Google Cloud credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS "
                "environment variable or pass credentials_path to constructor."
            )

        self.client = vision.ImageAnnotatorClient()

    def detect(self, image_bytes: bytes) -> VisionResult:
        """
        Send image to Google Cloud Vision and get back detected text.
        """
        try:
            # Create Vision API image object
            image = vision.Image(content=image_bytes)

            # Perform text detection
            response = self.client.text_detection(image=image)

            if response.error.message:
                return VisionResult(
                    detected_text=None,
                    confidence=0.0,
                    error_message=f"Google Vision API error: {response.error.message}",
                )

            # Extract detected text
            texts = response.text_annotations

            if not texts:
                return VisionResult(
                    detected_text=None, confidence=0.0, error_message="No text detected in image"
                )

            # First annotation contains the full detected text
            detected_text = texts[0].description.strip()

            # Calculate average confidence (Google Vision returns confidence per word)
            if len(texts) > 1:
                confidences = [
                    annotation.confidence
                    for annotation in texts[1:]
                    if hasattr(annotation, "confidence")
                ]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.9
            else:
                avg_confidence = 0.9  # Default high confidence if not provided

            return VisionResult(
                detected_text=detected_text, confidence=avg_confidence, error_message=None
            )

        except Exception as e:
            return VisionResult(
                detected_text=None, confidence=0.0, error_message=f"Error: {str(e)}"
            )
