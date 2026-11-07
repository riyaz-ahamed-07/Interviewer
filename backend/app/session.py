from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .config import get_settings
from .prompts import build_system_prompt, live_phase_briefing, opening_line
from .taxonomy import InterviewPlan, PlannedRound
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
    intro = "intro"
    debug = "debug"
    design = "design"
    llm = "llm"
    feedback = "feedback"
    done = "done"
    friend = "friend"
    design_teacher = "design_teacher"


PHASE_ORDER = [
    Phase.intro,
    Phase.debug,
    Phase.design,
    Phase.llm,
    Phase.feedback,
    Phase.done,
]


@dataclass
class ChatMessage:
    role: str
    content: str
    ts: float = field(default_factory=time.time)
    phase: str = ""


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
    llm_topic_index: int = 0
    scorecard: dict[str, Any] | None = None
    created_at: float = field(default_factory=time.time)
    plan: InterviewPlan | None = None
    round_index: int = 0
    persona: str = "friendly_senior"
    resume_text: str = ""
    jd_text: str = ""
    use_plan_engine: bool = False

    def current_round(self) -> PlannedRound | None:
        if not self.plan or not self.plan.rounds:
            return None
        if self.round_index < 0 or self.round_index >= len(self.plan.rounds):
            return None
        return self.plan.rounds[self.round_index]

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
                "duration_hint": "standard",
            },
            "run_style": self.run_style.value,
            "mode": self.mode.value,
            "llm_topics": self.llm_topics,
            "llm_topic_index": self.llm_topic_index,
        }

    def live_briefing(self) -> str:
        return live_phase_briefing(
            self.phase.value,
            self.context(),
            tone=self.mode.value,
            run_style=self.run_style.value,
        )

    def llm_topic_briefing(self) -> str:
        topics = self.llm_topics
        if not topics:
            return self.live_briefing()
        idx = max(0, min(self.llm_topic_index, len(topics) - 1))
        tech = topics[idx].get("technique") or "this topic"
        cat = topics[idx].get("category") or ""
        return (
            "[SYSTEM TOPIC NAV — do not restart the interview]\n"
            f"Stay in LLM techniques phase. Candidate jumped to topic "
            f"{idx + 1}/{len(topics)}"
            + (f" [{cat}]" if cat else "")
            + f".\nAsk ONLY: Define {tech}.\n"
            "One short question. STOP and wait. Do not teach. Do not wrap up."
        )

    def phase_budget_seconds(self) -> int:
        if self.use_plan_engine and self.current_round():
            return int(self.current_round().minutes) * 60
        s = get_settings()
        return {
            Phase.intro: s.intro_seconds,
            Phase.debug: s.debug_seconds,
            Phase.design: s.design_seconds,
            Phase.llm: s.llm_seconds,
            Phase.feedback: 180,
            Phase.friend: 0,
            Phase.design_teacher: 0,
        }.get(self.phase, 0)

    def seconds_remaining(self) -> int:
        budget = self.phase_budget_seconds()
        if budget <= 0:
            return 0
        elapsed = time.time() - self.phase_started_at
        return max(0, int(budget - elapsed))

    def system_prompt(self) -> str:
        if self.use_plan_engine and self.plan and self.current_round():
            from .round_prompts import full_system_prompt

            return full_system_prompt(self.plan, self.current_round())
        return build_system_prompt(
            self.mode.value,
            self.phase.value,
            self.context(),
            run_style=self.run_style.value,
        )

    def append(self, role: str, content: str) -> None:
        round_id = ""
        if self.use_plan_engine and self.current_round():
            round_id = self.current_round().id
        self.messages.append(
            ChatMessage(
                role=role,
                content=content,
                phase=round_id or self.phase.value,
            )
        )

    def to_public(self) -> dict[str, Any]:
        ctx = self.context()
        topics_public = [
            {
                "technique": t.get("technique", ""),
                "category": t.get("category", ""),
            }
            for t in self.llm_topics
        ]
        round_ = self.current_round()
        workspace = "none"
        if round_:
            from .taxonomy import load_taxonomy

            meta = load_taxonomy()["round_types"].get(round_.round_type) or {}
            workspace = str(meta.get("workspace") or "none")
        show_design = self.phase in (Phase.design, Phase.design_teacher) or (
            self.use_plan_engine and "whiteboard" in workspace
        )
        show_code = self.phase == Phase.debug or (
            self.use_plan_engine and "code" in workspace
        )
        return {
            "id": self.id,
            "mode": self.mode.value,
            "run_style": self.run_style.value,
            "debug_difficulty": self.debug_difficulty.value,
            "phase": self.phase.value,
            "seconds_remaining": self.seconds_remaining(),
            "phase_budget_seconds": self.phase_budget_seconds(),
            "code_panel": self.code_panel,
            "design_prompt": (ctx["design"] if show_design else None),
            "drill_title": self.drill_title if show_code else None,
            "llm_topics": topics_public,
            "llm_topic_index": self.llm_topic_index,
            "scorecard": self.scorecard,
            "plan": self.plan.model_dump() if self.plan else None,
            "round_index": self.round_index,
            "current_round": round_.model_dump() if round_ else None,
            "workspace": workspace if self.use_plan_engine else None,
            "persona": self.persona,
            "resume_text": self.resume_text if workspace == "resume" else None,
            "use_plan_engine": self.use_plan_engine,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "ts": m.ts,
                    "phase": m.phase,
                }
                for m in self.messages[-80:]
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
            phase=Phase.intro,
            phase_started_at=time.time(),
            code_panel="",
            drill_title="",
        )
        line = opening_line(
            Phase.intro.value, session.context(), session.run_style.value
        )
        session.append("assistant", line)
        self._sessions[session.id] = session
        return session

    def create_friend(self, mode: Mode) -> InterviewSession:
        session = InterviewSession(
            id=str(uuid.uuid4()),
            mode=mode,
            run_style=RunStyle.practice,
            debug_difficulty=DebugDifficulty.medium,
            phase=Phase.friend,
            phase_started_at=time.time(),
            code_panel="",
            drill_title="",
        )
        line = opening_line(
            Phase.friend.value, session.context(), session.run_style.value
        )
        session.append("assistant", line)
        self._sessions[session.id] = session
        return session

    def create_design_teacher(self, mode: Mode) -> InterviewSession:
        session = InterviewSession(
            id=str(uuid.uuid4()),
            mode=mode,
            run_style=RunStyle.practice,
            debug_difficulty=DebugDifficulty.medium,
            phase=Phase.design_teacher,
            phase_started_at=time.time(),
            code_panel="",
            drill_title="",
            design_prompt={},
        )
        self._sessions[session.id] = session
        return session

    def apply_drill(self, session: InterviewSession, drill: dict[str, Any]) -> None:
        session.drill_title = str(drill.get("title") or "PyTorch debug")
        session.code_panel = str(drill.get("code") or "")
        session.hidden_bugs = list(drill.get("hidden_bugs") or [])
        session.cascade_note = str(drill.get("cascade_note") or "")

    def apply_design(self, session: InterviewSession, design: dict[str, Any]) -> None:
        session.design_prompt = {
            "id": str(design.get("id") or "generated"),
            "title": str(design.get("title") or "System design"),
            "summary": str(design.get("summary") or ""),
            "ask": str(design.get("ask") or ""),
            "duration_hint": str(design.get("duration_hint") or "standard"),
        }

    def get(self, session_id: str) -> InterviewSession | None:
        return self._sessions.get(session_id)

    def put(self, session: InterviewSession) -> None:
        self._sessions[session.id] = session

    def create_from_plan(self, plan: InterviewPlan) -> InterviewSession:
        difficulty = DebugDifficulty(plan.difficulty)
        session = InterviewSession(
            id=str(uuid.uuid4()),
            mode=Mode(plan.mode),
            run_style=RunStyle(plan.run_style),
            debug_difficulty=difficulty,
            phase=Phase.intro,
            phase_started_at=time.time(),
            plan=plan,
            round_index=0,
            persona=plan.persona,
            resume_text=plan.resume_text,
            jd_text=plan.jd_text,
            use_plan_engine=True,
        )
        if plan.legacy:
            session.use_plan_engine = False
            line = opening_line(
                Phase.intro.value, session.context(), session.run_style.value
            )
            session.append("assistant", line)
        else:
            round_ = session.current_round()
            first_q = (
                round_.questions[0].text
                if round_ and round_.questions
                else "Tell me about yourself."
            )
            label = round_.round_type if round_ else "intro"
            session.append(
                "assistant",
                f"Hi — thanks for joining. We'll start with {label.replace('_', ' ')}. {first_q}",
            )
        self._sessions[session.id] = session
        return session

    def advance_phase(self, session: InterviewSession) -> InterviewSession:
        if session.phase in (Phase.friend, Phase.design_teacher):
            return session
        if session.use_plan_engine and session.plan:
            nxt = session.round_index + 1
            if nxt >= len(session.plan.rounds):
                session.phase = Phase.feedback
                session.use_plan_engine = False
                session.phase_started_at = time.time()
                return session
            session.round_index = nxt
            session.phase_started_at = time.time()
            session.code_panel = ""
            session.design_prompt = {}
            round_ = session.current_round()
            if round_:
                first_q = (
                    round_.questions[0].text
                    if round_.questions
                    else f"Let's begin {_round_label(round_.round_type)}."
                )
                session.append(
                    "assistant",
                    f"Thanks. Let's move to {_round_label(round_.round_type)}. {first_q}",
                )
            return session
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
            session.llm_topic_index = 0
        if nxt not in (Phase.debug, Phase.design, Phase.feedback, Phase.done):
            line = opening_line(nxt.value, session.context(), session.run_style.value)
            session.append("assistant", line)
        return session

    def append_phase_opening(self, session: InterviewSession) -> None:
        line = opening_line(
            session.phase.value, session.context(), session.run_style.value
        )
        session.append("assistant", line)

    def append_design_opening(self, session: InterviewSession) -> None:
        self.append_phase_opening(session)

    def set_llm_topic(self, session: InterviewSession, index: int) -> str:
        if not session.llm_topics:
            session.llm_topics = sample_session_topics()
        n = len(session.llm_topics)
        session.llm_topic_index = max(0, min(index, n - 1))
        tech = session.llm_topics[session.llm_topic_index].get("technique") or "this"
        line = (
            f"Let's revisit topic {session.llm_topic_index + 1} of {n}. "
            f"Define {tech}."
        )
        session.append("assistant", line)
        return session.llm_topic_briefing()

    def maybe_auto_advance(self, session: InterviewSession) -> bool:
        if session.phase in (
            Phase.lobby,
            Phase.done,
            Phase.feedback,
            Phase.friend,
            Phase.design_teacher,
        ):
            return False
        if session.use_plan_engine and session.run_style == RunStyle.practice:
            return False
        if (
            session.phase == Phase.intro
            and session.run_style == RunStyle.practice
            and not session.use_plan_engine
        ):
            return False
        if session.seconds_remaining() <= 0:
            self.advance_phase(session)
            return True
        return False


def _round_label(round_type: str) -> str:
    from .taxonomy import load_taxonomy

    meta = load_taxonomy()["round_types"].get(round_type) or {}
    return str(meta.get("label") or round_type.replace("_", " "))


store = SessionStore()
