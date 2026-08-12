# Agent Summary — Mikano Complaint Tracker

> **Date:** August 9, 2026
> **Project:** Mikano Technical Assessment — Customer Complaint Tracking System
> **Scope:** Full-stack application review, frontend build-out, and deployment preparation

---

## 1. What Was Done

### Phase 1: Backend Codebase Review

Performed a thorough review of the existing **backend**, which was already fully implemented. The backend is a **FastAPI (Python)** application with the following architecture:

#### Technology Stack

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI with versioned routes at `/api/v1` |
| Database | PostgreSQL 16 via SQLAlchemy 2.0 ORM |
| Migrations | Alembic (autogenerate from models) |
| Authentication | JWT (HS256) with bcrypt password hashing |
| Async Tasks | Celery + Redis for email notification delivery |
| Configuration | Pydantic Settings (env-based) |
| Testing | Pytest with SQLite test database |
| Infrastructure | Docker Compose (5 services) |

#### Database Models (5 tables)

| Model | File | Purpose |
|-------|------|---------|
| `User` | `backend/app/db/models/user.py` | Accounts with CUSTOMER, AGENT, ADMIN roles |
| `Complaint` | `backend/app/db/models/complaint.py` | Customer complaints with status + priority |
| `ComplaintStatusHistory` | `backend/app/db/models/complaint_history.py` | Immutable audit trail of status transitions |
| `Notification` | `backend/app/db/models/notification.py` | Email notification records (PENDING → SENT/FAILED) |
| `AuditLog` | `backend/app/db/models/audit_log.py` | Administrative action audit trail |

#### Complaint State Machine

The complaint lifecycle follows a strict state machine defined in `VALID_TRANSITIONS`:

```
SUBMITTED → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
                                         ↓           
                                    IN_PROGRESS (reopen)
```

- `CLOSED` is a terminal state — no further transitions allowed.
- Transitions are enforced in the service layer (`complaint_service.py`), not in route handlers.

#### Three-Role RBAC System

| Role | Capabilities |
|------|-------------|
| **CUSTOMER** | Self-register, submit complaints, view own complaints/dashboard |
| **AGENT** | View/update assigned complaints, transition status with comments |
| **ADMIN** | Full access — view all complaints, assign agents, create users, system-wide dashboard |

#### API Endpoints

**Authentication (`/api/v1/auth`)**
- `POST /register` — Customer self-registration
- `POST /login` — Email/password login, returns JWT (uses OAuth2PasswordRequestForm)
- `GET /me` — Current user profile

**Complaints (`/api/v1/complaints`)**
- `POST /` — Submit new complaint (CUSTOMER only)
- `GET /` — List complaints (role-scoped: own / assigned / all)
- `GET /{id}` — Complaint detail with ownership check
- `PUT /{id}/status` — Update status (AGENT/ADMIN, validates state machine)
- `POST /{id}/assign` — Assign to agent (ADMIN only)
- `GET /{id}/history` — Full status transition timeline

**Users (`/api/v1/users`)**
- `GET /` — List all users with optional role filter (ADMIN)
- `POST /` — Create AGENT or ADMIN account (ADMIN)
- `GET /agents` — List active agents for assignment dropdown (ADMIN)
- `PUT /{id}` — Update user name/active status (ADMIN)

**Dashboard (`/api/v1/dashboard`)**
- `GET /customer` — Customer stats (total/open/resolved + recent complaints)
- `GET /agent` — Agent workload (assigned/pending/in-progress/resolved + recent)
- `GET /admin` — System-wide stats + agent performance metrics (resolution rate, avg time)

#### Services Layer

| Service | File | Responsibility |
|---------|------|---------------|
| `auth_service` | `backend/app/services/auth_service.py` | Registration, authentication, token creation |
| `complaint_service` | `backend/app/services/complaint_service.py` | Complaint CRUD, state machine, assignment |
| `notification_service` | `backend/app/services/notification_service.py` | Create notification records + enqueue Celery tasks |
| `dashboard_service` | `backend/app/services/dashboard_service.py` | Aggregated stats per role |
| `audit_service` | `backend/app/services/audit_service.py` | Immutable audit log entries |
| `user_service` | `backend/app/services/user_service.py` | User CRUD operations |

#### Notification System (Celery)

The notification pipeline follows this pattern:
1. API handler calls `notification_service.notify_*()`
2. A `Notification` row is created in PostgreSQL with status `PENDING`
3. A Celery task is enqueued via Redis
4. The Celery worker picks it up, sends the email (or logs in dev mode), and marks it `SENT` or `FAILED`
5. Failed tasks retry up to 3 times with 60-second delays

#### Testing

5 test files using Pytest + SQLite in-memory database:
- `test_auth.py` — Registration, login, duplicate email
- `test_complaints.py` — CRUD, status transitions, invalid transitions
- `test_rbac.py` — Role-based access control enforcement
- `test_users.py` — Admin user management
- `test_notifications.py` — Notification creation

#### Seed Data

