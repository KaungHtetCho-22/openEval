from __future__ import annotations

import importlib
from collections.abc import Awaitable, Callable
from typing import Any, cast

from .anthropic import anthropic_adapter, anthropic_async_adapter
from .callable import callable_adapter
from .ollama import ollama_adapter, ollama_async_adapter
from .openai import openai_adapter, openai_async_adapter

SyncModelFn = Callable[[str], str]
AsyncModelFn = Callable[[str], Awaitable[str]]
AnyModelFn = SyncModelFn | AsyncModelFn


def parse_model_string(
    model: str,
    *,
    system_prompt: str = "",
    ollama_host: str = "http://localhost:11434",
    **kwargs: Any,
) -> SyncModelFn:
    """
    Parse strings like:
      - openai:gpt-4o
      - anthropic:claude-sonnet-4-20250514
      - ollama:llama3.2
      - callable:some_module:some_fn
    """

    if ":" not in model:
        raise ValueError("Model must be in the form provider:value (e.g. ollama:llama3.2)")

    provider, value = model.split(":", 1)
    provider = provider.strip().lower()
    value = value.strip()

    if provider == "openai":
        return openai_adapter(model=value, system_prompt=system_prompt, **kwargs)
    if provider == "anthropic":
        return anthropic_adapter(model=value, system_prompt=system_prompt, **kwargs)
    if provider == "ollama":
        return ollama_adapter(model=value, host=ollama_host, **kwargs)
    if provider == "callable":
        fn = _import_callable(value)
        return callable_adapter(fn)

    raise ValueError(f"Unknown model provider: {provider!r}")


def parse_model_string_async(
    model: str,
    *,
    system_prompt: str = "",
    ollama_host: str = "http://localhost:11434",
    **kwargs: Any,
) -> AnyModelFn:
    if ":" not in model:
        raise ValueError("Model must be in the form provider:value (e.g. ollama:llama3.2)")

    provider, value = model.split(":", 1)
    provider = provider.strip().lower()
    value = value.strip()

    if provider == "openai":
        return openai_async_adapter(model=value, system_prompt=system_prompt, **kwargs)
    if provider == "anthropic":
        return anthropic_async_adapter(model=value, system_prompt=system_prompt, **kwargs)
    if provider == "ollama":
        return ollama_async_adapter(model=value, host=ollama_host, **kwargs)
    if provider == "callable":
        fn = _import_callable(value)
        # arun can wrap sync model_fns safely.
        return callable_adapter(fn)

    raise ValueError(f"Unknown model provider: {provider!r}")


def _import_callable(spec: str) -> Callable[..., str]:
    # Prefer callable:module:attr, but also accept callable:module.attr.
    module_name: str
    attr_name: str

    if ":" in spec:
        module_name, attr_name = spec.rsplit(":", 1)
    elif "." in spec:
        module_name, attr_name = spec.rsplit(".", 1)
    else:
        raise ValueError(
            "callable model spec must be 'module:attribute' (preferred) or 'module.attribute'"
        )

    module = importlib.import_module(module_name)
    fn_obj = getattr(module, attr_name, None)
    if fn_obj is None:
        raise AttributeError(f"Callable not found: {module_name}.{attr_name}")
    if not callable(fn_obj):
        raise TypeError(f"Imported object is not callable: {module_name}.{attr_name}")
    return cast(Callable[..., str], fn_obj)
