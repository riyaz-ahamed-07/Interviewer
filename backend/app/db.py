from __future__ import annotations

import logging
from typing import Any

import asyncpg

from .config import get_settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS interview_sessions (
        id UUID PRIMARY KEY,
        mode TEXT NOT NULL,
        run_style TEXT NOT NULL,
        debug_difficulty TEXT NOT NULL,
        phase TEXT NOT NULL,
        phase_started_at TIMESTAMPTZ NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        code_panel TEXT NOT NULL DEFAULT '',
        drill_title TEXT NOT NULL DEFAULT '',
        hidden_bugs JSONB NOT NULL DEFAULT '[]'::jsonb,
        cascade_note TEXT NOT NULL DEFAULT '',
        design_prompt JSONB NOT NULL DEFAULT '{}'::jsonb,
        design_labels JSONB NOT NULL DEFAULT '[]'::jsonb,
        llm_topics JSONB NOT NULL DEFAULT '[]'::jsonb,
        llm_topic_index INT NOT NULL DEFAULT 0,
        scorecard JSONB,
        meta JSONB NOT NULL DEFAULT '{}'::jsonb
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS interview_messages (
        id BIGSERIAL PRIMARY KEY,
        session_id UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        phase TEXT NOT NULL DEFAULT '',
        ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_interview_messages_session
        ON interview_messages(session_id, id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_interview_sessions_created
        ON interview_sessions(created_at DESC)
    """,
]


def database_url() -> str:
    return (get_settings().database_url or "").strip()


def db_configured() -> bool:
    return bool(database_url())


def _asyncpg_dsn(url: str) -> str:
    cleaned = url
    for part in ("channel_binding=require", "channel_binding=prefer"):
        cleaned = cleaned.replace(f"&{part}", "").replace(f"?{part}", "?")
    return cleaned.replace("?&", "?").rstrip("?&")


async def init_db() -> None:
    global _pool
    url = database_url()
    if not url:
        logger.warning("DATABASE_URL not set — session persistence disabled")
        return
    if _pool is not None:
        return
    dsn = _asyncpg_dsn(url)
    try:
        _pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=1,
            max_size=10,
            timeout=5,
            command_timeout=15,
        )
        async with _pool.acquire() as conn:
            for stmt in SCHEMA_STATEMENTS:
                await conn.execute(stmt)
        logger.info("Neon Postgres pool ready (asyncpg)")
    except Exception:
        logger.exception(
            "Neon Postgres unavailable over TCP — app will run without persistence. "
            "Check outbound 5432 / IPv6, or use neon HTTP smoke (scripts/neon-smoke.mjs)."
        )
        if _pool is not None:
            try:
                await _pool.close()
            except Exception:
                pass
            _pool = None


async def close_db() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def pool() -> asyncpg.Pool | None:
    return _pool


async def ping() -> dict[str, Any]:
    if _pool is None:
        return {"ok": False, "configured": db_configured(), "error": "pool not open"}
    try:
        async with _pool.acquire() as conn:
            row = await conn.fetchrow("SELECT 1 AS n, current_database() AS db")
        return {
            "ok": True,
            "configured": True,
            "database": row["db"] if row else None,
            "driver": "asyncpg",
        }
    except Exception as exc:
        logger.exception("db ping failed")
        return {"ok": False, "configured": True, "error": str(exc)}
