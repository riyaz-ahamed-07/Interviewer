import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  explainSelection,
  fetchPaperRef,
  getPaper,
  paperAdvance,
  paperChat,
  setPaperPrereqs,
  startPaperSession,
  type FlashCard,
  type PaperConcept,
  type PaperDoc,
  type PaperMap,
  type PaperSession,
  type Prerequisite,
} from "../api";
import MermaidBlock from "../components/MermaidBlock";
import PaperMarkdown from "../components/PaperMarkdown";
import "../App.css";

type RightTab = "diagram" | "prereqs" | "glossary" | "notes" | "quiz";

type ExplainBox = {
  short: string;
  deeper: string;
  example?: string;
};

function highlightGlossary(text: string, glossary: Record<string, string>) {
  const terms = Object.keys(glossary).sort((a, b) => b.length - a.length);
  if (!terms.length) return [{ t: text, g: false as const }];
  const out: Array<{ t: string; g: boolean; def?: string }> = [];
  let rest = text;
  while (rest) {
    let hit: { i: number; term: string } | null = null;
    for (const term of terms) {
      const i = rest.toLowerCase().indexOf(term.toLowerCase());
      if (i >= 0 && (hit === null || i < hit.i)) hit = { i, term };
    }
    if (!hit) {
      out.push({ t: rest, g: false });
      break;
    }
    if (hit.i > 0) out.push({ t: rest.slice(0, hit.i), g: false });
    const raw = rest.slice(hit.i, hit.i + hit.term.length);
    out.push({ t: raw, g: true, def: glossary[hit.term] ?? glossary[Object.keys(glossary).find((k) => k.toLowerCase() === hit!.term.toLowerCase()) || ""] });
    rest = rest.slice(hit.i + hit.term.length);
  }
  return out;
}

