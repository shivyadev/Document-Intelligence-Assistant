import time
from app import db
from app.vector_store import FaissVectorStore
from app.services.retrieve import retrieve
from app.services.reranker import rerank

CHAT_ID = 1
QUESTIONS = [
    # Clearly answerable questions
    "Who directed Harry Potter and the Goblet of Fire, and who wrote its screenplay?",
    "What were the three tasks in the Triwizard Tournament?",
    "Who was responsible for putting Harry's name into the Goblet of Fire?",
    "Why did Nick Fury reactivate the Avengers Initiative?",
    "How did the Avengers ultimately stop Loki's invasion of Earth?",
    "Which actor replaced Edward Norton as Bruce Banner, and why was the replacement made?",

    # Near-miss questions
    "How many spectators attended the Quidditch World Cup in Harry Potter and the Goblet of Fire?",
    "Exactly how many minutes did Harry spend underwater during the second Triwizard task?",
    "How many individual Chitauri soldiers participated in the invasion of New York?",
    "What was the exact model and manufacturer of the nuclear missile launched towards Manhattan?",

    # Off-topic questions
    "What is the current population of Tokyo, Japan?",
    "How does gradient descent work in training a neural network?",

    # Vague follow-up questions
    "What did he have to save?",
    "Who helped him do that?",
    "What happened to him afterwards?"
]

conn = db.get_connection()
store = FaissVectorStore()

for q in QUESTIONS:
    candidates = retrieve(conn, store, CHAT_ID, q, k=20)

    print(f"\n{"=" * 20} {q}")
    print("FAISS order:")
    for i, c in enumerate(candidates[:5], 1):
        print(f"  {i}. {c['score']:.2f} | p.{c['page']} | {c['text'][:200]!r}")

    t = time.perf_counter()
    reranked = rerank(q, candidates, top_n=5)
    print(f"Reranked order ({time.perf_counter() - t:.2f}s):")
    for i, c in enumerate(reranked, 1):
        print(f"  {i}. {c['rerank_score']:.2f} | p.{c['page']} | {c['text'][:200]!r}")