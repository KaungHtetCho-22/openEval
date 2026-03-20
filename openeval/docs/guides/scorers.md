# Writing Scorers

Scorers are just Python callables:

```python
def scorer(input: str, output: str, expected: str = "") -> float:
    ...
```

Guidelines:

- Return a float in `[0.0, 1.0]`
- Be deterministic (avoid randomness)
- Keep it fast (you’ll run this N×cases×models)

## Example: length constraint

```python
def max_len(limit: int):
    def s(_input: str, output: str, _expected: str = "") -> float:
        return 1.0 if len(output) <= limit else 0.0
    return s
```

