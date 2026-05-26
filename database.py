from dotenv import load_dotenv
import os

import mysql.connector
import hashlib
conn = mysql.connector.connect(
    host="localhost",
    user="sailadmin",
    password=os.getenv("MYSQL_PASSWORD"),
    database="ai_chatbot"
)

cursor = conn.cursor()
load_dotenv()

def save_chat(user_message, ai_response):

    sql = """
    INSERT INTO chats (
        user_message,
        ai_response
    )
    VALUES (%s, %s)
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

def create_user(username, password):

    hashed_password = hashlib.sha256(
        password.encode()
    ).hexdigest()

    sql = """
    INSERT INTO users (
        username,
        password
    )
    VALUES (%s, %s)
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
    WHERE username=%s
    AND password=%s
    """

    values = (
        username,
        hashed_password
    )

    cursor.execute(sql, values)

    return cursor.fetchone()