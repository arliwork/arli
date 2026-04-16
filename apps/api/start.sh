#!/bin/bash
set -e
cd "$(dirname "$0")"

# Run migrations
python -m alembic upgrade head

# Start API
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
