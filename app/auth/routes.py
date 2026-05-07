from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from app.database.db import get_connection
from app.security.encryption import encrypt_value
import os
import json
import tempfile

router = APIRouter()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
REDIRECT_URI = os.getenv("REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

def get_flow(state=None):
    credentials_json = os.getenv("GOOGLE_CREDENTIALS")
    
    if credentials_json:
        # Production — load from environment variable
        credentials_dict = json.loads(credentials_json)
        if state:
            return Flow.from_client_config(
                credentials_dict,
                scopes=SCOPES,
                state=state,
                redirect_uri=REDIRECT_URI,
            )
        return Flow.from_client_config(
            credentials_dict,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
        )
    else:
        # Local development — load from file
        if state:
            return Flow.from_client_secrets_file(
                "credentials_web.json",
                scopes=SCOPES,
                state=state,
                redirect_uri=REDIRECT_URI,
            )
        return Flow.from_client_secrets_file(
            "credentials_web.json",
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
        )

@router.get("/login")
def login(request: Request):
    flow = get_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    request.session["oauth_state"] = state
    print("Stored state:", state)
    print("Using REDIRECT_URI:", REDIRECT_URI)
    return RedirectResponse(authorization_url)


@router.get("/auth/callback")
def auth_callback(request: Request, code: str, state: str):
    print("Callback route triggered")
    stored_state = request.session.get("oauth_state")

    print("Stored state:", stored_state)
    print("Returned state:", state)

    if not stored_state or stored_state != state:
        return {"error": "Invalid OAuth state"}

    flow = get_flow(state=state)
    flow.fetch_token(code=code)
    credentials = flow.credentials

    service = build("gmail", "v1", credentials=credentials)
    profile = service.users().getProfile(userId="me").execute()

    email = profile["emailAddress"]
    google_id = email
    access_token = encrypt_value(credentials.token)
    refresh_token = encrypt_value(credentials.refresh_token) if credentials.refresh_token else None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (
            email_address,
            google_id,
            access_token,
            refresh_token,
            token_expiry
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT(email_address) DO UPDATE SET
            access_token = EXCLUDED.access_token,
            refresh_token = COALESCE(EXCLUDED.refresh_token, users.refresh_token),
            token_expiry = EXCLUDED.token_expiry
    """, (
        email,
        google_id,
        access_token,
        refresh_token,
        credentials.expiry.strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()

    cursor.execute(
        "SELECT id FROM users WHERE email_address = %s",
        (email,)
    )

    user_id = cursor.fetchone()[0]
    conn.close()

    request.session["user_id"] = user_id
    return RedirectResponse(FRONTEND_URL)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return JSONResponse({"message": "Logged out successfully"})
