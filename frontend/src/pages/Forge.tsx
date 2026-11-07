import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { PILLARS, countLeaves, findNode } from "../forge/curriculum";
import {
  buildDailyQuests,
  levelForXp,
  loadStore,
  overallStats,
  pillarStats,
  saveStore,
  setNodeState,
  weekKey,
} from "../forge/progress";
import type { ForgeNode, ForgeStore, NodeState, Pillar } from "../forge/types";
import "../App.css";

type View = "today" | "list";

const TRACKS: { id: string; title: string; pillarIds: string[] }[] = [
  { id: "foundations", title: "Foundations", pillarIds: ["math", "ml", "aptitude"] },
  { id: "deep", title: "Deep learning", pillarIds: ["dl"] },
  { id: "modern", title: "Modern AI", pillarIds: ["llm", "papers", "mlops"] },
  { id: "systems", title: "Systems · NVIDIA path", pillarIds: ["systems", "corecs"] },
  {
    id: "interview",
    title: "Interview armor",
    pillarIds: ["dsa", "sql", "sysdesign", "comms", "career"],
  },
];

function cycleState(s: NodeState): NodeState {
  if (s === "todo") return "learning";
  if (s === "learning") return "done";
  if (s === "done") return "mastered";
  return "todo";
}

function mark(s: NodeState) {
  if (s === "todo") return "○";
  if (s === "learning") return "◐";
  if (s === "done") return "●";
  return "◆";
}

function TreeNode({
  node,
  depth,
  progress,
  onToggle,
  open,
  setOpen,
}: {
  node: ForgeNode;
  depth: number;
  progress: ForgeStore["progress"];
  onToggle: (id: string) => void;
  open: Record<string, boolean>;
  setOpen: (id: string, v: boolean) => void;
}) {
  const hasKids = Boolean(node.children?.length);
  const expanded = open[node.id] ?? false;
  const state = progress[node.id] ?? "todo";

  return (
    <div className="forge-node" style={{ marginLeft: depth ? 12 : 0 }}>
      <div className="forge-row">
        {hasKids ? (
          <button
            type="button"
            className="forge-twist"
            aria-expanded={expanded}
            onClick={() => setOpen(node.id, !expanded)}
          >
            {expanded ? "▾" : "▸"}
          </button>
        ) : (
          <button
            type="button"
            className={`forge-check ${state}`}
            onClick={() => onToggle(node.id)}
            title="tap: todo → learning → done → mastered"
          >
            {mark(state)}
          </button>
        )}
        <span className={`forge-title ${state}`}>{node.title}</span>
      </div>
      {hasKids && expanded
        ? node.children!.map((c) => (
            <TreeNode
              key={c.id}
              node={c}
              depth={depth + 1}
              progress={progress}
              onToggle={onToggle}
              open={open}
              setOpen={setOpen}
            />
          ))
        : null}
    </div>
  );
}

function trackProgress(progress: ForgeStore["progress"], pillarIds: string[]) {
  let total = 0;
  let done = 0;
  for (const id of pillarIds) {
    const s = pillarStats(progress, id);
    total += s.total;
    done += s.done;
  }
  return { total, done };
}

