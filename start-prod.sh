#!/bin/bash
set -e

echo "[$(date)] Starting production deployment..."

echo "[$(date)] Starting Redis..."
mkdir -p /tmp/redis
redis-server --daemonize yes --dir /tmp/redis
echo "[$(date)] Redis started"

echo "[$(date)] Starting RQ worker..."
(cd backend && rq worker 2>&1 | while read line; do echo "[RQ] $line"; done) &

echo "[$(date)] Starting backend..."
(cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 2>&1 | while read line; do echo "[BACKEND] $line"; done) &

echo "[$(date)] Starting frontend on port 5000..."
cd frontend && exec npm run start
