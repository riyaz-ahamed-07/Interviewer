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
  elements: Array<Record<string, unknown>>;
};

type Props = {
  onSubmit: (blob: Blob, labels: string[]) => Promise<void>;
  onWatch?: (scene: CanvasScene) => void;
  onFrame?: (blob: Blob, labels: string[]) => void;
  watchEnabled?: boolean;
  frameEnabled?: boolean;
};

const WATCH_MS = 2500;
const FRAME_MS = 10000;

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
  const idLabel = new Map<string, string>();
  for (const el of live) {
    const e = el as {
      id?: string;
      text?: string;
      label?: { text?: string };
    };
    const text = (e.text || e.label?.text || "").trim();
    if (e.id && text) idLabel.set(String(e.id), text.slice(0, 80));
  }

  const compact = live.slice(0, 160).map((el) => {
    const e = el as {
      id?: string;
      type?: string;
      text?: string;
      label?: { text?: string };
      x?: number;
      y?: number;
      width?: number;
      height?: number;
      points?: unknown;
      startBinding?: { elementId?: string } | null;
      endBinding?: { elementId?: string } | null;
    };
    const row: Record<string, unknown> = {
      id: e.id,
      type: e.type,
      x: Math.round(Number(e.x) || 0),
      y: Math.round(Number(e.y) || 0),
      w: Math.round(Number(e.width) || 0),
      h: Math.round(Number(e.height) || 0),
    };
    const text = (e.text || e.label?.text || "").trim();
    if (text) row.text = text.slice(0, 80);
    if (e.type === "arrow") {
      if (Array.isArray(e.points)) row.points = e.points.length;
      if (e.startBinding?.elementId) {
        row.startBinding = { elementId: e.startBinding.elementId };
        row.startLabel = idLabel.get(e.startBinding.elementId) || "";
      }
      if (e.endBinding?.elementId) {
        row.endBinding = { elementId: e.endBinding.elementId };
        row.endLabel = idLabel.get(e.endBinding.elementId) || "";
      }
    }
    return row;
  });
  return { labels: labelsFrom(live), elements: compact };
}

async function sceneBlob(
  api: ExcalidrawAPI,
): Promise<{ blob: Blob; labels: string[] }> {
  const elements = api.getSceneElements();
  const labels = labelsFrom(elements);
  const blob = await exportToBlob({
    elements: elements as never,
    appState: {
      ...api.getAppState(),
      exportBackground: true,
      exportWithDarkMode: false,
    } as never,
    files: api.getFiles() as never,
    mimeType: "image/jpeg",
    quality: 0.72,
  });
  return { blob, labels };
}

export function Board({
  onSubmit,
  onWatch,
  onFrame,
  watchEnabled = false,
  frameEnabled = false,
}: Props) {
  const [api, setApi] = useState<ExcalidrawAPI | null>(null);
  const [busy, setBusy] = useState(false);
  const dirtyRef = useRef(false);
  const lastJsonRef = useRef("");
  const lastFrameJsonRef = useRef("");
  const onWatchRef = useRef(onWatch);
  const onFrameRef = useRef(onFrame);
  const boardRef = useRef<HTMLDivElement>(null);
  onWatchRef.current = onWatch;
  onFrameRef.current = onFrame;

  const submit = useCallback(async () => {
    if (!api) return;
    setBusy(true);
    try {
      const { blob, labels } = await sceneBlob(api);
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

  useEffect(() => {
    if (!frameEnabled || !api || !onFrame) return;
    const tick = window.setInterval(() => {
      const scene = compactScene(api.getSceneElements());
      if (!scene.elements.length) return;
      const json = JSON.stringify(scene);
      if (json === lastFrameJsonRef.current) return;
      lastFrameJsonRef.current = json;
      void sceneBlob(api)
        .then(({ blob, labels }) => onFrameRef.current?.(blob, labels))
        .catch(() => undefined);
    }, FRAME_MS);
    return () => clearInterval(tick);
  }, [api, onFrame, frameEnabled]);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (!(e.ctrlKey || e.metaKey)) return;
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      const root = boardRef.current;
      if (!root) return;
      const t = e.target as Node | null;
      if (!t || !root.contains(t)) return;
      e.preventDefault();
    };
    window.addEventListener("keydown", onKeyDown, true);
    return () => window.removeEventListener("keydown", onKeyDown, true);
  }, []);

  return (
    <div className="board" ref={boardRef}>
      <div className="board-actions">
        <button
          type="button"
          className="board-ask-btn"
          onClick={() => void submit()}
          disabled={busy || !api}
        >
          {busy ? "Sending…" : "I'm done, review my diagram"}
        </button>
        {watchEnabled && (
          <span className="muted board-watch-hint">Canvas watch on</span>
        )}
      </div>
      <div className="board-canvas">
        <Excalidraw
          excalidrawAPI={(a) => setApi(a as unknown as ExcalidrawAPI)}
          theme="light"
          UIOptions={{
            dockedSidebarBreakpoint: 0,
            canvasActions: {
              changeViewBackgroundColor: false,
              clearCanvas: false,
              loadScene: false,
              saveToActiveFile: false,
              toggleTheme: false,
              saveAsImage: false,
            },
          }}
          onChange={() => {
            dirtyRef.current = true;
          }}
        />
      </div>
    </div>
  );
}
