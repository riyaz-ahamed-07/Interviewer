import { useEffect, useRef } from "react";
import type { AvatarProvider } from "./AvatarProvider";
import { resolveAvatarProvider } from "./AvatarProvider";
import { SvgFace, useSvgAvatar } from "./SvgFace";

type Props = {
  liveSpeaking: boolean;
  playContext: AudioContext | null;
  outputGain: GainNode | null;
  displayName?: string;
  enabled?: boolean;
};

export function AvatarStage({
  liveSpeaking,
  playContext,
  outputGain,
  displayName = "Interviewer",
  enabled = true,
}: Props) {
  const svg = useSvgAvatar();
  const providerRef = useRef<AvatarProvider | null>(null);
  const mode = resolveAvatarProvider();

  useEffect(() => {
    if (!enabled) {
      providerRef.current?.dispose();
      providerRef.current = null;
      return;
    }
    providerRef.current = svg.provider;
    return () => {
      providerRef.current?.dispose();
      providerRef.current = null;
    };
  }, [enabled, svg.provider]);

  useEffect(() => {
    if (!enabled || !playContext || !outputGain || !providerRef.current) return;
    void providerRef.current.attach({
      audioContext: playContext,
      outputGain,
    });
  }, [enabled, playContext, outputGain]);

  useEffect(() => {
    providerRef.current?.speakingChanged(liveSpeaking);
  }, [liveSpeaking]);

  useEffect(() => {
    if (!liveSpeaking) providerRef.current?.interrupt();
  }, [liveSpeaking]);

  if (!enabled) {
    return (
      <div className="call-tile avatar-tile muted">
        <div className="call-tile-head">
          <span>{displayName}</span>
          <span className="pill">avatar off</span>
        </div>
        <div className="tile-placeholder">Avatar disabled</div>
      </div>
    );
  }

  if (mode === "simli") {
    return (
      <div className="call-tile avatar-tile muted">
        <div className="call-tile-head">
          <span>{displayName}</span>
          <span className="pill">simli off</span>
        </div>
        <div className="tile-placeholder">
          Simli needs SIMLI_API_KEY. Using SVG face instead below.
        </div>
        <SvgFace
          speaking={liveSpeaking || svg.speaking}
          mouthOpen={svg.mouthOpen}
          name={displayName}
        />
      </div>
    );
  }

  if (mode === "talkinghead") {
    return (
      <div className="call-tile avatar-tile">
        <div className="call-tile-head">
          <span>{displayName}</span>
          <span className="pill">svg fallback</span>
        </div>
        <p className="tile-note">
          TalkingHead GLB pack not bundled yet. SVG lip-sync is active.
        </p>
        <SvgFace
          speaking={liveSpeaking || svg.speaking}
          mouthOpen={svg.mouthOpen}
          name={displayName}
        />
      </div>
    );
  }

  return (
    <SvgFace
      speaking={liveSpeaking || svg.speaking}
      mouthOpen={svg.mouthOpen}
      name={displayName}
    />
  );
}
