from pathlib import Path
import pymupdf
from fastapi import HTTPException, UploadFile

class ExtractionError(Exception):
     """Raised when an uploaded file can't be turned into text."""

async def extract_document(file: UploadFile):
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in [".pdf", ".txt"]:
        raise ExtractionError(
            "Only PDF and TXT files are supported."
        )

    content = await file.read()

    if not content:
        raise ExtractionError(
            "The upload file is empty"
        )

    if extension == ".txt":
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError: 
            raise ExtractionError(
                "The TXT file must use UTF-8 encoding."
            )

        return {
            "filename": filename,
            "file_type": "txt",
            "pages": [{
                "page": None,
                "text": text
            }]
        }

    try:

        pdf = pymupdf.open(stream=content, filetype="pdf")
            
        pages = [{
            "page": page.number + 1,
            "text": page.get_text()
        } for page in pdf]

        pdf.close()

    except Exception:

        raise ExtractionError(
            "Could not read the PDF file."
        )

    return {
        "filename": filename,
        "file_type": "pdf",
        "pages": pages
    }