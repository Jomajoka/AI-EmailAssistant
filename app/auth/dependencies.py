import secrets

from fastapi import Header, HTTPException, Request
from app.database.db import get_connection


CSRF_SESSION_KEY = "csrf_token"


def get_or_create_csrf_token(request: Request) -> str:
    token = request.session.get(CSRF_SESSION_KEY)

    if not token:
        token = secrets.token_urlsafe(32)
        request.session[CSRF_SESSION_KEY] = token

    return token


def get_current_user(request: Request) -> int:
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Verify user still exists
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()

    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="User not found")

    return user_id


def verify_csrf_token(
    request: Request,
    csrf_token: str | None = Header(default=None, alias="X-CSRF-Token")
) -> None:
    expected_token = request.session.get(CSRF_SESSION_KEY)

    if not expected_token or not csrf_token or not secrets.compare_digest(expected_token, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
