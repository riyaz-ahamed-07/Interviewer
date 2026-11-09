import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { PILLARS, countLeaves, findNode } from "../forge/curriculum";
import {
  levelForXp,
  loadStore,
  pillarStats,
  saveStore,
  setNodeState,
} from "../forge/progress";
import {
  buildWeekDayCards,
  forgeWeekNumber,
  getMaxPlannedWeek,
} from "../forge/weekPlan";
import { getWeek } from "../forge/plan/selectors";
import type { ForgeNode, ForgeStore, NodeState, Pillar } from "../forge/types";
import SoftCard from "../components/ui/SoftCard";
import "../App.css";

const TRACKS: { id: string; title: string; pillarIds: string[] }[] = [
  {
    id: "foundations",
    title: "Foundations",
    pillarIds: ["math", "ml", "aptitude"],
  },
  { id: "deep", title: "Deep learning", pillarIds: ["dl"] },
  {
    id: "modern",
    title: "Modern AI · Agents",
    pillarIds: ["llm", "agents", "papers", "mlops"],
  },
  {
    id: "practice",
    title: "TrenTorch practice",
    pillarIds: ["trentorch"],
  },
  {
    id: "systems",
    title: "Systems · Core CS",
    pillarIds: ["systems", "corecs"],
  },
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

export default function MasterList() {
  const [store, setStore] = useState<ForgeStore>(() => loadStore());
  const [trackId, setTrackId] = useState("foundations");
  const [pillarId, setPillarId] = useState("math");
  const [open, setOpenMap] = useState<Record<string, boolean>>({});
  const [flash, setFlash] = useState("");

  useEffect(() => {
    saveStore(store);
  }, [store]);

  const track = TRACKS.find((t) => t.id === trackId) ?? TRACKS[0];
  const trackPillars = track.pillarIds
    .map((id) => PILLARS.find((p) => p.id === id))
    .filter(Boolean) as Pillar[];
  const activePillar =
    trackPillars.find((p) => p.id === pillarId) ??
    trackPillars[0] ??
    PILLARS[0];
  const tp = trackProgress(store.progress, track.pillarIds);
  const weekNum = Math.min(forgeWeekNumber(), getMaxPlannedWeek());
  const planWeek = getWeek(weekNum);
  const weekCards = useMemo(
    () => buildWeekDayCards(store, weekNum),
    [store, weekNum],
  );

  const toggle = (id: string) => {
    const prev = store.progress[id] ?? "todo";
    const next = cycleState(prev);
    const updated = setNodeState(store, id, next);
    const before = levelForXp(store.xp).level;
    const after = levelForXp(updated.xp).level;
    setStore(updated);
    if (after > before)
      setFlash(`Level ${after} · ${levelForXp(updated.xp).title}`);
    else if (next === "done" || next === "mastered")
      setFlash(`+${findNode(id)?.node.xp ?? 12} XP`);
    window.setTimeout(() => setFlash(""), 1800);
  };

  const setOpen = (id: string, v: boolean) =>
    setOpenMap((m) => ({ ...m, [id]: v }));

  return (
    <div className="shell master-list-page habit-page">
      <header className="forge-hero">
        <h2>
          Master list <span>curriculum</span>
        </h2>
        {flash ? <p className="forge-flash">{flash}</p> : null}
      </header>
      {planWeek ? (
        <SoftCard style={{ padding: "0.9rem 1rem", marginBottom: "0.85rem" }}>
          <strong>This week’s plan · Week {weekNum}</strong>
          <p style={{ margin: "0.25rem 0 0.55rem", color: "var(--muted)" }}>
            {planWeek.theme}
          </p>
          <ul style={{ margin: 0, paddingLeft: "1.1rem" }}>
            {weekCards.slice(0, 5).map((c) => (
              <li key={c.dateKey}>
                <Link to={`/forge/day/${c.dateKey}`}>
                  {c.shortLabel}: {c.topic} · {c.practiceLabel}
                </Link>
              </li>
            ))}
          </ul>
        </SoftCard>
      ) : null}
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
    </div>
  );
}
