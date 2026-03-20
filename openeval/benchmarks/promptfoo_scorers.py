from __future__ import annotations

from typing import Any


def admits_uncertainty(output: str, context: dict[str, Any]) -> dict[str, Any]:
    o = (output or "").lower()
    phrases = ["i don't know", "i do not know", "not sure", "unknown", "unable", "cannot"]
    ok = any(p in o for p in phrases)
    return {"pass": ok, "score": 1.0 if ok else 0.0, "reason": "uncertainty" if ok else "hallucination"}

