# Atlas AI Command Center - Full-Stack Template

A production-ready template for building modern, AI-first web applications with Python/FastAPI backend, Next.js/React frontend, Keycloak for identity management, and integrated AI features (Gemini).

---

## 🚨 For New Client Projects - Read This First!

When starting a new project from this template, understand what's real functionality vs demo/placeholder:

### What's Real (Production-Ready)

| Component | Description |
|-----------|-------------|
| **Authentication** | Credentials-based login with NextAuth.js; optional OAuth2/OIDC with Keycloak |
| **Authorization Engine** | JSON-based RBAC via `authz.map.json` and `authz.py` |
| **User Registration** | Self-registration with domain-based auto-approval or admin approval |
| **Admin User Management** | `/admin/users` - Approve/reject pending users |
| **Audit Logging** | `/admin/audit` - Automatic request logging + custom events with export |
| **AI Policies** | `/ai/policies` - Natural language rule engine with DSL translation |
| **AI Insights** | `/ai/insights` - Proactive analysis and recommendations |
| **AI Manager** | Global chatbot modal - Agentic assistant with tool execution |
| **Database Setup** | PostgreSQL with Alembic migrations |
| **API Structure** | FastAPI with dependency injection |
| **Session Management** | NextAuth.js with JWT token handling |
| **Agents & Telemetry** | Agent registry and telemetry API endpoints |

### What's Demo (Replace for Production)

| Page | Location | Action Required |
|------|----------|-----------------|
| **Dashboard** | `/` (page.tsx) | Replace mock stats with real data |
| **Settings** | `/settings` | Implement real settings functionality |
| **AI Manager tools** | Backend `services/ai/tools.py` | Wire to real system APIs |

---

## ✨ Core Features

- **Production-Ready Stack**: FastAPI, Next.js, PostgreSQL, and Keycloak (optional)
- **AI Integration**: Policies, Insights, and AI Manager with Gemini
- **Pluggable Authorization Engine**: Endpoint-level access control in JSON
- **User Self-Registration**: With domain-based auto-approval or admin approval
- **Comprehensive Audit Logging**: Automatic request logging + custom business events
- **Fully Containerized**: Docker and Docker Compose
- **Cloud-Ready**: Structure supports deployment to Google Cloud Run with Cloud SQL

---

## 💻 Technology Stack

| Area | Technology | Purpose |
|------|------------|---------|
| Backend | Python 3.11 + FastAPI | High-performance API |
| Frontend | Next.js 14+ + React + TypeScript | Modern UI framework |
| AI | Gemini API | Policies, Insights, Chatbot |
| Identity | Keycloak 24 (optional) | Centralized IAM; local JWT also supported |
| Database | PostgreSQL 15 | Application data |
| DevOps | Docker + Docker Compose | Containerization |

---

## 🚀 Quick Start

Get the Atlas AI Command Center running locally in under 5 minutes.

### Prerequisites

| Tool | Required | Purpose |
|------|----------|---------|
| Docker Desktop | ✅ Yes | Runs all services |
| make | ✅ Yes | Dev commands (built-in on macOS/Linux; use WSL or Git Bash on Windows) |
| Google Cloud SDK | ❌ Optional | For cloud deployment |

### Step 1: Clone & Setup

```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo

# Create your environment file
cp .env.example .env
```

### Step 2: Configure Secrets

Edit `.env` and set these required values:

```bash
# REQUIRED: Generate and paste this secret
openssl rand -base64 32
# Copy the output and set: NEXTAUTH_SECRET=<paste-here>
# Also set: SECRET_KEY=<paste-here> (can be same or different)
```

**OPTIONAL but RECOMMENDED**: Enable AI features

- Get your API key from: https://aistudio.google.com/apikey  
- Set in `.env`: `GEMINI_API_KEY=your-api-key-here`

### Step 3: Start Everything

```bash
make up
```

This starts PostgreSQL, Keycloak (optional), Backend (FastAPI), and Frontend (Next.js).

### Step 4: Access the App

| Service | URL | Description |
|---------|-----|-------------|
| 🌐 Frontend | http://localhost:3000 | Main application |
| 📡 Backend API | http://localhost:8000/docs | Swagger API docs |
| 🔐 Keycloak Admin | http://localhost:8080 | Identity management (if enabled) |

**Default admin login** (after running migrations):

