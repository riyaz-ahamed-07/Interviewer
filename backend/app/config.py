from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_FILE, override=False)


def _numbered_keys(prefix: str, max_n: int = 16) -> list[str]:
    keys: list[str] = []
    for i in range(1, max_n + 1):
        val = (os.getenv(f"{prefix}_{i}") or "").strip()
        if val:
            keys.append(val)
    return keys


def _csv_keys(raw: str) -> list[str]:
    return [k.strip() for k in raw.split(",") if k.strip() and k.strip() not in ("key1", "key2", "key3", "key4")]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Optional legacy CSV forms (still supported)
    gemini_api_keys: str = ""
    groq_api_keys: str = ""
    grok_api_keys: str = ""

    gemini_live_model: str = "gemini-3.8-live"
    gemini_live_fallback_model: str = (
        "gemini-2.5-flash-native-audio-preview-12-2025"
    )
    gemini_text_model: str = "gemini/gemini-3.8-flash"
    # qwen returns normal content; gpt-oss-20b often fills reasoning and leaves content empty
    groq_text_model: str = "groq/qwen/qwen3.8-27b"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    debug_seconds: int = 10 * 60
    design_seconds: int = 12 * 60
    llm_seconds: int = 25 * 60

    @property
    def gemini_keys(self) -> list[str]:
        keys = _numbered_keys("GEMINI_API_KEY")
        keys.extend(_csv_keys(self.gemini_api_keys))
        # de-dupe, preserve order
        seen: set[str] = set()
        out: list[str] = []
        for k in keys:
            if k not in seen:
                seen.add(k)
                out.append(k)
        return out

    @property
    def groq_keys(self) -> list[str]:
        keys = _numbered_keys("GROQ_API_KEY")
        keys.extend(_csv_keys(self.groq_api_keys))
        keys.extend(_csv_keys(self.grok_api_keys))
        seen: set[str] = set()
        out: list[str] = []
        for k in keys:
            if k not in seen:
                seen.add(k)
                out.append(k)
        return out

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
