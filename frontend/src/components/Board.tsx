import { useCallback, useEffect, useRef, useState } from "react";
import { Excalidraw, exportToBlob } from "@excalidraw/excalidraw";
import "@excalidraw/excalidraw/index.css";

type ExcalidrawAPI = {
  getSceneElements: () => readonly Record<string, unknown>[];
  getAppState: () => Record<string, unknown>;
  getFiles: () => Record<string, unknown>;
};

export type CanvasScene = {
  labels: string[];
  /** Compact Excalidraw element inventory (JSON scene — not an image). */
  elements: Array<Record<string, unknown>>;
};

type Props = {
  /** Explicit submit still sends a PNG for vision critique (same as before). */
  onSubmit: (blob: Blob, labels: string[]) => Promise<void>;
  /** Silent continuous watch — scene JSON only; interviewer must not speak. */
  onWatch?: (scene: CanvasScene) => void;
  watchEnabled?: boolean;
};

const WATCH_MS = 2500;

function labelsFrom(elements: readonly Record<string, unknown>[]): string[] {
  return elements
    .map((el) => {
      const anyEl = el as { text?: string; label?: { text?: string } };
      return (anyEl.text || anyEl.label?.text || "").trim();
    })
    .filter(Boolean);
}

function compactScene(
  elements: readonly Record<string, unknown>[],
): CanvasScene {
  const live = elements.filter((el) => !el.isDeleted);
  const compact = live.slice(0, 120).map((el) => {
    const e = el as {
      type?: string;
      text?: string;
      label?: { text?: string };
      x?: number;
      y?: number;
      width?: number;
      height?: number;
      points?: unknown;
    };
    const row: Record<string, unknown> = {
      type: e.type,
      x: Math.round(Number(e.x) || 0),
      y: Math.round(Number(e.y) || 0),
      w: Math.round(Number(e.width) || 0),
      h: Math.round(Number(e.height) || 0),
    };
    const text = (e.text || e.label?.text || "").trim();
    if (text) row.text = text.slice(0, 80);
    if (e.type === "arrow" && Array.isArray(e.points)) {
      row.points = e.points.length;
    }
    return row;
  });
  return { labels: labelsFrom(live), elements: compact };
}

export function Board({ onSubmit, onWatch, watchEnabled = false }: Props) {
  const [api, setApi] = useState<ExcalidrawAPI | null>(null);
  const [busy, setBusy] = useState(false);
  const dirtyRef = useRef(false);
  const lastJsonRef = useRef("");
  const onWatchRef = useRef(onWatch);
  onWatchRef.current = onWatch;

  const submit = useCallback(async () => {
    if (!api) return;
    setBusy(true);
    try {
      const elements = api.getSceneElements();
      const labels = labelsFrom(elements);
      const blob = await exportToBlob({
        elements: elements as never,
        appState: {
          ...api.getAppState(),
          exportBackground: true,
        } as never,
        files: api.getFiles() as never,
        mimeType: "image/png",
      });
      await onSubmit(blob, labels);
    } finally {
      setBusy(false);
    }
  }, [api, onSubmit]);

  useEffect(() => {
    if (!watchEnabled || !api || !onWatch) return;
    dirtyRef.current = true;
    const tick = window.setInterval(() => {
      if (!dirtyRef.current) return;
      dirtyRef.current = false;
      const scene = compactScene(api.getSceneElements());
      if (!scene.elements.length) return;
      const json = JSON.stringify(scene);
      if (json === lastJsonRef.current) return;
      lastJsonRef.current = json;
      onWatchRef.current?.(scene);
    }, WATCH_MS);
    return () => clearInterval(tick);
  }, [api, onWatch, watchEnabled]);

  return (
    <div className="board">
      <div className="board-canvas">
        <Excalidraw
          excalidrawAPI={(a) => setApi(a as unknown as ExcalidrawAPI)}
          theme="light"
          onChange={() => {
            dirtyRef.current = true;
          }}
        />
      </div>
      <div className="board-toolbar">
        <button
          type="button"
          onClick={() => void submit()}
          disabled={busy || !api}
        >
          {busy ? "Sending…" : "I’ve drawn — ask me"}
        </button>
        {watchEnabled && (
          <span className="muted board-watch-hint">
            Watching scene JSON silently
          </span>
        )}
      </div>
    </div>
  );
}
