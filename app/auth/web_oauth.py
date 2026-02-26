from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime
from app.database.db import get_connection

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

WEB_CLIENT_FILE = "credentials_web.json"


def get_gmail_service(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT access_token, refresh_token, token_expiry
        FROM users
        WHERE id = ?
    """, (user_id,))

    row = cursor.fetchone()

    if not row:
        conn.close()
        raise Exception("User not found")

    access_token, refresh_token, token_expiry = row

    if not access_token:
        conn.close()
        raise Exception("User has not authenticated via Web OAuth")

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=_get_client_id(),
        client_secret=_get_client_secret(),
        scopes=SCOPES,
    )

    # Check expiry
    if token_expiry:
        expiry_dt = datetime.strptime(token_expiry, "%Y-%m-%d %H:%M:%S")
        creds.expiry = expiry_dt

    # Auto refresh if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        # Save new token + expiry
        cursor.execute("""
            UPDATE users
            SET access_token = ?, token_expiry = ?
            WHERE id = ?
        """, (
            creds.token,
            creds.expiry.strftime("%Y-%m-%d %H:%M:%S"),
            user_id
        ))

        conn.commit()

    conn.close()

    service = build("gmail", "v1", credentials=creds)

    return service


def _get_client_id():
    import json
    with open(WEB_CLIENT_FILE, "r") as f:
        data = json.load(f)
    return data["web"]["client_id"]


def _get_client_secret():
    import json
    with open(WEB_CLIENT_FILE, "r") as f:
        data = json.load(f)
    return data["web"]["client_secret"]