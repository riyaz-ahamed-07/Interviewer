import { useEffect, useRef, useState } from "react";
import type { AvatarProvider } from "./AvatarProvider";

type Props = {
  speaking: boolean;
  mouthOpen: number;
  name?: string;
};

export function SvgFace({ speaking, mouthOpen, name = "Interviewer" }: Props) {
  const open = Math.max(0, Math.min(1, mouthOpen));
  const mouthH = 4 + open * 22;
  const mouthY = 78 - open * 4;
  return (
    <div className={`call-tile avatar-tile ${speaking ? "speaking" : ""}`}>
      <div className="call-tile-head">
        <span>{name}</span>
        <span className="pill">{speaking ? "speaking" : "listening"}</span>
      </div>
      <svg viewBox="0 0 120 140" className="svg-face" aria-hidden="true">
        <ellipse
          cx="60"
          cy="70"
          rx="46"
          ry="52"
          fill="#f3e7d3"
          stroke="#2a241c"
          strokeWidth="2"
        />
        <circle cx="42" cy="58" r="4.5" fill="#2a241c" />
        <circle cx="78" cy="58" r="4.5" fill="#2a241c" />
        <path
          d={`M 40 ${mouthY} Q 60 ${mouthY + mouthH} 80 ${mouthY}`}
          fill="none"
          stroke="#2a241c"
          strokeWidth="3"
          strokeLinecap="round"
        />
        {open > 0.15 ? (
          <ellipse
            cx="60"
            cy={mouthY + mouthH * 0.35}
            rx={8 + open * 10}
            ry={mouthH * 0.35}
            fill="#5a1f1f"
          />
        ) : null}
      </svg>
    </div>
  );
}

export function createSvgAvatarController(
  setMouth: (n: number) => void,
  setSpeaking: (b: boolean) => void,
): AvatarProvider {
  let analyser: AnalyserNode | null = null;
  let raf = 0;
  let smoothed = 0;

  const tick = () => {
    if (!analyser) return;
    const data = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteTimeDomainData(data);
    let sum = 0;
    for (let i = 0; i < data.length; i++) {
      const v = (data[i] - 128) / 128;
      sum += v * v;
    }
    const rms = Math.sqrt(sum / data.length);
    smoothed = smoothed * 0.7 + Math.min(1, rms * 6) * 0.3;
    setMouth(smoothed);
    raf = requestAnimationFrame(tick);
  };

  return {
    name: "svg",
    attach({ outputGain }) {
      analyser = outputGain.context.createAnalyser();
      analyser.fftSize = 256;
      outputGain.connect(analyser);
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(tick);
    },
    speakingChanged(speaking) {
      setSpeaking(speaking);
      if (!speaking) {
        smoothed = 0;
        setMouth(0);
      }
    },
    interrupt() {
      setSpeaking(false);
      smoothed = 0;
      setMouth(0);
    },
    dispose() {
      cancelAnimationFrame(raf);
      try {
        analyser?.disconnect();
      } catch {
        /* ignore */
      }
      analyser = null;
    },
  };
}

export function useSvgAvatar() {
  const [mouthOpen, setMouthOpen] = useState(0);
  const [speaking, setSpeaking] = useState(false);
  const providerRef = useRef<AvatarProvider | null>(null);
  if (!providerRef.current) {
    providerRef.current = createSvgAvatarController(setMouthOpen, setSpeaking);
  }
  useEffect(() => () => providerRef.current?.dispose(), []);
  return {
    provider: providerRef.current,
    mouthOpen,
    speaking,
  };
}
