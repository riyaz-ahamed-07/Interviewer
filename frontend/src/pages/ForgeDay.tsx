import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import SoftCard from "../components/ui/SoftCard";
import PillButton from "../components/ui/PillButton";
import Mascot from "../components/ui/Mascot";
import CapsuleTodo from "../components/ui/CapsuleTodo";
import { loadStore, saveStore, toggleWeekTask } from "../forge/progress";
import {
  buildWeekDayCards,
  forgeWeekNumber,
  getMaxPlannedWeek,
  taskKey,
} from "../forge/weekPlan";
import type { ForgeStore } from "../forge/types";
import "../App.css";

export default function ForgeDay() {
  const { dateKey = "" } = useParams();
  const [store, setStore] = useState<ForgeStore>(() => loadStore());

  useEffect(() => {
    saveStore(store);
  }, [store]);

  const weekNumber = useMemo(() => {
    if (!dateKey) return Math.min(forgeWeekNumber(), getMaxPlannedWeek());
    const [y, m, d] = dateKey.split("-").map(Number);
    return Math.min(
      forgeWeekNumber(new Date(y, m - 1, d)),
      getMaxPlannedWeek(),
    );
  }, [dateKey]);

  const card = useMemo(() => {
    const cards = buildWeekDayCards(store, weekNumber);
    return cards.find((c) => c.dateKey === dateKey) ?? null;
  }, [store, weekNumber, dateKey]);

  if (!card) {
    return (
      <div className="habit-page">
        <SoftCard className="onboard-card">
          <Mascot mood="nudge" />
          <h2>Day not in plan</h2>
          <p>That date isn’t in the Weeks 1–{getMaxPlannedWeek()} catalog.</p>
          <Link to="/">
            <PillButton>Back home</PillButton>
          </Link>
        </SoftCard>
      </div>
    );
  }

  const required = card.tasks.filter((t) => !t.optional);
  const doneCount = required.filter(
    (t) => store.weekChecks[taskKey(card.dateKey, t.id)],
  ).length;

  return (
    <div className="habit-page">
      <div className="habit-hero">
        <div>
          <p className="eyebrow">Day detail</p>
          <h1>
            {card.label} · {card.topic}
          </h1>
          <p>
            {doneCount}/{required.length} required · budget {card.budgetMin}m ·{" "}
            {card.practiceLabel}
          </p>
        </div>
        <Mascot mood={doneCount === required.length ? "celebrate" : "idle"} />
      </div>

      <SoftCard style={{ padding: "1rem" }}>
        <ul className="day-detail-list">
          {card.tasks.map((task) => {
            const key = taskKey(card.dateKey, task.id);
            const done = Boolean(store.weekChecks[key]);
            return (
              <li key={task.id}>
                <CapsuleTodo
                  checked={done}
                  lane={task.lane}
                  optional={task.optional}
                  onChange={() =>
                    setStore(toggleWeekTask(store, card.dateKey, task.id))
                  }
                >
                  <span className={`lane-tag ${task.lane}`}>{task.lane}</span>{" "}
                  {task.text}
                  {task.estMin ? (
                    <em className="day-todo-est"> · {task.estMin}m</em>
                  ) : null}
                </CapsuleTodo>
              </li>
            );
          })}
        </ul>
      </SoftCard>

      <div className="onboard-actions">
        <Link to="/">
          <PillButton variant="soft">Week board</PillButton>
        </Link>
        <Link to="/forge/stats">
          <PillButton variant="ghost">Stats</PillButton>
        </Link>
      </div>
    </div>
  );
}
