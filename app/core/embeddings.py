from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable

from app.config import settings


_model = None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _fallback_embedding(text: str) -> list[float]:
    tokens = Counter(_tokenize(text))
    if not tokens:
        return [0.0]
    vocabulary = sorted(tokens)
    vector = [float(tokens[token]) for token in vocabulary]
    return vector


def generate_embedding(text: str) -> list[float]:
    global _model
    try:
        if _model is None:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(settings.embedding_model)
        embedding = _model.encode(text, normalize_embeddings=True)
        return [float(value) for value in embedding]
    except Exception:
        return _fallback_embedding(text)


def cosine_similarity(left: Iterable[float], right: Iterable[float]) -> float:
    left_values = list(left)
    right_values = list(right)
    if not left_values or not right_values:
        return 0.0
    if len(left_values) != len(right_values):
        max_len = max(len(left_values), len(right_values))
        left_values.extend([0.0] * (max_len - len(left_values)))
        right_values.extend([0.0] * (max_len - len(right_values)))
    dot = sum(a * b for a, b in zip(left_values, right_values))
    left_norm = math.sqrt(sum(a * a for a in left_values))
    right_norm = math.sqrt(sum(b * b for b in right_values))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
