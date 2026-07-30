"""LLM-backed translation endpoint (harness/translation/service.py). Used by
the frontend's `i18n.tsx` as a fallback for UI keys that don't have a
hand-curated `zh-CN` entry yet - most backend-sourced English content (paper
titles/abstracts, extracted reasoning) is translated server-side, inline,
at the routes that already produce it (see harness/api/generation.py,
harness/paper_extraction/reasoning_view.py), using the request's `X-Locale`
header; this route exists for the frontend-only case where there's no
backend round-trip to piggyback the translation onto.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from harness.translation.service import translate_batch

router = APIRouter(prefix="/api/translation", tags=["translation"])


class TranslateBatchBody(BaseModel):
    texts: list[str]
    target_locale: str = "zh-CN"


@router.post("/batch")
def translate_batch_route(body: TranslateBatchBody) -> dict:
    return {"translations": translate_batch(body.texts, body.target_locale)}
