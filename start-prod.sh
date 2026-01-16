#!/bin/bash

mkdir -p /tmp/redis

redis-server --daemonize yes --dir /tmp/redis &

(cd backend && rq worker) &

(cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000) &

cd frontend && exec npm run start
