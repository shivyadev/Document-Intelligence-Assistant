from fastapi import FastAPI
from app.routers import documents

app = FastAPI(
    title="Document Intelligence Assistant",
    description="An AI-powered document question-answering API.",
    version="0.1.0"
)

app.include_router(documents.router)

@app.get("/")
def root():
    return {"message": "Document Intelligence Assistant"}