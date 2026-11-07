from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from .db import pool
from .session import (
    ChatMessage,
    DebugDifficulty,
    InterviewSession,
    Mode,
    Phase,
    RunStyle,
)

logger = logging.getLogger(__name__)


def _ts(value: float) -> datetime:
    return datetime.fromtimestamp(value, tz=timezone.utc)


def _json(value: Any) -> str:
    return json.dumps(value if value is not None else None)


async def upsert_session(session: InterviewSession) -> None:
    p = pool()
    if p is None:
        return
    try:
        async with p.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO interview_sessions (
                        id, mode, run_style, debug_difficulty, phase,
                        phase_started_at, created_at, updated_at,
                        code_panel, drill_title, hidden_bugs, cascade_note,
                        design_prompt, design_labels, llm_topics, llm_topic_index,
                        scorecard
                    ) VALUES (
                        $1::uuid, $2, $3, $4, $5, $6, $7, NOW(),
                        $8, $9, $10::jsonb, $11, $12::jsonb, $13::jsonb,
                        $14::jsonb, $15, $16::jsonb
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        mode = EXCLUDED.mode,
                        run_style = EXCLUDED.run_style,
                        debug_difficulty = EXCLUDED.debug_difficulty,
                        phase = EXCLUDED.phase,
                        phase_started_at = EXCLUDED.phase_started_at,
                        updated_at = NOW(),
                        code_panel = EXCLUDED.code_panel,
                        drill_title = EXCLUDED.drill_title,
                        hidden_bugs = EXCLUDED.hidden_bugs,
                        cascade_note = EXCLUDED.cascade_note,
                        design_prompt = EXCLUDED.design_prompt,
                        design_labels = EXCLUDED.design_labels,
                        llm_topics = EXCLUDED.llm_topics,
                        llm_topic_index = EXCLUDED.llm_topic_index,
                        scorecard = EXCLUDED.scorecard
                    """,
                    session.id,
                    session.mode.value,
                    session.run_style.value,
                    session.debug_difficulty.value,
                    session.phase.value,
                    _ts(session.phase_started_at),
                    _ts(session.created_at),
                    session.code_panel,
                    session.drill_title,
                    _json(session.hidden_bugs),
                    session.cascade_note,
                    _json(session.design_prompt),
                    _json(session.design_labels),
                    _json(session.llm_topics),
                    session.llm_topic_index,
                    _json(session.scorecard),
                )
                await conn.execute(
                    "DELETE FROM interview_messages WHERE session_id = $1::uuid",
                    session.id,
                )
                if session.messages:
                    await conn.executemany(
                        """
                        INSERT INTO interview_messages
                            (session_id, role, content, phase, ts)
                        VALUES ($1::uuid, $2, $3, $4, $5)
                        """,
                        [
                            (
                                session.id,
                                m.role,
                                m.content,
                                m.phase,
                                _ts(m.ts),
                            )
                            for m in session.messages
                        ],
                    )
    except Exception:
        logger.exception("failed to persist session %s", session.id)


def _parse_json(value: Any, fallback: Any) -> Any:
    if value is None:
        return fallback
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return fallback
    return fallback


async def load_session(session_id: str) -> InterviewSession | None:
    p = pool()
    if p is None:
        return None
    try:
        async with p.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM interview_sessions WHERE id = $1::uuid",
                session_id,
            )
            if not row:
                return None
            messages = await conn.fetch(
                """
                SELECT role, content, phase, EXTRACT(EPOCH FROM ts) AS ts
                FROM interview_messages
                WHERE session_id = $1::uuid
                ORDER BY id ASC
                """,
                session_id,
            )
    except Exception:
        logger.exception("failed to load session %s", session_id)
        return None

    sid = row["id"]
    session = InterviewSession(
        id=str(sid) if isinstance(sid, UUID) else str(sid),
        mode=Mode(row["mode"]),
        run_style=RunStyle(row["run_style"]),
        debug_difficulty=DebugDifficulty(row["debug_difficulty"]),
        phase=Phase(row["phase"]),
        phase_started_at=row["phase_started_at"].timestamp(),
        code_panel=row["code_panel"] or "",
        drill_title=row["drill_title"] or "",
        hidden_bugs=list(_parse_json(row["hidden_bugs"], [])),
        cascade_note=row["cascade_note"] or "",
        design_prompt=dict(_parse_json(row["design_prompt"], {})),
        design_labels=list(_parse_json(row["design_labels"], [])),
        llm_topics=list(_parse_json(row["llm_topics"], [])),
        llm_topic_index=int(row["llm_topic_index"] or 0),
        scorecard=_parse_json(row["scorecard"], None),
        created_at=row["created_at"].timestamp(),
        messages=[
            ChatMessage(
                role=m["role"],
                content=m["content"],
                phase=m["phase"] or "",
                ts=float(m["ts"] or 0),
            )
            for m in messages
        ],
    )
    return session


async def list_history(limit: int = 20) -> list[dict[str, Any]]:
    p = pool()
    if p is None:
        return []
    try:
        async with p.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, mode, run_style, phase, created_at, updated_at,
                       drill_title, scorecard IS NOT NULL AS has_scorecard
                FROM interview_sessions
                ORDER BY created_at DESC
                LIMIT $1
                """,
                max(1, min(limit, 100)),
            )
    except Exception:
        logger.exception("failed to list history")
        return []
    return [
        {
            "id": str(r["id"]),
            "mode": r["mode"],
            "run_style": r["run_style"],
            "phase": r["phase"],
            "created_at": r["created_at"].isoformat(),
            "updated_at": r["updated_at"].isoformat(),
            "drill_title": r["drill_title"] or None,
            "has_scorecard": bool(r["has_scorecard"]),
        }
        for r in rows
    ]
