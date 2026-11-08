import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

from app import db
from app.vector_store import FaissVectorStore
from app.services.ingest import ingest_document
from app.services.chat import answer_question

db.init_db()
conn = db.get_connection()
store = FaissVectorStore()

doc = {
    "filename": "dog_care.txt",
    "file_type": "txt",
    "pages": [{"page": None, "text":
        "Adult dogs need at least two walks a day, about 30 minutes each. "
        "Puppies need shorter but more frequent walks, around 5 minutes per month of age. "
        "Dogs should be fed twice a day with a measured amount of food. " * 5}],
}

doc_id = ingest_document(conn, store, doc)
chat_id = db.create_chat(conn, "Dog chat")
db.attach_document(conn, chat_id, doc_id)

for q in ["How often should I walk my dog?", "What about puppies?"]:
    result = answer_question(conn, store, chat_id, q)
    print("\nQ:", q)
    print("A:", result["answer"])