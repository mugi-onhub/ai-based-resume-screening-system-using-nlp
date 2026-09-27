"""TF-IDF lexical similarity baseline."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def tfidf_similarity(job_text: str, resume_texts: list[str]) -> np.ndarray:
    """Returns cosine similarity of each resume against the job text, in [0, 1]."""
    if not resume_texts:
        return np.array([])
    docs = [job_text] + resume_texts
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), max_features=15000)
    matrix = vectorizer.fit_transform(docs)
    scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    return np.clip(scores, 0.0, 1.0)
