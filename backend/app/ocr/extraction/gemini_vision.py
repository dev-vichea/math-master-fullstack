"""
Gemini Multimodal Vision Engine for Khmer and English Math Exercises.

Uses Google's Gemini Vision API (e.g. gemini-2.5-flash or gemini-1.5-flash) to
transcribe, understand, and structure math exercises containing mixed Khmer
and English script, formulas, and diagrams with high accuracy.
"""

from __future__ import annotations

import base64
import json
import os
from typing import Any

import requests

from app.ocr.extraction.base import MathVisionEngine, VisionResult


class GeminiVisionEngine(MathVisionEngine):
    """
    Multimodal Math OCR and Exercise Understanding using Gemini Vision.

    Pros:
    - Superior understanding of complex Khmer script (subscripts, vowels, consonants)
    - Superior recognition of math notation, fractions, square roots, matrices, systems
    - Understands educational worksheet and textbook structure (headers, instructions, sub-items)
    - Distinguishes instructions ("Solve for x") from the actual equation

    Cons:
    - Requires GEMINI_API_KEY
    - Requires internet connection
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash",
        client_session: Any | None = None,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.session = client_session or requests.Session()

        if not self.api_key and client_session is None:
            raise ValueError(
                "Gemini vision provider requires GEMINI_API_KEY environment variable. "
                "Get an API key at https://aistudio.google.com/"
            )

    def detect(self, image_bytes: bytes) -> VisionResult:
        if not image_bytes:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message="Image data is empty",
            )

        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        prompt = (
            "You are a specialized OCR and math exercise understanding engine for Khmer and English.\n"
            "Analyze this image containing a math exercise, worksheet, or formula.\n\n"
            "Respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "raw_transcription": "exact transcription of text in the image",\n'
            '  "exercise_title": "e.g. លំហាត់ទី ១ or Exercise 1, or null",\n'
            '  "instruction": "e.g. ដោះស្រាយសមីការ or Solve for x, or null",\n'
            '  "primary_expression": "the clean mathematical equation or expression to solve (e.g. 2x + 5 = 15 or x^2 - 4 = 0)",\n'
            '  "sub_exercises": [\n'
            '     {"label": "ក", "expression": "2x + 4 = 10"}\n'
            "  ],\n"
            '  "confidence": 0.98\n'
            "}\n"
            "Ensure the primary_expression contains only standard math notation (use ^ for exponents, * for multiplication, / for division, <= and >= for inequalities).\n"
            "Do not wrap JSON in backticks."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": b64_image,
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 1024,
            },
        }

        try:
            resp = self.session.post(url, json=payload, timeout=30)
            if resp.status_code != 200:
                return VisionResult(
                    detected_text=None,
                    confidence=0.0,
                    error_message=f"Gemini API error ({resp.status_code}): {resp.text[:200]}",
                )

            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return VisionResult(
                    detected_text=None,
                    confidence=0.0,
                    error_message="Gemini returned no candidates",
                )

            part_text = candidates[0]["content"]["parts"][0]["text"].strip()
            # Remove potential markdown code block markers
            if part_text.startswith("```json"):
                part_text = part_text[7:]
            elif part_text.startswith("```"):
                part_text = part_text[3:]
            if part_text.endswith("```"):
                part_text = part_text[:-3]
            part_text = part_text.strip()

            parsed = json.loads(part_text)
            primary_expr = parsed.get("primary_expression") or parsed.get("raw_transcription")
            confidence = float(parsed.get("confidence", 0.95))

            exercise_meta = {
                "exercise_title": parsed.get("exercise_title"),
                "instruction": parsed.get("instruction"),
                "primary_expression": primary_expr,
                "sub_exercises": parsed.get("sub_exercises", []),
            }

            return VisionResult(
                detected_text=primary_expr,
                confidence=confidence,
                error_message=None,
                exercise_metadata=exercise_meta,
            )

        except Exception as e:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message=f"Gemini Vision error: {str(e)}",
            )
