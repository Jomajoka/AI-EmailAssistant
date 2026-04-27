from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime
from app.database.db import get_connection
import os
import json

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

WEB_CLIENT_FILE = "credentials_web.json"


def _get_google_config():
    credentials_json = os.getenv("GOOGLE_CREDENTIALS")

    if credentials_json:
        return json.loads(credentials_json)

    # fallback for local development
    with open("credentials_web.json", "r") as f:
        return json.load(f)



def get_gmail_service(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT access_token, refresh_token, token_expiry
        FROM users
        WHERE id = %s
    """, (user_id,))

    row = cursor.fetchone()

    if not row:
        conn.close()
        raise Exception("User not found")

    access_token, refresh_token, token_expiry = row

    if not access_token:
        conn.close()
        raise Exception("User has not authenticated via Web OAuth")

    config = _get_google_config()

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config["web"]["client_id"],
        client_secret=config["web"]["client_secret"],
        scopes=SCOPES,
    )

    if not refresh_token:
        raise Exception("No refresh token available. User must re-authenticate.")
    
    # Handle expiry
    if token_expiry:
        # Postgres may return datetime directly
        if isinstance(token_expiry, str):
            expiry_dt = datetime.strptime(token_expiry, "%Y-%m-%d %H:%M:%S")
        else:
            expiry_dt = token_expiry

        creds.expiry = expiry_dt

    # Auto refresh if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        cursor.execute("""
            UPDATE users
            SET access_token = %s, token_expiry = %s
            WHERE id = %s
        """, (
            creds.token,
            creds.expiry,
            user_id
        ))

        conn.commit()

    conn.close()

    service = build("gmail", "v1", credentials=creds)

    return service


def _get_client_id():
    return _get_google_config()["web"]["client_id"]


def _get_client_secret():
    return _get_google_config()["web"]["client_secret"]