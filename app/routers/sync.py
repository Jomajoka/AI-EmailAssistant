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

    print("LAST SYNC:", last_sync)

    # -------- Build query --------
    if last_sync:
        last_sync_dt = (
            datetime.strptime(last_sync, "%Y-%m-%d %H:%M:%S")
            if isinstance(last_sync, str)
            else last_sync
        )

        unix_timestamp = int(last_sync_dt.timestamp()) - 60
        query = f"after:{unix_timestamp}"
    else:
        query = "newer_than:7d"

    # -------- Fetch emails --------
    emails = fetch_recent_emails(service, max_results=20, query=query)
    print("EMAILS FETCHED:", len(emails))

    conn = get_connection()
    cursor = conn.cursor()

    new_count = 0

    try:
        # -------- Insert emails --------
        for email_data in emails:
            insert_email(cursor, user_id, email_data)

            # ✅ count only actual inserts
            if cursor.rowcount > 0:
                new_count += 1

        # -------- Update last sync (ALWAYS move forward) --------
        now_dt = datetime.now(timezone.utc)

        if emails:
            latest_timestamp = max(email["received_at"] for email in emails)
            latest_dt = datetime.strptime(latest_timestamp, "%Y-%m-%d %H:%M:%S")
            latest_dt = latest_dt.replace(tzinfo=timezone.utc)

            # choose the later one (safe)
            new_sync_dt = max(latest_dt, now_dt)
        else:
            new_sync_dt = now_dt

        new_sync_str = new_sync_dt.strftime("%Y-%m-%d %H:%M:%S")
        update_last_sync(cursor, user_id, new_sync_str)

        conn.commit()

    except Exception as e:
        print("SYNC ERROR:", e)
        raise

    finally:
        conn.close()

    return {
        "message": "Sync completed",
        "new_emails_fetched": new_count
    }