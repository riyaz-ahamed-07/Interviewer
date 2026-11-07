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
  | "done"
  | "friend"
  | "design_teacher";

export type ChatMsg = {
  role: string;
  content: string;
  ts: number;
  phase?: string;
};

export type PhaseScore = {
  score: number;
  strengths: string[];
  weaknesses: string[];
  note?: string;
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
  by_phase?: Record<string, PhaseScore | string>;
  copy_text: string;
};

export type LlmTopic = { technique: string; category: string };

export type PlannedQuestion = {
  text: string;
  source: "jd" | "resume" | "taxonomy" | "user_notes";
  follow_ups?: string[];
  what_good_looks_like?: string;
};

export type PlannedRound = {
  id: string;
  round_type: string;
  minutes: number;
  goal: string;
  questions: PlannedQuestion[];
  rubric: string[];
};

export type InterviewPlan = {
  company_name: string;
  company_type: string;
  role: string;
  level: string;
  persona: string;
  mode: Mode;
  run_style: RunStyle;
  difficulty: DebugDifficulty;
  jd_summary: string;
  resume_highlights: string[];
  jd_text?: string;
  resume_text?: string;
  user_notes?: string;
  voice?: boolean;
  camera?: boolean;
  avatar?: boolean;
  rounds: PlannedRound[];
  legacy?: boolean;
};

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
    duration_hint?: string;
  } | null;
  drill_title: string | null;
  llm_topics: LlmTopic[];
  llm_topic_index: number;
  scorecard: Scorecard | null;
  messages: ChatMsg[];
  plan?: InterviewPlan | null;
  round_index?: number;
  current_round?: PlannedRound | null;
  workspace?: string | null;
  persona?: string;
  resume_text?: string | null;
  use_plan_engine?: boolean;
};

