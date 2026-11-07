import { useEffect, useRef, useState } from "react";

type Props = {
  enabled: boolean;
  onEnabledChange?: (on: boolean) => void;
};

export function SelfView({ enabled, onEnabledChange }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [error, setError] = useState("");
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [deviceId, setDeviceId] = useState("");

  useEffect(() => {
    void navigator.mediaDevices
      ?.enumerateDevices()
      .then((list) => {
        const cams = list.filter((d) => d.kind === "videoinput");
        setDevices(cams);
        if (!deviceId && cams[0]?.deviceId) setDeviceId(cams[0].deviceId);
      })
      .catch(() => undefined);
  }, [deviceId]);

  useEffect(() => {
    let cancelled = false;
    const stop = () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
      if (videoRef.current) videoRef.current.srcObject = null;
    };

    if (!enabled) {
      stop();
      setError("");
      return stop;
    }

    void (async () => {
      try {
        stop();
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: deviceId
            ? { deviceId: { exact: deviceId }, facingMode: "user" }
            : { facingMode: "user" },
        });
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play().catch(() => undefined);
        }
        setError("");
      } catch (e) {
        setError(e instanceof Error ? e.message : "Camera blocked");
        onEnabledChange?.(false);
      }
    })();

    return () => {
      cancelled = true;
      stop();
    };
  }, [enabled, deviceId, onEnabledChange]);

  return (
    <div className="call-tile self-view">
      <div className="call-tile-head">
        <span>You</span>
        <label className="tile-toggle">
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => onEnabledChange?.(e.target.checked)}
          />
          Camera
        </label>
      </div>
      {enabled ? (
        <video ref={videoRef} muted playsInline autoPlay className="mirror" />
      ) : (
        <div className="tile-placeholder">Camera off</div>
      )}
      {enabled && devices.length > 1 ? (
        <select
          className="device-pick"
          value={deviceId}
          onChange={(e) => setDeviceId(e.target.value)}
        >
          {devices.map((d) => (
            <option key={d.deviceId} value={d.deviceId}>
              {d.label || "Camera"}
            </option>
          ))}
        </select>
      ) : null}
      <p className="tile-note">Only you can see this. Nothing is recorded.</p>
      {error ? <p className="tile-error">{error}</p> : null}
    </div>
  );
}
