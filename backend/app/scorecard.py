from __future__ import annotations

import json
import logging
import re
from typing import Any

from .llm_router import chat_completion

logger = logging.getLogger(__name__)

SCORECARD_SYSTEM = """You are a tough but fair ML interview coach.
You score a completed mock interview from the transcript.

Return ONLY valid JSON (no markdown fences) with this shape:
{
  "score": <integer 0-100 overall>,
  "summary": "<2-3 sentences overall>",
  "strengths": ["<overall bullet>", "..."],
  "improve": ["<what to fix next time>", "..."],
  "focus_next": ["<study focus>", "..."],
  "english": {
    "fillers_to_avoid": ["um", "like", "..."],
    "manner": "<how they should speak: short, definition-first, etc.>",
    "answer_openers": ["<template opener 1>", "<template opener 2>", "<template opener 3>"],
    "notes": ["<specific English habit to change>", "..."]
  },
  "by_phase": {
    "intro": {
      "score": <0-100>,
      "strengths": ["<bullet>"],
      "weaknesses": ["<bullet>"],
      "note": "<one line>"
    },
    "debug": {
      "score": <0-100>,
      "strengths": ["<bullet>"],
      "weaknesses": ["<bullet>"],
      "note": "<one line>"
    },
    "design": {
      "score": <0-100>,
      "strengths": ["<bullet>"],
      "weaknesses": ["<bullet>"],
      "note": "<one line>"
    },
    "llm": {
      "score": <0-100>,
      "strengths": ["<bullet>"],
      "weaknesses": ["<bullet>"],
      "note": "<one line>"
    }
  }
}

Scoring guide:
- 90-100: crisp definitions, strong debug reasoning, clear design trade-offs
- 70-89: solid with gaps
- 50-69: incomplete / vague / needs drills
- below 50: major gaps or mostly stuck

Be specific. Quote weak patterns from the transcript when useful.
Every phase that appears in the transcript MUST have score + strengths + weaknesses.
English coaching must be practical (fillers, answer structure, starting lines).
"""

PHASE_KEYS = ("intro", "debug", "design", "llm")


def _parse_json(raw: str) -> dict[str, Any] | None:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            return None
        try:
            data = json.loads(m.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None


def _normalize_phase_entry(raw: Any) -> dict[str, Any]:
    if isinstance(raw, str):
        return {
            "score": 0,
            "strengths": [],
            "weaknesses": [],
            "note": raw.strip(),
        }
    if not isinstance(raw, dict):
        return {"score": 0, "strengths": [], "weaknesses": [], "note": ""}
    try:
        score = int(raw.get("score", 0))
    except (TypeError, ValueError):
        score = 0
    strengths = raw.get("strengths") or []
    weaknesses = raw.get("weaknesses") or raw.get("improve") or []
    if isinstance(strengths, str):
        strengths = [strengths]
    if isinstance(weaknesses, str):
        weaknesses = [weaknesses]
    return {
        "score": max(0, min(100, score)),
        "strengths": [str(x) for x in strengths if str(x).strip()],
        "weaknesses": [str(x) for x in weaknesses if str(x).strip()],
        "note": str(raw.get("note") or "").strip(),
    }


def _fallback(reason: str) -> dict[str, Any]:
    return {
        "score": 0,
        "summary": f"Scorecard unavailable ({reason}). Re-run feedback when Groq is ready.",
        "strengths": [],
        "improve": ["Retry the end-of-interview scorecard when the text model is available."],
        "focus_next": ["Review your transcript manually for now."],
        "english": {
            "fillers_to_avoid": ["um", "uh", "like", "you know"],
            "manner": "Lead with a one-line definition, then one mechanism, then stop.",
            "answer_openers": [
                "In one line: …",
                "The key idea is …",
                "What changes is …",
            ],
            "notes": ["Keep answers under ~20 seconds for definition questions."],
        },
        "by_phase": {},
        "copy_text": "",
    }


def build_copy_text(card: dict[str, Any]) -> str:
    eng = card.get("english") or {}
    lines = [
        f"ML Mock Interview Score: {card.get('score', 0)}/100",
        "",
        "Summary",
        str(card.get("summary") or "").strip(),
        "",
        "Strengths",
        *[f"- {x}" for x in (card.get("strengths") or [])],
        "",
        "What to improve",
        *[f"- {x}" for x in (card.get("improve") or [])],
        "",
        "Focus next",
        *[f"- {x}" for x in (card.get("focus_next") or [])],
        "",
        "English",
        f"Manner: {eng.get('manner', '')}".strip(),
        "Fillers to avoid: " + ", ".join(eng.get("fillers_to_avoid") or []),
        "Start answers like:",
        *[f"- {x}" for x in (eng.get("answer_openers") or [])],
        *[f"- {x}" for x in (eng.get("notes") or [])],
    ]
    by = card.get("by_phase") or {}
    if by:
        lines.extend(["", "By phase"])
        for k in PHASE_KEYS:
            entry = by.get(k)
            if not entry:
                continue
            if isinstance(entry, str):
                lines.append(f"- {k}: {entry}")
                continue
            lines.append(f"- {k}: {entry.get('score', 0)}/100")
            if entry.get("note"):
                lines.append(f"  note: {entry['note']}")
            for s in entry.get("strengths") or []:
                lines.append(f"  + {s}")
            for w in entry.get("weaknesses") or []:
                lines.append(f"  - {w}")
    return "\n".join(lines).strip() + "\n"


async def generate_scorecard(
    *,
    mode: str,
    run_style: str,
    messages: list[dict[str, str]],
    llm_topics: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    transcript = "\n".join(
        f"{m.get('role', '?').upper()}: {m.get('content', '')}" for m in messages
    )
    topics = ""
    if llm_topics:
        topics = "Queued LLM topics:\n" + "\n".join(
            f"- {t.get('technique', '')}" for t in llm_topics
        )

    user = (
        f"Mode: {mode}. Run style: {run_style}.\n"
        f"{topics}\n\n"
        f"FULL TRANSCRIPT:\n{transcript}\n\n"
        "Produce the JSON scorecard now. Include per-phase score, strengths, and weaknesses."
    )

    raw = await chat_completion(
        SCORECARD_SYSTEM,
        [],
        user,
        prefer="groq",
    )
    if raw.startswith("[LLM error") or raw.startswith("[No API"):
        card = _fallback(raw[:120])
        card["copy_text"] = build_copy_text(card)
        return card

    data = _parse_json(raw)
    if not data:
        logger.warning("scorecard JSON parse failed: %s", raw[:400])
        card = _fallback("could not parse model JSON")
        card["copy_text"] = build_copy_text(card)
        return card

    try:
        score = int(data.get("score", 0))
    except (TypeError, ValueError):
        score = 0
    data["score"] = max(0, min(100, score))
    data.setdefault("strengths", [])
    data.setdefault("improve", [])
    data.setdefault("focus_next", [])
    data.setdefault("english", {})
    raw_phases = data.get("by_phase") or {}
    normalized: dict[str, Any] = {}
    if isinstance(raw_phases, dict):
        for key in PHASE_KEYS:
            if key in raw_phases:
                normalized[key] = _normalize_phase_entry(raw_phases[key])
        for key, val in raw_phases.items():
            if key not in normalized:
                normalized[str(key)] = _normalize_phase_entry(val)
    data["by_phase"] = normalized
    data["copy_text"] = build_copy_text(data)
    return data
