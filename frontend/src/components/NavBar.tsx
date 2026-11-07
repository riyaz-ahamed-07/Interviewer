import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { levelForXp, loadStore, overallStats } from "../forge/progress";

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
  const level = levelForXp(store.xp);
  const overall = overallStats(store.progress);

  return (
    <nav className="top-nav" aria-label="Main">
      <NavLink to="/" className="top-nav-brand" end>
        Interviewer
      </NavLink>
      <div className="top-nav-links">
        <NavLink to="/" end>
          Home
        </NavLink>
        <NavLink to="/setup">Interview</NavLink>
        <NavLink to="/buddies/paper">Dr. Delta</NavLink>
        <NavLink to="/history">History</NavLink>
      </div>
      <div className="top-nav-metrics" title="Forge progress">
        <span>{store.streak}d streak</span>
        <span>
          L{level.level} · {store.xp} XP
        </span>
        <span>
          {overall.done}/{overall.total}
        </span>
      </div>
    </nav>
  );
}
