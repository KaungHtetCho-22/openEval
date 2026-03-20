from __future__ import annotations

from collections.abc import Callable

import pytest

from openeval.adapters.registry import parse_model_string
from openeval.runner import run as run_eval

ModelFn = Callable[[str], str]


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("openeval")
    group.addoption(
        "--eval-model",
        action="store",
        default=None,
        help="Model string like ollama:llama3.2 (or callable:module:fn).",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "eval: mark a test as an OpenEval evaluation (uses eval_model/openeval_run fixtures).",
    )


@pytest.fixture()
def eval_model(request: pytest.FixtureRequest) -> ModelFn:
    model_str = request.config.getoption("--eval-model")
    if not model_str:
        raise pytest.UsageError("Missing --eval-model. Example: pytest --eval-model ollama:llama3.2")
    return parse_model_string(model_str)


@pytest.fixture()
def openeval_run():
    def _run(model_fn: ModelFn, dataset, scorers, pass_threshold: float = 0.7):
        return run_eval(model_fn, dataset, scorers, pass_threshold=pass_threshold)

    return _run

