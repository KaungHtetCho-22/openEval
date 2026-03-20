# Using Adapters

Adapters turn a model API into a simple callable.

## OpenAI

```python
from openeval.adapters import openai_adapter
model = openai_adapter(model="gpt-4o-mini")
```

## Anthropic

```python
from openeval.adapters import anthropic_adapter
model = anthropic_adapter(model="claude-sonnet-4-20250514")
```

## Ollama

```python
from openeval.adapters import ollama_adapter
model = ollama_adapter(model="llama3.2")
```

## Callable

```python
from openeval.adapters import callable_adapter
model = callable_adapter(lambda prompt: "hello")
```

## Async adapters

For parallel evaluation, use `*_async_adapter(...)` with `arun()`.

