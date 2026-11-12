from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app import db
from app.dependencies import get_conn, get_store
from app.services.chat import answer_question

router = APIRouter(prefix="/chats/{chat_id}/messages", tags=["messages"])

class Ask(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

@router.post("")
def ask(chat_id: int, body: Ask, conn=Depends(get_conn), store=Depends(get_store)):
    if not db.get_chat(conn, chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")

    try:
        result = answer_question(conn, store, chat_id, body.question.strip())
    except Exception:
        raise HTTPException(status_code=503, detail="The AI service is busy. Please try again.")

    return {
        "question": result['question'],
        "answer": result["answer"],
        "sources": [
            {"filename": c["filename"], "page": c["page"], "text": c["text"], "score": c["score"]}
            for c in result["sources"]
        ],
    }

@router.get("")
def list_messages(chat_id: int, conn=Depends(get_conn)):
    if not db.get_chat(conn, chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")
    return db.get_messages(conn, chat_id)