export default function PaperBuddy() {
  const { paperId = "" } = useParams();
  const [paper, setPaper] = useState<PaperDoc | null>(null);
  const [map, setMap] = useState<PaperMap | null>(null);
  const [cards, setCards] = useState<FlashCard[]>([]);
  const [session, setSession] = useState<PaperSession | null>(null);
  const [tab, setTab] = useState<RightTab>("diagram");
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("Loading…");
  const [explain, setExplain] = useState<ExplainBox | null>(null);
  const [refPop, setRefPop] = useState<{ title: string; body: string } | null>(null);
  const [oneLiner, setOneLiner] = useState("");
  const [quizIdx, setQuizIdx] = useState(0);
  const [quizReveal, setQuizReveal] = useState(false);
  const paperPane = useRef<HTMLDivElement>(null);
  const chatEnd = useRef<HTMLDivElement>(null);

  const concept: PaperConcept | null = useMemo(() => {
    if (!map?.concepts.length || !session) return null;
    const i = Math.max(
      0,
      Math.min(session.current_concept_index, map.concepts.length - 1),
    );
    return map.concepts[i] ?? null;
  }, [map, session]);

  const conceptSectionIds = useMemo(
    () => new Set(concept?.section_ids ?? []),
    [concept],
  );

  const boot = useCallback(async () => {
    if (!paperId) return;
    setStatus("Loading paper…");
    try {
      const data = await getPaper(paperId);
      setPaper(data.paper);
      setMap(data.map);
      setCards(data.cards);
      const started = await startPaperSession(paperId, "text");
      setSession(started.session);
      setMap(started.map);
      setStatus("");
    } catch (e) {
      setStatus(String(e));
    }
  }, [paperId]);

  useEffect(() => {
    void boot();
  }, [boot]);

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [session?.messages.length]);

  const send = async (text: string) => {
    if (!session || !text.trim() || busy) return;
    setBusy(true);
    try {
      const res = await paperChat(session.id, text.trim(), concept?.id);
      setSession(res.session);
      setMap(res.map);
      setInput("");
    } catch (e) {
      setStatus(String(e));
    } finally {
      setBusy(false);
    }
  };

  const advance = async (action: "got_it" | "skip" | "deeper") => {
    if (!session || busy) return;
    setBusy(true);
    try {
      const res = await paperAdvance(session.id, action, oneLiner.trim());
      setSession(res.session);
      setMap(res.map);
      if (action !== "deeper") setOneLiner("");
    } catch (e) {
      setStatus(String(e));
    } finally {
      setBusy(false);
    }
  };

  const onExplainSelection = async () => {
    if (!paper || !paperId) return;
    const sel = window.getSelection()?.toString().trim();
    if (!sel || sel.length < 2) return;
    setBusy(true);
    try {
      const kind = /[=\\^_{}]/.test(sel) ? "equation" : sel.split(/\s+/).length > 8 ? "sentence" : "term";
      const data = await explainSelection(paperId, {
        selection: sel,
        kind,
        paragraph: sel,
      });
      setExplain(data);
      if (kind === "term" && map) {
        setMap({
          ...map,
          glossary: { ...map.glossary, [sel]: data.short },
        });
      }
    } catch (e) {
      setStatus(String(e));
    } finally {
      setBusy(false);
    }
  };

  const openRef = async (index: number) => {
    if (!paperId) return;
    setBusy(true);
    try {
      const data = await fetchPaperRef(paperId, index);
      setRefPop({
        title: data.reference.title || data.reference.raw.slice(0, 80),
        body:
          data.reference.tldr ||
          data.reference.abstract ||
          data.context?.tldr ||
          data.reference.raw,
      });
    } catch (e) {
      setStatus(String(e));
    } finally {
      setBusy(false);
    }
  };

  const setPrereq = async (id: string, status: Prerequisite["status"]) => {
    if (!paperId || !map) return;
    const statuses = Object.fromEntries(
      map.prerequisites.map((p) => [p.id, p.id === id ? status : p.status]),
    ) as Record<string, Prerequisite["status"]>;
    const res = await setPaperPrereqs(paperId, statuses);
    setMap(res.map);
  };

  const notesMd = useMemo(() => {
    if (!map) return "";
    const lines = [
      `# ${paper?.title ?? "Paper"} notes`,
      "",
      "## Concepts",
      ...map.concepts.map(
        (c) =>
          `- **${c.title}** (${c.state})${c.learner_one_liner ? `: ${c.learner_one_liner}` : ""}`,
      ),
      "",
      "## Free notes",
      session?.notes || "_none yet_",
    ];
    return lines.join("\n");
  }, [map, paper, session]);

  const exportNotes = () => {
    const blob = new Blob([notesMd], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${paper?.arxiv_id || paper?.id || "notes"}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!paper || !map || !session) {
    return (
      <div className="shell lobby">
        <p className="eyebrow">
          <Link to="/buddies/paper">Library</Link>
        </p>
        <p className="status">{status || "Loading…"}</p>
      </div>
    );
  }

  const n = map.concepts.length;
  const ci = session.current_concept_index;
  const quizCard = cards[quizIdx % Math.max(cards.length, 1)] ?? null;

  return (
    <div className="paper-buddy">
      <header className="paper-buddy-top">
        <div>
          <p className="eyebrow">
            <Link to="/buddies/paper">Library</Link> · Dr. Delta
          </p>
          <h1>{paper.title}</h1>
          {paper.arxiv_id ? (
            <p className="lede">
              arXiv {paper.arxiv_id}
              {paper.authors?.length ? ` · ${paper.authors.slice(0, 3).join(", ")}` : ""}
            </p>
          ) : null}
        </div>
        <div className="pass1-card">
          <strong>Pass 1</strong>
          <p>{map.pass1.problem}</p>
          <p>
            <em>{map.pass1.core_claim}</em>
          </p>
          <p className="status">{map.pass1.verdict}</p>
          <p>
            Parent: <strong>{map.parent.title}</strong>
            {map.parent.arxiv_id ? ` (${map.parent.arxiv_id})` : ""} —{" "}
            {map.parent.one_liner}
          </p>
        </div>
      </header>
      {status ? <p className="status paper-status">{status}</p> : null}

      <div className="paper-panes">
        <aside className="paper-pane left" ref={paperPane}>
          <div className="pane-toolbar">
            <button type="button" className="cta ghost" onClick={() => void onExplainSelection()}>
              Explain selection
            </button>
          </div>
          <nav className="section-outline">
            {paper.sections.map((s) => (
              <a key={s.id} href={`#sec-${s.id}`}>
                {s.heading}
              </a>
            ))}
          </nav>
          <article className="paper-body">
            <h2>Abstract</h2>
            <p>
              {highlightGlossary(paper.abstract, map.glossary).map((part, i) =>
                part.g ? (
                  <abbr key={i} title={part.def} className="glossary-term">
                    {part.t}
                  </abbr>
                ) : (
                  <span key={i}>{part.t}</span>
                ),
              )}
            </p>
            {paper.sections.map((s) => {
              const hot = conceptSectionIds.size === 0 || conceptSectionIds.has(s.id);
              return (
                <section
                  key={s.id}
                  id={`sec-${s.id}`}
                  className={hot && conceptSectionIds.size ? "sec-hot" : undefined}
                >
                  <h2>{s.heading}</h2>
                  {s.paragraphs.map((para, pi) => (
                    <p key={pi}>
                      {highlightGlossary(para, map.glossary).map((part, i) =>
                        part.g ? (
                          <abbr
                            key={i}
                            title={part.def}
                            className="glossary-term"
                            onClick={() =>
                              setExplain({
                                short: part.def || part.t,
                                deeper: part.def || "",
                              })
                            }
                          >
                            {part.t}
                          </abbr>
                        ) : (
                          <span key={i}>{part.t}</span>
                        ),
                      )}
                    </p>
                  ))}
                </section>
              );
            })}
            {paper.equations.length ? (
              <section>
                <h2>Equations</h2>
                {paper.equations.map((eq) => (
                  <div key={eq.id} className="eq-block">
                    <PaperMarkdown text={`$$${eq.latex}$$`} />
                    <button
                      type="button"
                      className="linkish"
                      onClick={() =>
                        void explainSelection(paperId, {
                          selection: eq.latex,
                          kind: "equation",
                          section_id: eq.section_id,
                        }).then(setExplain)
                      }
                    >
                      Explain
                    </button>
                  </div>
                ))}
              </section>
            ) : null}
            {paper.references.length ? (
              <section>
                <h2>References</h2>
                <ol className="ref-list">
                  {paper.references.slice(0, 40).map((r, i) => (
                    <li key={i}>
                      <button type="button" className="linkish" onClick={() => void openRef(i)}>
                        {r.title || r.raw.slice(0, 120)}
                      </button>
                    </li>
                  ))}
                </ol>
              </section>
            ) : null}
          </article>
        </aside>

        <section className="paper-pane mid">
          <div className="concept-bar">
            <strong>
              Concept {Math.min(ci + 1, n)} of {n}: {concept?.title ?? "—"}
            </strong>
            <div className="concept-actions">
              <button
                type="button"
                disabled={busy || ci <= 0}
                onClick={() => {
                  if (!session) return;
                  setSession({
                    ...session,
                    current_concept_index: Math.max(0, ci - 1),
                  });
                }}
              >
                Back
              </button>
              <button type="button" disabled={busy} onClick={() => void advance("got_it")}>
                I got it, check me
              </button>
              <button type="button" disabled={busy} onClick={() => void advance("deeper")}>
                Go deeper
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => void send("Show the maths for this concept.")}
              >
                Show the maths
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => void send("Show a minimal code sketch for this concept.")}
              >
                Show code
              </button>
              <button type="button" disabled={busy} onClick={() => void advance("skip")}>
                Skip anyway
              </button>
            </div>
            <input
              className="one-liner"
              value={oneLiner}
              onChange={(e) => setOneLiner(e.target.value)}
              placeholder="Your one-liner for this concept (before Got it)"
            />
          </div>
          <div className="tutor-chat">
            {session.messages.map((m, i) => (
              <div key={i} className={`msg ${m.role}`}>
                <PaperMarkdown text={m.content} />
              </div>
            ))}
            <div ref={chatEnd} />
          </div>
          <form
            className="tutor-input"
            onSubmit={(e) => {
              e.preventDefault();
              void send(input);
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Dr. Delta…"
              disabled={busy}
            />
            <button type="submit" className="cta" disabled={busy || !input.trim()}>
              Send
            </button>
          </form>
        </section>

        <aside className="paper-pane right">
          <div className="right-tabs">
            {(
              [
                ["diagram", "Diagram"],
                ["prereqs", "Prereqs"],
                ["glossary", "Glossary"],
                ["notes", "Notes"],
                ["quiz", "Quiz"],
              ] as const
            ).map(([id, label]) => (
              <button
                key={id}
                type="button"
                className={tab === id ? "on" : ""}
                onClick={() => setTab(id)}
              >
                {label}
              </button>
            ))}
          </div>
          <div className="right-body">
            {tab === "diagram" ? (
              <>
                <h3>Parent</h3>
                <MermaidBlock chart={map.diagrams.parent_mermaid || ""} />
                <h3>This paper</h3>
                <MermaidBlock chart={map.diagrams.paper_mermaid || ""} />
                <table className="delta-table">
                  <thead>
                    <tr>
                      <th>Component</th>
                      <th>Before</th>
                      <th>After</th>
                    </tr>
                  </thead>
                  <tbody>
                    {map.parent.deltas.map((d, i) => (
                      <tr key={i}>
                        <td>{d.component}</td>
                        <td>{d.before}</td>
                        <td>{d.after}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </>
            ) : null}
            {tab === "prereqs" ? (
              <ul className="prereq-list">
                {map.prerequisites.map((p) => (
                  <li key={p.id}>
                    <strong>{p.name}</strong>
                    <p>{p.primer}</p>
                    <p className="lede">Check: {p.check_question}</p>
                    <div className="prereq-status">
                      {(["known", "shaky", "unknown"] as const).map((s) => (
                        <button
                          key={s}
                          type="button"
                          className={p.status === s ? "on" : ""}
                          onClick={() => void setPrereq(p.id, s)}
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </li>
                ))}
              </ul>
            ) : null}
            {tab === "glossary" ? (
              <ul className="glossary-list">
                {Object.entries(map.glossary).map(([term, def]) => (
                  <li key={term}>
                    <strong>{term}</strong>
                    <p>{def}</p>
                  </li>
                ))}
              </ul>
            ) : null}
            {tab === "notes" ? (
              <>
                <pre className="notes-preview">{notesMd}</pre>
                <button type="button" className="cta ghost" onClick={exportNotes}>
                  Export Markdown
                </button>
              </>
            ) : null}
            {tab === "quiz" ? (
              cards.length === 0 ? (
                <p className="lede">No cards yet.</p>
              ) : (
                <div className="quiz-card">
                  <p>
                    {quizIdx + 1}/{cards.length}
                  </p>
                  <p>{quizCard?.question}</p>
                  {quizReveal ? <p className="quiz-answer">{quizCard?.answer}</p> : null}
                  <div className="quiz-grades">
                    <button type="button" onClick={() => setQuizReveal(true)}>
                      Reveal
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setQuizReveal(false);
                        setQuizIdx((x) => x + 1);
                      }}
                    >
                      Next
                    </button>
                  </div>
                </div>
              )
            ) : null}
          </div>
        </aside>
      </div>

      {explain ? (
        <div className="paper-pop" role="dialog">
          <button type="button" className="pop-close" onClick={() => setExplain(null)}>
            ×
          </button>
          <h3>Explain</h3>
          <p>{explain.short}</p>
          {explain.deeper ? <p>{explain.deeper}</p> : null}
          {explain.example ? <p className="lede">{explain.example}</p> : null}
        </div>
      ) : null}
      {refPop ? (
        <div className="paper-pop" role="dialog">
          <button type="button" className="pop-close" onClick={() => setRefPop(null)}>
            ×
          </button>
          <h3>{refPop.title}</h3>
          <p>{refPop.body}</p>
        </div>
      ) : null}
    </div>
  );
}
