import { useEffect, useState } from "react";
import { CircleCheck, Flame, Gem, Zap } from "lucide-react";
import { NavLink } from "react-router-dom";
import { levelForXp, loadStore, overallStats } from "../forge/progress";
import { streakIsAlive } from "../forge/weekPlan";

export default function NavBar() {
  const [tick, setTick] = useState(0);
  useEffect(() => {
    const bump = () => setTick((n) => n + 1);
    window.addEventListener("forge-progress", bump);
    window.addEventListener("storage", bump);
    return () => {
      window.removeEventListener("forge-progress", bump);
      window.removeEventListener("storage", bump);
    };
  }, []);

  const store = loadStore();
  void tick;
  const overall = overallStats(store.progress);
  const level = levelForXp(store.xp);
  const alive = streakIsAlive(store);
  const StreakIcon = alive ? Zap : Flame;

  return (
    <nav className="top-nav" aria-label="Main">
      <NavLink to="/" className="top-nav-brand" end>
        Interviewer
      </NavLink>
      <div className="top-nav-links">
        <NavLink to="/" end>
          Home
        </NavLink>
        <NavLink to="/forge/list">Master list</NavLink>
        <NavLink to="/forge/calendar">Calendar</NavLink>
        <NavLink to="/forge/stats">Stats</NavLink>
        <NavLink to="/setup">Interview</NavLink>
        <NavLink to="/buddies/paper">Dr. Delta</NavLink>
        <NavLink to="/history">History</NavLink>
        <NavLink to="/settings">Settings</NavLink>
      </div>
      <div className="top-nav-metrics" aria-label="Forge stats">
        <span
          className={`top-nav-pill streak ${alive ? "on" : "off"}`}
          title={
            alive
              ? `${store.streak} day streak — on track`
              : store.streak > 0
                ? "Streak at risk — practice today"
                : "No active streak"
          }
        >
          <StreakIcon size={15} strokeWidth={2.4} aria-hidden />
          {store.streak}
        </span>
        <span
          className="top-nav-pill xp"
          title={`Level ${level.level} · ${store.xp} XP`}
        >
          <Gem size={15} strokeWidth={2.2} aria-hidden />
          {store.xp}
          <em>XP</em>
        </span>
        <span
          className="top-nav-done"
          title={`${overall.done} of ${overall.total} concepts done`}
        >
          <CircleCheck size={15} strokeWidth={2.3} aria-hidden />
          {overall.done}/{overall.total}
        </span>
      </div>
    </nav>
  );
}
