from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime
from app.database.db import get_connection
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse

router = APIRouter()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# IMPORTANT: This must match Google Cloud redirect URI
REDIRECT_URI = "http://localhost:8000/auth/callback"

WEB_CLIENT_FILE = "credentials_web.json"


@router.get("/login")
def login(request: Request):

    if request.session.get("oauth_state"):
        print("State already exists, not regenerating")
    else:
        print("Generating new OAuth state")

    flow = Flow.from_client_secrets_file(
        WEB_CLIENT_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    request.session["oauth_state"] = state
    print("Stored state:", state)

    return RedirectResponse(authorization_url)


@router.get("/auth/callback")
def auth_callback(request: Request, code: str, state: str):
    print("Callback route triggered")
    stored_state = request.session.get("oauth_state")

    print("Stored state:", stored_state)
    print("Returned state:", state)

    if not stored_state or stored_state != state:
        return {"error": "Invalid OAuth state"}

    flow = Flow.from_client_secrets_file(
        WEB_CLIENT_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI,
    )

    flow.fetch_token(code=code)
    credentials = flow.credentials

    service = build("gmail", "v1", credentials=credentials)
    profile = service.users().getProfile(userId="me").execute()

    email = profile["emailAddress"]
    google_id = email

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
            refresh_token = EXCLUDED.refresh_token,
            token_expiry = EXCLUDED.token_expiry
    """, (
        email,
        google_id,
        credentials.token,
        credentials.refresh_token or None,
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
    return RedirectResponse("http://localhost:3000")

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return JSONResponse({"message": "Logged out successfully"})