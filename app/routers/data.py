from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from app.database.db import get_emails_for_user
from app.database.db import get_connection
from app.auth.dependencies import get_current_user, get_or_create_csrf_token, verify_csrf_token
from app.database.db import (
    get_tasks_for_user,
    get_meetings_for_user
)
from app.database.db import update_task_status
from pydantic import BaseModel

class TaskStatusUpdate(BaseModel):
    status: Literal["pending", "completed"]

router = APIRouter()


@router.get("/tasks")
def get_tasks(user_id: int = Depends(get_current_user)):
    tasks = get_tasks_for_user(user_id)

    return [
        {
            "id": t[0],
            "title": t[1],
            "description": t[2],
            "due_date": t[3],
            "priority": t[4],
            "status": t[5],
        }
        for t in tasks
    ]


@router.patch("/tasks/{task_id}/status")
def patch_task_status(
    task_id: int,
    body: TaskStatusUpdate,
    user_id: int = Depends(get_current_user),
    _csrf: None = Depends(verify_csrf_token)
):
    updated = update_task_status(task_id, body.status, user_id)

    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")

    return { "message": "Task updated successfully" }


@router.get("/meetings")
def get_meetings(user_id: int = Depends(get_current_user)):
    meetings = get_meetings_for_user(user_id)

    return [
        {
            "id": m[0],
            "title": m[1],
            "meeting_date": m[2],
            "start_time": m[3],
            "end_time": m[4],
            "description": m[5],
        }
        for m in meetings
    ]

@router.get("/me")
def get_me(request: Request, user_id: int = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT email_address, created_at, last_sync_time
        FROM users
        WHERE id = %s
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    return {
        "user_id": user_id,
        "email": row[0],
        "created_at": row[1],
        "last_sync_time": row[2],
        "csrf_token": get_or_create_csrf_token(request)
    }

@router.get("/emails")
def get_emails(user_id: int = Depends(get_current_user)):
    emails = get_emails_for_user(user_id)

    return [
        {
            "sender": e[0],
            "subject": e[1],
            "received_at": e[2],
            "summary": e[3],
            "category": e[4],
            "priority": e[5],
        }
        for e in emails
    ]
