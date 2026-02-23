from app.database.db import (
    get_connection,
    get_unprocessed_emails,
    mark_email_processed,
    insert_task,
    insert_meeting
)

from app.services.agent_service import extract_email_intelligence


def process_unprocessed_emails():
    """
    Fetch all unprocessed emails,
    run LLM extraction,
    store results,
    mark them as processed.
    """

    emails = get_unprocessed_emails()

    if not emails:
        print("No emails to process.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    processed_count = 0


    for email in emails:
        email_id, subject, body, received_at = email

        try:
            result = extract_email_intelligence(subject, body, received_at)

            cursor.execute(
                "DELETE FROM tasks WHERE source_email_id = ?",
                (email_id,)
            )

            cursor.execute(
                "DELETE FROM meetings WHERE source_email_id = ?",
                (email_id,)
            )

            # Update email summary/category/priority
            cursor.execute("""
                UPDATE emails
                SET summary = ?, category = ?, priority = ?
                WHERE id = ?
            """, (
                result["summary"],
                result["category"],
                result["priority"],
                email_id
            ))

            # Insert tasks
            for task in result["tasks"]:
                task["source_email_id"] = email_id
                insert_task(cursor, task)

            # Insert meetings
            for meeting in result["meetings"]:
                meeting["source_email_id"] = email_id
                insert_meeting(cursor, meeting)

            # Mark as processed
            mark_email_processed(cursor, email_id)

            processed_count += 1

        except Exception as e:
            print(f"Failed to process email ID {email_id}: {e}")
            continue

    conn.commit()
    conn.close()

    print(f"{processed_count} emails analyzed.")