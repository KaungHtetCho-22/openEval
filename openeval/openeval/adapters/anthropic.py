from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

SyncModelFn = Callable[[str], str]
AsyncModelFn = Callable[[str], Awaitable[str]]
ModelFn = SyncModelFn


def anthropic_adapter(
    model: str = "claude-sonnet-4-20250514", system_prompt: str = "", **kwargs: Any
) -> ModelFn:
    try:
        from anthropic import Anthropic
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise ModuleNotFoundError(
            "anthropic is required for anthropic_adapter. Install with: pip install 'openeval[anthropic]'"
        ) from exc

    client = Anthropic()

    def model_fn(prompt: str) -> str:
        resp = client.messages.create(
            model=model,
            system=system_prompt or None,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        try:
            first = resp.content[0]
            text = getattr(first, "text", None) or (first.get("text") if isinstance(first, dict) else None)
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Unexpected Anthropic response format") from exc
        if not isinstance(text, str):
            raise RuntimeError("Unexpected Anthropic response format: missing text")
        return text.strip()

    return model_fn


def anthropic_async_adapter(
    model: str = "claude-sonnet-4-20250514", system_prompt: str = "", **kwargs: Any
) -> AsyncModelFn:
    try:
        from anthropic import AsyncAnthropic
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise ModuleNotFoundError(
            "anthropic is required for anthropic_async_adapter. Install with: pip install 'openeval[anthropic]'"
        ) from exc

    client = AsyncAnthropic()

    async def model_fn(prompt: str) -> str:
        resp = await client.messages.create(
            model=model,
            system=system_prompt or None,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        try:
            first = resp.content[0]
            text = getattr(first, "text", None) or (first.get("text") if isinstance(first, dict) else None)
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Unexpected Anthropic response format") from exc
        if not isinstance(text, str):
            raise RuntimeError("Unexpected Anthropic response format: missing text")
        return text.strip()

    return model_fn
