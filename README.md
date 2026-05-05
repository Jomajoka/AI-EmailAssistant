# EmailAssist

EmailAssist is an AI-powered email productivity assistant that connects to a user's Gmail account, syncs recent inbox messages, analyzes them with an LLM, and presents structured summaries, tasks, meetings, categories, and priorities in a web dashboard.

The project is built as a full-stack application with a FastAPI backend, a PostgreSQL database, Google OAuth/Gmail API integration, OpenRouter-powered LLM processing, and a Next.js frontend.

## Features

- Google OAuth 2.0 sign-in with session-based authentication
- Gmail inbox sync using the Gmail API with read-only access
- Incremental email fetching based on the user's last sync timestamp
- Duplicate prevention for previously synced Gmail messages
- LLM-based email analysis through OpenRouter
- Structured extraction of:
  - concise email summaries
  - email categories
  - priority levels
  - actionable tasks
  - scheduled meetings
- Dashboard view for emails, tasks, and meetings
- Task status updates with pending/completed tracking
- Task filtering by priority and due-date status
- Meeting list and calendar views
- User-scoped API access so each authenticated user only sees their own data

## System Architecture

```text
Gmail Account
    |
    | Google OAuth + Gmail API
    v
FastAPI Backend
    |
    | stores users, email metadata, tasks, meetings
    v
PostgreSQL Database
    |
    | unprocessed emails
    v
OpenRouter LLM Processing
    |
    | structured summaries, priorities, tasks, meetings
    v
Next.js Dashboard
```

## Tech Stack

**Backend**

- Python
- FastAPI
- PostgreSQL
- psycopg2
- Google OAuth / Gmail API
- OpenRouter Chat Completions API
- Starlette session middleware

**Frontend**

- Next.js
- React
- TypeScript
- Tailwind CSS
- Framer Motion
- React Hot Toast

## Backend Functionality

The backend exposes authenticated REST endpoints for login, Gmail sync, AI processing, and data retrieval. It stores OAuth tokens, refreshes expired Gmail access tokens, and keeps email/task/meeting data scoped to the signed-in user.

Email syncing fetches recent inbox messages from Gmail, normalizes key metadata such as sender, subject, received time, snippet, labels, and body content, then stores new messages in PostgreSQL.

The processing service sends unprocessed email content to an LLM and validates the response against a strict JSON structure. The extracted intelligence is saved back to the database, and related tasks or meetings are created from the result.

## Frontend Functionality

The frontend provides a dashboard for authenticated users to interact with their email intelligence data. Users can:

- sign in with Google
- sync new emails
- process emails with the AI pipeline
- view recent analyzed emails
- review extracted tasks
- mark tasks as completed or reopen them
- filter tasks by priority and due-date category
- view extracted meetings as a list or on a calendar
- access profile/session actions

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | API health/root message |
| `GET` | `/login` | Starts Google OAuth sign-in |
| `GET` | `/auth/callback` | Handles the Google OAuth callback |
| `GET` | `/logout` | Clears the authenticated session |
| `GET` | `/me` | Returns the current authenticated user |
| `GET` | `/sync` | Syncs new Gmail messages for the current user |
| `GET` | `/process` | Processes unprocessed emails with the LLM |
| `GET` | `/emails` | Returns recent analyzed emails |
| `GET` | `/tasks` | Returns extracted tasks |
| `PATCH` | `/tasks/{task_id}/status` | Updates a task's status |
| `GET` | `/meetings` | Returns extracted meetings |

## Database Tables

The application initializes the following PostgreSQL tables:

- `users`: authenticated users, Google account identifiers, OAuth tokens, token expiry, and sync timestamps
- `emails`: Gmail message metadata, body content, summaries, categories, priorities, and processing state
- `tasks`: actionable tasks extracted from emails
- `meetings`: scheduled meetings extracted from emails

Tasks and meetings are associated with their source email, which keeps data tied to the authenticated user.

## Environment Variables

Create a `.env` file in the project root for the backend:

```env
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your_session_secret
REDIRECT_URI=http://localhost:8000/auth/callback
FRONTEND_URL=http://localhost:3000
OPENROUTER_API_KEY=your_openrouter_api_key
LLM_MODEL=your_openrouter_model_name
```

For local Google OAuth development, place `credentials_web.json` in the project root. For deployment, Google OAuth credentials can be provided through the `GOOGLE_CREDENTIALS` environment variable as JSON.

Create `frontend/.env.local` for the frontend:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running Locally

### 1. Backend

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn run_api:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Typical Workflow

1. Sign in through Google OAuth.
2. Click **Sync** to fetch recent Gmail messages.
3. Click **Process** to run AI analysis on unprocessed emails.
4. Review summaries, priorities, tasks, and meetings in the dashboard.
5. Track task completion and switch between meeting list/calendar views.

## Project Structure

```text
EmailAssist/
  app/
    api.py                  # FastAPI app factory and middleware setup
    auth/                   # OAuth, session, and Gmail credential handling
    database/               # PostgreSQL connection and query helpers
    routers/                # API route modules
    services/               # Gmail sync and LLM processing services
  frontend/
    app/                    # Next.js app routes
    components/dashboard/   # Dashboard UI components
    hooks/                  # Frontend data-loading and action hooks
    lib/                    # API client helpers
    types/                  # Shared frontend TypeScript types
  run_api.py                # ASGI entry point
  requirements.txt          # Python dependencies
```

## Security Notes

- Gmail access is requested with the read-only scope.
- OAuth session state is validated during callback handling.
- Session cookies are configured differently for local and production environments.
- Secrets, OAuth credentials, token files, and environment files should not be committed to version control.

## Resume Summary

EmailAssist demonstrates a full-stack AI workflow that combines OAuth authentication, third-party API integration, database-backed synchronization, LLM-based structured extraction, and a responsive productivity dashboard.
