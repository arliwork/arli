#!/bin/bash
# ARLI Full Stack Startup Script (No Docker)
set -e

cd /home/paperclip/arli

echo "=== ARLI Startup ==="
echo "1. Checking PostgreSQL..."
if ! pg_isready -h 127.0.0.1 -p 5433 -U arli > /dev/null 2>&1; then
    echo "   ERROR: PostgreSQL not running on port 5433"
    exit 1
fi
echo "   OK"

echo "2. Checking Redis..."
if ! redis-cli -h 127.0.0.1 -p 6379 ping > /dev/null 2>&1; then
    echo "   ERROR: Redis not running on port 6379"
    exit 1
fi
echo "   OK"

echo "3. Starting Backend API..."
cd apps/api
pkill -f "uvicorn src.main:app" 2>/dev/null || true
PYTHONPATH=/home/paperclip/arli/apps/api/src venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-level info > /tmp/arli-api.log 2>&1 &
echo "   PID: $!"
cd ../..

echo "4. Starting Celery Worker..."
cd apps/api
pkill -f "celery -A src.celery_app worker" 2>/dev/null || true
source venv/bin/activate
PYTHONPATH=/home/paperclip/arli/apps/api/src celery -A src.celery_app worker --loglevel=info > /tmp/arli-worker.log 2>&1 &
echo "   PID: $!"
cd ../..

echo "5. Starting Celery Beat..."
cd apps/api
pkill -f "celery -A src.celery_app beat" 2>/dev/null || true
PYTHONPATH=/home/paperclip/arli/apps/api/src celery -A src.celery_app beat --loglevel=info > /tmp/arli-beat.log 2>&1 &
echo "   PID: $!"
cd ../..

echo "6. Starting Frontend..."
cd apps/web
pkill -f "npm run dev" 2>/dev/null || true
npm run dev > /tmp/arli-web.log 2>&1 &
echo "   PID: $!"
cd ../..

echo ""
echo "=== All services starting ==="
echo "API:     http://localhost:8000"
echo "Web:     http://localhost:3000"
echo "Swagger: http://localhost:8000/docs"
echo ""
echo "Waiting 8 seconds for startup..."
sleep 8

# Health check
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ API is healthy"
else
    echo "❌ API failed to start. Check /tmp/arli-api.log"
    exit 1
fi

echo ""
echo "=== Ready! ==="
echo "Logs:"
echo "  API:    tail -f /tmp/arli-api.log"
echo "  Worker: tail -f /tmp/arli-worker.log"
echo "  Beat:   tail -f /tmp/arli-beat.log"
echo "  Web:    tail -f /tmp/arli-web.log"
