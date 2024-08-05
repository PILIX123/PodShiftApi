#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Run Alembic migrations
alembic upgrade head

# Start the FastAPI application
exec "$@"
