from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from .models import (
    FlashCard,
    Paper,
    PaperMap,
    PaperSession,
    ReadingLogEntry,
)

DATA_ROOT = Path(__file__).resolve().parents[2] / "data" / "papers"


def _ensure() -> None:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    (DATA_ROOT / "maps").mkdir(exist_ok=True)
    (DATA_ROOT / "sessions").mkdir(exist_ok=True)
    (DATA_ROOT / "cards").mkdir(exist_ok=True)
    (DATA_ROOT / "log.json").touch(exist_ok=True)


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def save_paper(paper: Paper) -> Paper:
    _ensure()
    if not paper.created_at:
        paper.created_at = _now()
    path = DATA_ROOT / f"{paper.id}.json"
    path.write_text(paper.model_dump_json(indent=2), encoding="utf-8")
    return paper


def load_paper(paper_id: str) -> Paper | None:
    path = DATA_ROOT / f"{paper_id}.json"
    if not path.exists():
        return None
    return Paper.model_validate_json(path.read_text(encoding="utf-8"))


def list_papers() -> list[dict[str, Any]]:
    _ensure()
    out: list[dict[str, Any]] = []
    for path in sorted(DATA_ROOT.glob("*.json"), reverse=True):
        if path.name in ("log.json",):
            continue
        if path.parent.name != "papers" and path.parent != DATA_ROOT:
            continue
        if path.name.endswith(".json") and path.parent == DATA_ROOT:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                out.append(
                    {
                        "id": data.get("id"),
                        "title": data.get("title"),
                        "arxiv_id": data.get("arxiv_id"),
                        "created_at": data.get("created_at"),
                        "abstract": (data.get("abstract") or "")[:240],
                    }
                )
            except Exception:
                continue
    return out


def save_map(paper_id: str, paper_map: PaperMap) -> PaperMap:
    _ensure()
    path = DATA_ROOT / "maps" / f"{paper_id}.json"
    path.write_text(paper_map.model_dump_json(indent=2), encoding="utf-8")
    return paper_map


def load_map(paper_id: str) -> PaperMap | None:
    path = DATA_ROOT / "maps" / f"{paper_id}.json"
    if not path.exists():
        return None
    return PaperMap.model_validate_json(path.read_text(encoding="utf-8"))


def save_session(session: PaperSession) -> PaperSession:
    _ensure()
    path = DATA_ROOT / "sessions" / f"{session.id}.json"
    path.write_text(session.model_dump_json(indent=2), encoding="utf-8")
    return session


def load_session(session_id: str) -> PaperSession | None:
    path = DATA_ROOT / "sessions" / f"{session_id}.json"
    if not path.exists():
        return None
    return PaperSession.model_validate_json(path.read_text(encoding="utf-8"))


def new_session(paper_id: str, mode: str = "text") -> PaperSession:
    session = PaperSession(
        id=str(uuid.uuid4()),
        paper_id=paper_id,
        mode="voice" if mode == "voice" else "text",
        created_at=_now(),
    )
    return save_session(session)


def save_cards(paper_id: str, cards: list[FlashCard]) -> list[FlashCard]:
    _ensure()
    path = DATA_ROOT / "cards" / f"{paper_id}.json"
    path.write_text(
        json.dumps([c.model_dump() for c in cards], indent=2),
        encoding="utf-8",
    )
    return cards


def load_cards(paper_id: str) -> list[FlashCard]:
    path = DATA_ROOT / "cards" / f"{paper_id}.json"
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [FlashCard.model_validate(x) for x in raw]


def append_log(entry: ReadingLogEntry) -> None:
    _ensure()
    path = DATA_ROOT / "log.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "[]")
    except Exception:
        data = []
    if not isinstance(data, list):
        data = []
    data.insert(0, entry.model_dump())
    path.write_text(json.dumps(data[:100], indent=2), encoding="utf-8")


def list_log() -> list[dict[str, Any]]:
    _ensure()
    path = DATA_ROOT / "log.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "[]")
        return data if isinstance(data, list) else []
    except Exception:
        return []


def due_cards(limit: int = 20) -> list[FlashCard]:
    _ensure()
    now = _now()
    out: list[FlashCard] = []
    for path in (DATA_ROOT / "cards").glob("*.json"):
        for card in load_cards(path.stem):
            if not card.due_at or card.due_at <= now:
                out.append(card)
    return out[:limit]
