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

## Deployment

### Scripts
- `build.sh`: 빌드 스크립트 (Python 의존성 + Playwright + 프론트엔드 빌드)
- `start-prod.sh`: 프로덕션 실행 스크립트 (Redis + RQ 워커 + 백엔드 + 프론트엔드)
- `start.sh`: 개발 환경 실행 스크립트

### Deployment Configuration
- **타입**: VM (백그라운드 프로세스 필요)
- **빌드**: `bash ./build.sh`
- **실행**: `bash ./start-prod.sh`

## Deployment Troubleshooting

### 오류 기록 및 해결 방법

| 오류 | 원인 | 해결 방법 |
|------|------|-----------|
| `package.json not found in workspace root` | `bash -c "cd frontend && npm..."` 구문에서 서브쉘 컨텍스트 유실 | 별도 빌드 스크립트(`build.sh`) 생성하여 `cd` 후 명령 실행 |
| `npm ci lockfileVersion 3 requires npm >= 7` | 배포 환경의 npm 버전 호환성 문제 | `npm ci` 대신 `npm install` 사용 |
| `localhost binding not accessible` | 배포 환경에서 외부 헬스체크 불가 | 백엔드를 `0.0.0.0`으로 바인딩 |
| `npm --prefix frontend ci invalid syntax` | 일부 환경에서 `--prefix` 구문 지원 안됨 | `cd frontend && npm...` 또는 서브쉘 `(cd frontend && npm...)` 사용 |
| `working directory context lost` | bash 명령에서 `cd` 후 컨텍스트 유실 | 서브쉘 `()` 사용: `(cd backend && uvicorn ...) &` |

### 배포 시 체크리스트
1. 백엔드가 `0.0.0.0`에 바인딩되어 있는지 확인
2. 빌드 스크립트에서 Python 의존성 설치 포함 여부 확인
3. Playwright 브라우저 설치 (`playwright install chromium`) 포함 여부 확인
4. 프론트엔드가 프로덕션 모드(`npm run start`)로 실행되는지 확인
5. Redis 서버 시작이 실행 스크립트에 포함되어 있는지 확인
