from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

TAXONOMY_PATH = Path(__file__).resolve().parent / "interview_taxonomy.json"


class PlannedQuestion(BaseModel):
    text: str
    source: Literal["jd", "resume", "taxonomy", "user_notes"] = "taxonomy"
    follow_ups: list[str] = Field(default_factory=list)
    what_good_looks_like: str = ""


class PlannedRound(BaseModel):
    id: str
    round_type: str
    minutes: int
    goal: str = ""
    questions: list[PlannedQuestion] = Field(default_factory=list)
    rubric: list[str] = Field(default_factory=list)


class InterviewPlan(BaseModel):
    company_name: str = ""
    company_type: str = "product_india"
    role: str = "swe"
    level: str = "fresher"
    persona: str = "friendly_senior"
    mode: Literal["soft", "medium", "strict", "hardcore"] = "medium"
    run_style: Literal["practice", "interview"] = "interview"
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    jd_summary: str = ""
    resume_highlights: list[str] = Field(default_factory=list)
    jd_text: str = ""
    resume_text: str = ""
    user_notes: str = ""
    voice: bool = True
    camera: bool = False
    avatar: bool = False
    rounds: list[PlannedRound] = Field(default_factory=list)
    legacy: bool = False


class RoundDraft(BaseModel):
    round_type: str
    minutes: int | None = None


class PlanRequest(BaseModel):
    company_name: str
    company_type: str
    role: str
    level: str
    persona: str = "friendly_senior"
    mode: Literal["soft", "medium", "strict", "hardcore"] = "medium"
    run_style: Literal["practice", "interview"] = "interview"
    difficulty: Literal["easy", "medium", "hard"] | None = None
    jd_text: str = ""
    resume_text: str = ""
    user_notes: str = ""
    rounds: list[RoundDraft] = Field(default_factory=list)
    voice: bool = True
    camera: bool = False
    avatar: bool = False


@lru_cache
def load_taxonomy() -> dict[str, Any]:
    return json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))


def merge_default_rounds(
    company_type: str,
    role: str,
    level: str,
) -> list[dict[str, Any]]:
    tax = load_taxonomy()
    company = tax["company_types"].get(company_type) or tax["company_types"]["custom"]
    role_info = tax["roles"].get(role) or tax["roles"]["swe"]
    level_info = tax["experience_levels"].get(level) or tax["experience_levels"]["fresher"]
    round_types = tax["round_types"]

    ordered: list[str] = list(company.get("default_rounds") or [])
    for extra in role_info.get("add_rounds") or []:
        if extra not in ordered:
            insert_at = len(ordered)
            for i, r in enumerate(ordered):
                if r in ("behavioral", "hiring_manager", "hr"):
                    insert_at = i
                    break
            ordered.insert(insert_at, extra)

    drop = set(level_info.get("drop_rounds") or [])
    ordered = [r for r in ordered if r not in drop]

    out: list[dict[str, Any]] = []
    for rt in ordered:
        meta = round_types.get(rt) or {"label": rt, "default_minutes": 30}
        out.append(
            {
                "round_type": rt,
                "label": meta.get("label", rt),
                "minutes": int(meta.get("default_minutes") or 30),
                "workspace": meta.get("workspace", "none"),
                "family": meta.get("family", "knowledge"),
                "rubric_key": meta.get("rubric", "knowledge"),
            }
        )
    return out


def default_difficulty(company_type: str) -> str:
    tax = load_taxonomy()
    company = tax["company_types"].get(company_type) or {}
    return str(company.get("difficulty") or "medium")


def rap_legacy_rounds() -> list[RoundDraft]:
    return [
        RoundDraft(round_type="intro", minutes=5),
        RoundDraft(round_type="ml_coding", minutes=10),
        RoundDraft(round_type="genai_system_design", minutes=12),
        RoundDraft(round_type="ml_breadth", minutes=25),
    ]
