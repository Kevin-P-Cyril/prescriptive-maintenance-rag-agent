"""
LLM service.

Uses Ollama to run an open-source LLM (e.g. llama3.2) fully locally and
free of charge, replacing any paid API (such as Google Gemini) so the
project never incurs API costs. If Ollama is not running/reachable, calls
fail gracefully with a clear, actionable error instead of crashing the API.
"""
from __future__ import annotations

import logging
from functools import lru_cache

import requests
from langchain_ollama import ChatOllama

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMUnavailableError(RuntimeError):
    """Raised when the local Ollama server cannot be reached."""


@lru_cache
def get_llm() -> ChatOllama:
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=0.2,
    )


def is_ollama_available() -> bool:
    try:
        resp = requests.get(f"{settings.ollama_base_url}/api/tags", timeout=2)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def generate(prompt: str) -> str:
    """Invoke the local LLM with a prompt string, raising a clear error if unavailable."""
    if not is_ollama_available():
        raise LLMUnavailableError(
            "Could not reach Ollama at "
            f"{settings.ollama_base_url}. Start it with `ollama serve` and make sure "
            f"the model is pulled with `ollama pull {settings.ollama_model}`."
        )
    llm = get_llm()
    response = llm.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)
