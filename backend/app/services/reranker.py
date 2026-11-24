from fastembed.rerank.cross_encoder import TextCrossEncoder
from app.config import RERANKER_MODEL_NAME

_model = None

def get_reranker():
    global _model
    if _model is None:
        _model = TextCrossEncoder(model_name=RERANKER_MODEL_NAME)
    return _model


def rerank(query, chunks, top_n=5):
    if not chunks:
        return []
    scores = list(get_reranker().rerank(query, [c["text"] for c in chunks]))
    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = float(score)
    return sorted(chunks, key=lambda c: c["rerank_score"], reverse=True)[:top_n]