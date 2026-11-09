import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import DayTodoCard from "../components/DayTodoCard";
import {
  loadStore,
  saveStore,
  toggleWeekTask,
  weekKey,
} from "../forge/progress";
import {
  buildWeekDayCards,
  forgeWeekMeta,
  forgeWeekNumber,
  getMaxPlannedWeek,
} from "../forge/weekPlan";
import type { ForgeStore } from "../forge/types";
import { getWeek } from "../forge/plan/selectors";
import "../App.css";

export function ForgePanel({ compact = false }: { compact?: boolean }) {
  const [store, setStore] = useState<ForgeStore>(() => loadStore());
  const [flash, setFlash] = useState("");
  const [showPaper, setShowPaper] = useState(false);
  const [paperTitle, setPaperTitle] = useState(store.paperWeek?.title ?? "");
  const [paperArxiv, setPaperArxiv] = useState(store.paperWeek?.arxiv ?? "");
  const [weekNumber, setWeekNumber] = useState(() =>
    Math.min(forgeWeekNumber(), getMaxPlannedWeek()),
  );

  useEffect(() => {
    saveStore(store);
  }, [store]);

  const maxWeek = getMaxPlannedWeek();
  const planWeek = useMemo(() => getWeek(weekNumber), [weekNumber]);
  const weekMeta = useMemo(() => forgeWeekMeta(weekNumber), [weekNumber]);
  const weekCards = useMemo(
    () => buildWeekDayCards(store, weekNumber),
    [store, weekNumber],
  );

  const onDayToggle = (dateKey: string, taskId: string) => {
    setStore(toggleWeekTask(store, dateKey, taskId));
  };

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
    setFlash("Paper set");
    window.setTimeout(() => setFlash(""), 1800);
  };

  return (
    <div className={`forge-embed${compact ? " is-compact" : ""}`} id="forge">
      {flash ? <p className="forge-flash">{flash}</p> : null}

      <section className="forge-panel forge-week-panel">
        <div className="forge-week-toolbar">
          <div className="forge-today-head forge-week-nav">
            <div className="forge-week-nav-main">
              <button
                type="button"
                className="forge-week-arrow"
                aria-label="Previous week"
                disabled={weekNumber <= 1}
                onClick={() => setWeekNumber((n) => Math.max(1, n - 1))}
              >
                ‹
              </button>
              <div className="forge-week-nav-label">
                <h3>Week {weekMeta.weekNumber}</h3>
                <span className="forge-hours">{weekMeta.rangeLabel}</span>
                {planWeek ? (
                  <span className="forge-week-theme">{planWeek.theme}</span>
                ) : null}
              </div>
              <button
                type="button"
                className="forge-week-arrow"
                aria-label="Next week"
                disabled={weekNumber >= maxWeek}
                onClick={() =>
                  setWeekNumber((n) => Math.min(maxWeek, n + 1))
                }
              >
                ›
              </button>
            </div>
            {weekNumber !== Math.min(forgeWeekNumber(), maxWeek) ? (
              <button
                type="button"
                className="linkish forge-week-jump"
                onClick={() =>
                  setWeekNumber(Math.min(forgeWeekNumber(), maxWeek))
                }
              >
                This week
              </button>
            ) : null}
          </div>

          <div className="forge-kind-legend" aria-label="Task colors">
            <span className="forge-legend-item kind-leetcode">
              <i /> Practice
            </span>
            <span className="forge-legend-item kind-concept">
              <i /> Concept
            </span>
            <span className="forge-legend-item kind-module">
              <i /> Optional
            </span>
          </div>
        </div>

        <div className="forge-week-bento">
          {weekCards.map((card) => (
            <DayTodoCard
              key={card.dateKey}
              card={card}
              checks={store.weekChecks}
              onToggle={onDayToggle}
            />
          ))}
        </div>

        <div className="forge-mini-row">
          <button
            type="button"
            className="linkish"
            onClick={() => setShowPaper((v) => !v)}
          >
            {store.paperWeek?.title
              ? `Paper: ${store.paperWeek.title}`
              : "Set this week’s paper"}
          </button>
          <Link className="linkish" to="/forge/stats">
            Stats →
          </Link>
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
