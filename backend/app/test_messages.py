from app import db

db.init_db()
conn = db.get_connection()

chat_id = db.create_chat(conn, "Message test")

db.add_message(conn, chat_id, "user", "How often should I walk my dog?")
db.add_message(conn, chat_id, "assistant", "Daily walks are recommended.")
db.add_message(conn, chat_id, "user", "What about puppies?")

for m in db.get_recent_messages(conn, chat_id):
    print(m["role"], ":", m["content"])

print("--- last 2 only ---")
for m in db.get_recent_messages(conn, chat_id, limit=2):
    print(m["role"], ":", m["content"])