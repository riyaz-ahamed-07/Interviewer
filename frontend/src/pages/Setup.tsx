import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import {
  createPlan,
  createSessionFromPlan,
  fetchDefaultRounds,
  fetchTaxonomy,
  parseResume,
  type InterviewPlan,
  type Mode,
  type RunStyle,
  type Taxonomy,
} from "../api";
import "../App.css";

type RoundChip = { round_type: string; label: string; minutes: number };

const STEPS = ["Target", "Context", "Rounds", "Interviewer", "Review"] as const;

export default function Setup() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const quick = params.get("quick") === "1";

  const [step, setStep] = useState(0);
  const [tax, setTax] = useState<Taxonomy | null>(null);
  const [companyName, setCompanyName] = useState(quick ? "Product Co" : "");
  const [companyType, setCompanyType] = useState(
    quick ? "product_india" : "product_india",
  );
  const [role, setRole] = useState(quick ? "swe" : "swe");
  const [level, setLevel] = useState(quick ? "fresher" : "fresher");
  const [jdText, setJdText] = useState(
    quick
      ? "We need a software engineer strong in DSA, APIs, and SQL. Build reliable services."
      : "",
  );
  const [resumeText, setResumeText] = useState(
    quick
      ? "Built a FastAPI service for campus events. Used Postgres and Redis. Led a 3-person team."
      : "",
  );
  const [userNotes, setUserNotes] = useState("");
  const [rounds, setRounds] = useState<RoundChip[]>(
    quick
      ? [
          { round_type: "dsa", label: "DSA / live coding", minutes: 20 },
          {
            round_type: "behavioral",
            label: "Behavioural (STAR)",
            minutes: 10,
          },
        ]
      : [],
  );
  const [persona, setPersona] = useState("friendly_senior");
  const [mode, setMode] = useState<Mode>("medium");
  const [runStyle, setRunStyle] = useState<RunStyle>(
    quick ? "practice" : "interview",
  );
  const [difficulty, setDifficulty] = useState<"easy" | "medium" | "hard">(
    "medium",
  );
  const [voice, setVoice] = useState(true);
  const [camera, setCamera] = useState(false);
  const [avatar, setAvatar] = useState(false);
  const [plan, setPlan] = useState<InterviewPlan | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    void fetchTaxonomy()
      .then(setTax)
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    if (quick) return;
    void fetchDefaultRounds(companyType, role, level)
      .then((r) =>
        setRounds(
          r.rounds.map((x) => ({
            round_type: x.round_type,
            label: x.label,
            minutes: x.minutes,
          })),
        ),
      )
      .catch(() => undefined);
  }, [companyType, role, level, quick]);

  useEffect(() => {
    if (!tax) return;
    const d = tax.company_types[companyType]?.difficulty;
    if (d === "easy" || d === "medium" || d === "hard") setDifficulty(d);
  }, [companyType, tax]);

  const totalMinutes = useMemo(
    () => rounds.reduce((a, r) => a + r.minutes, 0),
    [rounds],
  );

  const addRound = (roundType: string) => {
    if (!tax) return;
    const meta = tax.round_types[roundType];
    if (!meta) return;
    setRounds((prev) => [
      ...prev,
      {
        round_type: roundType,
        label: meta.label,
        minutes: meta.default_minutes,
      },
    ]);
  };

  const onResumeFile = async (file: File | null) => {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const { text } = await parseResume(file);
      setResumeText(text);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  const buildPlan = async () => {
    setBusy(true);
    setError("");
    try {
      const { plan: p } = await createPlan({
        company_name: companyName || "Target company",
        company_type: companyType,
        role,
        level,
        persona,
        mode,
        run_style: runStyle,
        difficulty,
        jd_text: jdText,
        resume_text: resumeText,
        user_notes: userNotes,
        voice,
        camera,
        avatar,
        rounds: rounds.map((r) => ({
          round_type: r.round_type,
          minutes: r.minutes,
        })),
      });
      setPlan(p);
      setStep(4);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  const start = async () => {
    if (!plan) return;
    setBusy(true);
    setError("");
    try {
      const { session } = await createSessionFromPlan({
        ...plan,
        voice,
        camera,
        avatar,
      });
      navigate(`/interview/${session.id}`);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="shell lobby setup">
      <header>
        <p className="eyebrow">
          <Link to="/">Home</Link> · Setup
        </p>
        <h1>Interview setup</h1>
        <div className="setup-progress" aria-label="Setup progress">
          {STEPS.map((label, i) => (
            <button
              key={label}
              type="button"
              className={
                i === step ? "step on" : i < step ? "step done" : "step"
              }
              onClick={() => setStep(i)}
            >
              {i + 1}. {label}
            </button>
          ))}
        </div>
      </header>

      {error ? <p className="status error">{error}</p> : null}

      {step === 0 && tax && (
        <section className="setup-panel">
          <label>
            Company name
            <input
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="e.g. Swiggy"
            />
          </label>
          <label>
            Company type
            <select
              value={companyType}
              onChange={(e) => setCompanyType(e.target.value)}
            >
              {Object.entries(tax.company_types).map(([id, c]) => (
                <option key={id} value={id}>
                  {c.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Role
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              {Object.entries(tax.roles).map(([id, r]) => (
                <option key={id} value={id}>
                  {r.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Experience
            <select value={level} onChange={(e) => setLevel(e.target.value)}>
              {Object.entries(tax.experience_levels).map(([id]) => (
                <option key={id} value={id}>
                  {id}
                </option>
              ))}
            </select>
          </label>
          <button type="button" className="cta" onClick={() => setStep(1)}>
            Next
          </button>
        </section>
      )}

      {step === 1 && (
        <section className="setup-panel">
          <label>
            Job description
            <textarea
              rows={8}
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Paste the JD"
            />
          </label>
          <label>
            Resume (PDF or .txt)
            <input
              type="file"
              accept=".pdf,.txt,text/plain,application/pdf"
              onChange={(e) => void onResumeFile(e.target.files?.[0] ?? null)}
            />
          </label>
          <label>
            Resume text (editable)
            <textarea
              rows={8}
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
            />
          </label>
          <label>
            Anything you know about this loop
            <textarea
              rows={3}
              value={userNotes}
              onChange={(e) => setUserNotes(e.target.value)}
            />
          </label>
          <div className="cta-row">
            <button type="button" onClick={() => setStep(0)}>
              Back
            </button>
            <button type="button" className="cta" onClick={() => setStep(2)}>
              Next
            </button>
          </div>
        </section>
      )}

      {step === 2 && tax && (
        <section className="setup-panel">
          <p className="lede">Total ~{totalMinutes} min</p>
          <div className="round-chips">
            {rounds.map((r, i) => (
              <div key={`${r.round_type}-${i}`} className="round-chip">
                <span>
                  {r.label} · {r.minutes}m
                </span>
                <button
                  type="button"
                  onClick={() =>
                    setRounds((prev) => prev.filter((_, j) => j !== i))
                  }
                >
                  Remove
                </button>
                <input
                  type="number"
                  min={5}
                  max={120}
                  value={r.minutes}
                  onChange={(e) => {
                    const minutes = Number(e.target.value) || 5;
                    setRounds((prev) =>
                      prev.map((x, j) => (j === i ? { ...x, minutes } : x)),
                    );
                  }}
                />
              </div>
            ))}
          </div>
          <label>
            Add round
            <select
              defaultValue=""
              onChange={(e) => {
                if (e.target.value) addRound(e.target.value);
                e.target.value = "";
              }}
            >
              <option value="" disabled>
                Choose…
              </option>
              {Object.entries(tax.round_types).map(([id, meta]) => (
                <option key={id} value={id}>
                  {meta.label}
                </option>
              ))}
            </select>
          </label>
          <div className="cta-row">
            <button type="button" onClick={() => setStep(1)}>
              Back
            </button>
            <button type="button" className="cta" onClick={() => setStep(3)}>
              Next
            </button>
          </div>
        </section>
      )}

      {step === 3 && tax && (
        <section className="setup-panel">
          <label>
            Persona
            <select
              value={persona}
              onChange={(e) => setPersona(e.target.value)}
            >
              {Object.entries(tax.personas).map(([id, p]) => (
                <option key={id} value={id}>
                  {p.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Strictness
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as Mode)}
            >
              <option value="soft">Soft</option>
              <option value="medium">Medium</option>
              <option value="strict">Strict</option>
              <option value="hardcore">Hardcore</option>
            </select>
          </label>
          <label>
            Hint mode
            <select
              value={runStyle}
              onChange={(e) => setRunStyle(e.target.value as RunStyle)}
            >
              <option value="practice">Practice (hints on)</option>
              <option value="interview">Interview (no hints)</option>
            </select>
          </label>
          <label>
            Difficulty
            <select
              value={difficulty}
              onChange={(e) =>
                setDifficulty(e.target.value as "easy" | "medium" | "hard")
              }
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </label>
          <label className="voice-toggle">
            <input
              type="checkbox"
              checked={voice}
              onChange={(e) => setVoice(e.target.checked)}
            />
            Voice
          </label>
          <label className="voice-toggle">
            <input
              type="checkbox"
              checked={camera}
              onChange={(e) => setCamera(e.target.checked)}
            />
            Camera self-view (Phase 2)
          </label>
          <label className="voice-toggle">
            <input
              type="checkbox"
              checked={avatar}
              onChange={(e) => setAvatar(e.target.checked)}
            />
            Avatar (Phase 2)
          </label>
          <div className="cta-row">
            <button type="button" onClick={() => setStep(2)}>
              Back
            </button>
            <button
              type="button"
              className="cta"
              disabled={busy || rounds.length === 0}
              onClick={() => void buildPlan()}
            >
              {busy ? "Building plan…" : "Review plan"}
            </button>
          </div>
        </section>
      )}

      {step === 4 && plan && (
        <section className="setup-panel">
          <p className="lede">
            {plan.company_name} · {plan.role} · {plan.level} · {plan.run_style}
          </p>
          {plan.rounds.map((r) => (
            <article key={r.id} className="plan-card">
              <h3>
                {r.round_type.replaceAll("_", " ")} · {r.minutes}m
              </h3>
              <p>{r.goal}</p>
              <ul>
                {r.questions.map((q, i) => (
                  <li key={`${r.id}-${i}`}>
                    <span className="pill">{q.source}</span> {q.text}
                  </li>
                ))}
              </ul>
            </article>
          ))}
          <div className="cta-row">
            <button type="button" onClick={() => setStep(3)}>
              Back
            </button>
            <button
              type="button"
              className="cta"
              disabled={busy}
              onClick={() => void start()}
            >
              {busy ? "Starting…" : "Start interview"}
            </button>
          </div>
        </section>
      )}
    </div>
  );
}