`backend/scripts/seed.py` creates development data:
- **5 users:** 1 admin, 2 agents, 2 customers
- **5 complaints** across all statuses (SUBMITTED, ASSIGNED, IN_PROGRESS, RESOLVED, SUBMITTED)
- Complete status history for each complaint

Default credentials:
| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@example.com` | `admin123` |
| Agent 1 | `agent@example.com` | `agent123` |
| Agent 2 | `agent2@example.com` | `agent123` |
| Customer 1 | `customer@example.com` | `customer123` |
| Customer 2 | `jane@example.com` | `customer123` |

---

### Phase 2: Frontend Feature Requirements Analysis

Derived a complete list of frontend features required from the backend API surface:

- **7 feature categories** identified: Authentication, Dashboards, Complaint Management, State Machine UI, User Management, Notification Awareness, Cross-Cutting Concerns
- **3 role-specific dashboards** with different stat cards and tables
- **Full complaint lifecycle UI** — submit, list, detail, timeline, status update, assignment
- **Admin user management** — create, list, edit, activate/deactivate
- **State machine enforcement in UI** — only valid next-status buttons are shown

---

### Phase 3: Complete Frontend Build

Built the entire frontend from scratch — **18 source files** covering all features. The frontend had only configuration files (package.json, vite.config, tailwind.config, tsconfig, index.html); no `src/` directory existed.

#### Technology Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18.3 | UI library |
| TypeScript | 5.5 | Type safety |
| Vite | 5.4 | Build tool + dev server |
| Tailwind CSS | 3.4 | Styling |
| React Router DOM | 6.26 | Client-side routing |
| Axios | 1.7 | HTTP client |
| React Hook Form + Zod | Latest | Form handling (available in deps) |

#### Files Created

**Foundation (7 files)**

| File | Purpose |
|------|---------|
| `src/main.tsx` | React entry point |
| `src/App.tsx` | Router setup with role-gated routes |
| `src/index.css` | Design system — dark glassmorphism theme with custom utility classes |
| `src/vite-env.d.ts` | Vite type declarations |
| `src/types/index.ts` | All TypeScript interfaces mirroring backend Pydantic schemas + state machine |
| `src/api/client.ts` | Axios instance with JWT interceptor (auto-attaches Bearer token, redirects on 401) |
| `src/contexts/AuthContext.tsx` | Auth state management (login, register, logout, user fetch) |

**Shared Components (6 files)**

| File | Purpose |
|------|---------|
| `src/components/Layout.tsx` | Sidebar navigation shell with role-based menu items and user card |
| `src/components/ProtectedRoute.tsx` | Route guard — checks auth + optional role requirement |
| `src/components/StatusBadge.tsx` | Color-coded badge for complaint statuses (5 colors) |
| `src/components/PriorityBadge.tsx` | Color-coded badge for priorities with directional icons |
| `src/components/Timeline.tsx` | Vertical timeline with dots, actor info, comments, timestamps |
| `src/components/LoadingSpinner.tsx` | Animated loading indicator |

**Pages (5 page groups)**

| File | Purpose |
|------|---------|
| `src/pages/Login.tsx` | Login form with demo credential quick-fill buttons |
| `src/pages/Register.tsx` | Customer self-registration with password confirmation |
| `src/pages/dashboard/DashboardRouter.tsx` | Routes to correct dashboard by user role |
| `src/pages/dashboard/CustomerDashboard.tsx` | Stats cards + recent complaints table |
| `src/pages/dashboard/AgentDashboard.tsx` | Assigned workload stats + recent assignments |
| `src/pages/dashboard/AdminDashboard.tsx` | System-wide stats + agent performance table with progress bars |
| `src/pages/complaints/ComplaintList.tsx` | Role-aware complaint list with admin status filter tabs |
| `src/pages/complaints/CreateComplaint.tsx` | Complaint submission form with priority radio selector |
| `src/pages/complaints/ComplaintDetail.tsx` | Full detail view with status update, admin assignment, and timeline |
| `src/pages/users/UserManagement.tsx` | Admin user CRUD — create form, role filter, edit modal with toggle switch |

#### Design System

- **Dark glassmorphism theme** — `bg-gray-950` base, glass cards with `backdrop-blur-xl`
- **Inter font** from Google Fonts (already loaded in index.html)
- **Custom CSS utility classes:** `glass-card`, `stat-card`, `input-field`, `btn-primary`, `btn-secondary`, `btn-danger`, `data-table`, `sidebar-link`
- **Micro-animations:** fade-in, slide-in, slide-up, staggered children, soft pulse
- **Inline SVG icons** — zero external icon library dependency
- **Color system:** Blue/Cyan brand, Amber/Purple/Emerald/Red for status/priority

#### Routing Structure

```
/login              — Login page (public)
/register           — Registration page (public)
/dashboard          — Role-specific dashboard (protected)
/complaints         — Complaint list (protected)
/complaints/new     — New complaint form (CUSTOMER only)
/complaints/:id     — Complaint detail (protected, ownership enforced)
/users              — User management (ADMIN only)
/*                  — Redirects to /dashboard
```

---

### Phase 4: Deployment Preparation

Identified all prerequisites for testing the full stack:

#### Infrastructure (Docker Compose — 5 services)

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `postgres` | postgres:16-alpine | 5432 | Database |
| `redis` | redis:7-alpine | 6379 | Celery broker |
| `backend` | Python 3.12 | 8000 | FastAPI API |
| `celery-worker` | Python 3.12 | — | Background email tasks |
| `frontend` | Node 20 | 5173 | React dev server |

#### Setup Steps Identified

1. **Create `.env` file** from `.env.example` (no edits needed for Docker)
2. **Generate initial Alembic migration** (the `alembic/versions/` directory is empty — no migration file exists)
3. **Run `docker-compose up --build`** to start all 5 services
4. **Seed the database** with `docker-compose exec backend python -m scripts.seed`
5. **Access the app** at `http://localhost:5173`

#### Known Issue Identified

The `alembic/versions/` directory contains only a `.gitkeep` — **no migration file exists**. The Docker Compose backend startup command runs `alembic upgrade head`, which will do nothing without a migration file. Either:
- Generate a migration locally with `alembic revision --autogenerate -m "initial_schema"`
- Or add a fallback to create tables directly with `Base.metadata.create_all()`

---

## 2. Project File Structure

```
mikano-technical-assessment/
├── .env.example                    # Environment variable template
├── .gitignore
├── docker-compose.yml              # 5-service orchestration
├── agent_summary.md                # ← This file
│
├── backend/
│   ├── Dockerfile                  # Python 3.12 + psycopg2
│   ├── requirements.txt            # 16 Python packages
│   ├── alembic.ini                 # Alembic config
│   ├── alembic/
│   │   ├── env.py                  # Reads DATABASE_URL from settings
│   │   ├── script.py.mako
│   │   └── versions/               # ⚠️ Empty — needs initial migration
│   ├── app/
│   │   ├── main.py                 # FastAPI app with CORS
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic Settings
│   │   │   ├── security.py         # JWT + bcrypt
│   │   │   └── dependencies.py     # Auth + role dependencies
│   │   ├── db/
│   │   │   ├── base.py             # DeclarativeBase + TimestampMixin
│   │   │   ├── session.py          # Engine + SessionLocal
│   │   │   └── models/
│   │   │       ├── user.py
│   │   │       ├── complaint.py
│   │   │       ├── complaint_history.py
│   │   │       ├── notification.py
│   │   │       └── audit_log.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── complaint.py
│   │   │   └── dashboard.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── complaint_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── audit_service.py
│   │   │   └── user_service.py
│   │   ├── api/v1/
│   │   │   ├── router.py
│   │   │   ├── auth.py
│   │   │   ├── complaints.py
│   │   │   ├── users.py
│   │   │   └── dashboard.py
│   │   ├── workers/
│   │   │   ├── celery_app.py
│   │   │   └── tasks.py
│   │   └── templates/emails/       # Jinja2 HTML email templates
│   ├── scripts/
│   │   └── seed.py                 # Dev seed data
│   └── tests/
│       ├── conftest.py             # Fixtures (SQLite test DB)
│       ├── test_auth.py
│       ├── test_complaints.py
│       ├── test_rbac.py
│       ├── test_users.py
│       └── test_notifications.py
│
└── frontend/
    ├── Dockerfile                  # Node 20
    ├── index.html                  # Entry HTML + Inter font
    ├── package.json                # React 18 + Tailwind + Axios
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── tsconfig.json
    ├── postcss.config.js
    └── src/                        # ← All created in this session
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        ├── vite-env.d.ts
        ├── types/index.ts
        ├── api/client.ts
        ├── contexts/AuthContext.tsx
        ├── components/
        │   ├── Layout.tsx
        │   ├── ProtectedRoute.tsx
        │   ├── StatusBadge.tsx
        │   ├── PriorityBadge.tsx
        │   ├── Timeline.tsx
        │   └── LoadingSpinner.tsx
        └── pages/
            ├── Login.tsx
            ├── Register.tsx
            ├── dashboard/
            │   ├── DashboardRouter.tsx
            │   ├── CustomerDashboard.tsx
            │   ├── AgentDashboard.tsx
            │   └── AdminDashboard.tsx
            ├── complaints/
            │   ├── ComplaintList.tsx
            │   ├── CreateComplaint.tsx
            │   └── ComplaintDetail.tsx
            └── users/
                └── UserManagement.tsx
```

---

## 3. What Remains To Be Done

| Item | Status | Notes |
|------|--------|-------|
| Generate initial Alembic migration | ❌ Pending | `alembic/versions/` is empty |
| Create `.env` from `.env.example` | ❌ Pending | Defaults work for Docker |
| Run `npm install` in frontend | ❌ Pending | Terminal had permission issues |
| Run `docker-compose up --build` | ❌ Pending | Starts all 5 services |
| Seed the database | ❌ Pending | `python -m scripts.seed` |
| Test all user flows in the browser | ❌ Pending | Login as all 3 roles |
| Verify email templates exist | ⚠️ Unchecked | Templates dir has HTML files |
| Production deployment | ❌ Not started | Out of current scope |
