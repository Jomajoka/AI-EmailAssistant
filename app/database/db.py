import sqlite3
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()


'''def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )'''

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email_address TEXT UNIQUE NOT NULL,
        google_id TEXT UNIQUE,
        access_token TEXT,
        refresh_token TEXT,
        token_expiry TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_sync_time TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        gmail_message_id TEXT NOT NULL,
        thread_id TEXT,
        sender TEXT,
        subject TEXT,
        body TEXT,
        snippet TEXT,
        received_at TIMESTAMP,
        has_attachment BOOLEAN DEFAULT FALSE,
        labels TEXT,
        summary TEXT,
        category TEXT,
        priority TEXT,
        processed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, gmail_message_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        priority TEXT,
        status TEXT DEFAULT 'pending',
        source_email_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meetings (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        meeting_date TEXT NOT NULL,
        start_time TEXT,
        end_time TEXT,
        description TEXT,
        source_email_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def get_or_create_user(email_address):
    conn = get_connection()
    cursor = conn.cursor()
    # Insert if not exists
    cursor.execute("""
    INSERT INTO users (email_address)
    VALUES (%s)
    ON CONFLICT (email_address) DO NOTHING
    """, (email_address,))
    conn.commit()
    # Fetch user id
    cursor.execute("""
    SELECT id FROM users WHERE email_address = %s
    """, (email_address,))

    user_id = cursor.fetchone()[0]

    conn.close()
    return user_id


def insert_email(cursor, user_id, email_data):
    cursor.execute("""
    INSERT INTO emails (
        user_id,
        gmail_message_id,
        thread_id,
        sender,
        subject,
        body,
        snippet,
        received_at,
        has_attachment,
        labels
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (user_id, gmail_message_id) DO NOTHING
    """, (
        user_id,
        email_data["gmail_message_id"],
        email_data["thread_id"],
        email_data["sender"],
        email_data["subject"],
        email_data["body"],
        email_data["snippet"],
        email_data["received_at"],
        email_data["has_attachment"],
        email_data["labels"]
    ))


def get_latest_emails(user_id, limit=5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT sender, subject, received_at, body
    FROM emails
    WHERE user_id = %s
    ORDER BY received_at DESC
    LIMIT %s
    """, (user_id, limit))

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_last_sync(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT last_sync_time
    FROM users
    WHERE id = %s
    """, (user_id,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


def update_last_sync(cursor, user_id, timestamp):
    cursor.execute("""
    UPDATE users
    SET last_sync_time = %s
    WHERE id = %s
    """, (timestamp, user_id))


def get_unprocessed_emails(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, subject, body, received_at, sender
    FROM emails
    WHERE processed = FALSE AND user_id = %s
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def mark_email_processed(cursor, email_id):
    cursor.execute("""
    UPDATE emails
    SET processed = TRUE
    WHERE id = %s
    """, (email_id,))


def insert_task(cursor, task):
    cursor.execute("""
    INSERT INTO tasks (
        title,
        description,
        due_date,
        priority,
        source_email_id
    )
    VALUES (%s, %s, %s, %s, %s)
    """, (
        task["title"],
        task.get("description"),
        task.get("due_date"),
        task.get("priority"),
        task.get("source_email_id")
    ))  


def insert_meeting(cursor, meeting):
    cursor.execute("""
    INSERT INTO meetings (
        title,
        meeting_date,
        start_time,
        end_time,
        description,
        source_email_id
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        meeting["title"],
        meeting["meeting_date"],
        meeting.get("start_time"),
        meeting.get("end_time"),
        meeting.get("description"),
        meeting.get("source_email_id")
    ))


def get_tasks_for_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.id, t.title, t.description, t.due_date, t.priority, t.status
        FROM tasks t
        JOIN emails e ON t.source_email_id = e.id
        WHERE e.user_id = %s
        ORDER BY t.created_at DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_meetings_for_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.id, m.title, m.meeting_date, m.start_time, m.end_time, m.description
        FROM meetings m
        JOIN emails e ON m.source_email_id = e.id
        WHERE e.user_id = %s
        ORDER BY m.meeting_date ASC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def update_task_status(task_id: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET status = %s
        WHERE id = %s
    """, (status, task_id))

    conn.commit()
    conn.close()


def get_emails_for_user(user_id, limit=20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sender, subject, received_at, summary, category, priority
        FROM emails
        WHERE user_id = %s
        ORDER BY received_at DESC
        LIMIT %s
    """, (user_id, limit))

    rows = cursor.fetchall()
    conn.close()
    return rows