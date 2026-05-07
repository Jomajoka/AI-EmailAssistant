# EmailAssist

EmailAssist is an AI-powered productivity platform that converts unstructured Gmail inbox data into structured, actionable insights such as tasks, meetings, summaries, and priority classifications.

The system integrates Google OAuth 2.0, the Gmail API, Large Language Models, and a distributed full-stack architecture to provide an intelligent productivity workflow through a unified dashboard.

---

# Architecture

```text
Frontend (Next.js / Vercel)
        │
        │ REST APIs + Session Cookies
        ▼
Backend (FastAPI / Render)
        │
        ├── Gmail API Integration
        ├── OAuth Authentication
        ├── LLM Processing Pipeline
        └── Encryption + Validation Layer
        ▼
PostgreSQL Database (Supabase)
```

---

# Core Features

* Google OAuth 2.0 authentication with secure session-based login
* Gmail inbox synchronization using the Gmail API
* Incremental email ingestion with duplicate prevention
* AI-powered extraction of:

  * email summaries
  * priorities
  * categories
  * actionable tasks
  * meetings and scheduling information
* Task tracking with status management
* Meeting dashboard and calendar-style organization
* User-scoped data isolation across all APIs
* Application-level encryption for sensitive user data
* Distributed deployment across independently hosted frontend/backend services

---

# Tech Stack

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* Framer Motion

## Backend

* FastAPI
* PostgreSQL
* psycopg2
* Google OAuth 2.0
* Gmail API
* OpenRouter API
* Starlette Session Middleware

## AI / Processing

* Mistral LLM via OpenRouter
* Structured JSON extraction pipeline
* Schema validation and retry handling

## Deployment

* Frontend: Vercel
* Backend: Render
* Database: Supabase PostgreSQL

---

# System Design

The platform follows a distributed client-server architecture where the frontend communicates with a FastAPI backend through authenticated REST APIs.

The backend:

* manages Google OAuth authentication
* synchronizes Gmail data
* processes emails through an LLM pipeline
* validates extracted structured outputs
* stores processed productivity data in PostgreSQL

The frontend provides a productivity-focused dashboard for interacting with extracted tasks, meetings, and AI-generated summaries.

---

# AI Extraction Pipeline

The email processing pipeline converts unstructured email content into structured productivity entities.

### Processing Flow

1. Gmail emails are fetched through the Gmail API
2. Email metadata and content are normalized
3. Sensitive fields are encrypted before database storage
4. Unprocessed emails are passed to the LLM pipeline
5. The LLM generates structured JSON outputs
6. Backend validation ensures schema correctness
7. Tasks, meetings, summaries, and priorities are persisted to PostgreSQL

### Reliability Features

* Strict schema-constrained JSON generation
* Retry handling for malformed outputs
* Validation before database insertion
* Duplicate email prevention
* Incremental sync using last-sync timestamps

---

# Security Design

The system implements multiple security layers for authentication and sensitive data protection.

## Authentication

* Google OAuth 2.0 login
* Session-based authentication
* HttpOnly secure cookies
* SameSite cookie policies
* Cross-origin CORS configuration

## Data Protection

Application-level Fernet encryption is used for sensitive fields including:

* Gmail OAuth access tokens
* Gmail refresh tokens
* email sender fields
* email subjects
* raw email bodies

Encrypted values are decrypted only when required for authenticated processing or Gmail API access.

---

# Database Design

The database follows a relational structure centered around user-owned email data.

## Core Relationships

```text
User
 └── Emails
      ├── Tasks
      └── Meetings
```

### Relationship Model

* One user → many emails
* One email → many tasks
* One email → many meetings

Tasks and meetings are always linked through their source email, ensuring strict user-level data isolation and traceability.

---

# Engineering Challenges Solved

* Secure cross-domain authentication between Vercel-hosted frontend and Render-hosted backend
* Reliable handling of inconsistent LLM outputs through validation and retry mechanisms
* Protection of sensitive OAuth credentials and email data using application-level encryption
* Incremental Gmail synchronization without duplicate ingestion
* Managing asynchronous API-heavy workflows efficiently using FastAPI async architecture

---

# API Overview

| Method | Endpoint             | Description                 |
| ------ | -------------------- | --------------------------- |
| GET    | `/login`             | Start Google OAuth login    |
| GET    | `/auth/callback`     | Handle OAuth callback       |
| GET    | `/sync`              | Sync Gmail messages         |
| GET    | `/process`           | Run AI processing pipeline  |
| GET    | `/emails`            | Retrieve analyzed emails    |
| GET    | `/tasks`             | Retrieve extracted tasks    |
| PATCH  | `/tasks/{id}/status` | Update task status          |
| GET    | `/meetings`          | Retrieve extracted meetings |

---


