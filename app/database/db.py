import sqlite3
DB_NAME = "email_assistant.db"


def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_address TEXT UNIQUE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_sync_time DATETIME
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        gmail_message_id TEXT NOT NULL,
        thread_id TEXT,
        sender TEXT,
        subject TEXT,
        body TEXT,
        snippet TEXT,
        received_at DATETIME,
        has_attachment INTEGER DEFAULT 0,
        labels TEXT,
        category TEXT,
        priority_score REAL,
        processed INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, gmail_message_id)
    )
    """)

    conn.commit()
    conn.close()

def get_or_create_user(email_address):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users (email_address)
    VALUES (?)
    """, (email_address,))

    conn.commit()

    cursor.execute("""
    SELECT id FROM users WHERE email_address = ?
    """, (email_address,))

    user_id = cursor.fetchone()[0]

    conn.close()
    return user_id

def insert_email(cursor,user_id, email_data):
    cursor.execute("""
    INSERT OR IGNORE INTO emails (
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
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    WHERE user_id = ?
    ORDER BY received_at DESC
    LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

def get_last_sync(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT last_sync_time
    FROM users
    WHERE id = ?
    """, (user_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    return None


def update_last_sync(user_id, timestamp):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET last_sync_time = ?
    WHERE id = ?
    """, (timestamp, user_id))

    conn.commit()
    conn.close()

