import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.database.db import get_connection  # noqa: E402
from app.security.encryption import encrypt_value, is_encrypted, validate_encryption_config  # noqa: E402


EMAIL_FIELDS = ("sender", "subject", "body", "snippet")
USER_FIELDS = ("access_token", "refresh_token")


def _encrypt_row_values(row, fields):
    row_id = row[0]
    values = dict(zip(fields, row[1:]))
    encrypted_values = {field: encrypt_value(value) for field, value in values.items()}
    changed = any(values[field] != encrypted_values[field] for field in fields)
    already_encrypted = all(
        value is None or is_encrypted(value)
        for value in values.values()
    )
    return row_id, encrypted_values, changed, already_encrypted


def migrate_emails(cursor, dry_run):
    cursor.execute("""
        SELECT id, sender, subject, body, snippet
        FROM emails
    """)

    rows = cursor.fetchall()
    changed_count = 0
    encrypted_count = 0

    for row in rows:
        email_id, values, changed, already_encrypted = _encrypt_row_values(row, EMAIL_FIELDS)

        if already_encrypted:
            encrypted_count += 1

        if not changed:
            continue

        changed_count += 1

        if dry_run:
            continue

        cursor.execute("""
            UPDATE emails
            SET sender = %s, subject = %s, body = %s, snippet = %s
            WHERE id = %s
        """, (
            values["sender"],
            values["subject"],
            values["body"],
            values["snippet"],
            email_id,
        ))

    return len(rows), changed_count, encrypted_count


def migrate_users(cursor, dry_run):
    cursor.execute("""
        SELECT id, access_token, refresh_token
        FROM users
    """)

    rows = cursor.fetchall()
    changed_count = 0
    encrypted_count = 0

    for row in rows:
        user_id, values, changed, already_encrypted = _encrypt_row_values(row, USER_FIELDS)

        if already_encrypted:
            encrypted_count += 1

        if not changed:
            continue

        changed_count += 1

        if dry_run:
            continue

        cursor.execute("""
            UPDATE users
            SET access_token = %s, refresh_token = %s
            WHERE id = %s
        """, (
            values["access_token"],
            values["refresh_token"],
            user_id,
        ))

    return len(rows), changed_count, encrypted_count


def main():
    parser = argparse.ArgumentParser(description="Encrypt existing plaintext email and OAuth token data.")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without updating the database.")
    args = parser.parse_args()

    load_dotenv(ROOT_DIR / ".env")
    validate_encryption_config()

    conn = get_connection()
    cursor = conn.cursor()

    try:
        email_total, email_changed, email_encrypted = migrate_emails(cursor, args.dry_run)
        user_total, user_changed, user_encrypted = migrate_users(cursor, args.dry_run)

        if args.dry_run:
            conn.rollback()
        else:
            conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    action = "would encrypt" if args.dry_run else "encrypted"
    print(f"Emails: scanned={email_total}, already_encrypted={email_encrypted}, {action}={email_changed}")
    print(f"Users: scanned={user_total}, already_encrypted={user_encrypted}, {action}={user_changed}")


if __name__ == "__main__":
    main()
