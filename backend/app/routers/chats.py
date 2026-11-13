from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app import db
from app.dependencies import get_conn, get_store
from app.services.deletion import delete_chat

router = APIRouter(prefix="/chats", tags=["chats"])

class ChatCreate(BaseModel):
    title: str | None = None

@router.get("")
def list_chats(conn=Depends(get_conn)):
    return db.list_chats(conn)

@router.post("")
def create_chat(body: ChatCreate, conn=Depends(get_conn)):
    chat_id = db.create_chat(conn, body.title)
    return {"Chat-id:": chat_id, "title:": body.title}

@router.delete("/{chat_id}")
def remove_chat(chat_id: int, conn=Depends(get_conn), store=Depends(get_store)):
    if not db.get_chat(conn, chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")
    delete_chat(conn, store, chat_id)
    return {"deleted": chat_id}