export function ForgePanel() {
  const [store, setStore] = useState<ForgeStore>(() => loadStore());
  const [view, setView] = useState<View>("today");
  const [trackId, setTrackId] = useState("foundations");
  const [pillarId, setPillarId] = useState("math");
  const [open, setOpenMap] = useState<Record<string, boolean>>({});
  const [flash, setFlash] = useState("");
  const [showPaper, setShowPaper] = useState(false);
  const [paperTitle, setPaperTitle] = useState(store.paperWeek?.title ?? "");
  const [paperArxiv, setPaperArxiv] = useState(store.paperWeek?.arxiv ?? "");

  useEffect(() => {
    saveStore(store);
  }, [store]);

  const level = levelForXp(store.xp);
  const overall = overallStats(store.progress);
  const quests = useMemo(() => buildDailyQuests(store), [store]);
  const track = TRACKS.find((t) => t.id === trackId) ?? TRACKS[0];
  const trackPillars = track.pillarIds
    .map((id) => PILLARS.find((p) => p.id === id))
    .filter(Boolean) as Pillar[];
  const activePillar =
    trackPillars.find((p) => p.id === pillarId) ?? trackPillars[0] ?? PILLARS[0];
  const tp = trackProgress(store.progress, track.pillarIds);

  const celebrate = (msg: string) => {
    setFlash(msg);
    window.setTimeout(() => setFlash(""), 1800);
  };

  const toggle = (id: string) => {
    const prev = store.progress[id] ?? "todo";
    const next = cycleState(prev);
    const updated = setNodeState(store, id, next);
    const before = levelForXp(store.xp).level;
    const after = levelForXp(updated.xp).level;
    setStore(updated);
    if (after > before) celebrate(`Level ${after} · ${levelForXp(updated.xp).title}`);
    else if (next === "done" || next === "mastered")
      celebrate(`+${findNode(id)?.node.xp ?? 12} XP`);
  };

  const setOpen = (id: string, v: boolean) =>
    setOpenMap((m) => ({ ...m, [id]: v }));

  const savePaper = () => {
    setStore({
      ...store,
      paperWeek: {
        weekKey: weekKey(),
        title: paperTitle.trim() || "Untitled paper",
        arxiv: paperArxiv.trim() || undefined,
        notes: store.paperWeek?.notes ?? "",
      },
    });
    setShowPaper(false);
    celebrate("Paper set");
  };

  const hoursHint =
    new Date().getDay() === 0 ? "~5h Sunday deep work" : "~3h (7–8pm + 10–12)";

  return (
    <div className="forge-embed" id="forge">
      <header className="forge-hero">
        <p className="eyebrow">Forge · Invincible</p>
        <h2>
          NVIDIA north star <span>mastery</span>
        </h2>
        <p className="lede forge-one-liner">
          Mark concepts as you learn · one paper a week · no tutorial hell
        </p>
        <div className="forge-hud compact">
          <div className="forge-stat">
            <strong>{store.streak}</strong>
            <span>streak</span>
          </div>
          <div className="forge-stat">
            <strong>{store.xp}</strong>
            <span>XP · L{level.level}</span>
          </div>
          <div className="forge-stat">
            <strong>
              {overall.done}/{overall.total}
            </strong>
            <span>done</span>
          </div>
        </div>
        <div className="forge-xpbar" aria-hidden>
          <div style={{ width: `${Math.round(level.progress * 100)}%` }} />
        </div>
        {flash ? <p className="forge-flash">{flash}</p> : null}
      </header>

      <nav className="forge-tabs">
        <button
          type="button"
          className={view === "today" ? "on" : ""}
          onClick={() => setView("today")}
        >
          Today
        </button>
        <button
          type="button"
          className={view === "list" ? "on" : ""}
          onClick={() => setView("list")}
        >
          Master list
        </button>
      </nav>

      {view === "today" ? (
        <section className="forge-panel">
          <div className="forge-today-head">
            <h3>Do these</h3>
            <span className="forge-hours">{hoursHint}</span>
          </div>
          <ul className="forge-quests">
            {quests.map((q) => {
              const real = !q.id.startsWith("__paper__");
              const st = real ? store.progress[q.id] ?? "todo" : "todo";
              return (
                <li key={q.id} className={`forge-quest ${st}`}>
                  <div>
                    <strong>{q.title}</strong>
                    <p>{q.path.slice(0, 2).join(" · ")}</p>
                  </div>
                  {real ? (
                    <button type="button" className="cta ghost" onClick={() => toggle(q.id)}>
                      {mark(st)}
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="cta ghost"
                      onClick={() => setShowPaper(true)}
                    >
                      set
                    </button>
                  )}
                </li>
              );
            })}
          </ul>
          <div className="forge-mini-row">
            <button type="button" className="linkish" onClick={() => setShowPaper((v) => !v)}>
              {store.paperWeek?.title
                ? `Paper: ${store.paperWeek.title}`
                : "Set this week’s paper"}
            </button>
            <Link className="linkish" to="/buddies/paper">
              Dr. Delta →
            </Link>
          </div>
          {showPaper ? (
            <div className="forge-paper-form forge-paper-inline">
              <input
                value={paperTitle}
                onChange={(e) => setPaperTitle(e.target.value)}
                placeholder="Paper title"
              />
              <input
                value={paperArxiv}
                onChange={(e) => setPaperArxiv(e.target.value)}
                placeholder="arXiv id (optional)"
              />
              <button type="button" className="cta" onClick={savePaper}>
                Save paper
              </button>
            </div>
          ) : null}
        </section>
      ) : (
        <section className="forge-panel lattice">
          <div className="forge-tracks">
            {TRACKS.map((t) => {
              const s = trackProgress(store.progress, t.pillarIds);
              return (
                <button
                  key={t.id}
                  type="button"
                  className={`forge-track ${trackId === t.id ? "on" : ""}`}
                  onClick={() => {
                    setTrackId(t.id);
                    setPillarId(t.pillarIds[0]);
                  }}
                >
                  <strong>{t.title}</strong>
                  <span>
                    {s.done}/{s.total}
                  </span>
                </button>
              );
            })}
          </div>
          <div className="forge-subpillars">
            {trackPillars.map((p) => (
              <button
                key={p.id}
                type="button"
                className={activePillar.id === p.id ? "on" : ""}
                onClick={() => setPillarId(p.id)}
              >
                {p.title.replace(/ & .*/, "").replace(/ · .*/, "")}
              </button>
            ))}
          </div>
          <div className="forge-tree">
            <p className="lede">
              {activePillar.blurb} · {tp.done}/{tp.total} on this track
            </p>
            {activePillar.roots.map((root) => (
              <TreeNode
                key={root.id}
                node={root}
                depth={0}
                progress={store.progress}
                onToggle={toggle}
                open={open}
                setOpen={setOpen}
              />
            ))}
            <p className="forge-footnote">
              {countLeaves(activePillar.roots)} items · collapsed by default
            </p>
          </div>
        </section>
      )}
    </div>
  );
}

export default function Forge() {
  return (
    <div className="shell forge-page">
      <ForgePanel />
    </div>
  );
}
