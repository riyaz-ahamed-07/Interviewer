from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .config import get_settings
from .prompts import build_system_prompt, live_phase_briefing, opening_line
from .technique_bank import sample_session_topics


class Mode(str, Enum):
    soft = "soft"
    medium = "medium"
    strict = "strict"
    hardcore = "hardcore"


class RunStyle(str, Enum):
    practice = "practice"
    interview = "interview"


class DebugDifficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Phase(str, Enum):
    lobby = "lobby"
    debug = "debug"
    design = "design"
    llm = "llm"
    feedback = "feedback"
    done = "done"


PHASE_ORDER = [Phase.debug, Phase.design, Phase.llm, Phase.feedback, Phase.done]


@dataclass
class ChatMessage:
    role: str
    content: str
    ts: float = field(default_factory=time.time)


@dataclass
class InterviewSession:
    id: str
    mode: Mode
    run_style: RunStyle
    debug_difficulty: DebugDifficulty
    phase: Phase
    phase_started_at: float
    messages: list[ChatMessage] = field(default_factory=list)
    code_panel: str = ""
    drill_title: str = ""
    hidden_bugs: list[str] = field(default_factory=list)
    cascade_note: str = ""
    design_prompt: dict[str, Any] = field(default_factory=dict)
    design_labels: list[str] = field(default_factory=list)
    llm_topics: list[dict[str, str]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def context(self) -> dict[str, Any]:
        return {
            "drill_title": self.drill_title,
            "code": self.code_panel,
            "debug_difficulty": self.debug_difficulty.value,
            "hidden_bugs": self.hidden_bugs,
            "cascade_note": self.cascade_note,
            "design": self.design_prompt
            or {
                "id": "pending",
                "title": "System design",
                "summary": "Generating a unique design prompt…",
                "ask": "Wait a moment, then draw your architecture.",
            },
            "run_style": self.run_style.value,
            "mode": self.mode.value,
            "llm_topics": self.llm_topics,
        }

    def live_briefing(self) -> str:
        return live_phase_briefing(
            self.phase.value,
            self.context(),
            tone=self.mode.value,
            run_style=self.run_style.value,
        )

    def phase_budget_seconds(self) -> int:
        s = get_settings()
        return {
            Phase.debug: s.debug_seconds,
            Phase.design: s.design_seconds,
            Phase.llm: s.llm_seconds,
            Phase.feedback: 90,
        }.get(self.phase, 0)

    def seconds_remaining(self) -> int:
        budget = self.phase_budget_seconds()
        if budget <= 0:
            return 0
        elapsed = time.time() - self.phase_started_at
        return max(0, int(budget - elapsed))

    def system_prompt(self) -> str:
        return build_system_prompt(
            self.mode.value,
            self.phase.value,
            self.context(),
            run_style=self.run_style.value,
        )

    def to_public(self) -> dict[str, Any]:
        ctx = self.context()
        return {
            "id": self.id,
            "mode": self.mode.value,
            "run_style": self.run_style.value,
            "debug_difficulty": self.debug_difficulty.value,
            "phase": self.phase.value,
            "seconds_remaining": self.seconds_remaining(),
            "phase_budget_seconds": self.phase_budget_seconds(),
            "code_panel": self.code_panel,
            "design_prompt": ctx["design"] if self.phase == Phase.design else None,
            "drill_title": self.drill_title if self.phase == Phase.debug else None,
            "messages": [
                {"role": m.role, "content": m.content, "ts": m.ts}
                for m in self.messages[-40:]
            ],
        }


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, InterviewSession] = {}

    def create(
        self,
        mode: Mode,
        run_style: RunStyle,
        debug_difficulty: DebugDifficulty,
    ) -> InterviewSession:
        difficulty = debug_difficulty
        if run_style == RunStyle.interview and difficulty == DebugDifficulty.easy:
            difficulty = DebugDifficulty.medium

        session = InterviewSession(
            id=str(uuid.uuid4()),
            mode=mode,
            run_style=run_style,
            debug_difficulty=difficulty,
            phase=Phase.debug,
            phase_started_at=time.time(),
            code_panel="Generating unique debug snippet…",
            drill_title="Generating…",
        )
        self._sessions[session.id] = session
        return session

    def apply_drill(self, session: InterviewSession, drill: dict[str, Any]) -> None:
        session.drill_title = str(drill.get("title") or "PyTorch debug")
        session.code_panel = str(drill.get("code") or "")
        session.hidden_bugs = list(drill.get("hidden_bugs") or [])
        session.cascade_note = str(drill.get("cascade_note") or "")
        if not session.messages:
            line = opening_line(
                Phase.debug.value, session.context(), session.run_style.value
            )
            session.messages.append(ChatMessage(role="assistant", content=line))

    def apply_design(self, session: InterviewSession, design: dict[str, Any]) -> None:
        session.design_prompt = {
            "id": str(design.get("id") or "generated"),
            "title": str(design.get("title") or "System design"),
            "summary": str(design.get("summary") or ""),
            "ask": str(design.get("ask") or ""),
        }

    def get(self, session_id: str) -> InterviewSession | None:
        return self._sessions.get(session_id)

    def advance_phase(self, session: InterviewSession) -> InterviewSession:
        idx = PHASE_ORDER.index(session.phase)
        if idx >= len(PHASE_ORDER) - 1:
            session.phase = Phase.done
            return session
        nxt = PHASE_ORDER[idx + 1]
        session.phase = nxt
        session.phase_started_at = time.time()
        if nxt == Phase.design:
            session.code_panel = ""
        if nxt == Phase.llm and not session.llm_topics:
            session.llm_topics = sample_session_topics()
        if nxt == Phase.done:
            return session
        # Opening for design is appended after design prompt is applied (async)
        if nxt != Phase.design:
            line = opening_line(nxt.value, session.context(), session.run_style.value)
            session.messages.append(ChatMessage(role="assistant", content=line))
        return session

    def append_design_opening(self, session: InterviewSession) -> None:
        line = opening_line(
            Phase.design.value, session.context(), session.run_style.value
        )
        session.messages.append(ChatMessage(role="assistant", content=line))

    def maybe_auto_advance(self, session: InterviewSession) -> bool:
        if session.phase in (Phase.lobby, Phase.done, Phase.feedback):
            return False
        if session.seconds_remaining() <= 0:
            self.advance_phase(session)
            return True
        return False


store = SessionStore()
