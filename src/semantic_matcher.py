"""Sentence-Transformer semantic similarity, with Streamlit caching."""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def _get_cache_decorator():
    try:
        import streamlit as st
        if hasattr(st, "runtime") and st.runtime.exists():
            return st.cache_resource
        return lambda func: func
    except Exception:
        return lambda func: func

_cache_decorator = _get_cache_decorator()

from config import SEMANTIC_MODEL_NAME


@_cache_decorator
def load_semantic_model():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(SEMANTIC_MODEL_NAME)
    except Exception:
        return None


def semantic_similarity(job_text: str, resume_texts: list[str]) -> np.ndarray:
    if not resume_texts:
        return np.array([])
    model = load_semantic_model()
    if model is not None:
        try:
            job_embedding = model.encode([job_text], normalize_embeddings=True)
            resume_embeddings = model.encode(resume_texts, normalize_embeddings=True)
            scores = cosine_similarity(job_embedding, resume_embeddings)[0]
            # normalized embeddings -> cosine in [-1, 1]; clip to [0, 1] for display consistency
            return np.clip(scores, 0.0, 1.0)
        except Exception:
            pass

    # Lightweight Fallback: Character n-gram TF-IDF for sub-word semantic approximation
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(ngram_range=(2, 4), analyzer="char_wb", min_df=1)
    corpus = [job_text] + list(resume_texts)
    matrix = vectorizer.fit_transform(corpus)
    scores = cosine_similarity(matrix[0:1], matrix[1:])[0]
    return np.clip(scores, 0.0, 1.0)

