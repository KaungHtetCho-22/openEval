import pytest

from openeval.scorers import contains, exact_match, llm_judge, make_exact_match, regex


def test_semantic_sim_offline_normalization(monkeypatch: pytest.MonkeyPatch) -> None:
    from openeval.scorers import semantic as semantic_mod

    class _Vec:
        def __init__(self, value: float):
            self.value = value

        def __matmul__(self, other: "_Vec") -> float:
            return float(self.value * other.value)

    class _FakeModel:
        def encode(self, text: str, *, normalize_embeddings: bool = True):
            assert normalize_embeddings is True
            if text == "same":
                return _Vec(1.0)
            if text == "opposite":
                return _Vec(-1.0)
            return _Vec(0.0)

    monkeypatch.setattr(semantic_mod, "_get_model", lambda: _FakeModel())

    assert semantic_mod.semantic_sim("q", "same", "same") == 1.0
    assert semantic_mod.semantic_sim("q", "same", "opposite") == 0.0
    assert semantic_mod.semantic_sim("q", "neutral", "same") == 0.5


def test_exact_match_perfect_match() -> None:
    assert exact_match("q", "4", "4") == 1.0


def test_exact_match_wrong_answer() -> None:
    assert exact_match("q", "5", "4") == 0.0


def test_exact_match_case_insensitive_by_default() -> None:
    assert exact_match("q", "PARIS", "paris") == 1.0


def test_exact_match_case_sensitive_factory() -> None:
    scorer = make_exact_match(case_sensitive=True)
    assert scorer("q", "PARIS", "paris") == 0.0


def test_contains_match_case_insensitive() -> None:
    assert contains("q", "The color is Blue.", "blue") == 1.0


def test_contains_no_match() -> None:
    assert contains("q", "The color is red.", "blue") == 0.0


def test_regex_match() -> None:
    is_json = regex(r"^\{.*\}$")
    assert is_json("q", '{"key":"val"}', "") == 1.0


def test_regex_no_match() -> None:
    is_json = regex(r"^\{.*\}$")
    assert is_json("q", "not json", "") == 0.0


def test_llm_judge_parses_score() -> None:
    def judge_fn(_prompt: str) -> str:
        return "0.8"

    scorer = llm_judge(judge_fn, criteria="Be strict.")
    assert scorer("q", "out", "exp") == 0.8


def test_llm_judge_parse_failure_returns_0_5() -> None:
    def judge_fn(_prompt: str) -> str:
        return "I refuse."

    scorer = llm_judge(judge_fn)
    assert scorer("q", "out", "exp") == 0.5


def test_semantic_sim_optional_dependency() -> None:
    pytest.importorskip("sentence_transformers")
    import os

    if os.environ.get("OPENEVAL_TEST_SEMANTIC") != "1":
        pytest.skip("Set OPENEVAL_TEST_SEMANTIC=1 to run (requires model download/cache).")
    from openeval.scorers import semantic_sim

    score = semantic_sim("q", "hello world", "hello world")
    assert 0.9 <= score <= 1.0
