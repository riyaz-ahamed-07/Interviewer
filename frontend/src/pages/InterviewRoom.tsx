import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  advanceSession,
  getSession,
  logTurn,
  navigateLlmTopic,
  SessionGoneError,
  speakFallback,
  nextDesignTeacherQuestion,
  submitDiagram,
  summarizeDiagram,
  textTurn,
  type Session,
} from "../api";
import { AvatarStage } from "../avatar/AvatarStage";
import { Board, type CanvasScene } from "../components/Board";
import { CodePanel } from "../components/CodePanel";
import { ScorecardPanel } from "../components/ScorecardPanel";
import { SelfView } from "../components/SelfView";
import { useLiveVoice } from "../hooks/useLiveVoice";
import { latestTopicCue } from "../lib/topicCue";
import "../App.css";

const DESIGN_STEPS = [
  "requirements",
  "entities",
  "api",
  "hld",
  "deep_dive",
  "framing",
  "data",
  "model",
  "metrics",
  "serving",
] as const;

function playTimerBeep() {
  try {
    const Ctx =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext: typeof AudioContext })
        .webkitAudioContext;
    const ctx = new Ctx();
    const beep = (at: number, freq: number) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "square";
      osc.frequency.value = freq;
      gain.gain.value = 0.0001;
      osc.connect(gain);
      gain.connect(ctx.destination);
      const t0 = ctx.currentTime + at;
      gain.gain.setValueAtTime(0.0001, t0);
      gain.gain.exponentialRampToValueAtTime(0.18, t0 + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.22);
      osc.start(t0);
      osc.stop(t0 + 0.25);
    };
    beep(0, 880);
    beep(0.28, 660);
    window.setTimeout(() => void ctx.close(), 800);
  } catch {
    /* silent */
  }
}

