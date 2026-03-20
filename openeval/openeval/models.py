from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvalCase(BaseModel):
    input: str
    expected_output: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvalResult(BaseModel):
    case: EvalCase
    actual_output: str
    scores: dict[str, float]
    passed: bool


class EvalSummary(BaseModel):
    results: list[EvalResult]
    mean_score: float
    pass_rate: float
    total: int

