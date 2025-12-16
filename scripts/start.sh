#!/bin/bash
set -e

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Create admin user (idempotent) - workaround for Render Free Tier
echo "Ensuring admin user exists..."
python scripts/create_admin.py "${ADMIN_USERNAME:-admin}" "${ADMIN_PASSWORD:-admin123}"

# Start server
echo "Starting server..."
# Use exec to replace the shell process with uvicorn (better signal handling)
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2 --loop auto