export default function InterviewRoom() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<Session | null>(null);
  const [paste, setPaste] = useState("");
  const [statusLine, setStatusLine] = useState("Loading session…");
  const wantLive = true;
  const [busy, setBusy] = useState(false);
  const [phasePrep, setPhasePrep] = useState(false);
  const [localSecs, setLocalSecs] = useState(0);
  const [loadError, setLoadError] = useState("");
  const [cameraOn, setCameraOn] = useState(
    () => sessionStorage.getItem("coach.camera") === "1",
  );
  const [avatarOn, setAvatarOn] = useState(
    () => sessionStorage.getItem("coach.avatar") !== "0",
  );
  const [designStep, setDesignStep] = useState<string>("");
  const transcriptRef = useRef<HTMLDivElement>(null);

  const sessionIdRef = useRef<string | null>(null);
  const phaseRef = useRef<string>("lobby");
  const introBeepedRef = useRef(false);
  const liveStartedRef = useRef(false);

  const onTurn = useCallback((role: "user" | "assistant", text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    const sid = sessionIdRef.current;
    const phase = phaseRef.current;
    setSession((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        messages: [
          ...prev.messages,
          { role, content: trimmed, ts: Date.now() / 1000, phase },
        ],
      };
    });
    if (sid) {
      void logTurn(sid, role, trimmed).catch(() => {
        /* non-fatal — sync on advance still covers scoring */
      });
    }
  }, []);

  const live = useLiveVoice(onTurn);

  useEffect(() => {
    sessionIdRef.current = session?.id ?? null;
    phaseRef.current = session?.current_round?.id || session?.phase || "lobby";
  }, [session?.id, session?.phase, session?.current_round?.id]);

  const bumpToLobby = useCallback(
    (reason: string) => {
      live.disconnect();
      setSession(null);
      setPaste("");
      setStatusLine(reason);
      navigate("/", { replace: true, state: { notice: reason } });
    },
    [live, navigate],
  );

  useEffect(() => {
    if (!sessionId) {
      setLoadError("Missing session id");
      return;
    }
    let cancelled = false;
    setLoadError("");
    void getSession(sessionId)
      .then((r) => {
        if (cancelled) return;
        setSession(r.session);
        setStatusLine("Session ready");
      })
      .catch((e) => {
        if (cancelled) return;
        setLoadError(
          e instanceof Error
            ? e.message
            : "Could not load session. Is the backend running?",
        );
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  useEffect(() => {
    if (!session || !wantLive || liveStartedRef.current) return;
    if (live.status !== "idle" && live.status !== "error") return;
    liveStartedRef.current = true;
    void live.connect(session.id).catch(() => {
      liveStartedRef.current = false;
    });
  }, [session?.id, wantLive, live]);

  useEffect(() => {
    if (!session) return;
    setLocalSecs(session.seconds_remaining);
    introBeepedRef.current = false;
  }, [session?.id, session?.phase]);

  useEffect(() => {
    if (!session) return;
    setLocalSecs((s) => Math.min(s, session.seconds_remaining));
  }, [session?.seconds_remaining]);

  useEffect(() => {
    if (!session) return;
    if (
      session.phase === "friend" ||
      session.phase === "design_teacher" ||
      session.phase_budget_seconds <= 0
    )
      return;
    const t = window.setInterval(() => {
      setLocalSecs((s) => Math.max(0, s - 1));
    }, 1000);
    return () => window.clearInterval(t);
  }, [session?.id, session?.phase, session?.phase_budget_seconds]);

  useEffect(() => {
    if (!session) return;
    if (
      session.phase === "intro" &&
      session.run_style === "practice" &&
      localSecs <= 0 &&
      session.phase_budget_seconds > 0 &&
      !introBeepedRef.current
    ) {
      introBeepedRef.current = true;
      playTimerBeep();
      setStatusLine(
        "Intro time is up — beep. Tap Next phase when ready (not auto-advancing).",
      );
    }
  }, [localSecs, session]);

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
              scorecard: r.session.scorecard ?? prev.scorecard,
              llm_topics: r.session.llm_topics?.length
                ? r.session.llm_topics
                : prev.llm_topics,
              llm_topic_index:
                r.session.llm_topic_index ?? prev.llm_topic_index,
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
  }, [session?.messages.length, live.userPartial, live.assistantPartial]);

  const llmCue = useMemo(() => {
    if (!session || session.phase !== "llm") return null;
    const queued =
      session.llm_topics?.[session.llm_topic_index ?? 0]?.technique;
    if (queued) return queued;
    return latestTopicCue(session.messages, live.assistantPartial);
  }, [session, live.assistantPartial]);

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

  const phaseStillPreparing = (s: Session) => {
    if (s.phase === "debug" && s.code_panel.startsWith("Generating"))
      return true;
    if (
      s.phase === "design" &&
      (!s.design_prompt || s.design_prompt.id === "pending")
    )
      return true;
    if ((s.phase === "feedback" || s.phase === "done") && !s.scorecard)
      return true;
    return false;
  };

  const pollPhaseReady = async (id: string, phase: Session["phase"]) => {
    for (let i = 0; i < 90; i++) {
      await new Promise((r) => setTimeout(r, 400));
      try {
        const { session: s } = await getSession(id);
        setSession(s);
        if (s.phase !== phase || !phaseStillPreparing(s)) {
          return s;
        }
      } catch (e) {
        if (e instanceof SessionGoneError) {
          bumpToLobby(
            "Session expired (backend reloaded). Start a new interview.",
          );
          return null;
        }
      }
    }
    return null;
  };

  const nextDesignQuestion = async () => {
    if (!session || session.phase !== "design_teacher") return;
    setBusy(true);
    setStatusLine("New design question…");
    try {
      const { session: s, live_briefing } = await nextDesignTeacherQuestion(
        session.id,
      );
      setSession(s);
      setBusy(false);
      setStatusLine(`Design · ${s.design_prompt?.title ?? "new scenario"}`);
      if (voiceActive && live_briefing) {
        live.sendPhaseSync(live_briefing);
      } else {
        void playTts(s.messages.at(-1)?.content ?? "");
      }
    } catch (e) {
      if (e instanceof SessionGoneError) {
        bumpToLobby(
          "Session expired (backend reloaded). Start a new interview.",
        );
      } else setStatusLine(String(e));
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
      void summarizeDiagram(scene)
        .then((sum) => {
          live.sendText(
            "[CANVAS WATCH — silent context only. Do NOT speak or acknowledge. " +
              "Use this when you next reply to the candidate's voice.]\n" +
              sum.adjacency_text +
              "\n" +
              JSON.stringify(scene),
          );
        })
        .catch(() => {
          live.sendText(
            "[CANVAS WATCH — silent context only. Do NOT speak or acknowledge.]\n" +
              JSON.stringify(scene),
          );
        });
    },
    [live, voiceActive],
  );

  const onBoardFrame = useCallback(
    (blob: Blob, labels: string[]) => {
      if (!voiceActive) return;
      void blob.arrayBuffer().then((buf) => {
        live.sendImagePng(buf, {
          silent: true,
          mime: blob.type || "image/jpeg",
        });
        if (labels.length) {
          live.sendText(
            `[CANVAS WATCH frame labels — silent]: ${labels.slice(0, 40).join(", ")}`,
          );
        }
      });
    },
    [live, voiceActive],
  );

  const onBoard = useCallback(
    async (blob: Blob, labels: string[]) => {
      if (!session) return;
      setBusy(true);
      try {
        if (voiceActive) {
          live.sendImagePng(await blob.arrayBuffer(), {
            silent: false,
            mime: blob.type || "image/jpeg",
          });
          live.sendText(
            `Architecture diagram submitted. Labels: ${labels.join(", ") || "(none)"}. Critique out loud, briefly. Reference at least three labels from the board.`,
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

  useEffect(() => {
    const text = `${live.assistantPartial} ${session?.messages.at(-1)?.content ?? ""}`;
    const m = text.match(/\[STEP:\s*([a-z_]+)\]/i);
    if (m?.[1]) setDesignStep(m[1].toLowerCase());
  }, [live.assistantPartial, session?.messages]);

  useEffect(() => {
    sessionStorage.setItem("coach.camera", cameraOn ? "1" : "0");
  }, [cameraOn]);
  useEffect(() => {
    sessionStorage.setItem("coach.avatar", avatarOn ? "1" : "0");
  }, [avatarOn]);

  const nextPhase = async () => {
    if (!session || phasePrep) return;
    setBusy(true);
    setStatusLine("Switching phase…");
    try {
      const {
        session: s,
        live_briefing,
        preparing,
      } = await advanceSession(session.id, session.messages);
      setSession(s);
      setBusy(false);

      const speak = (ready: Session, briefing?: string) => {
        const line = ready.messages.at(-1)?.content ?? "";
        if (voiceActive) {
          live.sendPhaseSync(briefing ?? line);
        } else {
          void playTts(line);
        }
      };

      if (preparing || phaseStillPreparing(s)) {
        setPhasePrep(true);
        setStatusLine("Preparing next part…");
        if (voiceActive && live_briefing) {
          live.sendPhaseSync(live_briefing);
        }
        const ready = await pollPhaseReady(s.id, s.phase);
        setPhasePrep(false);
        if (ready) {
          setStatusLine(`${ready.phase} · ${ready.run_style}`);
          speak(ready);
        }
      } else {
        setStatusLine(`${s.phase} · ${s.run_style}`);
        speak(s, live_briefing);
      }
    } catch (e) {
      if (e instanceof SessionGoneError) {
        bumpToLobby(
          "Session expired (backend reloaded). Start a new interview.",
        );
      } else setStatusLine(String(e));
      setBusy(false);
      setPhasePrep(false);
    }
  };

  const jumpTopic = async (direction: "prev" | "next") => {
    if (!session || session.phase !== "llm") return;
    setBusy(true);
    try {
      const { session: s, live_briefing } = await navigateLlmTopic(
        session.id,
        direction,
      );
      setSession(s);
      setBusy(false);
      if (voiceActive && live_briefing) {
        live.sendPhaseSync(live_briefing);
      } else {
        void playTts(s.messages.at(-1)?.content ?? "");
      }
    } catch (e) {
      if (e instanceof SessionGoneError) {
        bumpToLobby(
          "Session expired (backend reloaded). Start a new interview.",
        );
      } else setStatusLine(String(e));
      setBusy(false);
    }
  };

  const mmss = (s: number) =>
    `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, "0")}`;

  const isFriend = session?.phase === "friend";
  const isDesignTeacher = session?.phase === "design_teacher";
  const isCoachMode = isFriend || isDesignTeacher;
  const timerExpired =
    Boolean(session) && session!.phase_budget_seconds > 0 && localSecs <= 0;

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
          <h1>Interview room</h1>
          <p className="lede">{loadError || statusLine}</p>
          <p className="status">
            <Link to="/">Back home</Link>
          </p>
        </header>
      </div>
    );
  }

  const roundLabel =
    session.current_round?.round_type?.replaceAll("_", " ") ||
    session.phase.toUpperCase();
  const workspace = session.workspace || "";
  const showBoard =
    session.phase === "design" ||
    session.phase === "design_teacher" ||
    workspace.includes("whiteboard");
  const showCode =
    session.phase === "debug" ||
    (workspace.includes("code") && session.phase !== "design_teacher");
  const showResume = workspace === "resume" && Boolean(session.resume_text);

  return (
    <div className="shell interview call-room habit-chrome">
      <header className="topbar">
        <div className="topbar-left">
          <strong>{roundLabel}</strong>
          {!isCoachMode ? (
            <>
              <span className="pill">{session.run_style}</span>
              {session.use_plan_engine ? (
                <span className="pill">
                  round {(session.round_index ?? 0) + 1}/
                  {session.plan?.rounds?.length ?? "?"}
                </span>
              ) : null}
              <span className={timerExpired ? "timer timer-expired" : "timer"}>
                {mmss(localSecs)}
              </span>
            </>
          ) : (
            <span className="pill">
              {isDesignTeacher ? "design teacher" : "study friend"}
            </span>
          )}
        </div>
        <div className="top-actions">
          <label className="tile-toggle compact">
            <input
              type="checkbox"
              checked={cameraOn}
              onChange={(e) => setCameraOn(e.target.checked)}
            />
            Cam
          </label>
          <label className="tile-toggle compact">
            <input
              type="checkbox"
              checked={avatarOn}
              onChange={(e) => setAvatarOn(e.target.checked)}
            />
            Avatar
          </label>
          {wantLive && (
            <button
              type="button"
              className="pause-btn"
              onClick={() => void (live.paused ? live.resume() : live.pause())}
            >
              {live.paused ? "Resume voice" : "Pause voice"}
            </button>
          )}
          {isDesignTeacher && (
            <button
              type="button"
              disabled={busy}
              onClick={() => void nextDesignQuestion()}
            >
              {busy ? "Loading…" : "Next question"}
            </button>
          )}
          {!isCoachMode && session.phase === "llm" && (
            <>
              <button
                type="button"
                disabled={busy || session.llm_topic_index <= 0}
                onClick={() => void jumpTopic("prev")}
              >
                ← Prev topic
              </button>
              <button
                type="button"
                disabled={
                  busy ||
                  session.llm_topic_index >=
                    Math.max(0, (session.llm_topics?.length ?? 1) - 1)
                }
                onClick={() => void jumpTopic("next")}
              >
                Next topic →
              </button>
            </>
          )}
          {!isCoachMode &&
            session.phase !== "done" &&
            session.phase !== "feedback" && (
              <button
                type="button"
                disabled={busy || phasePrep}
                onClick={() => void nextPhase()}
              >
                {busy ? "Loading…" : phasePrep ? "Preparing…" : "Next phase"}
              </button>
            )}
          {!isCoachMode && session.phase === "feedback" && (
            <button
              type="button"
              disabled={busy || phasePrep}
              onClick={() => void nextPhase()}
            >
              {busy || phasePrep ? "Loading…" : "Finish"}
            </button>
          )}
          {!isCoachMode && (
            <button
              type="button"
              disabled={!voiceActive}
              onClick={() =>
                live.sendText(
                  "[System] Candidate is thinking silently. Stay silent until they speak.",
                )
              }
            >
              Think 30s
            </button>
          )}
          <button
            type="button"
            onClick={() => {
              live.disconnect();
              navigate("/");
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

      <div className="call-strip">
        <AvatarStage
          enabled={avatarOn}
          liveSpeaking={live.status === "speaking"}
          playContext={live.playContext}
          outputGain={live.outputGain}
          displayName={session.persona?.replaceAll("_", " ") || "Interviewer"}
        />
        <SelfView enabled={cameraOn} onEnabledChange={setCameraOn} />
      </div>

      {showBoard ? (
        <div className="design-steps" aria-label="Design steps">
          {DESIGN_STEPS.filter((s) =>
            session.current_round?.round_type?.includes("ml") ||
            session.current_round?.round_type?.includes("genai")
              ? [
                  "framing",
                  "data",
                  "model",
                  "metrics",
                  "serving",
                  "deep_dive",
                ].includes(s)
              : [
                  "requirements",
                  "entities",
                  "api",
                  "hld",
                  "deep_dive",
                ].includes(s),
          ).map((s) => (
            <span
              key={s}
              className={designStep === s ? "design-step on" : "design-step"}
            >
              {s}
            </span>
          ))}
        </div>
      ) : null}

      <div className="main-grid">
        <section className="panel work">
          {session.phase === "friend" && (
            <div className="friend-hint">
              <p className="llm-kicker">Study friend</p>
              <h2 className="llm-cue">Explain it. Get grilled.</h2>
              <p className="llm-coach">
                Pick any concept you just learned. He will not nod along — wrong
                or fuzzy answers get called out, then you restate them properly.
              </p>
            </div>
          )}

          {session.phase === "design_teacher" && (
            <Board
              key={session.design_prompt?.id ?? "design-teacher"}
              onSubmit={onBoard}
              onWatch={onBoardWatch}
              onFrame={onBoardFrame}
              watchEnabled={voiceActive}
              frameEnabled={voiceActive}
            />
          )}

          {session.phase === "intro" && (
            <div className="llm-hint">
              <p className="llm-kicker">Part 0</p>
              <h2 className="llm-cue">Tell me about yourself</h2>
              <p className="llm-coach">
                A normal RAP intro only — no project deep-dives. When the timer
                beeps in practice, stay here until you tap Next phase.
              </p>
            </div>
          )}

          {showCode && (
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
              <CodePanel
                code={session.code_panel || "# Write your solution here"}
              />
            </div>
          )}

          {showBoard && session.phase !== "design_teacher" && (
            <Board
              onSubmit={onBoard}
              onWatch={onBoardWatch}
              onFrame={onBoardFrame}
              watchEnabled={voiceActive}
              frameEnabled={voiceActive}
            />
          )}

          {showResume && (
            <div className="llm-hint">
              <p className="llm-kicker">Resume</p>
              <pre className="resume-panel">{session.resume_text}</pre>
            </div>
          )}

          {session.use_plan_engine && session.current_round && (
            <div className="llm-hint">
              <p className="llm-kicker">{roundLabel}</p>
              <h2 className="llm-cue">
                {session.current_round.goal || "Answer clearly."}
              </h2>
              {session.current_round.questions?.[0]?.text ? (
                <p className="llm-coach">
                  Seed: {session.current_round.questions[0].text}
                </p>
              ) : null}
            </div>
          )}

          {session.phase === "llm" && (
            <div className="llm-hint">
              <p className="llm-kicker">
                Topic {(session.llm_topic_index ?? 0) + 1}
                {session.llm_topics?.length
                  ? ` / ${session.llm_topics.length}`
                  : ""}
              </p>
              {llmCue ? (
                <h2 className="llm-cue">{llmCue}</h2>
              ) : (
                <h2 className="llm-cue llm-cue-wait">
                  Waiting for next topic…
                </h2>
              )}
              <p className="llm-coach">Say the definition. Then stop.</p>
              {session.llm_topics?.length ? (
                <p className="topic-rail">
                  {session.llm_topics.map((t, i) => (
                    <span
                      key={`${t.technique}-${i}`}
                      className={
                        i === session.llm_topic_index
                          ? "topic-chip on"
                          : i < session.llm_topic_index
                            ? "topic-chip done"
                            : "topic-chip"
                      }
                    >
                      {t.technique}
                    </span>
                  ))}
                </p>
              ) : null}
            </div>
          )}

          {(session.phase === "feedback" || session.phase === "done") &&
            (session.scorecard ? (
              <ScorecardPanel card={session.scorecard} />
            ) : (
              <div className="llm-hint">
                <h2 className="llm-cue llm-cue-wait">
                  Building your scorecard…
                </h2>
                <p className="llm-coach">
                  Groq is scoring the full transcript.
                </p>
              </div>
            ))}
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
            {live.userPartial.trim() ? (
              <div className="msg user live">
                <span>You</span>
                <p>
                  {live.userPartial}
                  <span className="live-caret" aria-hidden="true" />
                </p>
              </div>
            ) : null}
            {live.assistantPartial.trim() ? (
              <div className="msg assistant live">
                <span>Interviewer</span>
                <p>
                  {live.assistantPartial}
                  <span className="live-caret" aria-hidden="true" />
                </p>
              </div>
            ) : null}
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
