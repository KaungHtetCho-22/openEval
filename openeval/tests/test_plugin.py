from __future__ import annotations


def test_pytest_plugin_adds_option_and_fixtures(pytester) -> None:
    pytester.makeini("[pytest]\nasyncio_default_fixture_loop_scope = function\n")
    pytester.makepyfile(
        my_models="""
def model(prompt: str) -> str:
    return "Paris" if "France" in prompt else "I don't know"
""",
        test_eval="""
import pytest

from openeval import EvalCase
from openeval.scorers import exact_match

@pytest.mark.eval
def test_custom(openeval_run, eval_model):
    cases = [EvalCase(input="What is the capital of France?", expected_output="Paris")]
    summary = openeval_run(eval_model, cases, {"exact": exact_match}, pass_threshold=0.7)
    assert summary.pass_rate == 1.0
""",
    )

    result = pytester.runpytest(
        "--eval-model",
        "callable:my_models:model",
        "-q",
    )
    result.assert_outcomes(passed=1)


def test_pytest_plugin_help_shows_eval_model(pytester) -> None:
    pytester.makeini("[pytest]\nasyncio_default_fixture_loop_scope = function\n")
    result = pytester.runpytest("--help")
    result.stdout.fnmatch_lines(["*--eval-model*"])
