from typing import Iterable
import httpx

from .config import get_settings
from .prompts import MODE_PERSONALITIES, build_system_prompt

settings = get_settings()


def fallback_reply(mode: str, user_text: str) -> str:
    mode_name = MODE_PERSONALITIES[mode]["label"]
    starters = {
        "red": "That sounds like a lot of pressure hitting at once. You don’t have to tidy it up for me. What part of it is making you feel most overwhelmed right now?",
        "blue": "I hear you. That kind of heaviness can make even ordinary things feel distant. I’m here to listen. What happened just before you started feeling this way?",
        "yellow": "Your mind sounds like it is running several loops at once. Let’s slow one loop down. What is the single thought that keeps coming back?",
        "green": "I’m listening. We can keep this completely ordinary or go somewhere deeper. What’s been on your mind lately?",
    }
    return starters.get(mode, f"I’m here with you in {mode_name.lower()}. What would feel useful to talk about?")


def _ollama_messages(mode: str, messages: list[dict]) -> list[dict]:
    return [{"role": "system", "content": build_system_prompt(mode)}] + messages


def generate_reply(mode: str, messages: list[dict]) -> tuple[str, str]:
    provider = settings.ai_provider.lower().strip()
    if provider == "ollama":
        try:
            payload = {
                "model": settings.ollama_model,
                "messages": _ollama_messages(mode, messages),
                "stream": False,
                "options": {"temperature": 0.7, "num_ctx": 8192},
            }
            with httpx.Client(timeout=90) as client:
                response = client.post(settings.ollama_base_url.rstrip("/") + "/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                content = data.get("message", {}).get("content", "").strip()
                if content:
                    return content, "ollama"
        except Exception:
            pass
    elif provider == "openai_compatible" and settings.openai_compatible_api_key and settings.openai_compatible_model:
        try:
            payload = {
                "model": settings.openai_compatible_model,
                "messages": _ollama_messages(mode, messages),
                "temperature": 0.7,
            }
            headers = {"Authorization": f"Bearer {settings.openai_compatible_api_key}"}
            with httpx.Client(timeout=90) as client:
                response = client.post(
                    settings.openai_compatible_base_url.rstrip("/") + "/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                if content:
                    return content, "openai_compatible"
        except Exception:
            pass

    if messages:
        return fallback_reply(mode, messages[-1]["content"]), "fallback"
    return MODE_PERSONALITIES[mode]["opening"], "fallback"
