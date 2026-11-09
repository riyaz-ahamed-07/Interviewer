import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import CapsuleTodo from "./ui/CapsuleTodo";
import type { DayCardModel, DayTask } from "../forge/weekPlan";
import { taskKey } from "../forge/weekPlan";

const CONFETTI = ["#a78bfa", "#c4b5fd", "#34d399", "#f59e0b", "#60a5fa"];

function ConfettiBurst() {
  const pieces = useMemo(
    () =>
      Array.from({ length: 18 }, (_, i) => ({
        i,
        left: Math.random() * 100,
        delay: Math.random() * 0.4,
        duration: 2 + Math.random(),
        size: 5 + Math.random() * 5,
        color: CONFETTI[i % CONFETTI.length],
      })),
    [],
  );
  return (
    <div className="day-card-confetti" aria-hidden>
      {pieces.map((p) => (
        <span
          key={p.i}
          className="day-card-confetti-piece"
          style={{
            left: `${p.left}%`,
            width: p.size,
            height: p.size * 0.4,
            background: p.color,
            animationDuration: `${p.duration}s`,
            animationDelay: `${p.delay}s`,
          }}
        />
      ))}
    </div>
  );
}

export default function DayTodoCard({
  card,
  checks,
  onToggle,
}: {
  card: DayCardModel;
  checks: Record<string, boolean>;
  onToggle: (dateKey: string, taskId: string) => void;
}) {
  const required = card.tasks.filter((t) => !t.optional);
  const allDone =
    required.length > 0 &&
    required.every((t) => checks[taskKey(card.dateKey, t.id)]);

  const [celebrating, setCelebrating] = useState(false);
  const wasAll = useRef(false);

  useEffect(() => {
    if (allDone && !wasAll.current) {
      wasAll.current = true;
      setCelebrating(true);
      const t = window.setTimeout(() => setCelebrating(false), 2800);
      return () => window.clearTimeout(t);
    }
    if (!allDone) {
      wasAll.current = false;
      setCelebrating(false);
    }
  }, [allDone]);

  return (
    <article
      className={`day-todo-card soft-card${allDone ? " is-done" : ""}${card.isToday ? " is-today" : ""}`}
    >
      <header className={`day-todo-head${allDone ? " done" : ""}`}>
        <div className="day-todo-date">
          <span className="day-todo-dow">{card.shortLabel}</span>
          <span className="day-todo-chip">{card.topic}</span>
          <span className="day-todo-chip soft">{card.practiceLabel}</span>
        </div>
        <div className="day-todo-head-right">
          <span className="day-todo-budget">{card.budgetMin}m</span>
          {allDone ? (
            <span className="day-todo-badge">Done</span>
          ) : card.isToday ? (
            <span className="day-todo-badge soft">Today</span>
          ) : null}
        </div>
      </header>

      <div className={`day-todo-body${allDone ? " done" : ""}`}>
        <ul className="day-todo-list">
          {card.tasks.map((task: DayTask) => {
            const key = taskKey(card.dateKey, task.id);
            const done = Boolean(checks[key]);
            return (
              <li
                key={task.id}
                className={`lane-${task.lane} kind-${task.kind}${done ? " done" : ""}${task.optional ? " optional" : ""}`}
              >
                <CapsuleTodo
                  checked={done}
                  lane={task.lane}
                  optional={task.optional}
                  onChange={() => onToggle(card.dateKey, task.id)}
                >
                  {task.text}
                  {task.estMin ? (
                    <em className="day-todo-est"> · {task.estMin}m</em>
                  ) : null}
                </CapsuleTodo>
              </li>
            );
          })}
        </ul>
        <Link className="day-todo-open" to={`/forge/day/${card.dateKey}`}>
          Open day →
        </Link>
        {celebrating ? <ConfettiBurst /> : null}
      </div>
    </article>
  );
}
