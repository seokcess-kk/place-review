# Backend

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment
Copy `.env.example` to `.env` and adjust values.

## Run (local)
```bash
APP_ENV=local uvicorn app.main:app --reload
```

## Test
```bash
APP_ENV=test pytest
```
