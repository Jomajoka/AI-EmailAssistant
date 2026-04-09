from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from app.auth.dependencies import get_current_user
from app.auth.web_oauth import get_gmail_service
from app.database.db import (
    get_connection,
    insert_email,
    get_last_sync,
    update_last_sync
)
from app.services.gmail_service import fetch_recent_emails

router = APIRouter()


@router.get("/sync")
def sync_emails(user_id: int = Depends(get_current_user)):
    service = get_gmail_service(user_id)
    last_sync = get_last_sync(user_id)

    if last_sync:
        last_sync_dt = datetime.strptime(last_sync, "%Y-%m-%d %H:%M:%S")
        last_sync_dt = last_sync_dt.replace(tzinfo=timezone.utc)
        unix_timestamp = int(last_sync_dt.timestamp())
        query = f"after:{unix_timestamp}"
        emails = fetch_recent_emails(service, max_results=20, query=query)
    else:
        emails = fetch_recent_emails(service, max_results=10)

    now = datetime.now(timezone.utc)
    update_last_sync(user_id, now.strftime("%Y-%m-%d %H:%M:%S"))

    conn = get_connection()
    cursor = conn.cursor()

    new_count = 0

    for email_data in emails:
        insert_email(cursor, user_id, email_data)
        new_count += 1

    if emails:
        latest_timestamp = max(email["received_at"] for email in emails)

        if not last_sync or latest_timestamp > last_sync:
            update_last_sync(cursor, user_id, latest_timestamp)

    conn.commit()
    conn.close()

    return {
        "message": "Sync completed",
        "new_emails_fetched": new_count
    }