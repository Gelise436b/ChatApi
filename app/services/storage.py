
import sqlite3

DB_PATH = "chat_history.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT, --主键 自增
        conversation_id TEXT NOT NULL, --属于哪个会话
        role TEXT NOT NULL, --user/assistant   
        content TEXT NOT NULL, --消息正文
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP --自动填时间   
    )
""")

conn.commit()
conn.close()

def save_message(conversation_id : str, role : str,content : str)-> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
    "INSERT INTO messages (conversation_id,role,content) VALUES (?,?,?)",
    (conversation_id,role,content),
    )
    conn.commit()
    conn.close()

def get_history(conversation_id : str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT role,content FROM messages WHERE conversation_id = ? ORDER BY id",
        (conversation_id,),
    ).fetchall()
    conn.close()
    return [{"role":role,"content":content} for role,content in rows]
