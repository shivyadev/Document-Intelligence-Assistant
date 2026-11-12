import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import documents, chats, messages
from app import db
from app.vector_store import FaissVectorStore

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    app.state.store = FaissVectorStore()
    yield

app = FastAPI(
    title="Document Intelligence Assistant",
    description="An AI-powered document question-answering API.",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(chats.router)
app.include_router(documents.router)
app.include_router(messages.router)

@app.get("/")
def root():
    return {"message": "Document Intelligence Assistant"}