from __future__ import annotations

import logging
from typing import Any, Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from .config import get_settings
from .debug_gen import generate_debug_drill
from .design_gen import generate_design_prompt
from .llm_router import chat_completion, encode_png_bytes, get_router
from .scorecard import generate_scorecard
from .session import (
    DebugDifficulty,
    InterviewSession,
    Mode,
    Phase,
    RunStyle,
    store,
)
from .tts import synthesize_mp3
from .voice_live import handle_live_socket, live_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAP Mock Interviewer", version="0.1.0")
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartRequest(BaseModel):
    mode: Literal["soft", "medium", "strict", "hardcore"] = "medium"
    run_style: Literal["practice", "interview"] = "interview"
    debug_difficulty: Literal["easy", "medium", "hard"] = "medium"


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


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "llm_ready": get_router() is not None,
        "live": live_status(),
    }


async def ensure_design_prompt(session: InterviewSession) -> None:
    if session.phase != Phase.design or session.design_prompt:
        return
    design = await generate_design_prompt(session.debug_difficulty.value)
    store.apply_design(session, design)
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


@app.post("/api/session/start")
async def start_session(body: StartRequest) -> dict[str, Any]:
    session = store.create(
        mode=Mode(body.mode),
        run_style=RunStyle(body.run_style),
        debug_difficulty=DebugDifficulty(body.debug_difficulty),
    )
    return {"session": session.to_public()}


@app.get("/api/session/{session_id}")
async def get_session(session_id: str) -> dict[str, Any]:
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    if store.maybe_auto_advance(session):
        await after_phase_enter(session)
    return {"session": session.to_public()}


@app.post("/api/session/{session_id}/log")
async def log_turn(session_id: str, body: LogTurnRequest) -> dict[str, Any]:
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    session.append(body.role, body.content.strip())
    return {"ok": True, "n": len(session.messages)}


@app.post("/api/session/{session_id}/sync")
async def sync_messages(
    session_id: str, body: SyncMessagesRequest
) -> dict[str, Any]:
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    _apply_client_messages(session, body.messages)
    return {"session": session.to_public()}


@app.post("/api/session/{session_id}/advance")
async def advance(session_id: str, body: AdvanceRequest | None = None) -> dict[str, Any]:
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    if body and body.messages:
        _apply_client_messages(session, body.messages)
    store.advance_phase(session)
    await after_phase_enter(session)
    return {
        "session": session.to_public(),
        "reason": (body.reason if body else "manual"),
        "live_briefing": session.live_briefing(),
    }


@app.post("/api/session/{session_id}/llm/topic")
async def llm_topic(session_id: str, body: LlmTopicRequest) -> dict[str, Any]:
    session = store.get(session_id)
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
    return {
        "session": session.to_public(),
        "live_briefing": briefing,
    }


@app.post("/api/session/{session_id}/turn")
async def text_turn(session_id: str, body: TextTurnRequest) -> dict[str, Any]:
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")

    advanced = store.maybe_auto_advance(session)
    if advanced:
        await after_phase_enter(session)
    if session.phase == Phase.done:
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
    return {"session": session.to_public(), "reply": reply, "advanced": advanced}


@app.post("/api/session/{session_id}/diagram")
async def submit_diagram(
    session_id: str,
    file: UploadFile = File(...),
    note: str = Form(""),
) -> dict[str, Any]:
    session = store.get(session_id)
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
