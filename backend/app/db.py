import sqlite3
from pathlib import Path
from app.services.chunking import chunk_document

DB_PATH = Path("data/app.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            filename  TEXT NOT NULL,
            file_type TEXT NOT NULL,
            status    TEXT NOT NULL DEFAULT 'processing'
        );

        CREATE TABLE IF NOT EXISTS chunks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            page        INTEGER,
            text        TEXT NOT NULL
        );
        """)

def create_document(conn, filename, file_type):
    cur = conn.execute(
        "INSERT INTO documents (filename, file_type) VALUES (?, ?)", (filename, file_type),
    )
    conn.commit()
    return cur.lastrowid

def insert_chunks(conn, document_id, chunks):
    chunk_ids = []
    for c in chunks:
        meta = c['metadata']
        cur = conn.execute(
            "INSERT INTO chunks (document_id, chunk_index, page, text) VALUES (?, ?, ?, ?)", 
            (document_id, meta['chunk_index'], meta['page_number'], c['text'])
        )
        chunk_ids.append(cur.lastrowid)
    conn.commit()
    return chunk_ids

def set_document_status(conn, document_id, status):
    conn.execute("UPDATE documents SET status = ? WHERE id = ?", (status, document_id))
    conn.commit()

def get_chunks(conn, chunk_ids):
    if not chunk_ids:
        return {}
    marks = ",".join("?" * len(chunk_ids))
    rows = conn.execute(
        f"""SELECT c.id, c.page, c.text, d.filename
            FROM chunks c JOIN documents d ON d.id = c.document_id
            WHERE c.id IN ({marks})""", 
            chunk_ids,
    )

    return {r['id']: dict(r) for r in rows}

if __name__ == "__main__":
       # adjust to your import path

    init_db()
    conn = get_connection()

    pages = [
        {"page": 1, "text": "Cats are small mammals. " * 60},
        {"page": 2, "text": "Dogs are loyal animals. " * 60},
    ]
    chunks = chunk_document(pages, "test.pdf", "pdf")

    doc_id = create_document(conn, "test.pdf", "pdf")
    chunk_ids = insert_chunks(conn, doc_id, chunks)

    print("Document id:", doc_id)
    print("Chunk ids:", chunk_ids)