- Email: `admin@atlasuniversity.edu.in`  
- Password: `admin123`

### Useful Commands

| Command | Description |
|---------|-------------|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make logs-be` | View backend logs |
| `make logs-fe` | View frontend logs |
| `make restart-be` | Restart backend only |
| `make migrate-up` | Apply database migrations |
| `make migrate-history` | View migration history |

### Troubleshooting Quick Start

| Issue | Solution |
|-------|----------|
| Port 3000/8000 in use | Stop other services or change ports in `.env` |
| Login returns 401 | Ensure NEXTAUTH_SECRET is set; clear cookies or use incognito |
| AI features not working | Check GEMINI_API_KEY is set in `.env` |
| Containers won't start | Run `docker compose down -v` then `make up` |

---

## 📂 Project Structure

```
.
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py             # API routes and app bootstrap
│   │   ├── authz.map.json     # Authorization rules (EDIT THIS)
│   │   ├── public.map.json    # Public endpoints list
│   │   ├── core/
│   │   │   ├── authz.py       # Authorization engine
│   │   │   ├── config.py      # Settings
│   │   │   ├── database.py    # DB connection
│   │   │   └── security.py    # JWT / password hashing
│   │   ├── api/
│   │   │   ├── auth.py        # Login / register
│   │   │   ├── users.py       # /users/me
│   │   │   ├── admin.py       # Admin users & audit
│   │   │   ├── ai.py          # AI endpoints (policies, insights, chat)
│   │   │   ├── agents.py      # Agent registry
│   │   │   └── telemetry.py   # Telemetry
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/
│   │   │   ├── audit.py       # Audit logging service
│   │   │   ├── keycloak.py    # Keycloak JWT validation
│   │   │   ├── keycloak_admin.py  # Keycloak Admin API
│   │   │   └── ai/            # AI services
│   │   │       ├── chat.py    # AI Manager chat logic
│   │   │       ├── gemini.py  # Gemini API client
│   │   │       ├── policy.py  # Policy translation
│   │   │       ├── insights.py # Insights generation
│   │   │       └── tools.py   # AI function tools
│   │   └── middleware/
│   │       └── audit.py       # Request audit middleware
│   ├── alembic/               # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                  # Next.js Frontend
│   └── src/
│       ├── app/
│       │   ├── (dashboard)/    # Protected dashboard pages
│       │   ├── admin/         # Admin pages (users, audit)
│       │   ├── ai/            # AI pages (policies, insights)
│       │   └── auth/          # Login, register, error
│       ├── components/
│       │   ├── ai/            # AIManager chatbot
│       │   ├── auth/          # AuthProvider
│       │   └── layout/        # Header, Sidebar
│       ├── lib/               # api.ts, store, utils
│       ├── middleware.ts     # Auth middleware
│       └── types/            # next-auth.d.ts
│
├── docker-compose.yml         # Local development
├── Makefile                   # Dev commands
├── .env.example               # Environment template
└── README.md                  # This file
```

---

## 📝 Environment Variables

The `.env` file is organized into Backend and Frontend sections.

### Backend Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| APP_ENV | development | Environment: development or production |
| LOG_LEVEL | INFO | Logging level: DEBUG, INFO, WARNING, ERROR |
| DATABASE_URL | (composed) | PostgreSQL connection string |
| SECRET_KEY | (required) | JWT signing key; use `openssl rand -base64 32` |
| STORAGE_BACKEND | local | File storage: local or gcs |
| GEMINI_API_KEY | (empty) | API key for AI features |
| AI_MODEL | gemini-2.0-flash-exp | AI model name |
| APPROVED_EMAIL_DOMAINS | atlasuniversity.edu.in | Comma-separated domains for auto-approval |
| KEYCLOAK_* | (empty) | Keycloak URL, realm, client ID/secret if using Keycloak |

### Frontend Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| NODE_ENV | development | Next.js environment mode |
| FRONTEND_TARGET | dev | Docker build target: dev or prod |
| NEXT_PUBLIC_API_URL | http://localhost:8000 | Backend API URL (browser) |
| NEXT_PUBLIC_BASE_PATH | (empty) | Base path for reverse proxy |
| NEXTAUTH_SECRET | (required) | Secret for NextAuth.js; use `openssl rand -base64 32` |
| NEXTAUTH_URL | http://localhost:3000 | App URL for NextAuth |

### Ports (optional overrides)

| Variable | Default |
|----------|---------|
| FRONTEND_PORT | 3000 |
| BACKEND_PORT | 8000 |
| DB_PORT | 5432 |
| KEYCLOAK_PORT | 8080 |

---

## 🤖 AI Features

### AI Policies (`/ai/policies`)

Define business rules in natural language. The AI translates them into executable logic.

- Natural language rule input  
- Automatic translation to logical DSL  
- Support for both logical (DSL) and natural language policies  
- Policy hierarchy with priority ordering  
- Conflict detection and validation  

### AI Insights (`/ai/insights`)

Proactive analysis and recommendations based on system data.

- Automated pattern detection  
- Anomaly identification  
- Severity-based prioritization (Critical, Warning, Recommendation)  
- Suggested actions with estimated impact  

### AI Manager (Global Chatbot)

Accessible from any page via the header (🤖 button). Opens as a centered modal with blurred backdrop.

- Context-aware (knows current page)  
- Tool execution (function calling)  
- Markdown rendering in responses  
- Keyboard shortcut: Enter to send  

---

## 🛠️ Make Commands

| Command | Description |
|---------|-------------|
| make up | Start all services |
| make down | Stop all services |
| make logs | View all logs |
| make logs-be | View backend logs |
| make logs-fe | View frontend logs |
| make logs-keycloak | View Keycloak logs |
| make restart-be | Restart backend |
| make restart-fe | Restart frontend |
| make format | Format all code |
| make lint | Lint all code |
| make test-be | Run backend tests |
| make migrate-up | Apply database migrations |
| make migrate-down | Rollback one migration |
| make migrate-create MSG='...' | Create new migration |
| make migrate-history | View migration history |
| make shell-be | Open backend shell |
| make shell-fe | Open frontend shell |
| make shell-db | Open database shell (psql) |
| make clean | Stop and remove volumes |

---

## 🗄️ Database Migrations

Alembic migrations manage schema. Apply them after starting the stack:

```bash
# View current migration status
make migrate-history

