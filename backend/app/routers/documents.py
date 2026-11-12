from fastapi import APIRouter, Depends, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool
from app.dependencies import get_conn, get_store
from app.services.extract_document import extract_document
from app.services.ingest import ingest_document
from app import db

router = APIRouter(prefix="/chats/{chat_id}/documents", tags=["documents"])

@router.post("")
async def upload_document(chat_id: int, file: UploadFile, conn=Depends(get_conn), store=Depends(get_store)):
    if not db.get_chat(conn, chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")

    extracted = await extract_document(file)

    try:
        doc_id = await run_in_threadpool(ingest_document, conn, store, extracted)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db.attach_document(conn, chat_id, doc_id)
    return {"document_id": doc_id, "filename": extracted["filename"], "status": "ready"}