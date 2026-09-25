#!/usr/bin/env bash

set -e

echo "Waiting for postgres..."

while !</dev/tcp/db/5432; do
    sleep 1
done

echo "Running migrations..."

alembic upgrade head

echo "Starting app..."

# exec uvicorn app.main:app --host 0.0.0.0 --port 8000
exec "$@"