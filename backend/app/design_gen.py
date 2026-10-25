"""Generate RAP-flavored system design prompts (moderate, interview-real)."""

from __future__ import annotations

import json
import logging
import random
import re
from typing import Any

from .llm_router import chat_completion_groq

logger = logging.getLogger(__name__)

_STYLE_FLAVORS = [
    "enterprise document / PDF Q&A with OCR and tables (longer architecture walk)",
    "telecom / network ops assistant with tools and escalation",
    "student tutoring chatbot — handle insufficient info + hallucinations",
    "internal support bot with RAG + human review",
    "short 5-minute scope: one clear failure mode (hallucination OR missing context)",
    "bidding / RFP assistant with citations",
    "manufacturing manual Q&A in customer VPC",
]

GEN_SYSTEM = """You invent ORIGINAL system-design interview prompts for an ML / LLM engineer intern
screen (RAP-style). Complexity should be MODERATE — not FAANG mega-scale.

Return ONLY valid JSON (no markdown fences) with keys:
- id: short snake_case id
- title: short title
- summary: 2–4 sentences (business problem + 1–2 constraints)
- ask: what to draw/defend
- duration_hint: "short" (≈5–10 min) or "standard" (≈20–40 min)

Rules:
- Match real RAP variety: sometimes a bigger architecture scenario, sometimes telecom,
  sometimes a student chatbot focused on insufficient information / hallucination.
- Require a practical architecture (ingest → understand/retrieve → generate → guardrails
  → optional human review → API) when duration_hint is standard.
- For short: narrow to ONE main risk (hallucination, missing context, latency, or tool failure)
  and ask how they handle it end-to-end.
- Include at most one RAP-ish constraint when relevant: private VPC, OCR/tables, RAG,
  Graph RAG optional, FastAPI serving, human-in-loop.
- Do NOT give the answer architecture — only the problem + what to defend.
- Keep summary/ask speakable aloud. No jargon walls.
"""

_FALLBACKS = [
    {
        "id": "student_tutor_bot",
        "title": "Student tutor chatbot",
        "summary": (
            "Build a chatbot for college students asking course questions. "
            "Sometimes the syllabus PDF lacks the answer. Model may hallucinate."
        ),
        "ask": (
            "Draw the flow. Explain how you detect insufficient context, refuse or "
            "clarify, ground answers, and stop hallucinations. Name metrics."
        ),
        "duration_hint": "short",
    },
    {
        "id": "enterprise_doc_qa",
        "title": "Enterprise document Q&A",
        "summary": (
            "Employees ask questions over large PDFs and Word manuals with tables and "
            "scanned pages. Need RAG, optional image retrieval, human review for "
            "high-stakes answers, FastAPI in the customer VPC."
        ),
        "ask": (
            "Draw ingest → OCR/understand → chunk/embed → retrieve → generate → "
            "guardrails → human-in-loop → API. Defend each box: why, alternative, failure, metric."
        ),
        "duration_hint": "standard",
    },
    {
        "id": "telecom_ops_assistant",
        "title": "Telecom ops assistant",
        "summary": (
            "Network ops wants an assistant that reads alerts, pulls runbooks, and "
            "suggests next steps. Wrong advice can page the wrong team."
        ),
        "ask": (
            "Sketch retrieval + tools + escalation. How do you handle stale runbooks, "
            "missing ticket context, and unsafe actions?"
        ),
        "duration_hint": "standard",
    },
]


async def generate_design_prompt(difficulty: str = "rap") -> dict[str, Any]:
    _ = difficulty
    flavor = random.choice(_STYLE_FLAVORS)
    seed = random.randint(1000, 9999)
    user = (
        f"Style flavor: {flavor}\n"
        f"Seed: {seed}\n"
        "Invent a NEW moderate RAP-style prompt. Avoid copying prior titles."
    )
    try:
        raw = await chat_completion_groq(GEN_SYSTEM, user)
    except Exception:
        logger.exception("Design gen threw")
        return dict(random.choice(_FALLBACKS))

    if raw.startswith("[LLM error"):
        logger.warning("Design gen LLM error: %s", raw[:200])
        return dict(random.choice(_FALLBACKS))

    parsed = _parse(raw)
    if not parsed.get("title") or not parsed.get("summary"):
        logger.warning("Design gen parse weak")
        return dict(random.choice(_FALLBACKS))
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
    hint = str(data.get("duration_hint") or "standard").strip().lower()
    if hint not in ("short", "standard"):
        hint = "standard"
    return {
        "id": str(data.get("id") or "generated"),
        "title": str(data.get("title") or "").strip(),
        "summary": str(data.get("summary") or "").strip(),
        "ask": str(data.get("ask") or "").strip(),
        "duration_hint": hint,
    }
