# Place Review Analyzer

A full-stack application for analyzing place reviews from Naver.

For detailed architecture documentation, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## Overview

This project consists of:
- **Frontend**: Next.js 14 application running on port 5000
- **Backend**: FastAPI application running on port 8000
- **Database**: PostgreSQL

## Project Structure

```
backend/
  app/
    api/        - API routes (analyze, health, jobs, scrape)
    core/       - Core settings
    db/         - Database models and session
    jobs/       - Background job handling
    models/     - Pydantic models
    services/   - Business logic services
  alembic/      - Database migrations
  tests/        - Test files

frontend/
  app/          - Next.js app router pages
  lib/          - API client utilities
  hooks/        - React hooks (useJobStatus)
  store/        - Zustand state management
```

## Running the Application

The application is configured to run via the "Start application" workflow which:
1. Starts Redis server for job queue management
2. Starts RQ worker for background job processing
3. Starts the FastAPI backend on localhost:8000
4. Starts the Next.js frontend on 0.0.0.0:5000
5. Frontend proxies /api/* requests to the backend

## Environment Variables

- `APP_ENV`: Application environment (dev/prod)
- `DATABASE_URL`: PostgreSQL connection string (auto-configured)

## Recent Updates (2026-01-16)

### Input Simplification
- Changed from full URL input to place_id only input (e.g., `1414590796`)
- Backend constructs full URL from place_id: `https://m.place.naver.com/place/{place_id}`

### Date Range Mode
- Added DATE_RANGE mode with start_date and end_date for collecting reviews within a specific period
- DATE mode now uses start_date (reviews from that date onwards)
- Proper validation: start_date must be before or equal to end_date

### Previous Updates
- Replaced Selenium with Playwright for web scraping (better Replit compatibility)
- Installed system Chromium and required libraries via Nix
- Updated CSS selectors for current Naver Place page structure
- Added automatic navigation to review tab (`/review/visitor`)
- Multiple fallback selectors for robust review extraction

## Architecture Notes

- Frontend uses Next.js rewrites to proxy API calls to the backend
- Backend uses SQLAlchemy with psycopg for PostgreSQL connectivity
- The database URL is automatically converted from `postgresql://` to `postgresql+psycopg://` format
