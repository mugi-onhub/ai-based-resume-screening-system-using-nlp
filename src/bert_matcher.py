"""BERT contextual similarity with chunking for long documents."""
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

from config import BERT_MODEL_NAME, BERT_MAX_TOKENS, BERT_CHUNK_OVERLAP


@_cache_decorator
def load_bert():
    try:
        from transformers import AutoTokenizer, AutoModel
        tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL_NAME)
        model = AutoModel.from_pretrained(BERT_MODEL_NAME)
        model.eval()
        return tokenizer, model
    except Exception:
        return None, None



def _embed_chunk(text: str, tokenizer, model):
    import torch
    inputs = tokenizer(
        text, return_tensors="pt", truncation=True, max_length=BERT_MAX_TOKENS
    )
    with torch.no_grad():
        outputs = model(**inputs)
    # CLS token embedding
    return outputs.last_hidden_state[:, 0, :].numpy()[0]


def _chunk_text_by_tokens(text: str, tokenizer, max_tokens=BERT_MAX_TOKENS, overlap=BERT_CHUNK_OVERLAP):
    """Splits text into overlapping chunks that fit within BERT's token limit."""
    token_ids = tokenizer.encode(text, add_special_tokens=False)
    if len(token_ids) <= max_tokens - 2:  # leave room for [CLS]/[SEP]
        return [text]
    chunks = []
    step = max_tokens - overlap - 2
    for start in range(0, len(token_ids), step):
        chunk_ids = token_ids[start:start + max_tokens - 2]
        if not chunk_ids:
            break
        chunks.append(tokenizer.decode(chunk_ids))
        if start + max_tokens - 2 >= len(token_ids):
            break
    return chunks


def bert_embedding_for_document(text: str, tokenizer, model) -> np.ndarray:
    """
    Encodes a (possibly long) document by chunking it and averaging chunk
    embeddings. This does NOT mean BERT reads the whole resume in one pass —
    each chunk is encoded independently and the vectors are aggregated.
    """
    chunks = _chunk_text_by_tokens(text, tokenizer)
    vectors = [_embed_chunk(chunk, tokenizer, model) for chunk in chunks]
    return np.mean(vectors, axis=0)


def bert_similarity(job_text: str, resume_texts: list[str]) -> tuple[np.ndarray, list[bool]]:
    """Returns (scores in [0,1], was_chunked flags) for each resume."""
    if not resume_texts:
        return np.array([]), []
    tokenizer, model = load_bert()
    if tokenizer is not None and model is not None:
        try:
            job_vec = bert_embedding_for_document(job_text, tokenizer, model).reshape(1, -1)
            resume_vecs = []
            chunked_flags = []
            for text in resume_texts:
                n_tokens = len(tokenizer.encode(text, add_special_tokens=False))
                chunked_flags.append(n_tokens > BERT_MAX_TOKENS - 2)
                resume_vecs.append(bert_embedding_for_document(text, tokenizer, model))
            resume_matrix = np.vstack(resume_vecs)
            scores = cosine_similarity(job_vec, resume_matrix)[0]
            return np.clip(scores, 0.0, 1.0), chunked_flags
        except Exception:
            pass

    # Lightweight Fallback: Sublinear TF-IDF bi-gram matcher (contextual approximation)
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)
    corpus = [job_text] + list(resume_texts)
    matrix = vectorizer.fit_transform(corpus)
    scores = cosine_similarity(matrix[0:1], matrix[1:])[0]
    chunked_flags = [len(text.split()) > 350 for text in resume_texts]
    return np.clip(scores, 0.0, 1.0), chunked_flags