export type Taxonomy = {
  version: number;
  round_types: Record<
    string,
    {
      label: string;
      default_minutes: number;
      workspace: string;
      rubric: string;
      family: string;
    }
  >;
  company_types: Record<
    string,
    {
      label: string;
      default_rounds: string[];
      difficulty: string;
      style_notes: string;
    }
  >;
  roles: Record<
    string,
    { label: string; add_rounds: string[]; topics: string[] }
  >;
  experience_levels: Record<string, { drop_rounds: string[]; depth: string }>;
  personas: Record<
    string,
    { label: string; probe_depth: number; interrupts: boolean }
  >;
  rubrics: Record<string, string[]>;
  score_bands: string[];
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

export function wsLiveUrl(sessionId: string, opts?: { resume?: boolean }) {
  const base = API_BASE.replace(/^http/, "ws");
  const q = opts?.resume ? "?resume=1" : "";
  return `${base}/ws/live/${sessionId}${q}`;
}

export async function health() {
  return json<{
    ok: boolean;
    llm_ready: boolean;
    live: Record<string, unknown>;
    db?: { ok?: boolean; error?: string };
    neon_branch?: string | null;
  }>("/api/health");
}

export async function fetchTaxonomy() {
  return json<Taxonomy>("/api/taxonomy");
}

export async function fetchDefaultRounds(
  companyType: string,
  role: string,
  level: string,
) {
  const q = new URLSearchParams({
    company_type: companyType,
    role,
    level,
  });
  return json<{
    rounds: Array<{
      round_type: string;
      label: string;
      minutes: number;
      workspace: string;
      family: string;
    }>;
  }>(`/api/taxonomy/defaults?${q}`);
}

export async function createPlan(body: Record<string, unknown>) {
  return json<{ plan: InterviewPlan }>("/api/plan", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function createSessionFromPlan(plan: InterviewPlan) {
  return json<{ session: Session; live_briefing?: string }>(
    "/api/session/create",
    {
      method: "POST",
      body: JSON.stringify({ plan }),
    },
  );
}

export async function startRapLegacy(
  mode: Mode = "medium",
  runStyle: RunStyle = "interview",
) {
  return json<{ session: Session }>("/api/session/legacy/rap", {
    method: "POST",
    body: JSON.stringify({
      mode,
      run_style: runStyle,
      debug_difficulty: "medium",
    }),
  });
}

export async function parseResume(file: File) {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`${API_BASE}/api/resume/parse`, {
    method: "POST",
    body: fd,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ text: string }>;
}

export async function summarizeDiagram(scene: {
  labels: string[];
  elements: Array<Record<string, unknown>>;
}) {
  return json<{
    labels: string[];
    edges: string[];
    adjacency_text: string;
    watch_blob: string;
  }>("/api/diagram/summary", {
    method: "POST",
    body: JSON.stringify(scene),
  });
}

export async function fetchHistory(limit = 20) {
  return json<{
    sessions: Array<{
      id: string;
      mode: string;
      run_style: string;
      phase: string;
      created_at: string;
      updated_at: string;
      drill_title: string | null;
      has_scorecard: boolean;
    }>;
  }>(`/api/history?limit=${limit}`);
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

export async function startFriendSession(mode: Mode = "medium") {
  return json<{ session: Session }>("/api/session/friend/start", {
    method: "POST",
    body: JSON.stringify({ mode }),
  });
}

export async function startDesignTeacherSession(mode: Mode = "medium") {
  return json<{ session: Session }>("/api/session/design-teacher/start", {
    method: "POST",
    body: JSON.stringify({ mode }),
  });
}

export async function nextDesignTeacherQuestion(id: string) {
  return json<{ session: Session; live_briefing?: string }>(
    `/api/session/${id}/design-teacher/next`,
    { method: "POST", body: "{}" },
  );
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

export type PaperSection = {
  id: string;
  heading: string;
  paragraphs: string[];
};

export type PaperEquation = {
  id: string;
  latex: string;
  section_id?: string;
  context?: string;
};

export type PaperReference = {
  raw: string;
  title?: string;
  arxiv_id?: string | null;
  doi?: string | null;
  year?: string | null;
  tldr?: string;
  abstract?: string;
};

export type PaperDoc = {
  id: string;
  title: string;
  authors: string[];
  arxiv_id?: string | null;
  abstract: string;
  sections: PaperSection[];
  equations: PaperEquation[];
  references: PaperReference[];
  source_url?: string;
  created_at?: string;
};

export type Pass1 = {
  problem: string;
  core_claim: string;
  method_one_line: string;
  key_figure?: string;
  main_results: string;
  five_cs: Record<string, string>;
  worth_deep_read: boolean;
  verdict: string;
};

export type ParentDelta = {
  component: string;
  before: string;
  after: string;
  why_it_matters?: string;
  section_id?: string;
};

export type ParentInfo = {
  title: string;
  arxiv_id?: string | null;
  one_liner: string;
  deltas: ParentDelta[];
};

export type Prerequisite = {
  id: string;
  name: string;
  why_needed?: string;
  check_question?: string;
  primer?: string;
  status: "known" | "shaky" | "unknown";
};

export type PaperConcept = {
  id: string;
  title: string;
  section_ids: string[];
  equation_ids: string[];
  summary: string;
  state: "not_started" | "taught" | "checked" | "mastered";
  learner_one_liner?: string;
};

export type PaperMap = {
  pass1: Pass1;
  parent: ParentInfo;
  prerequisites: Prerequisite[];
  concepts: PaperConcept[];
  glossary: Record<string, string>;
  diagrams: Record<string, string>;
};

export type FlashCard = {
  id: string;
  paper_id: string;
  concept_id?: string;
  question: string;
  answer: string;
  ease?: number;
  interval_days?: number;
  due_at?: string;
  reps?: number;
};

export type ReadingLogEntry = {
  id: string;
  paper_id: string;
  title?: string;
  started_at?: string;
  finished_at?: string | null;
  minutes?: number;
  concepts_mastered?: number;
  summary?: string;
};

export type PaperSession = {
  id: string;
  paper_id: string;
  current_concept_index: number;
  mode: "text" | "voice";
  messages: Array<{ role: string; content: string }>;
  notes: string;
  created_at?: string;
};

export type PaperLibrary = {
  papers: Array<{
    id: string;
    title: string;
    arxiv_id?: string | null;
    created_at?: string;
    abstract?: string;
  }>;
  log: ReadingLogEntry[];
  due_cards: FlashCard[];
};

export async function fetchPaperLibrary() {
  return json<PaperLibrary>("/api/paper/library");
}

export async function ingestPaper(body: {
  arxiv_url?: string;
  arxiv_id?: string;
  text?: string;
  title_hint?: string;
}) {
  return json<{ paper: PaperDoc; map: PaperMap; cards: FlashCard[] }>(
    "/api/paper/ingest",
    { method: "POST", body: JSON.stringify(body) },
  );
}

export async function ingestPaperPdf(file: File) {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`${API_BASE}/api/paper/ingest/pdf`, {
    method: "POST",
    body: fd,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{
    paper: PaperDoc;
    map: PaperMap;
    cards: FlashCard[];
  }>;
}

export async function getPaper(paperId: string) {
  return json<{
    paper: PaperDoc;
    map: PaperMap | null;
    cards: FlashCard[];
  }>(`/api/paper/${paperId}`);
}

export async function startPaperSession(
  paperId: string,
  mode: "text" | "voice" = "text",
) {
  return json<{ session: PaperSession; map: PaperMap }>(
    `/api/paper/${paperId}/session`,
    { method: "POST", body: JSON.stringify({ paper_id: paperId, mode }) },
  );
}

export async function getPaperSession(sessionId: string) {
  return json<{
    session: PaperSession;
    paper: PaperDoc | null;
    map: PaperMap | null;
  }>(`/api/paper/session/${sessionId}`);
}

export async function paperChat(
  sessionId: string,
  text: string,
  conceptId?: string,
) {
  return json<{
    session: PaperSession;
    reply: string;
    concept: PaperConcept;
    map: PaperMap;
  }>(`/api/paper/session/${sessionId}/chat`, {
    method: "POST",
    body: JSON.stringify({ text, concept_id: conceptId ?? null }),
  });
}

export async function paperAdvance(
  sessionId: string,
  action: "got_it" | "skip" | "deeper",
  oneLiner = "",
) {
  return json<{ session: PaperSession; map: PaperMap }>(
    `/api/paper/session/${sessionId}/advance`,
    {
      method: "POST",
      body: JSON.stringify({ action, one_liner: oneLiner }),
    },
  );
}

export async function setPaperPrereqs(
  paperId: string,
  statuses: Record<string, "known" | "shaky" | "unknown">,
) {
  return json<{ map: PaperMap }>(`/api/paper/${paperId}/prereqs`, {
    method: "POST",
    body: JSON.stringify({ statuses }),
  });
}

export async function explainSelection(
  paperId: string,
  body: {
    selection: string;
    paragraph?: string;
    section_id?: string;
    kind?: "term" | "equation" | "sentence";
  },
) {
  return json<{
    short: string;
    deeper: string;
    symbols?: Array<{ symbol: string; meaning: string; shape?: string }>;
    example?: string;
  }>(`/api/paper/${paperId}/explain`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function fetchPaperRef(
  paperId: string,
  index: number,
  citing = "",
) {
  const q = citing ? `?citing=${encodeURIComponent(citing)}` : "";
  return json<{
    reference: PaperReference;
    context: Record<string, string>;
  }>(`/api/paper/${paperId}/refs/${index}${q}`);
}

export async function reviewFlashCard(cardId: string, grade: number) {
  return json<{ card: FlashCard }>("/api/paper/cards/review", {
    method: "POST",
    body: JSON.stringify({ card_id: cardId, grade }),
  });
}