# Create a new migration (from repo root)
make migrate-create MSG='add_new_table'

# Apply pending migrations
make migrate-up

# Rollback one migration
make migrate-down
```

---

## 🔐 Authentication & Authorization

### How It Works

1. User clicks "Sign In" → Login page (credentials) or redirect to Keycloak if configured  
2. Backend validates credentials → Returns JWT to frontend  
3. Frontend stores token → NextAuth.js manages session  
4. API calls include token → Backend validates JWT  
5. Authorization engine checks → Rules in `authz.map.json`  

### Adding Protected Endpoints

In `backend/app/authz.map.json`:

```json
{
  "/api/my-endpoint": {
    "GET": ["ADMIN", "USER"],
    "POST": ["ADMIN"]
  }
}
```

In `backend/app/public.map.json` add paths that require no auth (e.g. `/health`, `/api/auth/login`).

### Adding Custom Audit Logs

```python
from app.services.audit import audit

await audit.log_user_action(
    db=db,
    action="user.approve",
    actor=current_user,
    target_user_id=user_id,
    target_user_email="john@example.com",
)
```

---

## ⚠️ Common Issues

| Problem | Solution |
|---------|----------|
| "OAuth error" or 401 when logging in | Clear cookies or use incognito; ensure NEXTAUTH_SECRET is set |
| API returns 401 | Check Authorization header is sent; token may be expired |
| AI features not working | Set GEMINI_API_KEY in `.env`; demo data loads without key |
| Frontend not updating after code changes | If using FRONTEND_TARGET=prod, rebuild: `docker compose build frontend` |
| Port already in use | Change FRONTEND_PORT / BACKEND_PORT in `.env` and restart |

---

## 🏁 Checklist for New Projects

- [ ] Clone template and rename repository  
- [ ] Update `.env` with new secrets (especially NEXTAUTH_SECRET and SECRET_KEY)  
- [ ] Add GEMINI_API_KEY for AI features  
- [ ] Update branding (logo, colors, company name)  
- [ ] Configure APPROVED_EMAIL_DOMAINS  
- [ ] Replace demo pages (Dashboard, Settings) with real data  
- [ ] Customize `authz.map.json` for your roles and endpoints  
- [ ] Change default admin password  
- [ ] Update this README for your project  
