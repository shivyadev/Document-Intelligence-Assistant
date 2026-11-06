from app import db
from app.services.embeddings import embed_query
from app.vector_store import FaissVectorStore

def retrieve(conn, store, question, k=5):
    hits = store.search(embed_query(question), k=k)
    rows = db.get_chunks(conn, [chunk_id for chunk_id, _ in hits])
    return [{**rows[chunk_id], "score": score} for chunk_id, score in hits if chunk_id in rows]

if __name__ == "__main__":

    conn = db.get_connection()
    store = FaissVectorStore()

    for r in retrieve(conn, store, "How often should I walk my dog?", k=3):
        print(round(r["score"], 3), r["filename"], "page", r["page"])
        print("   ", r["text"][:80])