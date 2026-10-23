import { useState } from "react";
import type { Scorecard } from "../api";

type Props = {
  card: Scorecard;
};

export function ScorecardPanel({ card }: Props) {
  const [copied, setCopied] = useState(false);
  const eng = card.english ?? {};

  const copyAll = async () => {
    const text =
      card.copy_text?.trim() ||
      `Score: ${card.score}/100\n\n${card.summary}\n`;
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
        <button type="button" className="copy-btn" onClick={() => void copyAll()}>
          {copied ? "Copied ✓" : "Copy all feedback"}
        </button>
      </div>

      <p className="score-summary">{card.summary}</p>

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
