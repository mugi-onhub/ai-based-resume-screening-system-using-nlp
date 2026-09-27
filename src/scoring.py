"""Score normalization and weighted fusion."""
import numpy as np
from config import WEIGHTS


def to_percentage(scores: np.ndarray) -> np.ndarray:
    """Converts a 0-1 similarity array to a 0-100 scale."""
    if len(scores) == 0:
        return scores
    return np.clip(scores, 0.0, 1.0) * 100.0


def fuse_scores(tfidf_pct, semantic_pct, bert_pct, weights: dict = None) -> np.ndarray:
    weights = weights or WEIGHTS
    total_weight = sum(weights.values())
    assert abs(total_weight - 1.0) < 1e-6, "WEIGHTS must sum to 1.0"
    final = (
        weights["tfidf"] * np.asarray(tfidf_pct)
        + weights["semantic"] * np.asarray(semantic_pct)
        + weights["bert"] * np.asarray(bert_pct)
    )
    return np.round(final, 2)
