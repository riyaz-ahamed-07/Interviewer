const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

export type Mode = "soft" | "medium" | "strict" | "hardcore";
export type RunStyle = "practice" | "interview";
export type DebugDifficulty = "easy" | "medium" | "hard";
export type Phase = "lobby" | "debug" | "design" | "llm" | "feedback" | "done";

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
  messages: { role: string; content: string; ts: number }[];
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

export async function advanceSession(id: string) {
  return json<{ session: Session; live_briefing?: string }>(
    `/api/session/${id}/advance`,
    {
      method: "POST",
      body: JSON.stringify({ reason: "manual" }),
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
  // labels go via a prior turn or note
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
