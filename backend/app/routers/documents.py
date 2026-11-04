from fastapi import APIRouter, File, HTTPException, UploadFile
from app.services.extract_document import extract_document
from app.services.chunking import chunk_document

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    extracted_document = await extract_document(file)

    chunked_document = chunk_document(**extracted_document)

    return chunked_document


