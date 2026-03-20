from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

import httpx

SyncModelFn = Callable[[str], str]
AsyncModelFn = Callable[[str], Awaitable[str]]
ModelFn = SyncModelFn


def ollama_adapter(model: str = "llama3.2", host: str = "http://localhost:11434", **kwargs: Any) -> ModelFn:
    url = host.rstrip("/") + "/api/generate"

    def model_fn(prompt: str) -> str:
        payload_kwargs = dict(kwargs)
        timeout = payload_kwargs.pop("timeout", 60.0)
        payload: dict[str, Any] = {"model": model, "prompt": prompt, "stream": False}
        payload.update(payload_kwargs)

        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
        except httpx.ConnectError as exc:
            raise RuntimeError(
                f"Could not connect to Ollama at {host}. Is Ollama running (default: http://localhost:11434)?"
            ) from exc

        data = resp.json()
        output = data.get("response", "")
        if not isinstance(output, str):
            raise RuntimeError("Unexpected Ollama response format: 'response' must be a string")
        return output.strip()

    return model_fn


def ollama_async_adapter(model: str = "llama3.2", host: str = "http://localhost:11434", **kwargs: Any) -> AsyncModelFn:
    url = host.rstrip("/") + "/api/generate"

    async def model_fn(prompt: str) -> str:
        payload_kwargs = dict(kwargs)
        timeout = payload_kwargs.pop("timeout", 60.0)
        payload: dict[str, Any] = {"model": model, "prompt": prompt, "stream": False}
        payload.update(payload_kwargs)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
        except httpx.ConnectError as exc:
            raise RuntimeError(
                f"Could not connect to Ollama at {host}. Is Ollama running (default: http://localhost:11434)?"
            ) from exc

        data = resp.json()
        output = data.get("response", "")
        if not isinstance(output, str):
            raise RuntimeError("Unexpected Ollama response format: 'response' must be a string")
        return output.strip()

    return model_fn
