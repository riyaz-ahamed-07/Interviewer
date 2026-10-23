from __future__ import annotations

import base64
import logging
from typing import Any

from litellm import Router

from .config import get_settings

logger = logging.getLogger(__name__)

_router: Router | None = None
_key_cursor = 0


def _build_router() -> Router | None:
    settings = get_settings()
    model_list: list[dict[str, Any]] = []

    for key in settings.gemini_keys:
        model_list.append(
            {
                "model_name": "interviewer-gemini",
                "litellm_params": {
                    "model": settings.gemini_text_model,
                    "api_key": key,
                },
                "rpm": 15,
            }
        )
        model_list.append(
            {
                "model_name": "interviewer-vision",
                "litellm_params": {
                    "model": settings.gemini_text_model,
                    "api_key": key,
                },
                "rpm": 10,
            }
        )

    for key in settings.groq_keys:
        model_list.append(
            {
                "model_name": "interviewer-groq",
                "litellm_params": {
                    "model": settings.groq_text_model,
                    "api_key": key,
                },
                "rpm": 30,
            }
        )

    if not model_list:
        logger.warning("No API keys configured - text LLM disabled")
        return None

    fallbacks: list[dict[str, list[str]]] = [
        {"interviewer-gemini": ["interviewer-groq"]},
        {"interviewer-vision": ["interviewer-gemini", "interviewer-groq"]},
    ]

    return Router(
        model_list=model_list,
        routing_strategy="simple-shuffle",
        num_retries=1,
        timeout=90,
        fallbacks=fallbacks,
    )


def reset_router() -> None:
    global _router
    _router = None


def get_router() -> Router | None:
    global _router
    if _router is None:
        _router = _build_router()
    return _router


def next_gemini_key() -> str | None:
    global _key_cursor
    keys = get_settings().gemini_keys
    if not keys:
        return None
    key = keys[_key_cursor % len(keys)]
    _key_cursor += 1
    return key


def _candidate_models(
    vision: bool,
    prefer: str = "auto",
) -> list[str]:
    settings = get_settings()
    if vision:
        order = ["interviewer-vision", "interviewer-gemini", "interviewer-groq"]
    elif prefer == "groq":
        # Groq only — no Gemini wait on 503 (caller can fall back if needed)
        order = ["interviewer-groq"]
    elif prefer == "gemini":
        order = ["interviewer-gemini", "interviewer-groq"]
    else:
        order = ["interviewer-gemini", "interviewer-groq"]
    out: list[str] = []
    for name in order:
        if name == "interviewer-groq" and not settings.groq_keys:
            continue
        if name.startswith("interviewer-gemini") and not settings.gemini_keys:
            continue
        if name == "interviewer-vision" and not settings.gemini_keys:
            continue
        if name not in out:
            out.append(name)
    if not out and settings.groq_keys:
        out = ["interviewer-groq"]
    return out


async def chat_completion(
    system: str,
    history: list[dict[str, str]],
    user_text: str,
    image_png_b64: str | None = None,
    *,
    prefer: str = "auto",
) -> str:
    router = get_router()
    if router is None:
        return (
            "[No API keys configured. Add GEMINI_API_KEY_1=... to backend/.env - "
            "see .env.example.]"
        )

    messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
    for m in history[-20:]:
        if m["role"] in ("user", "assistant"):
            messages.append({"role": m["role"], "content": m["content"]})

    if image_png_b64:
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{image_png_b64}",
                    },
                ],
            }
        )
    else:
        messages.append({"role": "user", "content": user_text})

    # Gemini 3+: temperature 1.0. Groq: slightly lower is fine.
    temperature = 0.8 if prefer == "groq" else 1.0
    errors: list[str] = []
    for model in _candidate_models(vision=bool(image_png_b64), prefer=prefer):
        try:
            logger.info("chat_completion trying model group=%s", model)
            resp = await router.acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=4096,
            )
            content = resp.choices[0].message.content or ""
            if content.strip():
                return content
            errors.append(f"{model}: empty content")
            logger.warning("model group %s returned empty content", model)
        except Exception as e:
            logger.warning("model group %s failed: %s", model, e)
            errors.append(f"{model}: {type(e).__name__}: {e}")
            continue

    logger.error("All LLM backends failed: %s", errors)
    return f"[LLM error: all backends failed. Last: {errors[-1] if errors else 'unknown'}]"


async def chat_completion_groq(
    system: str,
    user_text: str,
) -> str:
    """Groq-first path for debug snippet generation (Gemini only if Groq fails)."""
    settings = get_settings()
    if settings.groq_keys:
        raw = await chat_completion(system, [], user_text, prefer="groq")
        if not raw.startswith("[LLM error"):
            return raw
        logger.warning("Groq drill gen failed, falling back to Gemini")
    return await chat_completion(system, [], user_text, prefer="gemini")


def encode_png_bytes(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")
