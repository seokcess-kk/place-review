# Place Review Analyzer - Architecture Document

## Overview

Place Review Analyzer is a full-stack application for scraping and analyzing place reviews from Naver. The system follows a clean separation of concerns with a Python backend (FastAPI), TypeScript frontend (Next.js), and background job processing (Redis + RQ).

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Job Queue**: Redis + RQ (Python Redis Queue)
- **Web Scraping**: Selenium + BeautifulSoup4
- **AI Analysis**: OpenAI API

### Frontend
- **Framework**: Next.js 14 (React 18)
- **State Management**: Zustand
- **Data Fetching**: TanStack React Query
- **Language**: TypeScript

### Infrastructure
- **Database**: PostgreSQL (Neon-backed on Replit)
- **Queue**: Redis (in-memory)
- **Deployment**: Replit Autoscale

## Directory Structure

```
/
├── backend/
│   ├── alembic/              # Database migrations
│   │   └── env.py
│   ├── app/
│   │   ├── api/              # API route handlers (Controllers)
│   │   │   ├── analyze.py    # Review analysis endpoints
│   │   │   ├── health.py     # Health check endpoint
│   │   │   ├── jobs.py       # Job management endpoints
│   │   │   └── scrape.py     # Scraping endpoints
│   │   ├── core/             # Core configuration
│   │   │   └── settings.py   # Environment settings
│   │   ├── db/               # Database layer
│   │   │   ├── base.py       # SQLAlchemy base
│   │   │   ├── crud.py       # CRUD operations
│   │   │   ├── models.py     # ORM models
│   │   │   └── session.py    # Database session management
│   │   ├── jobs/             # Background job definitions
│   │   │   ├── queue.py      # Redis queue configuration
│   │   │   └── tasks.py      # Job task functions
│   │   ├── models/           # Pydantic models (DTOs)
│   │   │   ├── analyze.py    # Analysis request/response models
│   │   │   ├── job.py        # Job request/response models
│   │   │   └── scrape.py     # Scrape request/response models
│   │   ├── services/         # Business logic layer
│   │   │   ├── analyzer.py   # Review analysis service
│   │   │   └── scraper.py    # Web scraping service
│   │   └── main.py           # FastAPI application entry point
│   ├── tests/                # Backend tests
│   │   ├── test_analyze.py
│   │   ├── test_health.py
│   │   ├── test_jobs.py
│   │   ├── test_scrape.py
│   │   └── test_settings.py
│   └── requirements.txt      # Python dependencies
│
├── frontend/
│   ├── app/                  # Next.js App Router
│   │   ├── layout.tsx        # Root layout
│   │   ├── page.tsx          # Home page
│   │   ├── providers.tsx     # React Query provider
│   │   └── globals.css       # Global styles
│   ├── hooks/                # Custom React hooks
│   │   └── useJobStatus.ts   # Job status polling hook
│   ├── lib/                  # Utility libraries
│   │   └── api.ts            # API client functions
│   ├── store/                # Zustand state stores
│   │   └── scrapeStore.ts    # Scrape form state
│   ├── package.json          # Node.js dependencies
│   └── next.config.js        # Next.js configuration
│
├── start.sh                  # Application startup script
├── replit.md                 # Replit-specific documentation
└── ARCHITECTURE.md           # This file
```

## Layer Responsibilities

### 1. API Layer (`backend/app/api/`)
- HTTP request handling and routing
- Request validation using Pydantic models
- Response serialization
- Error handling and HTTP status codes
- **Naming**: `{resource}.py` (e.g., `jobs.py`, `analyze.py`)

### 2. Service Layer (`backend/app/services/`)
- Business logic implementation
- External API integrations (OpenAI, Naver)
- Web scraping logic
- **Naming**: `{action}r.py` (e.g., `analyzer.py`, `scraper.py`)

### 3. Data Layer (`backend/app/db/`)
- ORM models and database schema
- CRUD operations
- Database session management
- **Naming**: Descriptive (e.g., `models.py`, `crud.py`, `session.py`)

### 4. Models Layer (`backend/app/models/`)
- Pydantic models for request/response validation
- Data Transfer Objects (DTOs)
- **Naming**: Match API resource names

### 5. Jobs Layer (`backend/app/jobs/`)
- Background task definitions
- Queue management
- Long-running operations

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/jobs` | Create a new scrape/analyze job |
| GET | `/jobs/{job_id}` | Get job status and result |
| POST | `/scrape` | Direct scrape request |
| POST | `/analyze` | Direct analyze request |

## Data Flow

```
[Frontend] → [Next.js API Proxy] → [FastAPI] → [Service Layer]
                                        ↓
                                   [Redis Queue]
                                        ↓
                                   [RQ Worker]
                                        ↓
                               [Scraper/Analyzer]
                                        ↓
                                  [PostgreSQL]
```

## Job Processing Flow

1. **Job Creation**: Frontend submits job request to `/jobs`
2. **Queue**: FastAPI enqueues job in Redis via RQ
3. **Processing**: RQ Worker picks up job and executes `scrape_and_analyze`
4. **Status Polling**: Frontend polls `/jobs/{job_id}` for status updates
5. **Completion**: Worker stores result, frontend displays to user

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `APP_ENV` | Application environment (dev/prod) | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `OPENAI_API_KEY` | OpenAI API key for analysis | For analysis |

## Coding Standards

### Python (Backend)
- Use type hints for all function signatures
- Follow PEP 8 style guidelines
- Use Pydantic for data validation
- Async functions for I/O operations

### TypeScript (Frontend)
- Strict TypeScript mode enabled
- Use functional components with hooks
- Prefer Zustand for global state
- Use React Query for server state

## Security Guidelines

- Environment variables for all secrets
- Input validation via Pydantic
- SQL injection prevention via SQLAlchemy ORM
- CORS configuration for API endpoints

## Testing Strategy

- **Backend**: pytest with httpx for API testing
- **Location**: `backend/tests/`
- **Naming**: `test_{module}.py`

## Future Roadmap

- [ ] Add user authentication
- [ ] Implement rate limiting
- [ ] Add result caching
- [ ] Support batch job processing
- [ ] Add export functionality (CSV/Excel)
