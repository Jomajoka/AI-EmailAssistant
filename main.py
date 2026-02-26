from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from datetime import datetime, timezone
import pickle
from google.auth.transport.requests import Request
import sqlite3
from datetime import datetime
import base64
from app.database.db import (
    init_db,
    get_or_create_user,
    insert_email,
    get_latest_emails,
    get_last_sync,
    update_last_sync,
    get_connection
)
from app.services.gmail_service import fetch_recent_emails
from app.auth.gmail_auth import get_gmail_service
from app.services.agent_service import extract_email_intelligence
from app.services.processing_service import process_unprocessed_emails
init_db()


##--Call Auth--##
service = get_gmail_service()
profile = service.users().getProfile(userId='me').execute()
user_email = profile['emailAddress']
user_id = get_or_create_user(user_email)
last_sync = get_last_sync(user_id)
print("Last sync:", last_sync)
print("User ID from DB:", user_id)
print("Authenticated Gmail:", user_email)

##--Fetch Emails--##
if last_sync:
    # Convert stored ISO string back to datetime
    last_sync_dt = datetime.strptime(last_sync, "%Y-%m-%d %H:%M:%S")
    last_sync_dt = last_sync_dt.replace(tzinfo=timezone.utc)

    # Convert to Unix timestamp
    unix_timestamp = int(last_sync_dt.timestamp())

    query = f"after:{unix_timestamp}"
    print("Using query:", query)

    emails = fetch_recent_emails(service, max_results=20, query=query)
else:
    print("First run: Bootstrapping emails")
    emails = fetch_recent_emails(service, max_results=10)
##------------------------#

#process_unprocessed_emails()

##--Store Emails--##
conn = get_connection()
cursor = conn.cursor()

for email_data in emails:
    insert_email(cursor, user_id, email_data)
##-----Updating last_sync_time-----##
if emails:
    latest_timestamp = max(email["received_at"] for email in emails)

    if not last_sync or latest_timestamp > last_sync:
        update_last_sync(cursor, user_id, latest_timestamp)
        print("Updated last_sync_time to:", latest_timestamp)
    else:
        print("No newer emails found. Sync unchanged.")
else:
    print("No new emails returned by Gmail.")
##-------------------------------##

conn.commit()
conn.close()
##----------------------------------------##


##--Display Emails (just for testing sake)--##
print("\nLatest 5 Emails From Database:")
latest = get_latest_emails(user_id, limit=5)
for i, row in enumerate(latest, start=1):
    sender, subject, received_at, body = row
    print(f"\nEmail {i}")
    print("From:", sender)
    print("Subject:", subject)
    print("Date:", received_at)
    print("Body:", body)
    print("--------------------------------------------")
##----------------------------------------##

conn = sqlite3.connect("email_assistant.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())
cursor.execute("SELECT COUNT(*) FROM emails")
print("Total emails stored:", cursor.fetchone()[0])
conn.close()