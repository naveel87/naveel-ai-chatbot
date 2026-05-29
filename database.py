import sqlite3

conn = sqlite3.connect(
    "chatbot.db",
    check_same_thread=False
)

cursor = conn.cursor()

# Create chats table
cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_message TEXT,

    ai_response TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_sessions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    chat_id TEXT,

    user_message TEXT,

    ai_response TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

conn.commit()
# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,

    password TEXT

)
""")

conn.commit()
def save_chat_session(
    chat_id,
    user_message,
    ai_response
):

    sql = """
    INSERT INTO chat_sessions (
        chat_id,
        user_message,
        ai_response
    )
    VALUES (?, ?, ?)
    """

    cursor.execute(
        sql,
        (
            chat_id,
            user_message,
            ai_response
        )
    )

    conn.commit()
def get_session_messages(chat_id):

    sql = """
    SELECT
        user_message,
        ai_response
    FROM chat_sessions
    WHERE chat_id = ?
    ORDER BY id
    """

    cursor.execute(
        sql,
        (chat_id,)
    )

    return cursor.fetchall()
def save_chat(user_message, ai_response):

    sql = """
    INSERT INTO chats (
        user_message,
        ai_response
    )
    VALUES (?, ?)
    """

    values = (
        user_message,
        ai_response
    )

    cursor.execute(sql, values)

    conn.commit()


def get_chat_history():

    sql = """
    SELECT id, user_message
    FROM chats
    ORDER BY id DESC
    """

    cursor.execute(sql)

    return cursor.fetchall()


import hashlib


def create_user(username, password):

    hashed_password = hashlib.sha256(
        password.encode()
    ).hexdigest()

    sql = """
    INSERT INTO users (
        username,
        password
    )
    VALUES (?, ?)
    """

    values = (
        username,
        hashed_password
    )

    cursor.execute(sql, values)

    conn.commit()


def check_user(username, password):

    hashed_password = hashlib.sha256(
        password.encode()
    ).hexdigest()

    sql = """
    SELECT *
    FROM users
    WHERE username=?
    AND password=?
    """

    values = (
        username,
        hashed_password
    )

    cursor.execute(sql, values)

    return cursor.fetchone()