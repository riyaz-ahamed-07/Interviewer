from __future__ import annotations

import json
import logging
import re
import uuid
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from ..llm_router import chat_completion
from .analyze import analyze_paper, build_tutor_system, generate_cards
from .ingest import ingest_pdf, ingest_request
from .models import (
    AdvanceConceptRequest,
    ChatRequest,
    ExplainRequest,
    IngestRequest,
    PrereqStatusRequest,
    ReadingLogEntry,
)
from .prompts import EXPLAIN_SELECTION_PROMPT
from .refs import citation_context, enrich_reference
from . import store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/paper", tags=["paper"])


class StartBuddyRequest(BaseModel):
    paper_id: str = ""
    mode: str = "text"


@router.get("/library")
def library() -> dict[str, Any]:
    return {
        "papers": store.list_papers(),
        "log": store.list_log()[:20],
        "due_cards": [c.model_dump() for c in store.due_cards(10)],
    }


@router.post("/ingest")
async def ingest(body: IngestRequest) -> dict[str, Any]:
    try:
        paper = await ingest_request(
            arxiv_url=body.arxiv_url,
            arxiv_id=body.arxiv_id,
            text=body.text,
        )
        if body.title_hint:
            if not paper.title or paper.title == (paper.arxiv_id or ""):
                paper.title = body.title_hint
            elif body.title_hint.lower() not in paper.title.lower():
                paper.title = body.title_hint
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc
    store.save_paper(paper)
    paper_map = await analyze_paper(paper, timeout_s=40.0)
    cards = await generate_cards(paper, paper_map, timeout_s=20.0)
    store.append_log(
        ReadingLogEntry(
            id=str(uuid.uuid4()),
            paper_id=paper.id,
            title=paper.title,
            started_at=paper.created_at,
            minutes=0,
            concepts_mastered=0,
        )
    )
    return {
        "paper": paper.model_dump(),
        "map": paper_map.model_dump(),
        "cards": [c.model_dump() for c in cards],
    }


@router.post("/ingest/pdf")
async def ingest_pdf_route(file: UploadFile = File(...)) -> dict[str, Any]:
    raw = await file.read()
    try:
        paper = await ingest_pdf(raw, file.filename or "")
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc
    store.save_paper(paper)
    paper_map = await analyze_paper(paper)
    cards = await generate_cards(paper, paper_map)
    return {
        "paper": paper.model_dump(),
        "map": paper_map.model_dump(),
        "cards": [c.model_dump() for c in cards],
    }


@router.get("/{paper_id}")
def get_paper(paper_id: str) -> dict[str, Any]:
    paper = store.load_paper(paper_id)
    if not paper:
        raise HTTPException(404, "paper not found")
    paper_map = store.load_map(paper_id)
    cards = store.load_cards(paper_id)
    return {
        "paper": paper.model_dump(),
        "map": paper_map.model_dump() if paper_map else None,
        "cards": [c.model_dump() for c in cards],
    }


@router.post("/{paper_id}/analyze")
async def reanalyze(paper_id: str) -> dict[str, Any]:
    paper = store.load_paper(paper_id)
    if not paper:
        raise HTTPException(404, "paper not found")
    paper_map = await analyze_paper(paper)
    cards = await generate_cards(paper, paper_map)
    return {"map": paper_map.model_dump(), "cards": [c.model_dump() for c in cards]}


@router.post("/{paper_id}/prereqs")
def set_prereqs(paper_id: str, body: PrereqStatusRequest) -> dict[str, Any]:
    paper_map = store.load_map(paper_id)
    if not paper_map:
        raise HTTPException(404, "map not found")
    for p in paper_map.prerequisites:
        if p.id in body.statuses:
            p.status = body.statuses[p.id]
    store.save_map(paper_id, paper_map)
    return {"map": paper_map.model_dump()}


