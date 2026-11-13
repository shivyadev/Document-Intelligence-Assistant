from app import db

def delete_document(conn, store, document_id):
    chunk_ids = db.get_document_chunk_ids(conn, document_id)
    db.delete_document_row(conn, document_id)
    store.delete_chunks(chunk_ids)

def delete_chat(conn, store, chat_id):
    for document_id in db.get_exclusive_document_ids(conn, chat_id):
        delete_document(conn, store, document_id)
    db.delete_chat_row(conn, chat_id)

def remove_document_from_chat(conn, store, chat_id, document_id):
    db.detach_document(conn, chat_id, document_id)
    if not db.document_has_chats(conn, document_id):
        delete_document(conn, store, document_id)