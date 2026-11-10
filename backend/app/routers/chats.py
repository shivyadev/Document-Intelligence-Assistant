from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app import db
from app.dependencies import get_conn

router = APIRouter(prefix="/chats", tags=["chats"])

class ChatCreate(BaseModel):
    title: str | None = None

@router.post("")
def create_chat(body: ChatCreate, conn=Depends(get_conn)):
    chat_id = db.create_chat(conn, body.title)
    return {"Chat-id:": chat_id, "title:": body.title}