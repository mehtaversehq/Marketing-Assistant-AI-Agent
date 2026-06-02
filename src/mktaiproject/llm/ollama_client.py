from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class OllamaResponse:
    """Normalized response from the local Ollama API."""

    ok: bool
    content: str
    error: str | None = None


class OllamaClient:
    """Small standard-library client for Ollama's `/api/generate` endpoint."""

    def __init__(self, model: str | None = None, base_url: str | None = None) -> None:
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3:8b")
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")

    def generate(self, prompt: str, system: str | None = None, temperature: float = 0.1) -> OllamaResponse:
        """Generate text, returning a clean error instead of raising on connection issues."""
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system

        request = Request(
            url=f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
                return OllamaResponse(ok=True, content=str(data.get("response", "")).strip())
        except HTTPError as exc:
            return OllamaResponse(ok=False, content="", error=f"Ollama HTTP error: {exc.code}")
        except URLError:
            return OllamaResponse(
                ok=False,
                content="",
                error=f"Ollama is not reachable at {self.base_url}.",
            )
