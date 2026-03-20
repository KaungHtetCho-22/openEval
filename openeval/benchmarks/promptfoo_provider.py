from __future__ import annotations

from typing import Any

QA = {
    "What is 2+2?": "4",
    "Capital of France?": "Paris",
    "Capital of Japan?": "Tokyo",
    "Largest planet?": "Jupiter",
    "Chemical symbol for water?": "H2O",
    "Square root of 81?": "9",
    "How many continents?": "7",
    "Primary language in Brazil?": "Portuguese",
    "Freezing point of water (C)?": "0",
    "Who wrote 1984?": "George Orwell",
    "Capital of Canada?": "Ottawa",
    "Largest ocean?": "Pacific",
    "3*3?": "9",
    "Opposite of hot?": "cold",
    "Color of a clear daytime sky?": "blue",
    "First month of the year?": "January",
    "How many days in a week?": "7",
    "What is 10/2?": "5",
    "What is the capital of Italy?": "Rome",
    "What is the chemical symbol for oxygen?": "O",
}


def provider(prompt: str, options: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    # Promptfoo python provider protocol:
    # return { "output": "..." }
    cfg = (options or {}).get("config", {}) if isinstance(options, dict) else {}
    variant = cfg.get("variant", "good")

    if variant == "bad":
        return {"output": "I don't know"}
    if variant == "uncertain":
        return {"output": "I don't know."}

    return {"output": QA.get(prompt, "I don't know")}

