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
);

CREATE TABLE IF NOT EXISTS interview_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    phase TEXT NOT NULL DEFAULT '',
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_interview_messages_session
    ON interview_messages(session_id, id);

CREATE INDEX IF NOT EXISTS idx_interview_sessions_created
    ON interview_sessions(created_at DESC);
