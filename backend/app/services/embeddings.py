import numpy as np
from app.config import EMBEDDING_MODEL_NAME
from fastembed import TextEmbedding

_model = None

def get_model():
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=EMBEDDING_MODEL_NAME)
    return _model


def _normalize(vectors):
    vectors = np.asarray(vectors, dtype="float32")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.clip(norms, 1e-12, None)


def generate_embeddings(chunks):
    if not chunks:
        return []
    texts = [chunk["text"] for chunk in chunks]
    return _normalize(list(get_model().passage_embed(texts)))


def embed_query(question):
    return _normalize(list(get_model().query_embed(question)))[0]