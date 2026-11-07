from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class PaperSection(BaseModel):
    id: str
    heading: str
    paragraphs: list[str] = Field(default_factory=list)


class PaperEquation(BaseModel):
    id: str
    latex: str
    section_id: str = ""
    context: str = ""


class PaperReference(BaseModel):
    raw: str
    title: str = ""
    arxiv_id: str | None = None
    doi: str | None = None
    year: str | None = None
    tldr: str = ""
    abstract: str = ""


class Paper(BaseModel):
    id: str
    title: str
    authors: list[str] = Field(default_factory=list)
    arxiv_id: str | None = None
    abstract: str = ""
    sections: list[PaperSection] = Field(default_factory=list)
    equations: list[PaperEquation] = Field(default_factory=list)
    figures: list[dict[str, Any]] = Field(default_factory=list)
    references: list[PaperReference] = Field(default_factory=list)
    source_url: str = ""
    created_at: str = ""


class Pass1(BaseModel):
    problem: str = ""
    core_claim: str = ""
    method_one_line: str = ""
    key_figure: str = ""
    main_results: str = ""
    five_cs: dict[str, str] = Field(default_factory=dict)
    worth_deep_read: bool = True
    verdict: str = ""


class ParentDelta(BaseModel):
    component: str
    before: str
    after: str
    why_it_matters: str = ""
    section_id: str = ""


class ParentInfo(BaseModel):
    title: str = ""
    arxiv_id: str | None = None
    one_liner: str = ""
    deltas: list[ParentDelta] = Field(default_factory=list)


class Prerequisite(BaseModel):
    id: str
    name: str
    why_needed: str = ""
    check_question: str = ""
    primer: str = ""
    status: Literal["known", "shaky", "unknown"] = "unknown"


class Concept(BaseModel):
    id: str
    title: str
    section_ids: list[str] = Field(default_factory=list)
    equation_ids: list[str] = Field(default_factory=list)
    summary: str = ""
    state: Literal["not_started", "taught", "checked", "mastered"] = "not_started"
    learner_one_liner: str = ""


class PaperMap(BaseModel):
    pass1: Pass1 = Field(default_factory=Pass1)
    parent: ParentInfo = Field(default_factory=ParentInfo)
    prerequisites: list[Prerequisite] = Field(default_factory=list)
    concepts: list[Concept] = Field(default_factory=list)
    glossary: dict[str, str] = Field(default_factory=dict)
    diagrams: dict[str, str] = Field(default_factory=dict)


class FlashCard(BaseModel):
    id: str
    paper_id: str
    concept_id: str = ""
    question: str
    answer: str
    ease: float = 2.5
    interval_days: float = 0
    due_at: str = ""
    reps: int = 0


class ReadingLogEntry(BaseModel):
    id: str
    paper_id: str
    title: str = ""
    started_at: str = ""
    finished_at: str | None = None
    minutes: int = 0
    concepts_mastered: int = 0
    summary: str = ""


class PaperSession(BaseModel):
    id: str
    paper_id: str
    current_concept_index: int = 0
    mode: Literal["text", "voice"] = "text"
    messages: list[dict[str, Any]] = Field(default_factory=list)
    notes: str = ""
    created_at: str = ""


class IngestRequest(BaseModel):
    arxiv_url: str = ""
    arxiv_id: str = ""
    text: str = ""
    title_hint: str = ""


class ExplainRequest(BaseModel):
    selection: str
    paragraph: str = ""
    section_id: str = ""
    kind: Literal["term", "equation", "sentence"] = "term"


class ChatRequest(BaseModel):
    text: str
    concept_id: str | None = None


class PrereqStatusRequest(BaseModel):
    statuses: dict[str, Literal["known", "shaky", "unknown"]]


class AdvanceConceptRequest(BaseModel):
    action: Literal["got_it", "skip", "deeper"] = "got_it"
    one_liner: str = ""
