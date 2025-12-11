#!/bin/bash
set -e

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Start server
echo "Starting server..."
# Use exec to replace the shell process with uvicorn (better signal handling)
exec uvicorn app.main:app --host 0.0.0.0 --port 80 --workers 2 --loop auto