@router.post("/{paper_id}/session")
def start_session(paper_id: str, body: StartBuddyRequest | None = None) -> dict[str, Any]:
    paper = store.load_paper(paper_id)
    paper_map = store.load_map(paper_id)
    if not paper or not paper_map:
        raise HTTPException(404, "paper or map not found")
    mode = body.mode if body else "text"
    session = store.new_session(paper_id, mode=mode)
    concept = paper_map.concepts[0] if paper_map.concepts else None
    opening = (
        f"Pass-1: {paper_map.pass1.problem}\n"
        f"Core idea: {paper_map.pass1.core_claim}\n"
        f"Parent: {paper_map.parent.title} — big change: "
        f"{paper_map.parent.deltas[0].after if paper_map.parent.deltas else paper_map.parent.one_liner}\n"
        f"Verdict: {paper_map.pass1.verdict}\n\n"
        "Mark which prerequisites you already know, then we'll start concept 1 "
        f"({concept.title if concept else 'first concept'})."
    )
    session.messages.append({"role": "assistant", "content": opening})
    store.save_session(session)
    return {"session": session.model_dump(), "map": paper_map.model_dump()}


@router.get("/session/{session_id}")
def get_session(session_id: str) -> dict[str, Any]:
    session = store.load_session(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    paper = store.load_paper(session.paper_id)
    paper_map = store.load_map(session.paper_id)
    return {
        "session": session.model_dump(),
        "paper": paper.model_dump() if paper else None,
        "map": paper_map.model_dump() if paper_map else None,
    }


@router.post("/session/{session_id}/chat")
async def chat(session_id: str, body: ChatRequest) -> dict[str, Any]:
    session = store.load_session(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    paper = store.load_paper(session.paper_id)
    paper_map = store.load_map(session.paper_id)
    if not paper or not paper_map or not paper_map.concepts:
        raise HTTPException(400, "paper map incomplete")
    idx = session.current_concept_index
    idx = max(0, min(idx, len(paper_map.concepts) - 1))
    if body.concept_id:
        for i, c in enumerate(paper_map.concepts):
            if c.id == body.concept_id:
                idx = i
                session.current_concept_index = i
                break
    import asyncio

    concept = paper_map.concepts[idx]
    session.messages.append({"role": "user", "content": body.text})
    system = build_tutor_system(
        paper,
        paper_map,
        concept,
        mode=session.mode,
        notes=session.notes,
    )
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in session.messages[:-1]
        if m.get("role") in ("user", "assistant")
    ][-12:]
    try:
        reply = await asyncio.wait_for(
            chat_completion(system=system, history=history, user_text=body.text),
            timeout=55.0,
        )
    except Exception:
        logger.exception("paper chat LLM failed/timed out")
        deltas = paper_map.parent.deltas
        tip = (
            f"{deltas[0].component}: {deltas[0].before} -> {deltas[0].after}"
            if deltas
            else paper_map.parent.one_liner
        )
        reply = (
            f"(Tutor briefly offline.) Concept: {concept.title}. "
            f"Parent delta to hold onto: {tip}. "
            "Ask again in a moment, or tap Go deeper / Show the maths."
        )
    session.messages.append({"role": "assistant", "content": reply})
    if concept.state == "not_started":
        concept.state = "taught"
        store.save_map(paper.id, paper_map)
    store.save_session(session)
    return {
        "session": session.model_dump(),
        "reply": reply,
        "concept": concept.model_dump(),
        "map": paper_map.model_dump(),
    }


@router.post("/session/{session_id}/advance")
def advance(session_id: str, body: AdvanceConceptRequest) -> dict[str, Any]:
    session = store.load_session(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    paper_map = store.load_map(session.paper_id)
    if not paper_map or not paper_map.concepts:
        raise HTTPException(400, "no concepts")
    concept = paper_map.concepts[session.current_concept_index]
    if body.one_liner:
        concept.learner_one_liner = body.one_liner
        session.notes += f"\n- {concept.title}: {body.one_liner}"
    if body.action in ("got_it", "skip"):
        concept.state = "checked" if body.action == "got_it" else concept.state
        if session.current_concept_index < len(paper_map.concepts) - 1:
            session.current_concept_index += 1
            nxt = paper_map.concepts[session.current_concept_index]
            line = f"Next concept: {nxt.title}. Ready when you are — ask a question or say \"teach me\"."
        else:
            line = "You've reached the last concept. Ask for a recall quiz or close-the-paper challenge."
        session.messages.append({"role": "assistant", "content": line})
    elif body.action == "deeper":
        session.messages.append(
            {
                "role": "assistant",
                "content": f"Going deeper on {concept.title}. Ask what part you want expanded: maths, shapes, or code.",
            }
        )
    store.save_map(session.paper_id, paper_map)
    store.save_session(session)
    return {"session": session.model_dump(), "map": paper_map.model_dump()}


@router.post("/{paper_id}/explain")
async def explain(paper_id: str, body: ExplainRequest) -> dict[str, Any]:
    paper = store.load_paper(paper_id)
    paper_map = store.load_map(paper_id)
    if not paper:
        raise HTTPException(404, "paper not found")
    prompt = EXPLAIN_SELECTION_PROMPT.format(
        kind=body.kind,
        selection=body.selection[:1500],
        paragraph=body.paragraph[:2000],
        title=paper.title,
        abstract=paper.abstract[:1500],
    )
    try:
        raw = await chat_completion(
            system="Return only JSON for the explanation.",
            history=[],
            user_text=prompt,
        )
        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
    except Exception:
        data = {
            "short": body.selection[:200],
            "deeper": "I couldn't expand that cleanly. Try selecting a smaller phrase.",
            "symbols": [],
            "example": "",
        }
    if paper_map is not None and body.kind == "term":
        term = body.selection.strip()[:80]
        if term and term not in paper_map.glossary:
            paper_map.glossary[term] = str(data.get("short") or "")
            store.save_map(paper_id, paper_map)
    return data


@router.get("/{paper_id}/refs/{index}")
async def get_ref(paper_id: str, index: int, citing: str = "") -> dict[str, Any]:
    paper = store.load_paper(paper_id)
    if not paper or index < 0 or index >= len(paper.references):
        raise HTTPException(404, "reference not found")
    ref = await enrich_reference(paper.references[index])
    paper.references[index] = ref
    store.save_paper(paper)
    ctx = await citation_context(citing or ref.raw, ref) if citing or ref.abstract else {}
    return {"reference": ref.model_dump(), "context": ctx}


class CardReviewRequest(BaseModel):
    card_id: str
    grade: int = 3


@router.post("/cards/review")
def review_card(body: CardReviewRequest) -> dict[str, Any]:
    import time as _time

    grade = max(0, min(5, int(body.grade)))
    found = None
    paper_id = ""
    cards = []
    store.list_papers()
    for path in (store.DATA_ROOT / "cards").glob("*.json"):
        cards = store.load_cards(path.stem)
        for c in cards:
            if c.id == body.card_id:
                found = c
                paper_id = path.stem
                break
        if found:
            break
    if not found or not paper_id:
        raise HTTPException(404, "card not found")
    ease = float(found.ease or 2.5)
    interval = float(found.interval_days or 0)
    if grade < 3:
        interval = 0
        ease = max(1.3, ease - 0.2)
    else:
        if interval <= 0:
            interval = 1
        elif interval == 1:
            interval = 3
        else:
            interval = round(interval * ease, 2)
        ease = min(2.8, ease + 0.05 * (grade - 3))
    found.ease = ease
    found.interval_days = interval
    found.reps = int(found.reps or 0) + 1
    due = _time.time() + max(interval, 0.01) * 86400
    found.due_at = _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime(due))
    store.save_cards(paper_id, cards)
    if grade >= 4 and found.concept_id:
        paper_map = store.load_map(paper_id)
        if paper_map:
            for concept in paper_map.concepts:
                if concept.id == found.concept_id and concept.state == "checked":
                    concept.state = "mastered"
            store.save_map(paper_id, paper_map)
    return {"card": found.model_dump()}
