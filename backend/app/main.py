from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from .config import get_settings
from .db import init_db, close_db, ping as db_ping
from .debug_gen import generate_debug_drill
from .design_gen import generate_design_prompt
from .llm_router import chat_completion, encode_png_bytes, get_router
from .prompts import opening_line
from .scorecard import generate_scorecard
from .session import (
    DebugDifficulty,
    InterviewSession,
    Mode,
    Phase,
    RunStyle,
    store,
)
from . import storage as db_storage
from .diagram_summary import scene_to_adjacency
from .round_prompts import generate_plan, live_round_briefing
from .taxonomy import (
    InterviewPlan,
    PlanRequest,
    load_taxonomy,
    merge_default_rounds,
    rap_legacy_rounds,
)
from .paper.router import router as paper_router
from .tts import synthesize_mp3
from .voice_live import handle_live_socket, live_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(title="Interview Coach", version="0.2.0", lifespan=lifespan)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(paper_router)


class StartRequest(BaseModel):
    mode: Literal["soft", "medium", "strict", "hardcore"] = "medium"
    run_style: Literal["practice", "interview"] = "interview"
    debug_difficulty: Literal["easy", "medium", "hard"] = "medium"


class FriendStartRequest(BaseModel):
    mode: Literal["soft", "medium", "strict", "hardcore"] = "medium"


class TextTurnRequest(BaseModel):
    text: str = Field(min_length=1)
    diagram_labels: list[str] = Field(default_factory=list)


class MessageIn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)
    ts: float | None = None
    phase: str = ""


class AdvanceRequest(BaseModel):
    reason: str = "manual"
    messages: list[MessageIn] | None = None


