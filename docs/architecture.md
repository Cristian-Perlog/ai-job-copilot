# Architecture

## High-level overview

AI Job Application Copilot is a full-stack web application composed of:

- **Frontend**: Next.js (TypeScript) web app for the dashboard UI
- **Backend API**: FastAPI service providing REST endpoints and business logic
- **Database**: PostgreSQL as the system of record
- **Background processing**: Celery workers for async tasks (analytics aggregation, AI jobs, future email parsing)
- **Message broker / cache**: Redis for Celery broker (and optional caching)
- **Deployment**: Docker Compose for local development; production deployment on AWS (ECS + RDS + ElastiCache) later

The system is designed to be production-like while remaining simple enough to build as a solo flagship project.

---

## Components

### Frontend (Next.js)
Responsibilities:
- Authentication UI (sign-in / sign-out)
- Dashboard and pages (applications, interviews, analytics)
- Calls the backend API over HTTPS
- Handles client-side state and caching (e.g., TanStack Query)

Key pages:
- Dashboard (metrics, funnel, upcoming actions)
- Applications (CRUD)
- Application detail page (notes, interviews, status history)
- Interviews (CRUD)
- Settings (preferences for prioritization)

---

### Backend API (FastAPI)
Responsibilities:
- REST API for all core data (applications, interviews, analytics, preferences)
- Authorization and access control (per-user scoping)
- Validation and domain logic (status transitions, computed fields)
- Schedules/dispatches background jobs (Celery)

API style:
- Versioned endpoints: `/api/v1/...`
- OpenAPI auto docs (FastAPI)
- Clear separation: routers → services → repositories → models

---

### Database (PostgreSQL)
Responsibilities:
- Persist all application state and user data
- Support analytics queries and reporting
- Store preference configuration and scoring output (later)

Initial core tables (Phase 1):
- users
- job_applications
- interviews

Planned Phase 2+ tables:
- preferences
- events (or status_history)
- recommendations (optional cache)
- ai_generations (optional audit / history)

---

### Background workers (Celery)
Responsibilities:
- Run long or asynchronous tasks outside the request-response cycle
- Improve UX by keeping the API responsive

Planned jobs:
- Aggregate analytics snapshots (daily/weekly)
- Generate AI outputs (cover letters, interview questions)
- Email parsing and ingestion (optional future)

---

### Redis
Responsibilities:
- Celery broker (message queue)
- Optional caching layer (later if needed)

---

## Data flows (examples)

### User signs in
1. User authenticates via OAuth on the frontend
2. Frontend obtains identity info and sends authenticated requests to backend
3. Backend creates/updates the user record in PostgreSQL

### Create a job application
1. User submits application form in UI
2. Frontend calls `POST /api/v1/applications`
3. Backend validates input and stores in PostgreSQL
4. Backend optionally emits an event (Phase 2+) for analytics/history

### View dashboard
1. Frontend calls `GET /api/v1/dashboard`
2. Backend computes metrics from PostgreSQL (or reads precomputed snapshots later)
3. Frontend renders metrics, pipeline, and upcoming actions

### Run background task (Phase 2+)
1. Backend enqueues a job to Celery (Redis broker)
2. Worker consumes job and performs task (e.g., generate AI text)
3. Worker stores results in PostgreSQL
4. Frontend polls or refreshes to display results

---

## Security & auth (initial plan)

- OAuth login (Google) handled in frontend
- Backend validates and authorizes requests (user-scoped access)
- All endpoints scoped to the authenticated user
- Sensitive configuration stored via environment variables / secrets manager in production

---

## Deployment

### Local development
- Docker Compose runs:
  - postgres
  - redis
  - backend
  - worker
  - frontend

### Production (target)
- AWS ECS Fargate runs:
  - frontend container
  - backend container
  - worker container
- AWS RDS PostgreSQL
- AWS ElastiCache Redis
- AWS ECR for container images
- CloudWatch logs + health checks behind load balancer

---
