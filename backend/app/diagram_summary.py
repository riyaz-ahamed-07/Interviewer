from __future__ import annotations

from typing import Any


def scene_to_adjacency(scene: dict[str, Any]) -> dict[str, Any]:
    elements = list(scene.get("elements") or [])
    labels = [str(x) for x in (scene.get("labels") or []) if str(x).strip()]
    id_to_label: dict[str, str] = {}
    for el in elements:
        eid = str(el.get("id") or "")
        text = str(el.get("text") or "").strip()
        if eid and text:
            id_to_label[eid] = text

    edges: list[str] = []
    for el in elements:
        if el.get("type") != "arrow":
            continue
        start = el.get("startBinding") or {}
        end = el.get("endBinding") or {}
        s_id = str((start.get("elementId") if isinstance(start, dict) else "") or "")
        e_id = str((end.get("elementId") if isinstance(end, dict) else "") or "")
        s = id_to_label.get(s_id) or s_id or "?"
        e = id_to_label.get(e_id) or e_id or "?"
        if s != "?" or e != "?":
            edges.append(f"{s} -> {e}")

    lines = edges or [f"(node) {lab}" for lab in labels[:40]]
    summary = "\n".join(lines) if lines else "(empty diagram)"
    return {
        "labels": labels[:80],
        "edges": edges[:80],
        "adjacency_text": summary,
        "watch_blob": f"[CANVAS WATCH]\n{summary}",
    }
