from __future__ import annotations

import inspect
from collections.abc import Callable

ModelFn = Callable[[str], str]


def callable_adapter(fn: Callable[..., str]) -> ModelFn:
    if not callable(fn):
        raise TypeError("fn must be callable")

    signature = inspect.signature(fn)
    parameters = list(signature.parameters.values())

    required_positional = [
        p
        for p in parameters
        if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        and p.default is inspect.Parameter.empty
    ]

    if len(required_positional) != 1:
        raise TypeError("fn must accept exactly one required positional argument: prompt (str)")

    def model_fn(prompt: str) -> str:
        result = fn(prompt)
        if not isinstance(result, str):
            raise TypeError("model_fn must return a string")
        return result

    return model_fn

