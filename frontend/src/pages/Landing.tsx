import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  fetchHistory,
  health,
  startDesignTeacherSession,
  startFriendSession,
  startRapLegacy,
} from "../api";
import { ForgePanel } from "./Forge";
import "../App.css";

type Hist = {
  id: string;
  phase: string;
  created_at: string;
  has_scorecard: boolean;
};

export default function Landing() {
  const navigate = useNavigate();
  const location = useLocation();
  const notice = (location.state as { notice?: string } | null)?.notice;
  const [statusLine, setStatusLine] = useState("Checking backend…");
  const [backendOk, setBackendOk] = useState(true);
  const [busy, setBusy] = useState(false);
  const [recent, setRecent] = useState<Hist[]>([]);

  useEffect(() => {
    health()
      .then((h) => {
        setBackendOk(true);
        const keys = Number(h.live?.key_count ?? 0);
        setStatusLine(
          h.llm_ready
            ? `Backend OK · ${keys} Gemini keys`
            : "Backend OK · add GEMINI_API_KEY_1=... to backend/.env",
        );
      })
      .catch(() => {
        setBackendOk(false);
        setStatusLine(
          "Backend not reachable. Run uvicorn in backend/ or set VITE_API_BASE.",
        );
      });
    void fetchHistory(3)
      .then((r) => setRecent(r.sessions))
      .catch(() => setRecent([]));
  }, []);

  const goBuddy = async (kind: "friend" | "design") => {
    setBusy(true);
    try {
      const { session } =
        kind === "friend"
          ? await startFriendSession("medium")
          : await startDesignTeacherSession("medium");
      navigate(`/interview/${session.id}`);
    } catch (e) {
      setStatusLine(String(e));
    } finally {
      setBusy(false);
    }
  };

  const goLegacy = async () => {
    setBusy(true);
    try {
      const { session } = await startRapLegacy("medium", "interview");
      navigate(`/interview/${session.id}`);
    } catch (e) {
      setStatusLine(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="shell lobby landing">
      {!backendOk ? (
        <div className="health-banner" role="alert">
          {statusLine}
        </div>
      ) : null}
      {notice ? <p className="status">{notice}</p> : null}

      <header className="landing-hero">
        <p className="eyebrow">Interview coach · career forge</p>
        <h1>
          Practise interviews. <span>Forge invincible.</span>
        </h1>
        <p className="lede">
          Mock rounds from your JD, paper tutoring with Dr. Delta, and a mastery
          lattice aimed at NVIDIA-grade AI engineering.
        </p>
        <p className="status">{statusLine}</p>
        <div className="cta-row">
          <Link className="cta" to="/setup">
            Set up interview
          </Link>
          <a className="cta ghost" href="#forge">
            Jump to Forge
          </a>
        </div>
      </header>

      <ForgePanel />

      <section className="buddies">
        <h2>Practice tools</h2>
        <div className="buddy-grid">
          <Link className="buddy-card" to="/setup">
            <strong>Interviewer</strong>
            <span>Full mock from JD + resume</span>
          </Link>
          <button
            type="button"
            className="buddy-card"
            disabled={busy}
            onClick={() => void goBuddy("friend")}
          >
            <strong>Study Friend</strong>
            <span>Explain a concept, get grilled</span>
          </button>
          <button
            type="button"
            className="buddy-card"
            disabled={busy}
            onClick={() => void goBuddy("design")}
          >
            <strong>System Design</strong>
            <span>Walk a design prompt</span>
          </button>
          <Link className="buddy-card" to="/buddies/paper">
            <strong>Dr. Delta</strong>
            <span>Research paper buddy</span>
          </Link>
        </div>
      </section>

      <section className="recent">
        <div className="recent-head">
          <h2>Recent sessions</h2>
          <Link to="/history">History</Link>
        </div>
        {recent.length === 0 ? (
          <p className="lede">No saved sessions yet.</p>
        ) : (
          <ul className="recent-list">
            {recent.map((s) => (
              <li key={s.id}>
                <Link to={`/interview/${s.id}`}>
                  {new Date(s.created_at).toLocaleString()} · {s.phase}
                  {s.has_scorecard ? " · scored" : ""}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <footer className="landing-foot">
        <a
          className="notes-link"
          href="/notes/ml-engineer-interview-notes.html"
        >
          Master notes
        </a>
        <button
          type="button"
          className="linkish"
          disabled={busy}
          onClick={() => void goLegacy()}
        >
          RAP ML Intern (legacy)
        </button>
      </footer>
    </div>
  );
}
