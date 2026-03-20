from __future__ import annotations

import types
from dataclasses import dataclass

import pytest

from openeval.adapters import anthropic_adapter, callable_adapter, ollama_adapter, openai_adapter


def test_callable_adapter_returns_callable_and_string() -> None:
    model_fn = callable_adapter(lambda prompt: f"echo: {prompt}")
    assert callable(model_fn)
    assert model_fn("hi") == "echo: hi"


def test_callable_adapter_rejects_wrong_signature() -> None:
    def bad_fn(a: str, b: str) -> str:
        return a + b

    with pytest.raises(TypeError):
        callable_adapter(bad_fn)


def test_openai_adapter_mocked_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    @dataclass
    class _Msg:
        content: str

    @dataclass
    class _Choice:
        message: _Msg

    @dataclass
    class _Resp:
        choices: list[_Choice]

    class _Completions:
        def create(self, **_kwargs):
            return _Resp(choices=[_Choice(message=_Msg(content="hello"))])

    class _Chat:
        def __init__(self):
            self.completions = _Completions()

    class _Client:
        def __init__(self):
            self.chat = _Chat()

    import sys

    fake_openai = types.ModuleType("openai")
    fake_openai.OpenAI = lambda: _Client()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    model_fn = openai_adapter(model="gpt-test", system_prompt="sys", temperature=0)
    assert callable(model_fn)
    assert model_fn("prompt") == "hello"


def test_anthropic_adapter_mocked_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Block:
        def __init__(self, text: str):
            self.text = text

    class _Messages:
        def create(self, **_kwargs):
            return types.SimpleNamespace(content=[_Block("hi there")])

    class _Client:
        def __init__(self):
            self.messages = _Messages()

    import sys

    fake_anthropic = types.ModuleType("anthropic")
    fake_anthropic.Anthropic = lambda: _Client()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "anthropic", fake_anthropic)

    model_fn = anthropic_adapter(model="claude-test", system_prompt="sys")
    assert callable(model_fn)
    assert model_fn("prompt") == "hi there"


def test_ollama_adapter_mocked_httpx(monkeypatch: pytest.MonkeyPatch) -> None:
    import httpx

    class _Resp:
        def raise_for_status(self) -> None:
            return None

        def json(self):
            return {"response": "ok"}

    class _Client:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url: str, json):
            assert url.endswith("/api/generate")
            assert json["stream"] is False
            return _Resp()

    monkeypatch.setattr(httpx, "Client", _Client)
    model_fn = ollama_adapter(model="llama-test", host="http://localhost:11434")
    assert model_fn("prompt") == "ok"


def test_ollama_adapter_connection_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import httpx

    class _Client:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url: str, json):
            raise httpx.ConnectError("nope")

    monkeypatch.setattr(httpx, "Client", _Client)

    model_fn = ollama_adapter()
    with pytest.raises(RuntimeError, match="Could not connect to Ollama"):
        model_fn("prompt")
