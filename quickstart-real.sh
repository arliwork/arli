#!/bin/bash
set -e

echo "🚀 ARLI Real Integration Quickstart"
echo "===================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "📦 Step 1: Starting infrastructure (PostgreSQL + Redis)..."
docker-compose -f docker-compose.quickstart.yml up -d postgres redis

echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are healthy
echo "🔍 Checking PostgreSQL..."
until docker-compose -f docker-compose.quickstart.yml exec -T postgres pg_isready -U arli > /dev/null 2>&1; do
    echo "  Waiting for PostgreSQL..."
    sleep 2
done
echo "✅ PostgreSQL is ready"

echo "🔍 Checking Redis..."
until docker-compose -f docker-compose.quickstart.yml exec -T redis redis-cli ping > /dev/null 2>&1; do
    echo "  Waiting for Redis..."
    sleep 2
done
echo "✅ Redis is ready"

echo ""
echo "🗄️  Step 2: Setting up database..."
cd packages/database

# Create .env if not exists
if [ ! -f .env ]; then
    echo "DATABASE_URL=\"postgresql://arli:arli_dev_pass@localhost:5432/arli?schema=public\"" > .env
    echo "✅ Created .env file"
fi

echo "📊 Generating Prisma client..."
npx prisma generate

echo "🔄 Running migrations..."
npx prisma migrate dev --name init --skip-seed

echo "🌱 Seeding database..."
npx prisma db seed 2>/dev/null || echo "⚠️  No seed file found, skipping"

cd ../..

echo ""
echo "⚡ Step 3: Starting API server..."
cd apps/api

# Create .env if not exists
if [ ! -f .env ]; then
    cat > .env << EOF
DATABASE_URL=postgresql://arli:arli_dev_pass@localhost:5432/arli?schema=public
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET=dev-secret-key-change-in-production
PORT=3100
NODE_ENV=development
EOF
    echo "✅ Created API .env file"
fi

cd ../..

echo "🎯 Starting API on port 3100..."
nohup pnpm --filter api dev > /tmp/arli-api-real.log 2>&1 &
API_PID=$!

echo "🎯 Starting Dashboard on port 8080..."
nohup python3 -m http.server 8080 > /tmp/arli-web.log 2>&1 &
WEB_PID=$!

echo ""
echo "✅ ARLI Real Integration is starting up!"
echo ""
echo "📊 Services:"
echo "  • API:        http://localhost:3100"
echo "  • Dashboard:  http://localhost:8080/demo-dashboard.html"
echo "  • Database:   postgresql://arli:arli_dev_pass@localhost:5432/arli"
echo "  • Redis:      redis://localhost:6379"
echo ""
echo "📋 Next steps:"
echo "  1. Open dashboard: http://localhost:8080/demo-dashboard.html"
echo "  2. Test API: curl http://localhost:3100/health"
echo "  3. View logs: tail -f /tmp/arli-api-real.log"
echo ""
echo "🛑 To stop:"
echo "  kill $API_PID $WEB_PID"
echo "  docker-compose -f docker-compose.quickstart.yml down"
echo ""

# Wait a bit and check if API is up
sleep 3
if curl -s http://localhost:3100/health > /dev/null 2>&1; then
    echo "✅ API is responding!"
else
    echo "⏳ API is starting... check logs: tail -f /tmp/arli-api-real.log"
fi
