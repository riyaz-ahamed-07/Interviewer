import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  fetchHistory,
  health,
  startDesignTeacherSession,
  startFriendSession,
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
  const [statusLine, setStatusLine] = useState("");
  const [backendOk, setBackendOk] = useState(true);
  const [busy, setBusy] = useState(false);
  const [recent, setRecent] = useState<Hist[]>([]);

  useEffect(() => {
    health()
      .then((h) => {
        setBackendOk(true);
        if (!h.llm_ready) {
          setStatusLine("Add GEMINI_API_KEY_1=... to backend/.env");
        } else {
          setStatusLine("");
        }
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

  return (
    <div className="shell lobby landing landing-forge-first habit-page">
      {!backendOk || statusLine ? (
        <div
          className={`health-banner${backendOk ? " soft" : ""}`}
          role="status"
        >
          {statusLine || "Backend issue"}
        </div>
      ) : null}
      {notice ? <p className="status">{notice}</p> : null}

      <section className="landing-viewport" aria-label="Forge tracker">
        <ForgePanel compact />
      </section>

      <section
        className="buddies landing-quick soft-card"
        style={{ padding: "1rem" }}
      >
        <h2>Quick start</h2>
        <div className="buddy-grid">
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
        </div>
      </section>

      {recent.length > 0 ? (
        <section className="recent">
          <h2>Recent</h2>
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
        </section>
      ) : null}
    </div>
  );
}
