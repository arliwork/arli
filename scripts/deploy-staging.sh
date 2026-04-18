#!/bin/bash
set -e

echo "🚀 ARLI Staging Deployment"

# 1. Build canisters
echo "Building Rust canisters..."
cd canisters/agent_nft && cargo build --target wasm32-unknown-unknown --release && cd ../..
cd canisters/skills_marketplace && cargo build --target wasm32-unknown-unknown --release && cd ../..
cd canisters/experience_registry && cargo build --target wasm32-unknown-unknown --release && cd ../..

# 2. Deploy to ICP staging
echo "Deploying to ICP staging..."
icp-cli deploy --environment staging

# 3. Build frontend
echo "Building Next.js frontend..."
cd apps/web && npm install && npm run build && cd ../..

# 4. Deploy frontend canister
echo "Deploying frontend..."
icp-cli deploy --environment staging --canister frontend

# 5. Update env
echo "Updating environment variables..."
cp .env.staging apps/api/src/.env

# 6. Deploy API (Docker)
echo "Deploying API to staging..."
docker-compose -f docker-compose.prod.yml up -d --build api worker

echo "✅ Staging deployment complete!"
