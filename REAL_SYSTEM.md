# ARLI Real System - No Mocks, No Demo

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     REAL SERVICES                           │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL (Neon/Supabase)                                 │
│  - agents table                                             │
│  - tasks table                                              │
│  - sales table                                              │
│  - users table                                              │
├─────────────────────────────────────────────────────────────┤
│  ICP Canisters (Mainnet)                                    │
│  - experience_registry: Real agent data                     │
│  - agent_nft: Real NFT ownership                            │
│  - skills_marketplace: Real purchases                       │
│  - icp_ledger: Real ICP transfers                           │
├─────────────────────────────────────────────────────────────┤
│  External APIs (Real)                                       │
│  - GPT-4 API                                                │
│  - Trading APIs (Binance, etc.)                             │
│  - Web scraping services                                    │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema (Real)

```sql
-- Real PostgreSQL schema
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    owner_principal TEXT NOT NULL,
    creator_principal TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    tier TEXT DEFAULT 'NOVICE',
    total_xp BIGINT DEFAULT 0,
    total_tasks INTEGER DEFAULT 0,
    successful_tasks INTEGER DEFAULT 0,
    total_revenue DECIMAL(20, 2) DEFAULT 0,
    market_value DECIMAL(20, 2) DEFAULT 50,
    hourly_rate DECIMAL(10, 2) DEFAULT 10,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_listed BOOLEAN DEFAULT FALSE,
    listing_price DECIMAL(20, 2)
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    category TEXT NOT NULL,
    description TEXT,
    success BOOLEAN,
    execution_time_seconds INTEGER,
    revenue_generated DECIMAL(20, 2),
    client_rating DECIMAL(2, 1),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE sales (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    seller_principal TEXT NOT NULL,
    buyer_principal TEXT NOT NULL,
    price DECIMAL(20, 2) NOT NULL,
    platform_fee DECIMAL(20, 2),
    creator_royalty DECIMAL(20, 2),
    seller_receives DECIMAL(20, 2),
    icp_tx_hash TEXT,
    status TEXT DEFAULT 'pending', -- pending, confirmed, failed
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP
);

CREATE TABLE users (
    principal TEXT PRIMARY KEY,
    display_name TEXT,
    email TEXT,
    total_spent DECIMAL(20, 2) DEFAULT 0,
    total_earned DECIMAL(20, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## ICP Canisters (Real)

### 1. Experience Registry (Production)
- Real principal authentication
- Real stable memory persistence
- Real cycle costs
- Real inter-canister calls

### 2. Agent NFT (DIP-721 Real)
- Real minting with ICP fees
- Real transfers with ownership validation
- Real metadata on-chain
- Real sale history

### 3. ICP Ledger Integration
- Real ICP transfers
- Real balance checking
- Real transaction confirmation
- Real fee calculation

## Task Execution (Real)

### Workers
```python
# Real task workers
- TradingWorker: Real API calls to exchanges
- ContentWorker: Real GPT-4 API calls
- ResearchWorker: Real web scraping
- AnalysisWorker: Real data processing
```

### Queue
- Redis/RabbitMQ for real task queue
- Real retry logic
- Real error handling
- Real monitoring

## Security (Real)

- All endpoints require valid Principal
- Rate limiting
- Input validation
- SQL injection protection
- CORS properly configured

## Monitoring (Real)

- Sentry for error tracking
- Prometheus metrics
- Real logging (not console.log)
- Uptime monitoring
