"""
API endpoints for i18n language management, translations, and detection.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.i18n.glossary import translate_math_term
from app.i18n.language import (
    DEFAULT_LANGUAGE,
    LANGUAGE_INFO,
    SUPPORTED_LANGUAGES,
    Language,
    detect_language,
    get_language_info,
    normalize_language,
)
from app.i18n.translations import get_all_translations
from app.models.schemas import APIResponse

router = APIRouter(prefix="/i18n", tags=["i18n"])


class LanguageDetectRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze for language detection")


@router.get("/languages", response_model=APIResponse)
async def list_languages() -> APIResponse:
    """
    List all supported languages with metadata (Khmer & English).
    """
    languages_data = [
        get_language_info(lang)
        for lang in SUPPORTED_LANGUAGES
    ]
    return APIResponse(
        success=True,
        data={
            "default_language": DEFAULT_LANGUAGE.value,
            "supported_languages": languages_data,
        },
        error=None,
    )


@router.get("/translations", response_model=APIResponse)
async def get_translations(
    lang: Optional[str] = Query(None, description="Language code ('km' or 'en'). If omitted, returns both."),
) -> APIResponse:
    """
    Fetch localized application strings and UI messages for Khmer and/or English.
    """
    target_lang = normalize_language(lang) if lang else None
    translations = get_all_translations(target_lang)
    return APIResponse(
        success=True,
        data={
            "language": target_lang.value if target_lang else "bilingual",
            "translations": translations,
        },
        error=None,
    )


@router.post("/detect", response_model=APIResponse)
async def detect_text_language(payload: LanguageDetectRequest) -> APIResponse:
    """
    Automatically detect whether a math prompt/text is in Khmer or English.
    """
    detected = detect_language(payload.text)
    return APIResponse(
        success=True,
        data={
            "detected_language": detected.value,
            "language_info": get_language_info(detected),
            "text": payload.text,
        },
        error=None,
    )


@router.get("/terms/translate", response_model=APIResponse)
async def translate_term_endpoint(
    term: str = Query(..., min_length=1, description="Math term to translate"),
    target_lang: str = Query("km", description="Target language ('km' or 'en')"),
) -> APIResponse:
    """
    Translate a mathematical term between Khmer and English.
    """
    norm_lang = normalize_language(target_lang)
    translated = translate_math_term(term, norm_lang)
    return APIResponse(
        success=True,
        data={
            "original_term": term,
            "target_language": norm_lang.value,
            "translated_term": translated,
        },
        error=None,
    )
