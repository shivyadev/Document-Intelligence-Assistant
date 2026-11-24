import time
from app import db
from app.vector_store import FaissVectorStore
from app.services.retrieve import retrieve
from app.services.reranker import rerank

CHAT_ID = 3
QUESTIONS = [
    "is harry potter part of cars?",
    "who is ironman?",
]

conn = db.get_connection()
store = FaissVectorStore()

for q in QUESTIONS:
    candidates = retrieve(conn, store, CHAT_ID, q, k=20)

    print(f"\n=== {q}")
    print("FAISS order:")
    for i, c in enumerate(candidates[:5], 1):
        print(f"  {i}. {c['score']:.2f} | p.{c['page']} | {c['text'][:200]!r}")

    t = time.perf_counter()
    reranked = rerank(q, candidates, top_n=5)
    print(f"Reranked order ({time.perf_counter() - t:.2f}s):")
    for i, c in enumerate(reranked, 1):
        print(f"  {i}. {c['rerank_score']:.2f} | p.{c['page']} | {c['text'][:200]!r}")