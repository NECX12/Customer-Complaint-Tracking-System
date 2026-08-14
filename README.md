# Mikano Customer Complaint Tracking System

A full-stack complaint management platform —  The system streamlines how customer complaints are received, assigned, tracked, and resolved across three user roles, with an AI-powered knowledge base that helps support agents resolve issues faster.

**Author:** Nwakpa Ejike Chukwuma

---

## The Problem It Solves

Without a dedicated system, complaint management in a large organization becomes chaotic — complaints come in through different channels, there is no accountability for who is handling what, no visibility into complaint history, and no way to measure agent performance. Customers have no way to track their complaints after submitting them, and agents have no institutional memory of how similar issues were resolved in the past.

This system solves all of that in one place:

- Customers submit complaints and track their status in real time
- Admins assign complaints to the right agents and monitor overall system health
- Agents work through their assigned queue with full context and AI-assisted resolution guidance
- Every status change is logged with a timestamp, actor, and comment — creating an immutable audit trail
- Email notifications keep all parties informed at every step
- The RAG-powered AI panel surfaces relevant troubleshooting guides and past resolved complaints whenever an agent opens a ticket

---

## Features

### Authentication & Authorization
- JWT-based authentication (HS256) with bcrypt password hashing
- Three roles: **Customer**, **Agent**, **Admin**
- Role-based access control enforced at every endpoint
- Customer self-registration; Agent/Admin accounts created by admins only

### Complaint Lifecycle (State Machine)
Complaints follow a strict, enforced workflow:

```
SUBMITTED → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
                                          ↕
                                     (can reopen)
```

`CLOSED` is terminal — no further transitions allowed. Every transition is validated in the service layer and creates a permanent history record.

### Three Role-Specific Dashboards
- **Customer Dashboard** — total complaints, open count, resolved count, recent complaints list
- **Agent Dashboard** — assigned workload, pending vs in-progress vs resolved breakdown
- **Admin Dashboard** — system-wide stats, unassigned complaints count, per-agent performance metrics with resolution rates and average resolution times

### Complaint Management
- Submit, list, and view complaints with full detail
- Status update panel with only valid next-state buttons shown
- Admin assignment panel with agent dropdown
- Full status timeline showing every change, who made it, and any comments left

### AI-Powered Resolution Suggestions (RAG)
When an agent opens a complaint, an **AI Suggestion Panel** automatically surfaces the most relevant content from:
- A knowledge base of product documentation, troubleshooting guides, maintenance schedules, warranty policies, FAQs, and billing procedures (10 markdown documents)
- Previously resolved complaints that are similar to the current one

The system uses **sentence-transformers** for local embeddings and **ChromaDB** as the vector store. When a **Gemini API key** is configured, it synthesizes a tailored resolution suggestion from the retrieved context. Without a key, the raw retrieved knowledge base chunks are shown directly — still very useful.

Every complaint resolved in the system is automatically indexed into the knowledge base, so the AI gets smarter over time.

### Async Email Notifications (Celery + Redis)
Notifications are sent asynchronously via a Celery worker queue backed by Redis, so email delivery never blocks the API response. Notifications are sent when:
- A customer submits a new complaint
- A complaint is assigned to an agent
- A complaint status changes
- A complaint is resolved

Each notification is stored as a database record (`PENDING → SENT/FAILED`) with retry logic (3 attempts, 60-second delay).

### User Management (Admin)
- Create, list, and update Agent/Admin accounts
- Activate or deactivate user accounts
- Filter users by role

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI (Python 3.12) |
| Database | PostgreSQL (via SQLAlchemy 2.0 ORM) |
| DB Migrations | Alembic |
| Authentication | JWT + bcrypt (python-jose, passlib) |
| Background Tasks | Celery + Redis |
| Email Templates | Jinja2 HTML templates |
| AI Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector Store | ChromaDB (in-process, persistent) |
| LLM (optional) | Google Gemini (`gemini-1.5-flash`) |
| Frontend | React 18 + TypeScript + Vite |
| Styling | Tailwind CSS (dark glassmorphism theme) |
| HTTP Client | Axios with JWT interceptor |
| Routing | React Router DOM v6 |

---

## Project Structure

