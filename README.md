# 📬 Email Intelligence Assistant

An AI-powered Email Intelligence backend that:

- Connects to Gmail
- Syncs emails incrementally
- Uses an LLM to extract:
  - Summaries
  - Categories
  - Priorities
  - Actionable tasks
  - Scheduled meetings
- Exposes structured productivity data via REST APIs

---

# 🚀 Features

## 🔐 Authentication

- Google Web OAuth 2.0
- Session-based authentication (signed cookies)
- OAuth tokens stored securely in SQLite
- Automatic access token refresh
- Logout support
- Multi-user capable architecture

Desktop OAuth (token.pickle) is preserved for development/testing.

---

## 📥 Gmail Integration

- Gmail API (`gmail.readonly` scope)
- Incremental sync using `after:timestamp`
- Per-user email storage
- Duplicate protection via `UNIQUE(user_id, gmail_message_id)`

---

## 🧠 AI Intelligence Layer

Uses OpenRouter LLM to extract structured productivity data from emails:

- Summary
- Category (Work, Personal, Finance, Travel, etc.)
- Priority (High, Medium, Low)
- Tasks (title, description, due date)
- Meetings (date, start time, end time)

Strict JSON enforcement with validation.

---

## 📊 API Endpoints

### Authentication

| Endpoint | Method | Description |
|-----------|--------|------------|
| `/login` | GET | Redirects to Google OAuth |
| `/auth/callback` | GET | OAuth callback |
| `/logout` | GET | Clears session |
| `/me` | GET | Returns logged-in user info |

---

### Gmail Sync

| Endpoint | Method | Description |
|-----------|--------|------------|
| `/sync` | GET | Fetch new emails for logged-in user |
| `/process` | GET | Run LLM processing on unprocessed emails |

---

### Data Retrieval

| Endpoint | Method | Description |
|-----------|--------|------------|
| `/emails` | GET | Get recent emails with intelligence fields |
| `/tasks` | GET | Get extracted tasks |
| `/meetings` | GET | Get extracted meetings |

All endpoints are user-scoped and require authentication.

---

# 🗄 Database Schema

### users

- id
- email_address
- google_id
- access_token
- refresh_token
- token_expiry
- last_sync_time

### emails

- user_id
- gmail_message_id
- subject
- body
- summary
- category
- priority
- processed

### tasks

- source_email_id
- title
- description
- due_date
- priority
- status

### meetings

- source_email_id
- title
- meeting_date
- start_time
- end_time
- description

Tasks and meetings inherit user ownership via email relationship.


# To run : 
1) Install dependencies 
2) Create .env file and add :
OPENROUTER_API_KEY=your_key
LLM_MODEL=your_model_name
3) Add Google OAuth credentials in project root 

