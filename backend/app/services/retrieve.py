from app import db
from app.services.embeddings import embed_query
from app.vector_store import FaissVectorStore

def retrieve(conn, store, chat_id, question, k=5):
    doc_ids = db.get_chat_document_ids(conn, chat_id)
    if not doc_ids:
        return []
    hits = store.search(embed_query(question), k=k, document_ids=doc_ids)
    rows = db.get_chunks(conn, [chunk_id for chunk_id, _ in hits])
    return [{**rows[chunk_id], "score": score} for chunk_id, score in hits if chunk_id in rows]
