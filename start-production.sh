#!/bin/bash
set -e

echo "🚀 Starting ARLI Production Environment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and fill in your credentials:"
    echo "  cp .env.example .env"
    exit 1
fi

# Create necessary directories
mkdir -p logs ssl

# Pull latest images
echo "📦 Pulling Docker images..."
docker-compose -f docker-compose.prod.yml pull

# Build and start services
echo "🏗️ Building and starting services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for database
echo "⏳ Waiting for database..."
sleep 10

# Run migrations
echo "🗃️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head || true

# Health check
echo "🏥 Checking service health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo "✅ API is healthy!"
        break
    fi
    echo "  Waiting for API... ($i/30)"
    sleep 2
done

echo ""
echo "🎉 ARLI Production is running!"
echo ""
echo "📊 Access points:"
echo "  - Frontend: http://localhost (or your domain)"
echo "  - API: http://localhost/api"
echo "  - Health: http://localhost/health"
echo ""
echo "📝 Logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 To stop:"
echo "  docker-compose -f docker-compose.prod.yml down"
