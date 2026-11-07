from app import db
from app.services.chunking import chunk_document
from app.services.embeddings import generate_embeddings
from app.vector_store import FaissVectorStore
from app.services.retrieve import retrieve

def ingest_document(conn, store, extracted):

    doc_id = db.create_document(conn, extracted['filename'], extracted['file_type'])

    chunks = chunk_document(**extracted)
    chunk_ids = db.insert_chunks(conn, doc_id, chunks)

    vectors = generate_embeddings(chunks)
    store.add(chunk_ids, [doc_id] * len(chunk_ids), vectors)
    store.save()

    db.set_document_status(conn, doc_id, "ready")
    return doc_id

#  Uncomment to test the ingestion pipeline
# if __name__ == "__main__":

#     conn = db.get_connection()
#     db.init_db()
#     store = FaissVectorStore()

#     # 1. Two fake documents, in the same shape extract_document() returns
#     animals = {
#         "filename": "animals.txt",
#         "file_type": "txt",
#         "pages": [{"page": None, "text": "Dogs need daily walks to stay healthy. " * 40}],
#     }
#     finance = {
#         "filename": "finance.txt",
#         "file_type": "txt",
#         "pages": [{"page": None, "text": "The stock market fell as interest rates rose. " * 40}],
#     }

#     animals_id = ingest_document(conn, store, animals)
#     finance_id = ingest_document(conn, store, finance)

#     # 2. Create two test chats
#     chat1 = db.create_chat(conn, "Animals chat")
#     chat2 = db.create_chat(conn, "Finance chat")

#     # 3. Attach one document to each chat
#     db.attach_document(conn, chat1, animals_id)
#     db.attach_document(conn, chat2, finance_id)

#     # 4. Ask the same question in both chats
#     question = "How often should I walk my dog?"
#     for chat_id in (chat1, chat2):
#         print(f"\n--- Chat {chat_id} ---")
#         results = retrieve(conn, store, chat_id, question, k=3)
#         for r in results:
#             print(round(r["score"], 3), r["filename"], "|", r["text"][:50])