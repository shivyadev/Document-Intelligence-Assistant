from fastapi import Request
from app import db

def get_conn():
    conn = db.get_connection()
    try:
        yield conn
    finally:
        conn.close()

def get_store(request: Request):
    return request.app.state.store