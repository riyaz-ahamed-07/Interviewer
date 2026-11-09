import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  fetchPaperLibrary,
  ingestPaper,
  ingestPaperPdf,
  reviewFlashCard,
  type FlashCard,
  type PaperLibrary as Lib,
} from "../api";
import "../App.css";

export default function PaperLibrary() {
  const navigate = useNavigate();
  const [lib, setLib] = useState<Lib | null>(null);
  const [arxiv, setArxiv] = useState("2602.06036");
  const [paste, setPaste] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");
  const [quiz, setQuiz] = useState<FlashCard | null>(null);
  const [reveal, setReveal] = useState(false);

  const reload = () =>
    fetchPaperLibrary()
      .then(setLib)
      .catch((e) => setStatus(String(e)));

  useEffect(() => {
    void reload();
  }, []);

  const ingest = async () => {
    setBusy(true);
    setStatus("Ingesting and mapping…");
    try {
      const body = paste.trim()
        ? { text: paste, title_hint: arxiv.trim() || undefined }
        : { arxiv_id: arxiv.trim(), arxiv_url: arxiv.trim() };
      const { paper } = await ingestPaper(body);
      setStatus(`Ready: ${paper.title}`);
      navigate(`/buddies/paper/${paper.id}`);
    } catch (e) {
      setStatus(String(e));
    } finally {
      setBusy(false);
    }
  };

  const onPdf = async (file: File | null) => {
    if (!file) return;
    setBusy(true);
    setStatus("Parsing PDF…");
    try {
      const { paper } = await ingestPaperPdf(file);
      navigate(`/buddies/paper/${paper.id}`);
    } catch (e) {
      setStatus(String(e));
    } finally {
      setBusy(false);
    }
  };

  const due = lib?.due_cards ?? [];
  const active = quiz ?? due[0] ?? null;

  return (
    <div className="shell lobby paper-lib habit-page">
      <header className="habit-hero">
        <div>
        <p className="eyebrow">
          <Link to="/">Home</Link> · Dr. Delta
        </p>
        <h1>Research Paper Buddy</h1>
        <p className="lede">
          Paste an arXiv id, upload a PDF, or drop raw text. Dr. Delta maps the
          parent, prerequisites, and a concept-by-concept lesson plan.
        </p>
        {status ? <p className="status">{status}</p> : null}
        </div>
      </header>

      <section className="paper-ingest">
        <label className="section-label">Ingest</label>
        <div className="field-row">
          <input
            value={arxiv}
            onChange={(e) => setArxiv(e.target.value)}
            placeholder="arXiv id or URL (e.g. 2602.06036)"
            disabled={busy}
          />
          <button type="button" className="cta" disabled={busy} onClick={() => void ingest()}>
            {busy ? "Working…" : "Open with Dr. Delta"}
          </button>
        </div>
        <textarea
          rows={4}
          value={paste}
          onChange={(e) => setPaste(e.target.value)}
          placeholder="Or paste paper text / abstract here (optional if using arXiv)"
          disabled={busy}
        />
        <label className="file-btn">
          Upload PDF
          <input
            type="file"
            accept="application/pdf,.pdf"
            hidden
            disabled={busy}
            onChange={(e) => void onPdf(e.target.files?.[0] ?? null)}
          />
        </label>
      </section>

      {due.length ? (
        <section className="paper-quiz">
          <h2>
            Review due <span className="badge">{due.length}</span>
          </h2>
          {active ? (
            <div className="quiz-card">
              <p>{active.question}</p>
              {reveal ? (
                <p className="quiz-answer">{active.answer}</p>
              ) : (
                <button type="button" className="cta ghost" onClick={() => setReveal(true)}>
                  Reveal
                </button>
              )}
              {reveal ? (
                <div className="quiz-grades">
                  {[1, 2, 3, 4, 5].map((g) => (
                    <button
                      key={g}
                      type="button"
                      onClick={() => {
                        void reviewFlashCard(active.id, g).then(() => {
                          setReveal(false);
                          setQuiz(null);
                          void reload();
                        });
                      }}
                    >
                      {g}
                    </button>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
        </section>
      ) : null}

      <section>
        <h2>Library</h2>
        {!lib?.papers.length ? (
          <p className="lede">No papers yet. Try DFlash: 2602.06036</p>
        ) : (
          <ul className="recent-list">
            {lib.papers.map((p) => (
              <li key={p.id}>
                <Link to={`/buddies/paper/${p.id}`}>
                  {p.title}
                  {p.arxiv_id ? ` · ${p.arxiv_id}` : ""}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2>Reading log</h2>
        {!lib?.log.length ? (
          <p className="lede">Your weekly log appears here after ingest.</p>
        ) : (
          <ul className="recent-list">
            {lib.log.map((e) => (
              <li key={e.id}>
                <Link to={`/buddies/paper/${e.paper_id}`}>
                  {e.title || e.paper_id} · started{" "}
                  {e.started_at ? new Date(e.started_at).toLocaleDateString() : "—"}
                  {typeof e.concepts_mastered === "number"
                    ? ` · ${e.concepts_mastered} mastered`
                    : ""}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
