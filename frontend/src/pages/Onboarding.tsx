import { useState } from "react";
import { useNavigate } from "react-router-dom";
import SoftCard from "../components/ui/SoftCard";
import PillButton from "../components/ui/PillButton";
import Mascot from "../components/ui/Mascot";

const SLIDES = [
  {
    title: "Your real schedule",
    body: "Weekdays ~3h (7–8pm + 10pm–12am). Gatherly 8–10pm stays sacred. Saturday light, Sunday deep.",
  },
  {
    title: "Two lanes",
    body: "Practice (LeetCode, SQL, TrenTorch, SysDesign…) and Concepts (OS/DBMS/CN/DSA/AIML) are separate checklist items every day.",
  },
  {
    title: "TrenTorch + videos",
    body: "ML practice lives on TrenTorch modules. Video timestamps are planned at ~2.5× so rewind and notes fit.",
  },
];

const KEY = "interviewer.onboarded.v1";

export function markOnboarded() {
  localStorage.setItem(KEY, "1");
}

export function needsOnboarding() {
  return localStorage.getItem(KEY) !== "1";
}

export default function Onboarding() {
  const [i, setI] = useState(0);
  const navigate = useNavigate();
  const slide = SLIDES[i];

  const finish = () => {
    markOnboarded();
    navigate("/", { replace: true });
  };

  return (
    <div className="habit-page">
      <SoftCard className="onboard-card">
        <Mascot mood={i === 2 ? "celebrate" : "idle"} size={88} />
        <h2>{slide.title}</h2>
        <p>{slide.body}</p>
        <div className="onboard-actions">
          {i > 0 ? (
            <PillButton variant="ghost" onClick={() => setI((n) => n - 1)}>
              Back
            </PillButton>
          ) : null}
          {i < SLIDES.length - 1 ? (
            <PillButton onClick={() => setI((n) => n + 1)}>Next</PillButton>
          ) : (
            <PillButton onClick={finish}>Start Forge</PillButton>
          )}
        </div>
      </SoftCard>
    </div>
  );
}
