import { useState } from "react";
import type { PhaseScore, Scorecard } from "../api";

type Props = {
  card: Scorecard;
};

const PHASE_LABELS: Record<string, string> = {
  intro: "Intro",
  debug: "Debug",
  design: "Design",
  llm: "LLM techniques",
};

function asPhaseScore(raw: PhaseScore | string | undefined): PhaseScore | null {
  if (!raw) return null;
  if (typeof raw === "string") {
    return { score: 0, strengths: [], weaknesses: [], note: raw };
  }
  return {
    score: Number(raw.score) || 0,
    strengths: raw.strengths || [],
    weaknesses: raw.weaknesses || [],
    note: raw.note,
  };
}

export function ScorecardPanel({ card }: Props) {
  const [copied, setCopied] = useState(false);
  const eng = card.english ?? {};
  const byPhase = card.by_phase ?? {};
  const phaseKeys = ["intro", "debug", "design", "llm"].filter(
    (k) => byPhase[k],
  );

  const copyAll = async () => {
    const text =
      card.copy_text?.trim() || `Score: ${card.score}/100\n\n${card.summary}\n`;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="scorecard">
      <div className="scorecard-top">
        <div>
          <p className="llm-kicker">Your scorecard</p>
          <h2 className="score-num">
            {card.score}
            <span>/100</span>
          </h2>
        </div>
        <button
          type="button"
          className="copy-btn"
          onClick={() => void copyAll()}
        >
          {copied ? "Copied ✓" : "Copy all feedback"}
        </button>
      </div>

      <p className="score-summary">{card.summary}</p>

      {phaseKeys.length > 0 ? (
        <section className="score-sec score-phases">
          <h3>By phase</h3>
          {phaseKeys.map((key) => {
            const p = asPhaseScore(byPhase[key]);
            if (!p) return null;
            return (
              <div key={key} className="phase-score-block">
                <div className="phase-score-head">
                  <strong>{PHASE_LABELS[key] ?? key}</strong>
                  <span className="phase-score-num">{p.score}/100</span>
                </div>
                {p.note ? <p className="phase-score-note">{p.note}</p> : null}
                {p.strengths.length > 0 ? (
                  <>
                    <p className="phase-sub">Strengths</p>
                    <ul>
                      {p.strengths.map((x) => (
                        <li key={`${key}-s-${x}`}>{x}</li>
                      ))}
                    </ul>
                  </>
                ) : null}
                {p.weaknesses.length > 0 ? (
                  <>
                    <p className="phase-sub">Weaknesses</p>
                    <ul>
                      {p.weaknesses.map((x) => (
                        <li key={`${key}-w-${x}`}>{x}</li>
                      ))}
                    </ul>
                  </>
                ) : null}
              </div>
            );
          })}
        </section>
      ) : null}

      <section className="score-sec">
        <h3>Strengths</h3>
        <ul>
          {(card.strengths || []).map((x) => (
            <li key={x}>{x}</li>
          ))}
        </ul>
      </section>

      <section className="score-sec">
        <h3>What to improve</h3>
        <ul>
          {(card.improve || []).map((x) => (
            <li key={x}>{x}</li>
          ))}
        </ul>
      </section>

      <section className="score-sec">
        <h3>Focus next</h3>
        <ul>
          {(card.focus_next || []).map((x) => (
            <li key={x}>{x}</li>
          ))}
        </ul>
      </section>

      <section className="score-sec score-english">
        <h3>English</h3>
        {eng.manner ? <p className="score-manner">{eng.manner}</p> : null}
        {(eng.fillers_to_avoid || []).length > 0 ? (
          <p>
            <strong>Avoid fillers:</strong>{" "}
            {(eng.fillers_to_avoid || []).join(", ")}
          </p>
        ) : null}
        {(eng.answer_openers || []).length > 0 ? (
          <>
            <p>
              <strong>Start answers like:</strong>
            </p>
            <ul>
              {(eng.answer_openers || []).map((x) => (
                <li key={x}>{x}</li>
              ))}
            </ul>
          </>
        ) : null}
        {(eng.notes || []).length > 0 ? (
          <ul>
            {(eng.notes || []).map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
        ) : null}
      </section>
    </div>
  );
}
