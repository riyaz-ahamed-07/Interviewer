import { useEffect, useId, useState } from "react";
import mermaid from "mermaid";

mermaid.initialize({
  startOnLoad: false,
  securityLevel: "loose",
  theme: "neutral",
});

export default function MermaidBlock({ chart }: { chart: string }) {
  const rid = useId().replace(/:/g, "");
  const [svg, setSvg] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      if (!chart.trim()) {
        setSvg("");
        return;
      }
      try {
        const { svg: out } = await mermaid.render(`mmd-${rid}`, chart);
        if (!cancelled) {
          setSvg(out);
          setErr("");
        }
      } catch (e) {
        if (!cancelled) {
          setSvg("");
          setErr(String(e));
        }
      }
    };
    void run();
    return () => {
      cancelled = true;
    };
  }, [chart, rid]);

  if (err) return <pre className="mermaid-err">{err}</pre>;
  if (!svg) return <p className="lede">Rendering diagram…</p>;
  return (
    <div
      className="mermaid-out"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
