from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from .models import PaperReference
from .prompts import CITATION_CONTEXT_PROMPT
from ..llm_router import chat_completion
import json
import re

logger = logging.getLogger(__name__)

S2 = "https://api.semanticscholar.org/graph/v1"


def _headers() -> dict[str, str]:
    key = (os.getenv("SEMANTIC_SCHOLAR_API_KEY") or "").strip()
    h = {"User-Agent": "Interviewer-DrDelta/0.1"}
    if key:
        h["x-api-key"] = key
    return h


async def enrich_reference(ref: PaperReference) -> PaperReference:
    if ref.abstract or ref.tldr:
        return ref
    try:
        async with httpx.AsyncClient(timeout=20.0, headers=_headers()) as client:
            if ref.arxiv_id:
                r = await client.get(
                    f"{S2}/paper/ARXIV:{ref.arxiv_id}",
                    params={
                        "fields": "title,year,venue,abstract,tldr,externalIds",
                    },
                )
                if r.status_code == 200:
                    data = r.json()
                    ref.title = data.get("title") or ref.title
                    ref.year = str(data.get("year") or "") or ref.year
                    ref.abstract = (data.get("abstract") or "")[:2000]
                    tldr = data.get("tldr") or {}
                    if isinstance(tldr, dict):
                        ref.tldr = (tldr.get("text") or "")[:800]
                    return ref
            q = ref.title or ref.raw[:120]
            r = await client.get(
                f"{S2}/paper/search/match",
                params={"query": q, "fields": "title,year,abstract,tldr"},
            )
            if r.status_code == 200:
                data = r.json()
                data = data.get("data") or data
                if isinstance(data, list) and data:
                    data = data[0]
                if isinstance(data, dict):
                    ref.title = data.get("title") or ref.title
                    ref.year = str(data.get("year") or "") or ref.year
                    ref.abstract = (data.get("abstract") or "")[:2000]
                    tldr = data.get("tldr") or {}
                    if isinstance(tldr, dict):
                        ref.tldr = (tldr.get("text") or "")[:800]
    except Exception:
        logger.exception("semantic scholar lookup failed")
    return ref


async def citation_context(citing: str, ref: PaperReference) -> dict[str, Any]:
    summary = ref.tldr or ref.abstract or ref.raw
    try:
        raw = await chat_completion(
            system="Return only JSON.",
            history=[],
            user_text=CITATION_CONTEXT_PROMPT.format(
                citing=citing[:600],
                title=ref.title or "unknown",
                summary=summary[:1500],
            ),
        )
        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except Exception:
        return {
            "what_it_did": (ref.tldr or ref.abstract or "Abstract unavailable")[:300],
            "why_cited": "Cited in this paper; abstract-level only.",
            "relation": "background",
        }
