import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import SoftCard from "../components/ui/SoftCard";
import PillButton from "../components/ui/PillButton";
import Mascot from "../components/ui/Mascot";
import { loadStore } from "../forge/progress";
import { todayKey } from "../forge/dates";
import "../App.css";

function hitsForDay(checks: Record<string, boolean>, dateKey: string) {
  let n = 0;
  for (const [k, v] of Object.entries(checks)) {
    if (v && k.startsWith(`${dateKey}::`)) n += 1;
  }
  return n;
}

export default function ForgeCalendar() {
  const [store] = useState(() => loadStore());
  const [cursor, setCursor] = useState(() => {
    const n = new Date();
    return new Date(n.getFullYear(), n.getMonth(), 1);
  });

  const today = todayKey();
  const cells = useMemo(() => {
    const year = cursor.getFullYear();
    const month = cursor.getMonth();
    const firstDow = (new Date(year, month, 1).getDay() + 6) % 7;
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const out: { key: string; label: string; hits: number }[] = [];
    for (let i = 0; i < firstDow; i++) {
      out.push({ key: `pad-${i}`, label: "", hits: -1 });
    }
    for (let d = 1; d <= daysInMonth; d++) {
      const key = todayKey(new Date(year, month, d));
      out.push({
        key,
        label: String(d),
        hits: hitsForDay(store.weekChecks, key),
      });
    }
    return out;
  }, [cursor, store.weekChecks]);

  const title = cursor.toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
  });

  return (
    <div className="habit-page">
      <div className="habit-hero">
        <div>
          <p className="eyebrow">Calendar</p>
          <h1>{title}</h1>
          <p>Completion density from your week checks</p>
        </div>
        <Mascot mood="idle" />
      </div>

      <div className="onboard-actions" style={{ justifyContent: "flex-start" }}>
        <PillButton
          variant="soft"
          onClick={() =>
            setCursor(new Date(cursor.getFullYear(), cursor.getMonth() - 1, 1))
          }
        >
          Prev
        </PillButton>
        <PillButton
          variant="ghost"
          onClick={() =>
            setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1))
          }
        >
          Next
        </PillButton>
      </div>

      <SoftCard style={{ padding: "1rem", marginTop: "0.75rem" }}>
        <div className="calendar-grid" style={{ marginBottom: "0.4rem" }}>
          {["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"].map((d) => (
            <div
              key={d}
              style={{
                textAlign: "center",
                fontWeight: 800,
                fontSize: "0.75rem",
                color: "var(--muted)",
              }}
            >
              {d}
            </div>
          ))}
        </div>
        <div className="calendar-grid">
          {cells.map((c) => {
            if (c.hits < 0) return <div key={c.key} />;
            const hitClass =
              c.hits >= 4 ? "hit-3" : c.hits >= 2 ? "hit-2" : c.hits >= 1 ? "hit-1" : "";
            return (
              <Link
                key={c.key}
                to={`/forge/day/${c.key}`}
                className={`calendar-cell ${hitClass}${c.key === today ? " today" : ""}`}
              >
                {c.label}
              </Link>
            );
          })}
        </div>
      </SoftCard>

      <div className="onboard-actions">
        <Link to="/">
          <PillButton variant="soft">Home</PillButton>
        </Link>
        <Link to="/forge/stats">
          <PillButton>Stats</PillButton>
        </Link>
      </div>
    </div>
  );
}
