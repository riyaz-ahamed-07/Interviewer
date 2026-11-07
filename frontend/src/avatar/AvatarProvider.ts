export type AvatarProviderName = "svg" | "talkinghead" | "simli";

export type AvatarAttachOpts = {
  audioContext: AudioContext;
  outputGain: GainNode;
};

export interface AvatarProvider {
  name: AvatarProviderName;
  attach(opts: AvatarAttachOpts): Promise<void> | void;
  speakingChanged(speaking: boolean): void;
  interrupt(): void;
  dispose(): void;
}

export function resolveAvatarProvider(): AvatarProviderName {
  const raw = String(import.meta.env.VITE_AVATAR_PROVIDER || "svg").toLowerCase();
  if (raw === "talkinghead" || raw === "simli" || raw === "svg") return raw;
  return "svg";
}
