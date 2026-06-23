# Employee Management System

A production-ready, full-stack **Employee Management System** with a **FastAPI** backend and **React** frontend. It provides JWT authentication, role-based access control (RBAC), employee CRUD with soft delete, Redis caching, Celery background tasks, audit logging, and Prometheus metrics.

**Repository:** [github.com/sudarshantanwer/Employee-Management-System](https://github.com/sudarshantanwer/Employee-Management-System)

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start-docker)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Role-Based Access Control](#role-based-access-control)
- [Frontend](#frontend)
- [Testing](#testing)
- [MongoDB Compass](#mongodb-compass)
- [Observability](#observability)
- [Security Notes](#security-notes)
- [License](#license)

---

## Features

### Backend
- **JWT Authentication** — access tokens (15 min) and refresh tokens (7 days)
- **Token Blacklisting** — Redis-backed logout invalidation
- **RBAC Authorization** — `ADMIN`, `MANAGER`, `EMPLOYEE` roles with permission dependencies
- **Employee CRUD** — create, read, update, soft delete
- **Search & Filtering** — pagination, full-text search, department filter, sorting
- **Redis Caching** — employee list cached for 5 minutes with automatic invalidation
- **Audit Logging** — tracks login, logout, and employee mutations
- **Celery Tasks** — welcome email, password reset email, audit processing (simulated)
- **Centralized Error Handling** — standardized JSON error responses
- **Health Checks** — MongoDB, Redis, and application status
- **Prometheus Metrics** — request count, duration, errors, active requests
- **Structured Logging** — Loguru with console and file output (`logs/app.log`)

### Frontend
- **React + TypeScript + Tailwind CSS** — modern, responsive UI
- **Auth flows** — login, register, logout with automatic token refresh
- **Role-aware UI** — features shown/hidden based on user role
- **Employee management** — table view with search, filters, pagination, create/edit/delete modals
- **Dashboard** — user profile summary and live system health status

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.13, FastAPI, Pydantic v2, Motor (async MongoDB) |
| **Auth** | JWT (python-jose), Passlib + bcrypt |
| **Cache / Queue** | Redis, Celery |
| **Database** | MongoDB |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Axios, React Router |
| **DevOps** | Docker, Docker Compose |
| **Testing** | Pytest, pytest-asyncio, httpx |
| **Observability** | Loguru, Prometheus |

---

## Architecture

The backend follows a **Repository–Service pattern** with clear separation of concerns:

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  React UI   │────▶│  API Layer  │────▶│  Service Layer   │────▶│ Repository  │
│  (Vite)     │     │  (FastAPI)  │     │  (Business Logic)│     │  (Motor)    │
└─────────────┘     └─────────────┘     └──────────────────┘     └──────┬──────┘
                           │                      │                      │
                           │                      ▼                      ▼
                           │               ┌──────────────┐       ┌─────────────┐
                           │               │    Redis     │       │   MongoDB   │
                           │               │ Cache/Blacklist│     │  users      │
                           │               └──────────────┘       │  employees  │
                           │                      │               │  audit_logs │
                           ▼                      ▼               └─────────────┘
                    ┌─────────────┐       ┌──────────────┐
                    │  Middleware │       │    Celery    │
                    │ Logging/Metrics│     │  Background  │
                    └─────────────┘       └──────────────┘
```

**Request flow:**
1. Request passes through Request ID → Logging → Prometheus middleware
2. JWT validated; token blacklist checked in Redis
3. RBAC dependency enforces role/permission
4. Service layer applies business rules, caching, and audit logging
5. Repository layer performs MongoDB operations

---

## Project Structure

```
Employee-Management-System/
├── app/                          # FastAPI backend
│   ├── main.py                   # Application entry point
│   ├── api/v1/                   # API routes (auth, employees, health)
│   ├── core/                     # Config, database, redis, security, celery
│   ├── models/                   # Domain models and enums
│   ├── schemas/                  # Pydantic request/response schemas
│   ├── repositories/             # MongoDB data access layer
│   ├── services/                 # Business logic layer
│   ├── dependencies/             # Auth and RBAC dependencies
│   ├── middleware/               # Request ID, logging, Prometheus
│   ├── tasks/                    # Celery background tasks
│   ├── utils/                    # Shared helpers
│   └── tests/                    # Pytest test suite
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── api/                  # Axios client and API calls
│   │   ├── context/              # Auth context provider
│   │   ├── components/           # Reusable UI components
│   │   ├── pages/                # Route pages
│   │   └── types/                # TypeScript interfaces
│   └── package.json
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

---

## Prerequisites

- **Docker & Docker Compose** (recommended), or:
- **Python 3.13+**
- **Node.js 20+** and npm
- **MongoDB 7+** (running locally or via Docker)
- **Redis 7+** (running locally or via Docker)

---

## Quick Start (Docker)

The fastest way to run the entire backend stack:

```bash
# Clone the repository
git clone https://github.com/sudarshantanwer/Employee-Management-System.git
cd Employee-Management-System

# Configure environment
cp .env.example .env
# Edit .env — set strong JWT secrets before production use

# Start all services
docker compose up --build
```

### Docker Services

| Service | URL | Description |
|---------|-----|-------------|
| **FastAPI** | http://localhost:8000 | REST API |
| **Swagger UI** | http://localhost:8000/docs | Interactive API docs |
| **ReDoc** | http://localhost:8000/redoc | Alternative API docs |
| **Mongo Express** | http://localhost:8081 | MongoDB web UI (admin / admin123) |
| **MongoDB** | localhost:27017 | Database |
| **Redis** | localhost:6379 | Cache & message broker |

Then start the frontend separately:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend: **http://localhost:5173**

---

## Local Development

### Backend

```bash
# Create and activate virtual environment
python3.13 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (use localhost URLs for local dev)
cp .env.example .env
```

For local development, update `.env`:

```env
MONGO_URI=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

```bash
# Start API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start Celery worker (separate terminal)
celery -A app.core.celery_app.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Set `VITE_API_URL=http://localhost:8000` in `frontend/.env`.

### Production Build (Frontend)

```bash
cd frontend
npm run build
npm run preview    # Preview production build at http://localhost:4173
```

---

## Environment Variables

### Backend (`.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application display name | `Employee Management System` |
| `APP_ENV` | Environment (`development`, `staging`, `production`) | `development` |
| `DEBUG` | Debug mode | `false` |
| `LOG_LEVEL` | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | MongoDB database name | `employee_management` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | Secret for access token signing | **Required — change in production** |
| `JWT_REFRESH_SECRET_KEY` | Secret for refresh token signing | **Required — change in production** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `CELERY_BROKER_URL` | Celery broker (Redis) | `redis://localhost:6379/1` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://localhost:6379/2` |

### Frontend (`frontend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` |

---

## API Reference

All API responses follow a standard envelope:

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {}
}
```

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/v1/auth/register` | Register new user (EMPLOYEE role) | No |
| `POST` | `/api/v1/auth/login` | Login and receive JWT tokens | No |
| `POST` | `/api/v1/auth/refresh` | Refresh access token | No |
| `POST` | `/api/v1/auth/logout` | Blacklist tokens | Yes |

**Login example:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "AdminPass123!"}'
```

### Employees

| Method | Endpoint | Description | Required Role |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/employees` | List employees (paginated) | ADMIN, MANAGER |
| `GET` | `/api/v1/employees/{id}` | Get employee by ID | ADMIN, MANAGER, or own profile |
| `POST` | `/api/v1/employees` | Create employee | ADMIN, MANAGER |
| `PUT` | `/api/v1/employees/{id}` | Update employee | ADMIN, MANAGER |
| `DELETE` | `/api/v1/employees/{id}` | Soft delete employee | ADMIN |

**Query parameters for list:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (default: 1) |
| `limit` | int | Items per page (default: 10, max: 100) |
| `search` | string | Search name, email, department, designation |
| `department` | string | Filter by department |
| `sort` | string | Sort field: `name`, `email`, `department`, `salary`, `created_at` |

**Create employee example:**

```bash
curl -X POST http://localhost:8000/api/v1/employees \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@company.com",
    "department": "IT",
    "designation": "Senior Developer",
    "salary": 95000
  }'
```

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (MongoDB, Redis, app status) |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc documentation |

---

## Role-Based Access Control

| Permission | ADMIN | MANAGER | EMPLOYEE |
|------------|:-----:|:-------:|:--------:|
| View all employees | ✅ | ✅ | ❌ |
| View own profile | ✅ | ✅ | ✅ |
| Create employee | ✅ | ✅ | ❌ |
| Update employee | ✅ | ✅ | ❌ |
| Delete employee | ✅ | ❌ | ❌ |
| Manage users | ✅ | ❌ | ❌ |

**Roles are enforced via FastAPI dependencies:**

```python
from app.dependencies.rbac import require_role, require_permission
from app.models.enums import Role, Permission

@router.delete("/employees/{id}", dependencies=[Depends(require_role(Role.ADMIN))])
async def delete_employee(...): ...

@router.post("/employees", dependencies=[Depends(require_permission(Permission.CREATE_EMPLOYEE))])
async def create_employee(...): ...
```

**Creating ADMIN/MANAGER users:** Self-registration only allows the `EMPLOYEE` role. To create admin or manager accounts, insert users directly via MongoDB or use the Swagger UI at `/docs` with an existing admin token.

---

## Frontend

### Pages

| Route | Description | Access |
|-------|-------------|--------|
| `/login` | Sign in | Public |
| `/register` | Create account (EMPLOYEE) | Public |
| `/dashboard` | Overview and system health | Authenticated |
| `/employees` | Employee list and CRUD | ADMIN, MANAGER |

### Auth Flow

1. User logs in → access + refresh tokens stored in `localStorage`
2. Axios interceptor attaches `Authorization: Bearer <token>` to every request
3. On `401`, the client automatically refreshes tokens and retries
4. Logout blacklists both tokens server-side and clears local storage

---

## Testing

Tests require MongoDB and Redis running locally (or via Docker):

```bash
# Ensure MongoDB and Redis are running
docker compose up mongodb redis -d

# Run all tests
source .venv/bin/activate
pytest app/tests/ -v

# Run with coverage
pytest app/tests/ -v --cov=app --cov-report=term-missing
```

**Test coverage includes:**
- Authentication (register, login, refresh, logout, token blacklist)
- Authorization (role-based access for all CRUD operations)
- Employee CRUD (create, list, search, filter, update, soft delete)

---

## MongoDB Compass

[MongoDB Compass](https://www.mongodb.com/products/compass) is the official GUI for browsing and querying your local database visually.

### Option 1 — One-command launcher (recommended)

```bash
# Make script executable (first time only)
chmod +x scripts/compass.sh

# Verify MongoDB is running and open Compass
./scripts/compass.sh
```

Install Compass if you don't have it yet:

```bash
./scripts/compass.sh --install    # macOS via Homebrew
# Or download: https://www.mongodb.com/try/download/compass
```

### Option 2 — Import saved connection

1. Open **MongoDB Compass**
2. Click **Connect** → **Import saved connections**
3. Select: `config/compass/ems-local.connections.json`
4. Click **Connect** on **EMS - Local (employee_management)**

### Option 3 — Manual connection string

Paste this URI in Compass:

```
mongodb://localhost:27017/employee_management
```

### What you'll see

| Collection | Contents |
|------------|----------|
| `users` | Registered users, hashed passwords, roles |
| `employees` | Employee records (name, email, department, salary, etc.) |
| `audit_logs` | Login, logout, and CRUD audit entries |

### Ensure MongoDB is running first

```bash
# Check connection
mongosh --eval "db.runCommand({ ping: 1 })"

# Start via Homebrew
brew services start mongodb-community

# Or start via Docker
docker compose up mongodb -d
```

### Docker vs local Compass URI

| Setup | Compass connection string |
|-------|--------------------------|
| MongoDB via Homebrew | `mongodb://localhost:27017/employee_management` |
| MongoDB via Docker Compose | `mongodb://localhost:27017/employee_management` |

Both expose port `27017` on localhost, so the Compass URI is the same.

---

## Observability

### Logging

Logs are written to:
- **Console** — colored output with request ID and user ID
- **File** — `logs/app.log` (rotates at 10 MB, retained 30 days)

Every request logs: `request_id`, `method`, `path`, `status_code`, `duration_ms`, `user_id`.

### Prometheus Metrics

Available at `GET /metrics`:

| Metric | Description |
|--------|-------------|
| `http_requests_total` | Total HTTP requests by method, endpoint, status |
| `http_request_duration_seconds` | Request latency histogram |
| `http_errors_total` | Error responses (4xx/5xx) |
| `http_active_requests` | Currently in-flight requests |

### Audit Trail

All significant actions are recorded in the `audit_logs` MongoDB collection:

| Action | Trigger |
|--------|---------|
| `LOGIN` | User authentication |
| `LOGOUT` | User logout |
| `CREATE_EMPLOYEE` | New employee created |
| `UPDATE_EMPLOYEE` | Employee record updated |
| `DELETE_EMPLOYEE` | Employee soft deleted |
| `ROLE_CHANGE` | User role modified |

---

## Security Notes

- **Change JWT secrets** in production — never use default values from `.env.example`
- **`.env` files are gitignored** — never commit secrets to the repository
- Passwords are hashed with **bcrypt** via Passlib
- Tokens are **blacklisted in Redis** on logout and checked on every authenticated request
- Self-registration is restricted to the **EMPLOYEE** role only
- Mongo Express default credentials (`admin` / `admin123`) should be changed or disabled in production

---

## License

This project is open source and available for personal and educational use.

---

## Author

**Sudarshan Tanwer** — [GitHub](https://github.com/sudarshantanwer)
