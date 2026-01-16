# Place Review Analyzer

A full-stack application for analyzing place reviews from Naver.

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
1. Starts the FastAPI backend on localhost:8000
2. Starts the Next.js frontend on 0.0.0.0:5000
3. Frontend proxies /api/* requests to the backend

## Environment Variables

- `APP_ENV`: Application environment (dev/prod)
- `DATABASE_URL`: PostgreSQL connection string (auto-configured)

## Architecture Notes

- Frontend uses Next.js rewrites to proxy API calls to the backend
- Backend uses SQLAlchemy with psycopg for PostgreSQL connectivity
- The database URL is automatically converted from `postgresql://` to `postgresql+psycopg://` format
