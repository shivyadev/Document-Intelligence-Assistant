import sqlite3
from pathlib import Path
from app.services.chunking import chunk_document

DB_PATH = Path("data/app.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            filename        TEXT NOT NULL,
            file_type       TEXT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'processing',
            content_hash    TEXT
        );

        CREATE TABLE IF NOT EXISTS chunks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            page        INTEGER,
            text        TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chats (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT,
            created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chat_documents(
            chat_id         INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
            document_id    INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            PRIMARY KEY     (chat_id, document_id)
        );

        CREATE TABLE IF NOT EXISTS messages(
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id     INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
            role        TEXT NOT NULL,
            content     TEXT NOT NULL,
            sources     TEXT,
            created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)

def create_document(conn, filename, file_type, content_hash):
    cur = conn.execute(
        "INSERT INTO documents (filename, file_type, content_hash) VALUES (?, ?, ?)", (filename, file_type, content_hash),
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

def create_chat(conn, title=None):
    cur = conn.execute("INSERT INTO chats (title) VALUES (?)", (title,))
    conn.commit()
    return cur.lastrowid

def get_chat(conn, chat_id):
    return conn.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()

def attach_document(conn, chat_id, document_id):
    conn.execute(
        "INSERT OR IGNORE INTO chat_documents (chat_id, document_id) VALUES (?, ?)",
        (chat_id, document_id)
    )
    conn.commit()

def get_chat_document_ids(conn, chat_id):
    rows = conn.execute(
        """SELECT cd.document_id FROM chat_documents cd 
        JOIN documents d ON d.id = cd.document_id 
        WHERE cd.chat_id = ? AND d.status = 'ready'""",
        (chat_id,),
    )
    return [r['document_id'] for r in rows]

def add_message(conn, chat_id, role, content, sources=None):
    cur = conn.execute(
        "INSERT INTO messages (chat_id, role, content, sources) VALUES (?, ?, ?, ?)", (chat_id, role, content, sources)
    )
    conn.commit()
    return cur.lastrowid

def get_recent_messages(conn, chat_id, limit=6):
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY id DESC LIMIT ?", (chat_id, limit)
    ).fetchall()

    return [dict(r) for r in reversed(rows)]

def get_messages(conn, chat_id):
    rows = conn.execute(
        "SELECT id, role, content, sources, created_at FROM messages WHERE chat_id = ? ORDER BY id",
        (chat_id,),
    )
    return [dict(r) for r in rows]

def list_chats(conn):
    rows = conn.execute("SELECT id, title, created_at FROM chats ORDER BY id DESC")
    return [dict(r) for r in rows]

def list_chat_documents(conn, chat_id):
    rows = conn.execute(
        """SELECT d.id, d.filename, d.file_type, d.status
           FROM chat_documents cd JOIN documents d ON d.id = cd.document_id
           WHERE cd.chat_id = ? ORDER BY d.id""",
        (chat_id,),
    )
    return [dict(r) for r in rows]

def document_in_chat(conn, chat_id, document_id):
    row = conn.execute(
        "SELECT 1 FROM chat_documents WHERE chat_id = ? AND document_id = ?",
        (chat_id, document_id),
    ).fetchone()
    return row is not None

def find_document_in_chat(conn, chat_id, content_hash):
    row = conn.execute(
        """SELECT d.id, d.filename FROM chat_documents cd
           JOIN documents d ON d.id = cd.document_id
           WHERE cd.chat_id = ? AND d.content_hash = ?""",
        (chat_id, content_hash),
    ).fetchone()
    return dict(row) if row else None

def get_document_chunk_ids(conn, document_id):
    rows = conn.execute("SELECT id FROM chunks WHERE document_id = ?", (document_id,))
    return [r["id"] for r in rows]

def get_exclusive_document_ids(conn, chat_id):
    """Documents attached to this chat and to no other chat."""
    rows = conn.execute(
        """SELECT document_id FROM chat_documents
           WHERE chat_id = ?
             AND document_id NOT IN (
                 SELECT document_id FROM chat_documents WHERE chat_id != ?)""",
        (chat_id, chat_id),
    )
    return [r["document_id"] for r in rows]

def detach_document(conn, chat_id, document_id):
    conn.execute(
        "DELETE FROM chat_documents WHERE chat_id = ? AND document_id = ?",
        (chat_id, document_id),
    )
    conn.commit()


def document_has_chats(conn, document_id):
    row = conn.execute(
        "SELECT 1 FROM chat_documents WHERE document_id = ? LIMIT 1", (document_id,)
    ).fetchone()
    return row is not None

def delete_document_row(conn, document_id):
    conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    conn.commit()


def delete_chat_row(conn, chat_id):
    conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()