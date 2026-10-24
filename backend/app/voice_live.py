"""Bridge browser mic PCM <-> Gemini Live API (native speech-to-speech)."""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import traceback
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

from .config import get_settings
from .llm_router import next_gemini_key
from .session import store

logger = logging.getLogger(__name__)

INPUT_RATE = 16000


def _live_config(system_text: str) -> types.LiveConnectConfig:
    return types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
            )
        ),
        system_instruction=types.Content(parts=[types.Part(text=system_text)]),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )


async def _run_live_session(
    websocket: WebSocket,
    session_id: str,
    api_key: str,
    model: str,
    system_text: str,
    opening: str,
    *,
    resume: bool = False,
) -> None:
    client = genai.Client(api_key=api_key)
    audio_in: asyncio.Queue[bytes] = asyncio.Queue(maxsize=128)
    text_in: asyncio.Queue[str] = asyncio.Queue(maxsize=32)
    image_in: asyncio.Queue[bytes] = asyncio.Queue(maxsize=8)
    stop = asyncio.Event()

    async def pump_client() -> None:
        try:
            while not stop.is_set():
                raw = await websocket.receive()
                if raw.get("type") == "websocket.disconnect":
                    break
                if "bytes" in raw and raw["bytes"] is not None:
                    try:
                        audio_in.put_nowait(raw["bytes"])
                    except asyncio.QueueFull:
                        _ = audio_in.get_nowait()
                        audio_in.put_nowait(raw["bytes"])
                    continue
                text = raw.get("text")
                if not text:
                    continue
                msg = json.loads(text)
                mtype = msg.get("type")
                if mtype == "text":
                    await text_in.put(msg.get("text", ""))
                elif mtype == "image_png_b64":
                    data = base64.b64decode(msg["data"])
                    mime = msg.get("mime") or "image/png"
                    silent = bool(msg.get("silent"))
                    try:
                        image_in.put_nowait((data, mime, silent))
                    except asyncio.QueueFull:
                        # keep newest frame
                        try:
                            _ = image_in.get_nowait()
                        except asyncio.QueueEmpty:
                            pass
                        try:
                            image_in.put_nowait((data, mime, silent))
                        except asyncio.QueueFull:
                            pass
                elif mtype == "phase_sync":
                    fresh = store.get(session_id)
                    if fresh:
                        briefing = msg.get("briefing") or fresh.live_briefing()
                        await text_in.put(briefing)
                elif mtype == "pause":
                    await text_in.put(
                        "[System] Candidate paused. Stay completely silent until they resume."
                    )
                elif mtype == "end":
                    break
        except WebSocketDisconnect:
            pass
        except Exception:
            logger.exception("pump_client failed")
        finally:
            stop.set()

    config = _live_config(system_text)
    logger.info("Connecting Gemini Live model=%s", model)

    async with client.aio.live.connect(model=model, config=config) as live:
        await websocket.send_json({"type": "live_connected", "model": model})
        if resume:
            await live.send_realtime_input(
                text=(
                    "[System] Candidate just resumed the live call after a pause. "
                    "Stay silent for a moment. Do NOT re-read old openings or restart the phase. "
                    "Wait for their voice or a short continue cue, then pick up briefly where you left off."
                )
            )
        else:
            await live.send_realtime_input(
                text=(
                    "You are in a LIVE voice conversation. Speak naturally — "
                    "short sentences, conversational, not reading an essay. "
                    "Begin now by saying this opening out loud (paraphrase slightly if natural):\n"
                    f"{opening}"
                )
            )

        async def send_audio() -> None:
            while not stop.is_set():
                chunk = await audio_in.get()
                await live.send_realtime_input(
                    audio=types.Blob(
                        data=chunk,
                        mime_type=f"audio/pcm;rate={INPUT_RATE}",
                    )
                )

        async def send_text() -> None:
            while not stop.is_set():
                t = await text_in.get()
                await live.send_realtime_input(text=t)

        async def send_images() -> None:
            while not stop.is_set():
                item = await image_in.get()
                if isinstance(item, tuple):
                    data, mime, _silent = item
                else:
                    data, mime = item, "image/png"
                # Video/image frames enrich context; Live replies on voice VAD,
                # not on frames alone — do not send companion text for silent watches.
                await live.send_realtime_input(
                    video=types.Blob(data=data, mime_type=mime or "image/jpeg")
                )

        async def receive_loop() -> None:
            while not stop.is_set():
                async for response in live.receive():
                    if stop.is_set():
                        break
                    sc = response.server_content
                    if not sc:
                        continue
                    if sc.interrupted:
                        await websocket.send_json({"type": "interrupted"})
                    if sc.model_turn:
                        for part in sc.model_turn.parts or []:
                            if part.inline_data and part.inline_data.data:
                                await websocket.send_bytes(part.inline_data.data)
                    interim = getattr(sc, "interim_input_transcription", None)
                    if interim is not None and getattr(interim, "text", None):
                        await websocket.send_json(
                            {
                                "type": "user_transcript_interim",
                                "text": interim.text,
                            }
                        )
                    if sc.input_transcription and sc.input_transcription.text:
                        payload: dict[str, Any] = {
                            "type": "user_transcript",
                            "text": sc.input_transcription.text,
                        }
                        if getattr(sc.input_transcription, "finished", None):
                            payload["finished"] = True
                        await websocket.send_json(payload)
                    if sc.output_transcription and sc.output_transcription.text:
                        await websocket.send_json(
                            {
                                "type": "assistant_transcript",
                                "text": sc.output_transcription.text,
                            }
                        )
                    if sc.turn_complete:
                        await websocket.send_json({"type": "turn_complete"})

        tasks = [
            asyncio.create_task(pump_client(), name="pump"),
            asyncio.create_task(send_audio(), name="audio"),
            asyncio.create_task(send_text(), name="text"),
            asyncio.create_task(send_images(), name="images"),
            asyncio.create_task(receive_loop(), name="recv"),
        ]
        try:
            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_EXCEPTION
            )
            for t in done:
                exc = t.exception()
                if exc:
                    raise exc
        finally:
            stop.set()
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)


