import { Link, useParams } from "react-router-dom";
import "../App.css";

export default function Report() {
  const { sessionId } = useParams();
  return (
    <div className="shell lobby">
      <header>
        <p className="eyebrow">
          <Link to="/">Home</Link>
        </p>
        <h1>Report</h1>
        <p className="lede">
          Full round reports land in Phase 4. For now open the session and check
          the scorecard after feedback.
        </p>
        {sessionId ? (
          <Link className="cta" to={`/interview/${sessionId}`}>
            Open session
          </Link>
        ) : null}
      </header>
    </div>
  );
}
