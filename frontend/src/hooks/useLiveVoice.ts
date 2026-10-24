import { useCallback, useEffect, useRef, useState } from "react";
import { wsLiveUrl } from "../api";

export type LiveStatus =
  | "idle"
  | "connecting"
  | "live"
  | "speaking"
  | "listening"
  | "paused"
  | "fallback"
  | "error";

type TurnHandler = (role: "user" | "assistant", text: string) => void;

/**
 * Real-time Gemini Live. Pause stops mic uplink + closes Live WS (saves tokens).
 * Resume reconnects with same session id (resume=1 so AI does not re-open).
 */
export function useLiveVoice(onTurnComplete?: TurnHandler) {
  const [status, setStatus] = useState<LiveStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [userPartial, setUserPartial] = useState("");
  const [assistantPartial, setAssistantPartial] = useState("");
  const [paused, setPaused] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const captureCtxRef = useRef<AudioContext | null>(null);
  const playCtxRef = useRef<AudioContext | null>(null);
  const playTimeRef = useRef(0);
  const sourcesRef = useRef<AudioBufferSourceNode[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const sessionIdRef = useRef<string | null>(null);
  const micEnabledRef = useRef(true);
  const allowPlaybackRef = useRef(true);
  const userAccRef = useRef("");
  const asstAccRef = useRef("");
  const clearPartialsTimer = useRef<number | null>(null);
  const onTurnRef = useRef(onTurnComplete);
  onTurnRef.current = onTurnComplete;

  const stopPlayback = useCallback(() => {
    for (const s of sourcesRef.current) {
      try {
        s.stop();
      } catch {
        /* already stopped */
      }
    }
    sourcesRef.current = [];
    playTimeRef.current = playCtxRef.current?.currentTime ?? 0;
  }, []);

  const ensurePlayCtx = useCallback(async () => {
    if (!playCtxRef.current || playCtxRef.current.state === "closed") {
      playCtxRef.current = new AudioContext({ sampleRate: 24000 });
    }
    const ctx = playCtxRef.current;
    if (ctx.state === "suspended") {
      try {
        await ctx.resume();
      } catch {
        /* browser may block until next gesture */
      }
    }
    return ctx;
  }, []);

  const playPcm24k = useCallback(
    async (pcm: ArrayBuffer) => {
      if (!allowPlaybackRef.current) return;
      const ctx = await ensurePlayCtx();
      if (!allowPlaybackRef.current) return;

      setStatus("speaking");
      const int16 = new Int16Array(pcm);
      const float32 = new Float32Array(int16.length);
      for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 32768;
      const buffer = ctx.createBuffer(1, float32.length, 24000);
      buffer.copyToChannel(float32, 0);
      const src = ctx.createBufferSource();
      src.buffer = buffer;
      src.connect(ctx.destination);
      const now = ctx.currentTime;
      const startAt = Math.max(now, playTimeRef.current);
      src.start(startAt);
      playTimeRef.current = startAt + buffer.duration;
      sourcesRef.current.push(src);
      src.onended = () => {
        sourcesRef.current = sourcesRef.current.filter((x) => x !== src);
        if (sourcesRef.current.length === 0 && allowPlaybackRef.current) {
          setStatus("listening");
        }
      };
    },
    [ensurePlayCtx],
  );

  const teardownMedia = useCallback(() => {
    stopPlayback();
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    void captureCtxRef.current?.close();
    void playCtxRef.current?.close();
    captureCtxRef.current = null;
    playCtxRef.current = null;
    playTimeRef.current = 0;
  }, [stopPlayback]);

  const disconnect = useCallback(() => {
    try {
      wsRef.current?.send(JSON.stringify({ type: "end" }));
    } catch {
      /* ignore */
    }
    wsRef.current?.close();
    wsRef.current = null;
    teardownMedia();
    micEnabledRef.current = true;
    allowPlaybackRef.current = true;
    setPaused(false);
    setStatus("idle");
    setUserPartial("");
    setAssistantPartial("");
    if (clearPartialsTimer.current) {
      window.clearTimeout(clearPartialsTimer.current);
      clearPartialsTimer.current = null;
    }
  }, [teardownMedia]);

  const connect = useCallback(
    async (sessionId: string, opts?: { resume?: boolean }) => {
      if (!sessionId) {
        setError("missing session id");
        setStatus("error");
        return;
      }
      sessionIdRef.current = sessionId;
      micEnabledRef.current = true;
      allowPlaybackRef.current = true;
      setPaused(false);

      try {
        wsRef.current?.send(JSON.stringify({ type: "end" }));
      } catch {
        /* ignore */
      }
      wsRef.current?.close();
      wsRef.current = null;
      teardownMedia();

      setError(null);
      setStatus("connecting");
      setUserPartial("");
      setAssistantPartial("");
      userAccRef.current = "";
      asstAccRef.current = "";
      if (clearPartialsTimer.current) {
        window.clearTimeout(clearPartialsTimer.current);
        clearPartialsTimer.current = null;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      streamRef.current = stream;

      const captureCtx = new AudioContext({ sampleRate: 16000 });
      captureCtxRef.current = captureCtx;
      if (captureCtx.state === "suspended") await captureCtx.resume();

      // Unlock playback AudioContext while we still have the user gesture
      // (resume / Start click). Otherwise post-pause AI audio is silent.
      await ensurePlayCtx();
      playTimeRef.current = playCtxRef.current?.currentTime ?? 0;

      const source = captureCtx.createMediaStreamSource(stream);
      const processor = captureCtx.createScriptProcessor(4096, 1, 1);
      const mute = captureCtx.createGain();
      mute.gain.value = 0;
      source.connect(processor);
      processor.connect(mute);
      mute.connect(captureCtx.destination);

      const ws = new WebSocket(
        wsLiveUrl(sessionId, { resume: Boolean(opts?.resume) }),
      );
      ws.binaryType = "arraybuffer";
      wsRef.current = ws;

      await new Promise<void>((resolve, reject) => {
        const timer = window.setTimeout(
          () => reject(new Error("Live WebSocket timeout")),
          20000,
        );
        ws.onopen = () => {
          window.clearTimeout(timer);
          resolve();
        };
        ws.onerror = () => {
          window.clearTimeout(timer);
          reject(new Error("Live WebSocket failed to open"));
        };
      });

      const appendChunk = (acc: { current: string }, chunk: string) => {
        const t = chunk;
        if (!t) return acc.current;
        // Prefer cumulative snapshot if model sends growing full text
        if (!acc.current || t.startsWith(acc.current)) {
          acc.current = t;
        } else if (acc.current.startsWith(t)) {
          /* older shorter snapshot — ignore */
        } else {
          acc.current += t;
        }
        return acc.current;
      };

      ws.onmessage = (ev) => {
        if (ev.data instanceof ArrayBuffer) {
          void playPcm24k(ev.data);
          return;
        }
        try {
          const msg = JSON.parse(ev.data as string);
          if (msg.type === "interrupted") {
            stopPlayback();
            if (allowPlaybackRef.current) setStatus("listening");
          }
          if (msg.type === "user_transcript_interim" && msg.text) {
            // Live while speaking — replace with latest interim snapshot
            userAccRef.current = String(msg.text);
            setUserPartial(userAccRef.current);
          }
          if (msg.type === "user_transcript" && msg.text) {
            setUserPartial(appendChunk(userAccRef, String(msg.text)));
          }
          if (msg.type === "assistant_transcript" && msg.text) {
            setAssistantPartial(appendChunk(asstAccRef, String(msg.text)));
          }
          if (msg.type === "turn_complete") {
            if (userAccRef.current.trim()) {
              onTurnRef.current?.("user", userAccRef.current.trim());
            }
            if (asstAccRef.current.trim()) {
              onTurnRef.current?.("assistant", asstAccRef.current.trim());
            }
            // Keep live strip visible briefly so it does not flash empty
            if (clearPartialsTimer.current) {
              window.clearTimeout(clearPartialsTimer.current);
            }
            clearPartialsTimer.current = window.setTimeout(() => {
              userAccRef.current = "";
              asstAccRef.current = "";
              setUserPartial("");
              setAssistantPartial("");
              clearPartialsTimer.current = null;
            }, 600);
            if (allowPlaybackRef.current) setStatus("listening");
          }
          if (msg.type === "live_connected" || msg.type === "ready") {
            if (allowPlaybackRef.current) setStatus("listening");
          }
          if (msg.type === "error") {
            setError(msg.error ?? "live error");
            setStatus(msg.fallback ? "fallback" : "error");
          }
        } catch {
          /* ignore */
        }
      };

      ws.onclose = () => {
        try {
          processor.disconnect();
          source.disconnect();
          mute.disconnect();
        } catch {
          /* ignore */
        }
      };

      processor.onaudioprocess = (e) => {
        if (!micEnabledRef.current) return;
        if (ws.readyState !== WebSocket.OPEN) return;
        const input = e.inputBuffer.getChannelData(0);
        const pcm = floatTo16BitPCM(input);
        const copy = new Int16Array(pcm.length);
        copy.set(pcm);
        ws.send(copy.buffer);
      };

      setStatus("listening");
    },
    [ensurePlayCtx, playPcm24k, stopPlayback, teardownMedia],
  );

  const pause = useCallback(() => {
    micEnabledRef.current = false;
    allowPlaybackRef.current = false;
    setPaused(true);
    stopPlayback();
    try {
      wsRef.current?.send(JSON.stringify({ type: "end" }));
    } catch {
      /* ignore */
    }
    wsRef.current?.close();
    wsRef.current = null;
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    void captureCtxRef.current?.close();
    captureCtxRef.current = null;
    // Close playback ctx too — a fresh one is unlocked on resume click
    void playCtxRef.current?.close();
    playCtxRef.current = null;
    playTimeRef.current = 0;
    setStatus("paused");
    setUserPartial("");
    setAssistantPartial("");
  }, [stopPlayback]);

  const resume = useCallback(async () => {
    const id = sessionIdRef.current;
    if (!id) return;
    setPaused(false);
    allowPlaybackRef.current = true;
    await connect(id, { resume: true });
    // Nudge after reconnect — AudioContext already resumed in connect()
    window.setTimeout(() => {
      void ensurePlayCtx();
      wsRef.current?.send(
        JSON.stringify({
          type: "text",
          text: "Candidate resumed the live call. Continue briefly from where you left off. Do not restart the whole intro or re-ask old openings.",
        }),
      );
    }, 600);
  }, [connect, ensurePlayCtx]);

  const sendText = useCallback((text: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "text", text }));
    }
  }, []);

  const sendPhaseSync = useCallback((briefing?: string) => {
    if (wsRef.current?.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(
      JSON.stringify({
        type: "phase_sync",
        briefing: briefing || undefined,
      }),
    );
  }, []);

  const sendImagePng = useCallback(
    (bytes: ArrayBuffer, opts?: { silent?: boolean; mime?: string }) => {
      if (wsRef.current?.readyState !== WebSocket.OPEN) return;
      wsRef.current.send(
        JSON.stringify({
          type: "image_png_b64",
          data: arrayBufferToBase64(bytes),
          silent: opts?.silent ?? false,
          mime: opts?.mime ?? "image/png",
        }),
      );
    },
    [],
  );

  useEffect(() => () => disconnect(), [disconnect]);

  return {
    status,
    error,
    userPartial,
    assistantPartial,
    paused,
    connect,
    disconnect,
    pause,
    resume,
    sendText,
    sendPhaseSync,
    sendImagePng,
    stopPlayback,
  };
}

function floatTo16BitPCM(input: Float32Array): Int16Array {
  const out = new Int16Array(input.length);
  for (let i = 0; i < input.length; i++) {
    const s = Math.max(-1, Math.min(1, input[i]));
    out[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  return out;
}

function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
  }
  return btoa(binary);
}
