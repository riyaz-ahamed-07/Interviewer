const API_BASE = String(
  import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000",
).replace(/\/+$/, "");

export type Mode = "soft" | "medium" | "strict" | "hardcore";
export type RunStyle = "practice" | "interview";
export type DebugDifficulty = "easy" | "medium" | "hard";
export type Phase =
  | "lobby"
  | "intro"
  | "debug"
  | "design"
  | "llm"
  | "feedback"
  | "done";

export type ChatMsg = {
  role: string;
  content: string;
  ts: number;
  phase?: string;
};

export type Scorecard = {
  score: number;
  summary: string;
  strengths: string[];
  improve: string[];
  focus_next: string[];
  english: {
    fillers_to_avoid?: string[];
    manner?: string;
    answer_openers?: string[];
    notes?: string[];
  };
  by_phase?: Record<string, string>;
  copy_text: string;
};

export type LlmTopic = { technique: string; category: string };

export type Session = {
  id: string;
  mode: Mode;
  run_style: RunStyle;
  debug_difficulty: DebugDifficulty;
  phase: Phase;
  seconds_remaining: number;
  phase_budget_seconds: number;
  code_panel: string;
  design_prompt: {
    id: string;
    title: string;
    summary: string;
    ask: string;
  } | null;
  drill_title: string | null;
  llm_topics: LlmTopic[];
  llm_topic_index: number;
  scorecard: Scorecard | null;
  messages: ChatMsg[];
};

export class SessionGoneError extends Error {
  constructor(message = "session not found") {
    super(message);
    this.name = "SessionGoneError";
  }
}

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    if (res.status === 404 && /session not found/i.test(text)) {
      throw new SessionGoneError(text);
    }
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export function apiBase() {
  return API_BASE;
}

export function wsLiveUrl(sessionId: string) {
  const base = API_BASE.replace(/^http/, "ws");
  return `${base}/ws/live/${sessionId}`;
}

export async function health() {
  return json<{
    ok: boolean;
    llm_ready: boolean;
    live: Record<string, unknown>;
  }>("/api/health");
}

export async function startSession(
  mode: Mode,
  runStyle: RunStyle,
  debugDifficulty: DebugDifficulty,
) {
  return json<{ session: Session }>("/api/session/start", {
    method: "POST",
    body: JSON.stringify({
      mode,
      run_style: runStyle,
      debug_difficulty: debugDifficulty,
    }),
  });
}

export async function getSession(id: string) {
  return json<{ session: Session }>(`/api/session/${id}`);
}

export async function advanceSession(id: string, messages?: ChatMsg[]) {
  return json<{
    session: Session;
    live_briefing?: string;
    preparing?: boolean;
  }>(`/api/session/${id}/advance`, {
    method: "POST",
    body: JSON.stringify({
      reason: "manual",
      messages: messages?.map((m) => ({
        role: m.role,
        content: m.content,
        ts: m.ts,
        phase: m.phase ?? "",
      })),
    }),
  });
}

export async function logTurn(
  id: string,
  role: "user" | "assistant",
  content: string,
) {
  return json<{ ok: boolean }>(`/api/session/${id}/log`, {
    method: "POST",
    body: JSON.stringify({ role, content }),
  });
}

export async function navigateLlmTopic(
  id: string,
  direction: "prev" | "next" | "goto",
  index?: number,
) {
  return json<{ session: Session; live_briefing?: string }>(
    `/api/session/${id}/llm/topic`,
    {
      method: "POST",
      body: JSON.stringify({ direction, index }),
    },
  );
}

export async function textTurn(
  id: string,
  text: string,
  diagramLabels: string[] = [],
) {
  return json<{ session: Session; reply: string }>(`/api/session/${id}/turn`, {
    method: "POST",
    body: JSON.stringify({ text, diagram_labels: diagramLabels }),
  });
}

export async function submitDiagram(
  id: string,
  blob: Blob,
  note: string,
  labels: string[],
) {
  const fd = new FormData();
  fd.append("file", blob, "diagram.png");
  fd.append("note", note);
  if (labels.length) {
    fd.set("note", `${note}\nLabels: ${labels.join(", ")}`);
  }
  const res = await fetch(`${API_BASE}/api/session/${id}/diagram`, {
    method: "POST",
    body: fd,
  });
  if (!res.ok) {
    const text = await res.text();
    if (res.status === 404 && /session not found/i.test(text)) {
      throw new SessionGoneError(text);
    }
    throw new Error(text);
  }
  return res.json() as Promise<{ session: Session; reply: string }>;
}

export async function speakFallback(text: string) {
  const res = await fetch(`${API_BASE}/api/tts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error("tts failed");
  return res.blob();
}
