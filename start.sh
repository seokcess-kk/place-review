#!/bin/bash

mkdir -p /tmp/redis

redis-server --daemonize yes --dir /tmp/redis

cd backend && rq worker &

cd backend && uvicorn app.main:app --host localhost --port 8000 &

cd frontend && npm run dev &

wait