class LogTurnRequest(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class SyncMessagesRequest(BaseModel):
    messages: list[MessageIn]


class LlmTopicRequest(BaseModel):
    direction: Literal["prev", "next", "goto"] = "prev"
    index: int | None = None


def _apply_client_messages(
    session: InterviewSession, messages: list[MessageIn]
) -> None:
    """Prefer the client transcript (includes Gemini Live turns)."""
    if not messages:
        return
    from .session import ChatMessage

    session.messages = [
        ChatMessage(
            role=m.role,
            content=m.content,
            ts=m.ts if m.ts is not None else session.created_at,
            phase=m.phase or session.phase.value,
        )
        for m in messages
        if m.content.strip()
    ]


async def _persist(session: InterviewSession) -> None:
    await db_storage.upsert_session(session)


async def _get_session(session_id: str) -> InterviewSession | None:
    session = store.get(session_id)
    if session:
        return session
    loaded = await db_storage.load_session(session_id)
    if loaded:
        store.put(loaded)
    return loaded


@app.get("/api/health")
async def health() -> dict[str, Any]:
    db = await db_ping()
    return {
        "ok": True,
        "llm_ready": get_router() is not None,
        "live": live_status(),
        "db": db,
        "neon_branch": settings.neon_branch or None,
    }


@app.get("/api/history")
async def history(limit: int = 20) -> dict[str, Any]:
    return {"sessions": await db_storage.list_history(limit)}


@app.get("/api/taxonomy")
def taxonomy() -> dict[str, Any]:
    return load_taxonomy()


class DiagramSceneRequest(BaseModel):
    labels: list[str] = Field(default_factory=list)
    elements: list[dict[str, Any]] = Field(default_factory=list)


@app.post("/api/diagram/summary")
def diagram_summary(body: DiagramSceneRequest) -> dict[str, Any]:
    return scene_to_adjacency(body.model_dump())


@app.get("/api/taxonomy/defaults")
def taxonomy_defaults(
    company_type: str = "product_india",
    role: str = "swe",
    level: str = "fresher",
) -> dict[str, Any]:
    return {
        "rounds": merge_default_rounds(company_type, role, level),
    }


class CreateSessionRequest(BaseModel):
    plan: InterviewPlan


@app.post("/api/plan")
async def create_plan(body: PlanRequest) -> dict[str, Any]:
    plan = await generate_plan(body)
    return {"plan": plan.model_dump()}


@app.post("/api/resume/parse")
async def parse_resume(file: UploadFile = File(...)) -> dict[str, Any]:
    raw = await file.read()
    name = (file.filename or "resume").lower()
    text = ""
    if name.endswith(".txt") or (file.content_type or "").startswith("text/"):
        text = raw.decode("utf-8", errors="ignore")
    elif name.endswith(".pdf") or (file.content_type or "") == "application/pdf":
        try:
            from pypdf import PdfReader
            import io

            reader = PdfReader(io.BytesIO(raw))
            text = "\n".join((p.extract_text() or "") for p in reader.pages)
        except Exception as exc:
            raise HTTPException(400, f"Could not parse PDF: {exc}") from exc
    else:
        text = raw.decode("utf-8", errors="ignore")
    text = text.strip()
    if not text:
        raise HTTPException(400, "No text extracted. Paste the resume instead.")
    return {"text": text[:50000]}


@app.post("/api/session/create")
async def create_session_from_plan(body: CreateSessionRequest) -> dict[str, Any]:
    session = store.create_from_plan(body.plan)
    await kick_phase_prep(session)
    await _persist(session)
    briefing = None
    if session.use_plan_engine and session.plan and session.current_round():
        briefing = live_round_briefing(session.plan, session.current_round())
    return {"session": session.to_public(), "live_briefing": briefing}


@app.post("/api/session/legacy/rap")
async def start_rap_legacy(
    body: StartRequest | None = None,
) -> dict[str, Any]:
    req = body or StartRequest()
    plan = InterviewPlan(
        company_name="RAP",
        company_type="ai_startup",
        role="ml_engineer",
        level="intern",
        persona="friendly_senior",
        mode=req.mode,
        run_style=req.run_style,
        difficulty=req.debug_difficulty,
        legacy=True,
        rounds=[],
    )
    from .taxonomy import PlannedRound, PlannedQuestion

    drafts = rap_legacy_rounds()
    tax = load_taxonomy()
    rounds = []
    for i, d in enumerate(drafts, start=1):
        meta = tax["round_types"].get(d.round_type) or {}
        rounds.append(
            PlannedRound(
                id=f"r{i}",
                round_type=d.round_type,
                minutes=int(d.minutes or meta.get("default_minutes") or 30),
                goal=str(meta.get("label") or d.round_type),
                questions=[
                    PlannedQuestion(
                        text="Legacy RAP flow",
                        source="taxonomy",
                    )
                ],
                rubric=list(
                    tax["rubrics"].get(meta.get("rubric", "knowledge"), [])
                ),
            )
        )
    plan.rounds = rounds
    session = store.create(
        mode=Mode(req.mode),
        run_style=RunStyle(req.run_style),
        debug_difficulty=DebugDifficulty(req.debug_difficulty),
    )
    session.plan = plan
    session.persona = plan.persona
    await _persist(session)
    return {"session": session.to_public()}


async def ensure_design_prompt(session: InterviewSession) -> None:
    needs = session.phase in (Phase.design, Phase.design_teacher)
    if session.use_plan_engine and session.current_round():
        from .taxonomy import load_taxonomy as _lt

        meta = _lt()["round_types"].get(session.current_round().round_type) or {}
        needs = "whiteboard" in str(meta.get("workspace") or "")
    if not needs:
        return
    if session.design_prompt:
        return
    round_type = (
        session.current_round().round_type
        if session.use_plan_engine and session.current_round()
        else "rap"
    )
    company_type = session.plan.company_type if session.plan else "custom"
    role = session.plan.role if session.plan else "ml_engineer"
    jd = session.jd_text or (session.plan.jd_text if session.plan else "")
    design = await generate_design_prompt(
        round_type,
        role=role,
        company_type=company_type,
        jd_text=jd,
    )
    store.apply_design(session, design)
    if not session.use_plan_engine:
        store.append_design_opening(session)


async def ensure_debug_drill(session: InterviewSession) -> None:
    if session.phase != Phase.debug:
        return
    if session.code_panel.strip() and not session.code_panel.startswith("Generating"):
        return
    drill = await generate_debug_drill(session.debug_difficulty.value)
    store.apply_drill(session, drill)
    store.append_phase_opening(session)


async def ensure_scorecard(session: InterviewSession) -> None:
    if session.phase not in (Phase.feedback, Phase.done):
        return
    if session.scorecard:
        return
    msgs = [{"role": m.role, "content": m.content} for m in session.messages]
    session.scorecard = await generate_scorecard(
        mode=session.mode.value,
        run_style=session.run_style.value,
        messages=msgs,
        llm_topics=session.llm_topics,
    )
    if session.phase == Phase.feedback:
        store.append_phase_opening(session)


async def after_phase_enter(session: InterviewSession) -> None:
    await ensure_debug_drill(session)
    await ensure_design_prompt(session)
    await ensure_scorecard(session)


def _phase_needs_async_prep(session: InterviewSession) -> bool:
    if session.phase == Phase.debug and (
        not session.code_panel.strip()
        or session.code_panel.startswith("Generating")
    ):
        return True
    if session.phase in (Phase.design, Phase.design_teacher) and not session.design_prompt:
        return True
    if session.phase in (Phase.feedback, Phase.done) and not session.scorecard:
        return True
    return False


async def _run_phase_prep(session_id: str) -> None:
    session = store.get(session_id)
    if not session:
        return
    try:
        await after_phase_enter(session)
        await _persist(session)
    except Exception:
        logger.exception("phase prep failed for %s", session_id)
        session = store.get(session_id)
        if not session:
            return
        if session.phase == Phase.debug and session.code_panel.startswith(
            "Generating"
        ):
            session.code_panel = (
                "# Could not generate the debug drill.\n"
                "# Tap Next phase again, or End and start a new run.\n"
            )
            await _persist(session)


async def kick_phase_prep(session: InterviewSession) -> None:
    """Return control immediately; heavy Groq work continues in the background."""
    if session.phase == Phase.debug and not session.code_panel.strip():
        session.code_panel = "Generating debug drill…"
    if _phase_needs_async_prep(session):
        asyncio.create_task(_run_phase_prep(session.id))
        return
    await after_phase_enter(session)


@app.post("/api/session/start")
async def start_session(body: StartRequest) -> dict[str, Any]:
    session = store.create(
        mode=Mode(body.mode),
        run_style=RunStyle(body.run_style),
        debug_difficulty=DebugDifficulty(body.debug_difficulty),
    )
    await _persist(session)
    return {"session": session.to_public()}


@app.post("/api/session/friend/start")
async def start_friend_session(body: FriendStartRequest) -> dict[str, Any]:
    session = store.create_friend(mode=Mode(body.mode))
    await _persist(session)
    return {"session": session.to_public()}


@app.post("/api/session/design-teacher/start")
async def start_design_teacher_session(
    body: FriendStartRequest,
) -> dict[str, Any]:
    session = store.create_design_teacher(mode=Mode(body.mode))
    await ensure_design_prompt(session)
    await _persist(session)
    return {"session": session.to_public()}


@app.post("/api/session/{session_id}/design-teacher/next")
async def design_teacher_next(session_id: str) -> dict[str, Any]:
    session = await _get_session(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    if session.phase != Phase.design_teacher:
        raise HTTPException(400, "design-teacher next only in design_teacher phase")
    session.design_prompt = {}
    design = await generate_design_prompt("rap")
    store.apply_design(session, design)
    line = opening_line(
        Phase.design_teacher.value, session.context(), session.run_style.value
    )
    session.append("assistant", line)
    await _persist(session)
    return {
        "session": session.to_public(),
        "live_briefing": session.live_briefing(),
    }


@app.get("/api/session/{session_id}")
async def get_session(session_id: str) -> dict[str, Any]:
    session = await _get_session(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    if store.maybe_auto_advance(session):
        await kick_phase_prep(session)
        await _persist(session)
    return {"session": session.to_public()}


@app.post("/api/session/{session_id}/log")
async def log_turn(session_id: str, body: LogTurnRequest) -> dict[str, Any]:
    session = await _get_session(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    session.append(body.role, body.content.strip())
    await _persist(session)
    return {"ok": True, "n": len(session.messages)}


@app.post("/api/session/{session_id}/sync")
async def sync_messages(
    session_id: str, body: SyncMessagesRequest
) -> dict[str, Any]:
    session = await _get_session(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    _apply_client_messages(session, body.messages)
    await _persist(session)
    return {"session": session.to_public()}


@app.post("/api/session/{session_id}/advance")
async def advance(session_id: str, body: AdvanceRequest | None = None) -> dict[str, Any]:
    session = await _get_session(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    if body and body.messages:
        _apply_client_messages(session, body.messages)
    store.advance_phase(session)
    await kick_phase_prep(session)
    await _persist(session)
    briefing = session.live_briefing()
    if session.use_plan_engine and session.plan and session.current_round():
        briefing = live_round_briefing(session.plan, session.current_round())
    return {
        "session": session.to_public(),
        "reason": (body.reason if body else "manual"),
        "live_briefing": briefing,
        "preparing": _phase_needs_async_prep(session),
    }


@app.post("/api/session/{session_id}/llm/topic")
async def llm_topic(session_id: str, body: LlmTopicRequest) -> dict[str, Any]:
    session = await _get_session(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    if session.phase != Phase.llm:
        raise HTTPException(400, "topic navigation only in llm phase")
    if not session.llm_topics:
        raise HTTPException(400, "no topics queued")

    n = len(session.llm_topics)
    cur = session.llm_topic_index
    if body.direction == "goto" and body.index is not None:
        idx = body.index
    elif body.direction == "prev":
        idx = cur - 1
    else:
        idx = cur + 1
    if idx < 0 or idx >= n:
        raise HTTPException(400, "topic index out of range")

    briefing = store.set_llm_topic(session, idx)
    await _persist(session)
    return {
        "session": session.to_public(),
        "live_briefing": briefing,
    }


@app.post("/api/session/{session_id}/turn")
async def text_turn(session_id: str, body: TextTurnRequest) -> dict[str, Any]:
    session = await _get_session(session_id)
    if not session:
        raise HTTPException(404, "session not found")

    advanced = store.maybe_auto_advance(session)
    if advanced:
        await kick_phase_prep(session)
    if session.phase == Phase.done:
        await _persist(session)
        return {
            "session": session.to_public(),
            "reply": "Interview complete.",
            "advanced": advanced,
        }

    user_text = body.text.strip()
    if body.diagram_labels:
        session.design_labels = body.diagram_labels
        labels = ", ".join(body.diagram_labels[:80])
        user_text = (
            f"{user_text}\n\n[Excalidraw labels / inventory]: {labels}"
            if user_text
            else f"[Excalidraw labels / inventory]: {labels}"
        )

    session.append("user", user_text)
    history = [{"role": m.role, "content": m.content} for m in session.messages[:-1]]

    reply = await chat_completion(
        system=session.system_prompt(),
        history=history,
        user_text=user_text,
    )
    session.append("assistant", reply)
    await _persist(session)
    return {"session": session.to_public(), "reply": reply, "advanced": advanced}


@app.post("/api/session/{session_id}/diagram")
async def submit_diagram(
    session_id: str,
    file: UploadFile = File(...),
    note: str = Form(""),
) -> dict[str, Any]:
    session = await _get_session(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    if session.phase != Phase.design:
        raise HTTPException(400, "diagram only accepted in design phase")

    raw = await file.read()
    if len(raw) > 4_000_000:
        raise HTTPException(400, "image too large")

    labels_note = ""
    if session.design_labels:
        labels_note = "Labels: " + ", ".join(session.design_labels[:80])
    user_text = (
        "Here is my architecture diagram (PNG). Critique it like a RAP interviewer: "
        "goal, boxes, flow, failures, metrics, why not alternatives. Keep it short.\n"
        f"{note}\n{labels_note}"
    ).strip()

    b64 = encode_png_bytes(raw)
    history = [{"role": m.role, "content": m.content} for m in session.messages]
    session.append("user", user_text + " [diagram attached]")
    reply = await chat_completion(
        system=session.system_prompt(),
        history=history,
        user_text=user_text,
        image_png_b64=b64,
    )
    session.append("assistant", reply)
    await _persist(session)
    return {"session": session.to_public(), "reply": reply}


@app.post("/api/tts")
async def tts(body: dict[str, str]) -> Response:
    text = (body.get("text") or "").strip()
    if not text:
        raise HTTPException(400, "text required")
    audio = await synthesize_mp3(text[:2000])
    if not audio:
        raise HTTPException(502, "tts failed")
    return Response(content=audio, media_type="audio/mpeg")


@app.websocket("/ws/live/{session_id}")
async def ws_live(websocket: WebSocket, session_id: str) -> None:
    await handle_live_socket(websocket, session_id)
