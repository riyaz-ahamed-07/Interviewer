import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import SoftCard from "../components/ui/SoftCard";
import Mascot from "../components/ui/Mascot";
import PillButton from "../components/ui/PillButton";
import ProgressRing from "../components/ui/ProgressRing";
import { levelForXp, loadStore, overallStats } from "../forge/progress";
import {
  buildWeekDayCards,
  forgeWeekNumber,
  getMaxPlannedWeek,
  streakIsAlive,
  taskKey,
} from "../forge/weekPlan";
import "../App.css";

export default function ForgeStats() {
  const [store] = useState(() => loadStore());
  const level = levelForXp(store.xp);
  const overall = overallStats(store.progress);
  const alive = streakIsAlive(store);
  const week = Math.min(forgeWeekNumber(), getMaxPlannedWeek());
  const cards = useMemo(() => buildWeekDayCards(store, week), [store, week]);

  let practiceDone = 0;
  let practiceTotal = 0;
  let conceptDone = 0;
  let conceptTotal = 0;
  for (const card of cards) {
    for (const t of card.tasks) {
      if (t.optional) continue;
      const done = Boolean(store.weekChecks[taskKey(card.dateKey, t.id)]);
      if (t.lane === "practice") {
        practiceTotal += 1;
        if (done) practiceDone += 1;
      } else {
        conceptTotal += 1;
        if (done) conceptDone += 1;
      }
    }
  }

  return (
    <div className="habit-page">
      <div className="habit-hero">
        <div>
          <p className="eyebrow">Insights</p>
          <h1>Your Forge pulse</h1>
          <p>
            Week {week} lanes · streak {alive ? "alive" : "at risk"}
          </p>
        </div>
        <Mascot mood={alive ? "celebrate" : "nudge"} />
      </div>

      <div className="stat-rings">
        <SoftCard className="stat-tile ring">
          <ProgressRing
            value={practiceTotal ? (practiceDone / practiceTotal) * 100 : 0}
            label={`${practiceDone}/${practiceTotal}`}
          />
          <span>practice</span>
        </SoftCard>
        <SoftCard className="stat-tile ring">
          <ProgressRing
            value={conceptTotal ? (conceptDone / conceptTotal) * 100 : 0}
            label={`${conceptDone}/${conceptTotal}`}
          />
          <span>concepts</span>
        </SoftCard>
        <SoftCard className="stat-tile ring">
          <ProgressRing
            value={overall.total ? (overall.done / overall.total) * 100 : 0}
            label={`${overall.done}/${overall.total}`}
          />
          <span>mastery</span>
        </SoftCard>
      </div>

      <div className="stat-grid">
        <SoftCard className="stat-tile">
          <strong>{store.streak}</strong>
          <span>streak days</span>
        </SoftCard>
        <SoftCard className="stat-tile">
          <strong>{store.xp}</strong>
          <span>XP · L{level.level}</span>
        </SoftCard>
        <SoftCard className="stat-tile">
          <strong>{store.freezeLeft}</strong>
          <span>streak savers</span>
        </SoftCard>
      </div>

      <div className="onboard-actions">
        <Link to="/">
          <PillButton variant="soft">Home</PillButton>
        </Link>
        <Link to="/forge/calendar">
          <PillButton>Calendar</PillButton>
        </Link>
      </div>
    </div>
  );
}
