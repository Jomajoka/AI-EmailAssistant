import base64
from email.utils import parsedate_to_datetime
from datetime import timezone


def get_body(payload):
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
    else:
        data = payload['body'].get('data')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
    return None


def fetch_recent_emails(service, max_results=5, query=None):
    
    list_kwargs = {
    "userId": "me",
    "maxResults": max_results
    }
    if query:
        list_kwargs["q"] = query
    results = service.users().messages().list(**list_kwargs).execute()

    messages = results.get('messages', [])

    email_list = []

    for msg in messages:
        message = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        headers = message['payload']['headers']

        subject = sender = date = None

        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'From':
                sender = header['value']
            if header['name'] == 'Date':
                date = header['value']

        ##--Convert Gmail date header to ISO format--##
        parsed_dt = parsedate_to_datetime(date)
        parsed_dt_utc = parsed_dt.astimezone(timezone.utc)
        iso_date = parsed_dt_utc.strftime("%Y-%m-%d %H:%M:%S")
        body = get_body(message['payload'])

        email_data = {
            "gmail_message_id": msg['id'],
            "thread_id": message.get('threadId'),
            "sender": sender,
            "subject": subject,
            "body": body,
            "snippet": message.get('snippet'),
            "received_at": iso_date,
            "has_attachment": 1 if 'parts' in message['payload'] else 0,
            "labels": str(message.get('labelIds'))
        }

        email_list.append(email_data)

    return email_list