```
technical_assessment/
├── .env.example                  # Environment variable template
├── .gitignore
├── ARCHITECTURE.md               # Detailed backend architecture walkthrough
├── README.md                     # This file
│
├── backend/
│   ├── alembic/                  # Database migration files
│   ├── app/
│   │   ├── main.py               # FastAPI app entry point, CORS, router
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic Settings — all env vars
│   │   │   ├── security.py       # JWT creation/decoding, bcrypt hashing
│   │   │   └── dependencies.py   # Auth dependencies: get_current_user, require_role
│   │   ├── db/
│   │   │   ├── base.py           # SQLAlchemy base + TimestampMixin
│   │   │   ├── session.py        # DB engine + per-request session
│   │   │   └── models/           # 5 ORM models (User, Complaint, History, Notification, AuditLog)
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── services/             # Business logic layer (6 services)
│   │   ├── api/v1/               # HTTP route handlers (auth, complaints, users, dashboard, ai)
│   │   ├── workers/              # Celery app + email task
│   │   └── ai/                   # RAG pipeline (embeddings, vector store, ingest, engine)
│   ├── knowledge_base/           # 10 markdown documents for RAG
│   │   ├── faq/
│   │   ├── maintenance/
│   │   ├── policies/
│   │   ├── products/
│   │   └── troubleshooting/
│   ├── scripts/
│   │   ├── seed.py               # Populates DB with sample users and complaints
│   │   └── ingest.py             # Indexes knowledge base into ChromaDB
│   ├── tests/                    # Pytest test suite (6 test files)
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── api/client.ts         # Axios instance with JWT interceptor
    │   ├── contexts/             # React AuthContext
    │   ├── components/           # Layout, StatusBadge, Timeline, AiSuggestionPanel, etc.
    │   ├── pages/                # Login, Register, Dashboards, Complaints, Users
    │   └── types/index.ts        # TypeScript interfaces mirroring backend schemas
    ├── package.json
    └── vite.config.ts
```

---

## API Endpoints

### Authentication — `/api/v1/auth`
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/register` | Public | Customer self-registration |
| POST | `/login` | Public | Email/password login, returns JWT |
| GET | `/me` | All roles | Current user profile |

### Complaints — `/api/v1/complaints`
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/` | Customer | Submit a new complaint |
| GET | `/` | All roles | List complaints (role-scoped) |
| GET | `/{id}` | All roles | Complaint detail (ownership enforced) |
| PUT | `/{id}/status` | Agent, Admin | Update status (state machine validated) |
| POST | `/{id}/assign` | Admin | Assign complaint to an agent |
| GET | `/{id}/history` | All roles | Full status transition timeline |

### Users — `/api/v1/users`
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/` | Admin | List all users (optional role filter) |
| POST | `/` | Admin | Create Agent or Admin account |
| GET | `/agents` | Admin | List active agents (for assignment) |
| PUT | `/{id}` | Admin | Update user name or active status |

### Dashboard — `/api/v1/dashboard`
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/customer` | Customer | Personal complaint stats |
| GET | `/agent` | Agent | Assigned workload stats |
| GET | `/admin` | Admin | System-wide stats + agent performance |

### AI / RAG — `/api/v1/ai`
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/suggestions/{complaint_id}` | Agent, Admin | Get AI resolution suggestions |
| POST | `/ingest` | Admin | Trigger full knowledge base re-index |
| GET | `/status` | Admin | Knowledge base stats and chunk count |

Interactive API docs available at `http://localhost:8000/docs` when the backend is running.

---

## Running the Project Locally

### Prerequisites

Make sure these are installed on your machine before starting:

