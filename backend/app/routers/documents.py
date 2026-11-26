from fastapi import APIRouter, Depends, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from app import db
from app.dependencies import get_conn, get_store
from app.services.extract_document import extract_document, ExtractionError
from app.services.ingest import ingest_document, hash_extracted
from app.services.deletion import remove_document_from_chat

router = APIRouter(prefix="/chats/{chat_id}/documents", tags=["documents"])

@router.get("")
def list_documents(chat_id: int, conn=Depends(get_conn)):
    if not db.get_chat(conn, chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")
    return db.list_chat_documents(conn, chat_id)

@router.post("")
async def upload_document(chat_id: int, file: UploadFile, conn=Depends(get_conn), store=Depends(get_store)):
    if not db.get_chat(conn, chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")

    try:
        extracted = await extract_document(file)
    except ExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    content_hash = hash_extracted(extracted)
    existing = db.find_document_in_chat(conn, chat_id, content_hash)
    if existing:
        return {"document_id": existing["id"], "filename": existing["filename"],
                "status": "ready", "duplicate": True}

    try:
        doc_id = await run_in_threadpool(ingest_document, conn, store, extracted, content_hash)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db.attach_document(conn, chat_id, doc_id)
    return {"document_id": doc_id, "filename": extracted["filename"], "status": "ready", "skipped_pages": extracted.get("skipped_pages", 0)}

@router.delete("/{document_id}")
def remove_document(chat_id: int, document_id: int, conn=Depends(get_conn), store=Depends(get_store)):
    if not db.document_in_chat(conn, chat_id, document_id):
        raise HTTPException(status_code=404, detail="Document not found in this chat")
    remove_document_from_chat(conn, store, chat_id, document_id)
    return {"deleted": document_id}