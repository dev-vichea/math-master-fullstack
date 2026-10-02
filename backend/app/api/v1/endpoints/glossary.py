"""
Glossary API Endpoints for Bilingual Khmer-English Mathematics Terminology.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Query

from app.knowledge.bilingual_glossary import (
    EXAMPLE_USAGES,
    get_all_categories,
    lookup_english,
    lookup_khmer,
    search_glossary,
)
from app.models.schemas import APIResponse

router = APIRouter(prefix="/glossary", tags=["glossary"])


@router.get("", response_model=APIResponse)
async def list_glossary_terms(
    q: Optional[str] = Query(None, description="Search term in English, Khmer, or formula"),
    category: Optional[str] = Query(None, description="Filter by category"),
) -> APIResponse:
    """
    Search and list bilingual Khmer-English math terms.
    """
    entries = search_glossary(query=q or "", category=category)
    return APIResponse(
        success=True,
        data={
            "total": len(entries),
            "terms": [e.to_dict() for e in entries],
            "query": q,
            "category": category,
        },
        error=None,
    )


@router.get("/categories", response_model=APIResponse)
async def list_categories() -> APIResponse:
    """
    List all available mathematical categories in the bilingual glossary.
    """
    categories = get_all_categories()
    return APIResponse(
        success=True,
        data={"categories": categories},
        error=None,
    )


@router.get("/lookup", response_model=APIResponse)
async def quick_lookup(
    term: str = Query(..., min_length=1, description="Term to lookup in Khmer or English")
) -> APIResponse:
    """
    Instant lookup of a math term in either Khmer or English.
    """
    khmer_val = lookup_khmer(term)
    english_val = lookup_english(term)

    return APIResponse(
        success=True,
        data={
            "input": term,
            "khmer_translation": khmer_val,
            "english_translation": english_val,
        },
        error=None,
    )


@router.get("/examples", response_model=APIResponse)
async def list_example_usages() -> APIResponse:
    """
    Get curated bilingual math exercise phrasing examples from BacII/CSCA standards.
    """
    return APIResponse(
        success=True,
        data={"examples": EXAMPLE_USAGES},
        error=None,
    )
