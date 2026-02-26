from fastapi import Request, HTTPException
from app.database.db import get_connection


def get_current_user(request: Request) -> int:
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Verify user still exists
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="User not found")

    return user_id