async def handle_live_socket(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    interview = store.get(session_id)
    if interview is None:
        await websocket.send_json({"type": "error", "error": "session not found"})
        await websocket.close()
        return

    resume = (websocket.query_params.get("resume") or "").lower() in (
        "1",
        "true",
        "yes",
    )

    settings = get_settings()
    api_key = next_gemini_key()
    if not api_key:
        await websocket.send_json(
            {"type": "error", "error": "No Gemini keys configured", "fallback": True}
        )
        await websocket.close()
        return

    system_text = (
        "LANGUAGE LOCK: Reply in English only. Never switch to Spanish, French, "
        "or any other language even if speech recognition sounds non-English "
        "(e.g. LoRA misheard as Flora).\n\n"
        + interview.system_prompt()
    )
    opening = (
        interview.messages[-1].content
        if interview.messages
        else "Begin the interview."
    )
    models = [settings.gemini_live_model, settings.gemini_live_fallback_model]
    # de-dupe
    tried: list[str] = []
    for m in models:
        if m and m not in tried:
            tried.append(m)

    await websocket.send_json(
        {
            "type": "ready",
            "models": tried,
            "phase": interview.phase.value,
            "resume": resume,
        }
    )

    last_err: Exception | None = None
    for i, model in enumerate(tried):
        try:
            if i > 0:
                await websocket.send_json(
                    {"type": "retrying", "fallback_model": model}
                )
            await _run_live_session(
                websocket,
                session_id,
                api_key,
                model,
                system_text,
                opening,
                resume=resume,
            )
            return
        except Exception as e:
            last_err = e
            logger.error(
                "Live model %s failed: %s\n%s", model, e, traceback.format_exc()
            )
            # rotate key for next attempt
            api_key = next_gemini_key() or api_key

    try:
        await websocket.send_json(
            {
                "type": "error",
                "error": f"{type(last_err).__name__}: {last_err}" if last_err else "live failed",
                "fallback": True,
            }
        )
    except Exception:
        pass
    try:
        await websocket.close()
    except Exception:
        pass


def live_status() -> dict[str, Any]:
    s = get_settings()
    return {
        "configured": bool(s.gemini_keys),
        "model": s.gemini_live_model,
        "fallback_model": s.gemini_live_fallback_model,
        "key_count": len(s.gemini_keys),
    }
