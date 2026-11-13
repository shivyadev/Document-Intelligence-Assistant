import json
from app import db
from app.services.retrieve import retrieve
from app.services.generation import generate_answer, generate_answer_stream
from app.services.generation import rewrite_query
from app.config import REWRITE_QUERIES, MIN_RELEVANCE_SCORE

def answer_question(conn, store, chat_id, question):
    history = db.get_recent_messages(conn, chat_id)
    search_query = rewrite_query(question, history) if REWRITE_QUERIES else question
    chunks = retrieve(conn, store, chat_id, search_query)
    chunks = [c for c in chunks if c["score"] >= MIN_RELEVANCE_SCORE]

    if not chunks:
        answer = "I couldn't find anything to search. Please upload a document to this chat first."
    else:
        answer = generate_answer(question, chunks, history)

    db.add_message(conn, chat_id, "user", question)
    db.add_message(conn, chat_id, "assistant", answer, sources=json.dumps([c['id'] for c in chunks]))

    return {"question": search_query, "answer": answer, "sources": chunks}

def answer_question_stream(conn, store, chat_id, question):
    history = db.get_recent_messages(conn, chat_id)
    search_query = rewrite_query(question, history) if REWRITE_QUERIES else question
    chunks = retrieve(conn, store, chat_id, search_query)
    chunks = [c for c in chunks if c["score"] >= MIN_RELEVANCE_SCORE]

    yield {"type": "sources", "sources": [
        {"filename": c["filename"], "page": c["page"], "text": c["text"], "score": c["score"]}
        for c in chunks
    ]}

    if not chunks:
        answer = "I couldn't find anything to search. Please upload a document to this chat first."
        yield {"type": "token", "text": answer}
    else:
        parts = []
        try:
            for text in generate_answer_stream(question, chunks, history):
                parts.append(text)
                yield {"type": "token", "text": text}
        except Exception:
            yield {"type": "error", "detail": "The AI service is busy. Please try again."}
            return
        answer = "".join(parts)

    db.add_message(conn, chat_id, "user", question)
    db.add_message(conn, chat_id, "assistant", answer, sources=json.dumps([c['id'] for c in chunks]))

    yield {"type": "done"}