# Eval Suites

Suites are prebuilt datasets + scorers you can run in one line.

```python
from openeval.suites import factuality
summary = factuality.run(lambda _: "Paris")
```

Suites included:

- `hallucination`
- `factuality`
- `instruction_following`

