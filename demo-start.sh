#!/bin/bash

echo "🚀 ARLI Platform Demo Starter"
echo "=============================="
echo ""

# Check dependencies
echo "📋 Checking dependencies..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 20+"
    exit 1
fi

if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm not found. Installing..."
    npm install -g pnpm
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ pnpm version: $(pnpm --version)"
echo ""

# Check database
echo "🗄️  Checking database..."
if command -v psql &> /dev/null; then
    if pg_isready &> /dev/null; then
        echo "✅ PostgreSQL is running"
    else
        echo "⚠️  PostgreSQL not running. Starting..."
        service postgresql start 2>/dev/null || echo "Please start PostgreSQL manually"
    fi
else
    echo "⚠️  PostgreSQL not installed"
fi

# Check Redis
echo "💾 Checking Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis not running. Starting..."
        redis-server --daemonize yes 2>/dev/null || echo "Please start Redis manually"
    fi
else
    echo "⚠️  Redis not installed"
fi

echo ""
echo "📦 Installing dependencies..."
pnpm install

echo ""
echo "🔧 Setting up database..."
cd packages/database

# Create .env if not exists
if [ ! -f .env ]; then
    echo "DATABASE_URL=\"postgresql://postgres:postgres@localhost:5432/arli?schema=public\"" > .env
    echo "Created .env file"
fi

echo "Generating Prisma client..."
npx prisma generate

echo ""
echo "🚀 Starting development servers..."
echo ""
echo "  API will be available at: http://localhost:3100"
echo "  Web will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Start both servers
cd ../..
pnpm dev
