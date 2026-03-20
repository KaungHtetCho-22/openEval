from __future__ import annotations

from typing import Any

_MODEL: Any | None = None


def _get_model() -> Any:
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    try:
        from sentence_transformers import SentenceTransformer
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise ModuleNotFoundError(
            "sentence-transformers is required for semantic_sim. "
            "Install with: pip install 'openeval[semantic]'"
        ) from exc

    _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


def semantic_sim(_input: str, output: str, expected: str = "") -> float:
    if not expected:
        return 0.0

    model = _get_model()
    output_vec = model.encode(output, normalize_embeddings=True)
    expected_vec = model.encode(expected, normalize_embeddings=True)

    # With normalized embeddings, dot product == cosine similarity in [-1, 1].
    cos_sim = float(output_vec @ expected_vec)
    score = (cos_sim + 1.0) / 2.0
    if score < 0.0:
        return 0.0
    if score > 1.0:
        return 1.0
    return score
