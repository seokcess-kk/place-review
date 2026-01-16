#!/bin/bash

mkdir -p /tmp/redis

redis-server --daemonize yes --dir /tmp/redis

sleep 2

(cd backend && rq worker) &

(cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000) &

sleep 3

(cd frontend && npm run start) &

wait
