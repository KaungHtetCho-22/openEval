from __future__ import annotations

"""
Example 05 — Chatbot eval (multi-turn)

Run:
  python examples/05_chatbot_eval.py
"""

from openeval import EvalCase, run
from openeval.scorers import llm_judge


def main() -> None:
    # A "chat" is still just a string prompt; you can serialize turns however you want.
    chat_cases = [
        EvalCase(
            input="User: Hi!\nAssistant: Hello! How can I help?\nUser: What is 2+2?\nAssistant:",
            expected_output="4",
        ),
        EvalCase(
            input="User: I'm feeling stressed.\nAssistant:",
            expected_output="empathetic",
        ),
    ]

    def chatbot(prompt: str) -> str:
        if "2+2" in prompt:
            return "2+2 is 4."
        return "I'm sorry you're feeling stressed. Want to talk about what's going on?"

    # Heuristic judge so the example runs without an external judge model.
    def judge_fn(judge_prompt: str) -> str:
        p = judge_prompt.lower()
        if "expected output" in p and "empathetic" in p:
            return "1.0" if "sorry" in p or "want to talk" in p else "0.0"
        return "1.0" if "4" in p else "0.0"

    summary = run(chatbot, chat_cases, {"chat_quality": llm_judge(judge_fn, criteria="Be helpful and accurate.")})
    print(f"Pass rate: {summary.pass_rate:.0%}")


if __name__ == "__main__":
    main()

