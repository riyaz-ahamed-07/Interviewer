import { BatteryCharging, Flame, Zap } from "lucide-react";
import { todayKey } from "../forge/progress";
import type { ForgeStore } from "../forge/types";

const DAY_LABELS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"] as const;

export type StreakDayStatus = "done" | "today" | "ghost" | "empty";

export type StreakDayModel = {
  key: string;
  label: string;
  status: StreakDayStatus;
  band: "none" | "mid" | "end" | "solo";
};

function mondayStart(from = new Date()): Date {
  const d = new Date(from);
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
  return d;
}

function shiftKey(key: string, days: number): string {
  const [y, m, d] = key.split("-").map(Number);
  const dt = new Date(y, m - 1, d);
  dt.setDate(dt.getDate() + days);
  return todayKey(dt);
}

function dayHasActivity(store: ForgeStore, dateKey: string): boolean {
  const day = store.days[dateKey];
  if (day && (day.checked.length > 0 || day.xp > 0)) return true;
  if (store.lastActiveDate === dateKey) return true;
  for (const k of Object.keys(store.weekChecks)) {
    if (k.startsWith(`${dateKey}::`) && store.weekChecks[k]) return true;
  }
  return false;
}

function streakKeys(store: ForgeStore): Set<string> {
  const set = new Set<string>();
  if (!store.lastActiveDate || store.streak <= 0) return set;
  let cursor = store.lastActiveDate;
  for (let i = 0; i < store.streak; i++) {
    set.add(cursor);
    cursor = shiftKey(cursor, -1);
  }
  return set;
}

export function buildStreakDays(
  store: ForgeStore,
  from = new Date(),
): StreakDayModel[] {
  const start = mondayStart(from);
  const today = todayKey(from);
  const chain = streakKeys(store);
  const raw: { key: string; label: string; status: StreakDayStatus }[] = [];

  for (let i = 0; i < 7; i++) {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    const key = todayKey(d);
    const hit = dayHasActivity(store, key);
    let status: StreakDayStatus = "empty";
    if (chain.has(key) || (key === today && hit)) status = "done";
    else if (key === today) status = "today";
    else if (hit && key < today) status = "ghost";
    raw.push({ key, label: DAY_LABELS[i], status });
  }

  return raw.map((day, i) => {
    const isDone = day.status === "done";
    const prev = i > 0 && raw[i - 1].status === "done";
    const next = i < 6 && raw[i + 1].status === "done";
    let band: StreakDayModel["band"] = "none";
    if (isDone) {
      if (prev && next) band = "mid";
      else if (prev && !next) band = "end";
      else if (!prev && next) band = "mid";
      else band = "solo";
    }
    return { ...day, band };
  });
}

function DayIcon({
  variant,
  tone,
}: {
  variant: "flash" | "flame";
  tone: "hot" | "mute";
}) {
  const Icon = variant === "flame" ? Flame : Zap;
  return (
    <Icon
      size={22}
      strokeWidth={2.4}
      className={`streak-week-ico ${tone}`}
      aria-hidden
    />
  );
}

export default function StreakWeek({
  store,
  variant = "flash",
  className = "",
}: {
  store: ForgeStore;
  variant?: "flash" | "flame";
  className?: string;
}) {
  const days = buildStreakDays(store);
  const length = store.streak;
  const savers = Math.max(0, Math.min(2, store.freezeLeft));
  const hot = length > 0;
  const Icon = variant === "flame" ? Flame : Zap;
  const unit = length === 1 ? "day" : "days";

  return (
    <div
      className={`streak-week${hot ? " is-hot" : " is-cold"}${className ? ` ${className}` : ""}`}
      role="status"
      aria-label={`${length} ${unit} streak`}
    >
      <div className="streak-week-top">
        {days.map((day) => (
          <div key={day.key} className={`streak-week-day band-${day.band}`}>
            <span className="streak-week-label">{day.label}</span>
            <div className={`streak-week-bg status-${day.status}`}>
              <span className={`streak-week-ring status-${day.status}`}>
                {day.status === "done" ? (
                  <DayIcon variant={variant} tone="hot" />
                ) : day.status === "ghost" ? (
                  <DayIcon variant={variant} tone="mute" />
                ) : null}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="streak-week-bottom">
        <div className="streak-week-count">
          <Icon
            size={20}
            strokeWidth={2.4}
            className={`streak-week-ico ${hot ? "hot" : "mute"}`}
            aria-hidden
          />
          <span>
            {length} {unit}
          </span>
        </div>
        <div className="streak-week-savers" title="Streak savers">
          {[0, 1].map((i) => (
            <BatteryCharging
              key={i}
              size={20}
              strokeWidth={2.2}
              className={`streak-week-saver ${i < savers ? "on" : "off"}`}
              aria-hidden
            />
          ))}
        </div>
      </div>
    </div>
  );
}
