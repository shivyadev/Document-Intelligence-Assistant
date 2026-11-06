from app import db
from app.services.chunking import chunk_document
from app.services.embeddings import generate_embeddings
from app.vector_store import FaissVectorStore

def ingest_document(conn, store, extracted):

    doc_id = db.create_document(conn, extracted['filename'], extracted['file_type'])

    chunks = chunk_document(**extracted)
    chunk_ids = db.insert_chunks(conn, doc_id, chunks)

    vectors = generate_embeddings(chunks)
    store.add(chunk_ids, vectors)
    store.save()

    db.set_document_status(conn, doc_id, "ready")
    return doc_id

if __name__ == "__main__":

    conn = db.get_connection()
    db.init_db()
    store = FaissVectorStore()

    extracted = {
        "filename": "animals.txt",
        "file_type": "txt",
        "pages": [{"page": None, "text": "Cats purr when they are happy. " * 40
                                         + "Dogs need daily walks to stay healthy. " * 40}],
    }

    doc_id = ingest_document(conn, store, extracted)
    print("Document id:", doc_id)
    print("Vectors in FAISS:", store.index.ntotal)
    print("Chunks in SQLite:", conn.execute("SELECT COUNT(*) FROM chunks WHERE document_id = ?", (doc_id,)).fetchone()[0])