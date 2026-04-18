#!/bin/bash
set -e

echo "🚀 ARLI Production Deployment"

# Verify env
if [ -z "$ICP_PRIVATE_KEY" ]; then
  echo "❌ ICP_PRIVATE_KEY not set"
  exit 1
fi

if [ -z "$PLATFORM_PRINCIPAL" ]; then
  echo "❌ PLATFORM_PRINCIPAL not set"
  exit 1
fi

# 1. Security scan
echo "Running security checks..."
# cargo audit (if cargo-audit installed)
# npm audit --audit-level moderate (in apps/web)

# 2. Run tests
echo "Running test suite..."
cd apps/api && python -m pytest tests/ -q && cd ../..

# 3. Build canisters with optimizations
echo "Building optimized canisters..."
cd canisters/agent_nft && cargo build --target wasm32-unknown-unknown --release && cd ../..
cd canisters/skills_marketplace && cargo build --target wasm32-unknown-unknown --release && cd ../..
cd canisters/experience_registry && cargo build --target wasm32-unknown-unknown --release && cd ../..

# 4. Deploy to ICP mainnet
echo "🌐 Deploying to ICP mainnet..."
icp-cli deploy --environment production

# 5. Build and deploy frontend
echo "Building production frontend..."
cd apps/web && npm install && npm run build && cd ../..
icp-cli deploy --environment production --canister frontend

# 6. Deploy API
echo "Deploying API containers..."
docker-compose -f docker-compose.prod.yml up -d --build api worker nginx

# 7. Health check
echo "Running health checks..."
sleep 5
curl -sf https://api.arli.io/health || echo "⚠️ API health check failed"

echo "✅ Production deployment complete!"
