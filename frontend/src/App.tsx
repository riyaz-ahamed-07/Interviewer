import { useCallback, useEffect, useRef, useState } from "react";
import {
  advanceSession,
  getSession,
  health,
  SessionGoneError,
  speakFallback,
  startSession,
  submitDiagram,
  textTurn,
  type DebugDifficulty,
  type Mode,
  type RunStyle,
  type Session,
} from "./api";
import { Board, type CanvasScene } from "./components/Board";
import { useLiveVoice } from "./hooks/useLiveVoice";
import "./App.css";

const TONES: { id: Mode; label: string; blurb: string }[] = [
  { id: "soft", label: "Soft", blurb: "Calm tone" },
  { id: "medium", label: "Medium", blurb: "Crisp" },
  { id: "strict", label: "Strict", blurb: "Cut waffle" },
  { id: "hardcore", label: "Hardcore", blurb: "Skeptical" },
];

export default function App() {
  const [mode, setMode] = useState<Mode>("medium");
  const [runStyle, setRunStyle] = useState<RunStyle>("interview");
  const [debugDifficulty, setDebugDifficulty] =
    useState<DebugDifficulty>("medium");
  const [session, setSession] = useState<Session | null>(null);
  const [paste, setPaste] = useState("");
  const [statusLine, setStatusLine] = useState("Checking backend…");
  const [wantLive, setWantLive] = useState(true);
  const [busy, setBusy] = useState(false);
  const transcriptRef = useRef<HTMLDivElement>(null);

  const onTurn = useCallback((role: "user" | "assistant", text: string) => {
    setSession((prev) => {
      if (!prev || !text.trim()) return prev;
      return {
        ...prev,
        messages: [
          ...prev.messages,
          { role, content: text, ts: Date.now() / 1000 },
        ],
      };
    });
  }, []);

  const live = useLiveVoice(onTurn);

  const bumpToLobby = useCallback(
    (reason: string) => {
      live.disconnect();
      setSession(null);
      setPaste("");
      setStatusLine(reason);
    },
    [live],
  );

  useEffect(() => {
    health()
      .then((h) => {
        setStatusLine(
          h.llm_ready
            ? `Backend OK · ${h.live.key_count ?? 0} Gemini keys`
            : "Backend OK · add GEMINI_API_KEY_1=... to backend/.env",
        );
      })
      .catch(() => setStatusLine("Backend offline — start uvicorn on :8000"));
  }, []);

  useEffect(() => {
    if (!session) return;
    const t = setInterval(() => {
      void getSession(session.id)
        .then((r) =>
          setSession((prev) => {
            if (!prev) return r.session;
            return {
              ...r.session,
              messages:
                prev.messages.length >= r.session.messages.length
                  ? prev.messages
                  : r.session.messages,
              code_panel: r.session.code_panel || prev.code_panel,
              drill_title: r.session.drill_title ?? prev.drill_title,
            };
          }),
        )
        .catch((e) => {
          if (e instanceof SessionGoneError) {
            bumpToLobby(
              "Session expired (backend reloaded). Start a new interview.",
            );
          }
        });
    }, 10000);
    return () => clearInterval(t);
  }, [session?.id, bumpToLobby]);

  // Keep transcript scrolled inside its panel only — never jump the page
  useEffect(() => {
    const el = transcriptRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [session?.messages.length]);

  const playTts = async (text: string) => {
    if (!text.trim()) return;
    try {
      const blob = await speakFallback(text);
      const url = URL.createObjectURL(blob);
      await new Audio(url).play();
    } catch {
      /* silent */
    }
  };

  const start = async () => {
    setBusy(true);
    setStatusLine("Generating a unique debug snippet…");
    try {
      const { session: s } = await startSession(
        mode,
        runStyle,
        debugDifficulty,
      );
      setSession(s);
      setStatusLine(
        `${s.run_style} · debug ${s.debug_difficulty} · ${s.drill_title ?? ""}`,
      );
      if (wantLive) {
        try {
          await live.connect(s.id);
        } catch (e) {
          setWantLive(false);
          setStatusLine(`Live failed (${String(e)}). Text + TTS fallback.`);
          await playTts(s.messages.at(-1)?.content ?? "");
        }
      } else {
        await playTts(s.messages.at(-1)?.content ?? "");
      }
    } finally {
      setBusy(false);
    }
  };

  const voiceActive =
    wantLive &&
    !live.paused &&
    (live.status === "listening" ||
      live.status === "speaking" ||
      live.status === "connecting" ||
      live.status === "live");

  const sendPaste = async () => {
    if (!session || !paste.trim()) return;
    setBusy(true);
    try {
      if (voiceActive) {
        live.sendText(
          `Candidate pasted this while debugging (respond by voice):\n\`\`\`\n${paste}\n\`\`\``,
        );
        onTurn("user", `[paste]\n${paste}`);
        setPaste("");
      } else {
        const { session: s, reply } = await textTurn(session.id, paste);
        setSession(s);
        setPaste("");
        await playTts(reply);
      }
    } catch (e) {
      if (e instanceof SessionGoneError) {
        bumpToLobby(
          "Session expired (backend reloaded). Start a new interview.",
        );
      } else setStatusLine(String(e));
    } finally {
      setBusy(false);
    }
  };

  const onBoardWatch = useCallback(
    (scene: CanvasScene) => {
      if (!voiceActive) return;
      // Excalidraw scene JSON (not an image). Silent context only.
      live.sendText(
        "[CANVAS WATCH — silent context only. Do NOT speak or acknowledge. " +
          "Use this when you next reply to the candidate's voice.]\n" +
          JSON.stringify(scene),
      );
    },
    [live, voiceActive],
  );

  const onBoard = useCallback(
    async (blob: Blob, labels: string[]) => {
      if (!session) return;
      setBusy(true);
      try {
        if (voiceActive) {
          // Same as before: PNG + labels, then ask for a spoken critique.
          live.sendImagePng(await blob.arrayBuffer(), {
            silent: false,
            mime: "image/png",
          });
          live.sendText(
            `Architecture diagram submitted. Labels: ${labels.join(", ") || "(none)"}. Critique out loud, briefly.`,
          );
        } else {
          const { session: s, reply } = await submitDiagram(
            session.id,
            blob,
            "Please critique my architecture.",
            labels,
          );
          setSession(s);
          await playTts(reply);
        }
      } catch (e) {
        if (e instanceof SessionGoneError) {
          bumpToLobby(
            "Session expired (backend reloaded). Start a new interview.",
          );
        }
      } finally {
        setBusy(false);
      }
    },
    [bumpToLobby, live, session, voiceActive],
  );

  const nextPhase = async () => {
    if (!session) return;
    try {
      const { session: s, live_briefing } = await advanceSession(session.id);
      setSession(s);
      const line = s.messages.at(-1)?.content ?? "";
      if (voiceActive) {
        live.sendPhaseSync(live_briefing ?? line);
      } else await playTts(line);
    } catch (e) {
      if (e instanceof SessionGoneError) {
        bumpToLobby(
          "Session expired (backend reloaded). Start a new interview.",
        );
      }
    }
  };

  const mmss = (s: number) =>
    `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, "0")}`;

  const liveLabel =
    live.status === "paused"
      ? "Paused (tokens saved)"
      : live.status === "speaking"
        ? "AI speaking"
        : live.status === "listening"
          ? "Listening"
          : live.status === "connecting"
            ? "Connecting…"
            : live.status === "error" || live.status === "fallback"
              ? `Live issue: ${live.error ?? live.status}`
              : live.status;

  if (!session) {
    return (
      <div className="shell lobby">
        <header>
          <p className="eyebrow">Same notebook feel as the master notes</p>
          <h1>
            ML Mock <span>Interviewer</span>
          </h1>
          <p className="lede">
            Each run builds a new chained debug. Practice gives hints. Interview
            does not.
          </p>
          <p className="status">{statusLine}</p>
          <p className="lede">
            <a
              className="notes-link"
              href="/notes/ml-engineer-interview-notes.html"
            >
              Open master notes →
            </a>
          </p>
        </header>

        <p className="section-label">Run style</p>
        <section className="modes two">
          <button
            type="button"
            className={runStyle === "practice" ? "mode active" : "mode"}
            onClick={() => setRunStyle("practice")}
          >
            <strong>Practice</strong>
            <span>Easier help · AI coaches</span>
          </button>
          <button
            type="button"
            className={runStyle === "interview" ? "mode active" : "mode"}
            onClick={() => {
              setRunStyle("interview");
              if (debugDifficulty === "easy") setDebugDifficulty("medium");
            }}
          >
            <strong>Interview</strong>
            <span>No hints · real RAP vibe</span>
          </button>
        </section>

        <p className="section-label">Debug code difficulty</p>
        <section className="modes three">
          {(["easy", "medium", "hard"] as DebugDifficulty[]).map((d) => (
            <button
              key={d}
              type="button"
              className={debugDifficulty === d ? "mode active" : "mode"}
              onClick={() => setDebugDifficulty(d)}
              disabled={runStyle === "interview" && d === "easy"}
            >
              <strong>{d}</strong>
              <span>
                {d === "easy"
                  ? "2 bugs"
                  : d === "medium"
                    ? "3–4 chained"
                    : "4–6 cascade"}
              </span>
            </button>
          ))}
        </section>

        <p className="section-label">Interviewer tone</p>
        <section className="modes">
          {TONES.map((m) => (
            <button
              key={m.id}
              type="button"
              className={mode === m.id ? "mode active" : "mode"}
              onClick={() => setMode(m.id)}
            >
              <strong>{m.label}</strong>
              <span>{m.blurb}</span>
            </button>
          ))}
        </section>

        <label className="voice-toggle">
          <input
            type="checkbox"
            checked={wantLive}
            onChange={(e) => setWantLive(e.target.checked)}
          />
          Gemini Live realtime voice
        </label>

        <button
          type="button"
          className="cta"
          disabled={busy}
          onClick={() => void start()}
        >
          {busy ? "Generating debug code…" : "Start"}
        </button>
      </div>
    );
  }

  return (
    <div className="shell interview">
      <header className="topbar">
        <div className="topbar-left">
          <strong>{session.phase.toUpperCase()}</strong>
          <span className="pill">{session.run_style}</span>
          <span className="pill">{session.debug_difficulty}</span>
          <span className="timer">{mmss(session.seconds_remaining)}</span>
        </div>
        <div className="top-actions">
          {wantLive && (
            <button
              type="button"
              className="pause-btn"
              onClick={() => void (live.paused ? live.resume() : live.pause())}
            >
              {live.paused ? "Resume voice" : "Pause voice"}
            </button>
          )}
          <button type="button" onClick={() => void nextPhase()}>
            Next phase
          </button>
          <button
            type="button"
            onClick={() => {
              live.disconnect();
              setSession(null);
            }}
          >
            End
          </button>
        </div>
      </header>

      <div className="live-strip" aria-live="polite">
        <span className={`live-badge ${live.status}`}>{liveLabel}</span>
        <span className="live-partials-fixed">
          {live.userPartial ? `You: ${live.userPartial}` : ""}
          {live.assistantPartial ? ` · AI: ${live.assistantPartial}` : ""}
          {!live.userPartial && !live.assistantPartial ? "\u00a0" : ""}
        </span>
      </div>

      <div className="main-grid">
        <section className="panel work">
          {session.phase === "debug" && (
            <div className="work-fill debug-fill">
              <button
                type="button"
                className="work-float-btn"
                onClick={() =>
                  void navigator.clipboard.writeText(session.code_panel)
                }
              >
                Copy for Colab
              </button>
              <pre className="code">{session.code_panel}</pre>
            </div>
          )}

          {session.phase === "design" && (
            <Board
              onSubmit={onBoard}
              onWatch={onBoardWatch}
              watchEnabled={voiceActive}
            />
          )}

          {(session.phase === "llm" || session.phase === "feedback") && (
            <div className="llm-hint">
              <h2>
                {session.phase === "feedback" ? "Feedback" : "LLM techniques"}
              </h2>
              <p>Talk. Definition first, then stop.</p>
            </div>
          )}

          {session.phase === "done" && (
            <div className="llm-hint">
              <h2>Done</h2>
              <p>Mock complete.</p>
            </div>
          )}
        </section>

        <section className="panel transcript">
          <h2>Transcript</h2>
          <div className="messages" ref={transcriptRef}>
            {session.messages.map((m, i) => (
              <div key={`${m.ts}-${i}`} className={`msg ${m.role}`}>
                <span>{m.role === "assistant" ? "Interviewer" : "You"}</span>
                <p>{m.content}</p>
              </div>
            ))}
          </div>

          <div className="compose">
            <textarea
              value={paste}
              onChange={(e) => setPaste(e.target.value)}
              placeholder={
                session.phase === "debug"
                  ? "Paste Colab errors / snippets (optional)"
                  : "Side channel…"
              }
              rows={3}
            />
            <button
              type="button"
              disabled={busy}
              onClick={() => void sendPaste()}
            >
              Send paste
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}
