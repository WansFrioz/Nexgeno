# # utils/redis_handler.py

# import redis
# import json
# import sqlite3
# from datetime import datetime

# # Connect or create the database
# conn = sqlite3.connect('chat_history.db', check_same_thread=False)
# cursor = conn.cursor()



# # redis_client = redis.Redis(
# #     host='coherent-antelope-22626.upstash.io',
# #     port=6379,
# #     ssl_cert_reqs="none",
# #     password='AVhiAAIjcDFjNjk5YjFhYjIzM2U0YWQxYmEyNmQzYjlhMTEyZmUyMHAxMA',
# #     ssl=True,
# #     decode_responses=True

# # )

# redis_client = redis.Redis(
#     host='localhost',   # or 127.0.0.1
#     port=6379,
#     db=0,               # default database index
#     decode_responses=True
# )

# # Function to save chat to DB
# def save_chat_to_db(user_id, message, role):
#     cursor.execute('''
#         INSERT INTO chat_history (user_id, message, role)
#         VALUES (?, ?, ?)
#     ''', (user_id, message, role))
#     conn.commit()


# def save_chat_history(user_id, message, role="user"):
#     key = f"chat_history:{user_id}"
#     history = redis_client.get(key)
#     history = json.loads(history) if history else []

#     history.append({"role": role, "message": message})
#     history = history[-50:]  # Keep only last 50 messages in Redis
#     redis_client.set(key, json.dumps(history))

#     # Also store in SQLite DB
#     save_chat_to_db(user_id, message, role)


# def load_chat_history(user_id):
#     key = f"chat_history:{user_id}"
#     history = redis_client.get(key)
#     return json.loads(history) if history else []



import redis
import json
import sqlite3
from datetime import datetime

# Connect or create the database
conn = sqlite3.connect('chat_history.db', check_same_thread=False)
cursor = conn.cursor()

# ✅ Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        message TEXT NOT NULL,
        role TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# ✅ Create model_usage table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS model_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        model TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Redis client (local or production)
redis_client = redis.Redis(
    host='localhost',   # or your remote Redis config
    port=6379,
    db=0,
    decode_responses=True
)

def log_model_usage(user_id, model):
    cursor.execute('''
        INSERT INTO model_usage (user_id, model)
        VALUES (?, ?)
    ''', (user_id, model))
    conn.commit()


# Save chat to SQLite
def save_chat_to_db(user_id, message, role):
    cursor.execute('''
        INSERT INTO chat_history (user_id, message, role)
        VALUES (?, ?, ?)
    ''', (user_id, message, role))
    conn.commit()

# Save chat to Redis + SQLite
def save_chat_history(user_id, message, role="user"):
    key = f"chat_history:{user_id}"
    history = redis_client.get(key)
    history = json.loads(history) if history else []

    history.append({"role": role, "message": message})
    history = history[-50:]  # Keep only last 50 messages in Redis
    redis_client.set(key, json.dumps(history))

    # Also store permanently in SQLite DB
    save_chat_to_db(user_id, message, role)

# Optional: Load recent chat from Redis (not permanent)
def load_chat_history(user_id):
    key = f"chat_history:{user_id}"
    history = redis_client.get(key)
    return json.loads(history) if history else []
