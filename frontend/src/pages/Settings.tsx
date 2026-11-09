import { useEffect, useState } from "react";
import SoftCard from "../components/ui/SoftCard";
import PillButton from "../components/ui/PillButton";
import Mascot from "../components/ui/Mascot";

const PREFS = "interviewer.prefs.v1";

type Prefs = {
  mascot: boolean;
  reduceMotion: boolean;
};

function loadPrefs(): Prefs {
  try {
    const raw = localStorage.getItem(PREFS);
    if (!raw) return { mascot: true, reduceMotion: false };
    return { mascot: true, reduceMotion: false, ...JSON.parse(raw) };
  } catch {
    return { mascot: true, reduceMotion: false };
  }
}

export default function Settings() {
  const [prefs, setPrefs] = useState<Prefs>(() => loadPrefs());

  useEffect(() => {
    localStorage.setItem(PREFS, JSON.stringify(prefs));
    document.documentElement.dataset.reduceMotion = prefs.reduceMotion
      ? "1"
      : "0";
    document.documentElement.dataset.mascot = prefs.mascot ? "1" : "0";
  }, [prefs]);

  return (
    <div className="habit-page">
      <div className="habit-hero">
        <div>
          <p className="eyebrow">Profile</p>
          <h1>Settings</h1>
          <p>Local prefs only — nothing leaves this browser.</p>
        </div>
        {prefs.mascot ? <Mascot mood="idle" /> : null}
      </div>

      <SoftCard style={{ padding: "1.1rem", display: "grid", gap: "0.85rem" }}>
        <label style={{ display: "flex", justifyContent: "space-between", gap: "1rem" }}>
          <span>
            <strong>Mascot</strong>
            <br />
            <span style={{ color: "var(--muted)", fontSize: "0.85rem" }}>
              Show the Forge buddy on habit screens
            </span>
          </span>
          <input
            type="checkbox"
            checked={prefs.mascot}
            onChange={(e) => setPrefs((p) => ({ ...p, mascot: e.target.checked }))}
          />
        </label>
        <label style={{ display: "flex", justifyContent: "space-between", gap: "1rem" }}>
          <span>
            <strong>Reduce motion</strong>
            <br />
            <span style={{ color: "var(--muted)", fontSize: "0.85rem" }}>
              Cut confetti / bounce animations
            </span>
          </span>
          <input
            type="checkbox"
            checked={prefs.reduceMotion}
            onChange={(e) =>
              setPrefs((p) => ({ ...p, reduceMotion: e.target.checked }))
            }
          />
        </label>
      </SoftCard>

      <SoftCard style={{ padding: "1.1rem", marginTop: "0.85rem" }}>
        <strong>Schedule reminder</strong>
        <p style={{ color: "var(--muted)", margin: "0.4rem 0 0" }}>
          Weekdays 7–8pm + 10pm–12am (~3h). Gatherly 8–10pm protected. Sat light ~
          2h. Sun deep ~5h.
        </p>
      </SoftCard>

      <div className="onboard-actions">
        <PillButton
          variant="ghost"
          onClick={() => {
            localStorage.removeItem("interviewer.onboarded.v1");
            window.location.href = "/onboarding";
          }}
        >
          Replay onboarding
        </PillButton>
      </div>
    </div>
  );
}
