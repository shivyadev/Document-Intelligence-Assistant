from pathlib import Path
import pymupdf
from fastapi import UploadFile
from app.config import MAX_EMPTY_PAGE_RATIO, MIN_CHARS_PER_PAGE

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
        if pdf.needs_pass:
            pdf.close()
            raise ExtractionError("This PDF is password protected.")

        pages = [{
            "page": page.number + 1,
            "text": page.get_text()
        } for page in pdf]

        pdf.close()

    except ExtractionError:
        raise
    except Exception:
        raise ExtractionError("Could not read the PDF file.")

    if not pages:
        raise ExtractionError("The PDF has no pages.")

    empty_pages = sum(1 for p in pages if len(p["text"].strip()) < MIN_CHARS_PER_PAGE)
    if empty_pages / len(pages) >= MAX_EMPTY_PAGE_RATIO:
        raise ExtractionError(
            "This PDF looks like a scanned document (no readable text). "
            "Scanned files are not supported yet."
        )

    return {
        "filename": filename,
        "file_type": "pdf",
        "pages": pages,
        "skipped_pages": empty_pages,
    }