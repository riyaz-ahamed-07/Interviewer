import { Flame, Gem, Zap } from "lucide-react";
import type { ForgeStore } from "../forge/types";
import { streakIsAlive } from "../forge/weekPlan";

export default function ForgeMiniStats({ store }: { store: ForgeStore }) {
  const alive = streakIsAlive(store);
  const StreakIcon = alive ? Zap : Flame;

  return (
    <div className="forge-mini-stats" aria-label="Forge stats">
      <div
        className={`forge-mini-pill streak ${alive ? "on" : "off"}`}
        title={
          alive
            ? `${store.streak} day streak — on track`
            : store.streak > 0
              ? "Streak at risk — practice today"
              : "No active streak"
        }
      >
        <StreakIcon
          size={18}
          strokeWidth={2.4}
          className="forge-mini-ico"
          aria-hidden
        />
        <span className="forge-mini-num">{store.streak}</span>
      </div>
      <div
        className="forge-mini-pill xp"
        title={`Level progress · ${store.xp} XP`}
      >
        <Gem
          size={18}
          strokeWidth={2.2}
          className="forge-mini-ico"
          aria-hidden
        />
        <span className="forge-mini-num">{store.xp}</span>
        <span className="forge-mini-unit">XP</span>
      </div>
    </div>
  );
}
