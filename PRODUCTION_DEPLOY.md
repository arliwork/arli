# ARLI Production Deployment

## Prerequisites

```bash
# Required environment variables
cp .env.example .env
```

Edit `.env`:
```env
# Database
DB_USER=arli
DB_PASSWORD=secure_password_here
DB_NAME=arli_prod

# ICP (Internet Computer)
ICP_NETWORK=ic  # 'ic' for mainnet
ICP_PRIVATE_KEY=-----BEGIN EC PRIVATE KEY-----
...
-----END EC PRIVATE KEY-----
PLATFORM_PRINCIPAL=your-principal-here

# API Keys (Real)
OPENAI_API_KEY=sk-...
BINANCE_API_KEY=...
BINANCE_SECRET=...

# Canister IDs (after deployment)
EXPERIENCE_REGISTRY_CANISTER_ID=...
AGENT_NFT_CANISTER_ID=...
SKILLS_MARKETPLACE_CANISTER_ID=...
```

## Deploy ICP Canisters

```bash
# Install deps
npm install -g @icp-sdk/icp-cli

# Deploy to mainnet
icp deploy -e production

# Get canister IDs
icp canister list

# Update .env with canister IDs
```

## Deploy Backend

```bash
# Start everything
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f api

# Run migrations
docker-compose -f docker-compose.prod.yml exec api python -m alembic upgrade head
```

## Verify Deployment

```bash
# Health check
curl https://your-domain.com/health

# Check API
curl https://your-domain.com/api/agents

# Check ICP canister
dfx canister --network ic call experience_registry get_stats
```

## Monitoring

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Metrics
curl http://localhost:8000/metrics

# Database
psql $DATABASE_URL -c "SELECT COUNT(*) FROM agents;"
```

## Backup

```bash
# Database backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U arli arli_prod > backup.sql

# ICP state (stable memory is persistent, but backup IDs)
icp canister list > canister-backup.txt
```

## Troubleshooting

### API not responding
```bash
docker-compose -f docker-compose.prod.yml restart api
docker-compose -f docker-compose.prod.yml logs api
```

### Database issues
```bash
docker-compose -f docker-compose.prod.yml exec postgres psql -U arli -d arli_prod
```

### ICP canister out of cycles
```bash
icp cycles top-up 1000000000000 experience_registry -e production
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable SSL/TLS
- [ ] Configure firewall rules
- [ ] Set up monitoring alerts
- [ ] Enable rate limiting
- [ ] Review API keys (rotate regularly)
- [ ] Backup strategy tested

## Scaling

```bash
# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale workers=5

# Database connection pooling (already configured)
# Redis clustering for task queue (future)
```
