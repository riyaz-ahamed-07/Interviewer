import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchHistory } from "../api";
import "../App.css";

export default function History() {
  const [rows, setRows] = useState<
    Array<{
      id: string;
      phase: string;
      created_at: string;
      has_scorecard: boolean;
      mode: string;
      run_style: string;
    }>
  >([]);
  const [error, setError] = useState("");

  useEffect(() => {
    void fetchHistory(40)
      .then((r) => setRows(r.sessions))
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="shell lobby">
      <header>
        <p className="eyebrow">
          <Link to="/">Home</Link>
        </p>
        <h1>History</h1>
      </header>
      {error ? <p className="status">{error}</p> : null}
      <ul className="recent-list">
        {rows.map((s) => (
          <li key={s.id}>
            <Link to={`/interview/${s.id}`}>
              {new Date(s.created_at).toLocaleString()} · {s.phase} · {s.mode} ·{" "}
              {s.run_style}
              {s.has_scorecard ? " · scored" : ""}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
