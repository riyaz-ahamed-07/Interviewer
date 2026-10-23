"""Generate unique RAP-flavored system design prompts each session."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from .llm_router import chat_completion_groq

logger = logging.getLogger(__name__)

GEN_SYSTEM = """You invent ORIGINAL system-design interview prompts for an ML / LLM engineer intern
at an enterprise AI company like RAP (document intelligence, RAG, agents, OCR, serving in customer VPC).

Return ONLY valid JSON (no markdown fences) with keys:
- id: short snake_case id
- title: short title
- summary: 2-4 sentences describing the business problem and hard constraints
- ask: what the candidate must draw/defend (boxes, flow, failures, metrics, alternatives)

Rules:
- Each prompt must be DIFFERENT (vary domain: manufacturing, telecom, legal, healthcare, bidding, support, audio, etc.).
- Must require an architecture (ingest → understanding → retrieval/agents → guardrails → human review → API/serve) flavor when relevant.
- Include at least one RAP-ish constraint: private VPC, Graph RAG optional, Image/HyDE RAG, OCR/tables, multi-agent workgroup, memory, RPA, or FastAPI serving.
- Do NOT give the answer architecture — only the problem + what to draw.
- Keep summary and ask speakable (interviewer may read them aloud).
"""

_FALLBACK = {
    "id": "enterprise_doc_qa",
    "title": "Enterprise document Q&A",
    "summary": (
        "Employees ask questions over large PDFs and Word manuals with tables and "
        "scanned pages. Need RAG, optional Image/HyDE retrieval, human review for "
        "high-stakes answers, FastAPI in the customer VPC."
    ),
    "ask": (
        "Draw ingest → OCR/understand → chunk/embed → retrieve → agent/tools/memory → "
        "guardrails → human-in-loop → API. Defend each box: why, alternative, failure, metric."
    ),
}


async def generate_design_prompt(difficulty: str = "medium") -> dict[str, Any]:
    user = (
        f"Difficulty flavor: {difficulty} "
        "(easy=narrower scope, hard=more constraints / multi-agent / failure modes).\n"
        "Invent a NEW prompt now. Avoid repeating the classic 'manufacturing PDF Q&A' wording."
    )
    try:
        raw = await chat_completion_groq(GEN_SYSTEM, user)
    except Exception:
        logger.exception("Design gen threw")
        return dict(_FALLBACK)

    if raw.startswith("[LLM error"):
        logger.warning("Design gen LLM error: %s", raw[:200])
        return dict(_FALLBACK)

    parsed = _parse(raw)
    if not parsed.get("title") or not parsed.get("summary"):
        logger.warning("Design gen parse weak")
        return dict(_FALLBACK)
    return parsed


def _parse(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            return {}
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError:
            return {}
    if not isinstance(data, dict):
        return {}
    return {
        "id": str(data.get("id") or "generated"),
        "title": str(data.get("title") or "").strip(),
        "summary": str(data.get("summary") or "").strip(),
        "ask": str(data.get("ask") or "").strip(),
    }