- **Python 3.10+** — [python.org](https://python.org)
- **Node.js 18+** — [nodejs.org](https://nodejs.org)
- **Git** — [git-scm.com](https://git-scm.com)
- **A PostgreSQL database** — local install or a cloud provider like [Supabase](https://supabase.com) (free tier works)
- **Redis** — see the Redis setup section below

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/NECX12/Customer-Complaint-Tracking-System.git
cd Customer-Complaint-Tracking-System
```

---

### Step 2 — Set Up Redis Locally

Redis is required for the Celery background task queue that handles email notifications. Redis does not have a native Windows installer, so use one of the options below based on your OS.

**On macOS:**
```bash
brew install redis
brew services start redis
```

**On Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install redis-server -y
sudo service redis-server start
```

**On Windows — via WSL 2 (recommended):**

First check if WSL is installed:
```cmd
wsl --list --verbose
```

If not installed, run this in an Administrator Command Prompt then restart:
```cmd
wsl --install
```

Once WSL is running, open it and install Redis:
```bash
sudo apt update
sudo apt install redis-server -y
sudo service redis-server start
redis-cli ping   # should return: PONG
```

To start Redis in WSL on future sessions (run this before starting the backend):
```cmd
wsl sudo service redis-server start
```

Once Redis is running, confirm it responds:
```bash
redis-cli ping
# Expected output: PONG
```

---

### Step 3 — Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Open `.env` and fill in the required values:

```env
# Your PostgreSQL connection string
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Generate a long random string for JWT signing
SECRET_KEY=your-long-random-secret-key-here

# Redis (local WSL or native)
REDIS_URL=redis://localhost:6379/0

# Optional — Gemini API key enables AI answer synthesis
# Without this, the AI panel still works in retrieval-only mode
GEMINI_API_KEY=your-gemini-api-key

# Embedding model (do not change unless you know what you're doing)
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# LLM model
LLM_MODEL=gemini-1.5-flash

# AI provider
AI_PROVIDER=gemini
```

> SMTP fields can be left blank — emails will be logged to the console in development mode instead of being sent.

---

### Step 4 — Set Up the Backend

Open a terminal and navigate to the backend folder:

```bash
cd backend
```

Create and activate a Python virtual environment:

```bash
# Create
python -m venv .venv

# Activate on macOS/Linux
source .venv/bin/activate

# Activate on Windows (Command Prompt)
.venv\Scripts\activate.bat

# Activate on Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Install all Python dependencies:

```bash
pip install -r requirements.txt
```

> This installs PyTorch, sentence-transformers, ChromaDB, FastAPI, Celery, and all other dependencies. It may take a few minutes on first run.

---

### Step 5 — Run Database Migrations

With the virtual environment active and inside the `backend/` directory:

```bash
alembic upgrade head
```

This creates all 5 tables in your PostgreSQL database:
- `users`
- `complaints`
- `complaint_status_history`
- `notifications`
- `audit_logs`

---

### Step 6 — Seed the Database

Populate the database with sample users and complaints for testing:

```bash
python -m scripts.seed
```

This creates:
- **5 users** — 1 admin, 2 agents, 2 customers
- **5 complaints** across all statuses (SUBMITTED, ASSIGNED, IN_PROGRESS, RESOLVED, SUBMITTED)
- Complete status history for each complaint

---

### Step 7 — Index the RAG Knowledge Base

This step loads the knowledge base markdown documents and generates vector embeddings in ChromaDB. It is required for the AI Suggestion Panel to return results.

```bash
python -m scripts.ingest
```

> The first run downloads the `all-MiniLM-L6-v2` embedding model (~90 MB). This is a one-time download cached locally by sentence-transformers. Subsequent runs are fast.

Expected output:
```
============================================================
  Mikano RAG Knowledge Base Indexer
============================================================
[1/5] Checking knowledge base directory...
  OK — found 10 markdown file(s)
[2/5] Loading and chunking documents...
  OK — produced 87 chunk(s)
[3/5] Loading embedding model: all-MiniLM-L6-v2
  OK — model loaded, vector dimensions: 384
[4/5] Skipping wipe (run with --rebuild to start fresh)
[5/5] Embedding 87 chunks and writing to ChromaDB...
============================================================
  SUCCESS — Knowledge base indexed
============================================================
```

---

### Step 8 — Start the Backend API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend is now running at `http://localhost:8000`.
Interactive API docs: `http://localhost:8000/docs`

---

### Step 9 — Start the Celery Worker

Open a **second terminal**, navigate to the backend, activate the venv, then run:

```bash
# macOS/Linux
celery -A app.workers.celery_app worker --loglevel=info

# Windows (Command Prompt) — --pool=solo required on Windows
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

This worker processes background email notification tasks.

---

### Step 10 — Set Up and Start the Frontend

Open a **third terminal** and navigate to the frontend folder:

```bash
cd frontend
npm install
npm run dev
```

The frontend is now running at `http://localhost:5173`.

---

### You're Ready

Open `http://localhost:5173` in your browser. Use these credentials to explore all three roles:

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@example.com` | `admin123` |
| Agent | `agent@example.com` | `agent123` |
| Agent 2 | `agent2@example.com` | `agent123` |
| Customer | `customer@example.com` | `customer123` |
| Customer 2 | `jane@example.com` | `customer123` |

---

## Testing the Application

### Run the Automated Test Suite

From the `backend/` directory with the venv active:

```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_complaints.py -v
pytest tests/test_rbac.py -v
pytest tests/test_ai_rag.py -v
```

Tests use an in-memory SQLite database — no running PostgreSQL required.

### Test the RAG / AI Feature from the Frontend

1. Log in as **Agent** (`agent@example.com` / `agent123`) or **Admin**
2. Click **Complaints** in the sidebar
3. Open any complaint from the list
4. Scroll down to the **AI Resolution Suggestions** panel (visible only to Agents and Admins)
5. Click **Search Knowledge Base for Suggestions**
6. Results appear ranked by relevance score — click any card to expand the full content

> The AI panel is intentionally hidden from Customers — they only see complaint status and history.

### Re-index the Knowledge Base

If you edit any files in `backend/knowledge_base/`, re-run the ingest script with the rebuild flag:

```bash
python -m scripts.ingest --rebuild
```

---

## Default Login Credentials

| Role | Email | Password | Capabilities |
|------|-------|----------|-------------|
| Admin | admin@example.com | admin123 | Full access — assign complaints, manage users, system dashboard |
| Agent | agent@example.com | agent123 | View/update assigned complaints, AI suggestions panel |
| Agent 2 | agent2@example.com | agent123 | Same as Agent |
| Customer | customer@example.com | customer123 | Submit complaints, view own complaint status |
| Customer 2 | jane@example.com | customer123 | Same as Customer |

---

## Architecture

For a detailed walkthrough of the backend architecture — from database models to the async notification pipeline — see [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## Author

**Nwakpa Ejike Chukwuma**
