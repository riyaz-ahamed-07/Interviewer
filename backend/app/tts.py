"""Fallback TTS via edge-tts (free, no key)."""

from __future__ import annotations

import io
import logging

logger = logging.getLogger(__name__)


async def synthesize_mp3(text: str, voice: str = "en-US-GuyNeural") -> bytes:
    try:
        import edge_tts

        communicate = edge_tts.Communicate(text, voice)
        buf = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buf.write(chunk["data"])
        return buf.getvalue()
    except Exception:
        logger.exception("edge-tts failed")
        return b""
