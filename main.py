from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import pickle
from google.auth.transport.requests import Request
import sqlite3
from datetime import datetime
import base64
from app.database.db import init_db, get_or_create_user, insert_email,get_latest_emails,get_connection
from app.services.gmail_service import fetch_recent_emails
from app.auth.gmail_auth import get_gmail_service
init_db()

##--Call Auth--##
service = get_gmail_service()
profile = service.users().getProfile(userId='me').execute()
user_email = profile['emailAddress']
user_id = get_or_create_user(user_email)
print("User ID from DB:", user_id)
print("Authenticated Gmail:", user_email)

##--Fetch Emails--##
emails = fetch_recent_emails(service, max_results=5)
##------------------------#


##--Store Emails--##
conn = get_connection()
cursor = conn.cursor()
for email_data in emails:
    insert_email(cursor, user_id, email_data)
conn.commit()
conn.close()

print(f"{len(emails)} emails processed.")
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