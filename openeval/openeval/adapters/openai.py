from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

SyncModelFn = Callable[[str], str]
AsyncModelFn = Callable[[str], Awaitable[str]]
ModelFn = SyncModelFn


def openai_adapter(model: str = "gpt-4o", system_prompt: str = "", **kwargs: Any) -> ModelFn:
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise ModuleNotFoundError(
            "openai is required for openai_adapter. Install with: pip install 'openeval[openai]'"
        ) from exc

    client = OpenAI()

    def model_fn(prompt: str) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        resp = client.chat.completions.create(model=model, messages=messages, **kwargs)
        try:
            content = resp.choices[0].message.content
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Unexpected OpenAI response format") from exc
        return (content or "").strip()

    return model_fn


def openai_async_adapter(model: str = "gpt-4o", system_prompt: str = "", **kwargs: Any) -> AsyncModelFn:
    try:
        from openai import AsyncOpenAI
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise ModuleNotFoundError(
            "openai is required for openai_async_adapter. Install with: pip install 'openeval[openai]'"
        ) from exc

    client = AsyncOpenAI()

    async def model_fn(prompt: str) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        resp = await client.chat.completions.create(model=model, messages=messages, **kwargs)
        try:
            content = resp.choices[0].message.content
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Unexpected OpenAI response format") from exc
        return (content or "").strip()

    return model_fn
