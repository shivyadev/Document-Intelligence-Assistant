from pathlib import Path
import pymupdf
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in [".pdf", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The upload file is empty"
        )

    if extension == ".txt":
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError: 
            raise HTTPException(
                status_code=400,
                detail="The TXT file must use UTF-8 encoding."
            )

        return {
            "filename": filename,
            "file_type": "txt",
            "text": text
        }


    try:

        pdf = pymupdf.open(stream=content, filetype="pdf")
            
        pages = [{
            "page": page.number + 1,
            "text": page.get_text()
        } for page in pdf]

        pdf.close()

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Could not read the PDF file."
        )

    return {
        "filename": filename,
        "file_type": "pdf",
        "pages": pages
    }

