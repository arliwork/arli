# ARLI Platform - ICP Deployment Guide

## 🚀 Quick Start

Deploy ARLI on Internet Computer in 5 minutes.

## Prerequisites

```bash
# Install ICP CLI
npm install -g @icp-sdk/icp-cli @icp-sdk/ic-wasm

# Install Rust target
rustup target add wasm32-unknown-unknown

# Verify installation
icp --version  # Should show >= 0.2.0
```

## Deployment Steps

### 1. Local Development

```bash
# Start local network
icp network start -d

# Build all canisters
icp build

# Deploy to local
icp deploy -e local

# Get canister IDs
icp canister list
```

### 2. Mainnet Deployment

```bash
# Create identity (if not exists)
icp identity new mainnet-deployer
icp identity default mainnet-deployer

# Get principal
icp identity principal

# Fund with ICP (via NNS or exchange)
# Then convert to cycles

# Deploy to staging first
icp deploy -e staging

# Then production
icp deploy -e production
```

## Architecture

### Canisters

| Canister | Purpose | Memory |
|----------|---------|--------|
| `experience_registry` | Agent XP, levels, marketplace | 1-2GB |
| `skills_marketplace` | Skill packages, purchases | 1-2GB |
| `agent_nft` | NFT ownership, transfers | 512MB |
| `frontend` | Next.js app (asset canister) | dynamic |

### Data Flow

```
User → Frontend (Asset Canister)
  ↓
Experience Registry (Agent data, XP)
  ↓
Skills Marketplace (Purchases)
  ↓
Agent NFT (Ownership)
```

## Configuration

### `icp.yaml`

```yaml
name: arli-platform
version: 0.1.0

environments:
  - name: production
    network: ic
    canisters: [experience_registry, skills_marketplace, agent_nft, frontend]
    settings:
      experience_registry:
        compute_allocation: 20
        memory_allocation: 2GB
```

## NFT Integration

Agents are represented as NFTs with metadata:

```json
{
  "name": "Crypto Trader Pro",
  "description": "Level 5 EXPERT Agent with 150 tasks",
  "level": 5,
  "tier": "EXPERT",
  "market_value": 250000,
  "attributes": {
    "Success Rate": "94.5%",
    "Total Revenue": "$12,450.00",
    "Domains": "trading, analysis"
  }
}
```

## Wallet Integration

### Supported Wallets

- Internet Identity
- Plug Wallet
- Stoic Wallet
- OISY Wallet

### Connection Example

```typescript
import { AuthClient } from '@dfinity/auth-client';

const authClient = await AuthClient.create();
await authClient.login({
  identityProvider: 'https://identity.ic0.app',
  onSuccess: () => {
    // Connected!
  }
});
```

## Cost Estimation

### Cycles Required

| Operation | Cycles |
|-----------|--------|
| Deploy canister | 100B |
| Store 1GB data | 127K/s |
| Query call | 0 (free) |
| Update call | 590K |

### Monthly Estimates

| Tier | Storage | Compute | Total |
|------|---------|---------|-------|
| Starter | 1GB | 5% | $5/mo |
| Growth | 5GB | 15% | $25/mo |
| Enterprise | 20GB | 50% | $100/mo |

## Monitoring

```bash
# Check canister status
icp canister status experience_registry -e production

# Get logs
icp canister logs experience_registry

# Monitor cycles
icp cycles balance
```

## Security

### Access Control

```rust
#[update]
fn sensitive_operation() {
    let caller = ic_cdk::caller();
    assert!(is_authorized(caller));
    // ...
}
```

### Best Practices

1. Never hardcode principals
2. Use stable memory for persistence
3. Validate all inputs
4. Rate limit expensive operations
5. Monitor cycles usage

## Troubleshooting

### Common Issues

**Out of cycles:**
```bash
icp cycles top-up 1000000000000 experience_registry -e production
```

**Canister frozen:**
```bash
icp canister unfreeze experience_registry -e production
```

**Build fails:**
```bash
# Clean and rebuild
rm -rf .icp/cache
icp build
```

## Mainnet URLs

After deployment:

- Frontend: `https://<canister-id>.ic0.app`
- API: `https://icp-api.io`

## Next Steps

1. ✅ Deploy to ICP
2. 🔄 Configure custom domain
3. 🔄 Add monitoring (sentry/alerts)
4. 🔄 Token economics (ARLI token)
5. 🔄 DAO governance

## Resources

- [ICP Documentation](https://internetcomputer.org/docs)
- [icp-cli Reference](https://cli.internetcomputer.org)
- [Rust CDK Guide](https://docs.rs/ic-cdk)

---

**Status:** Ready for mainnet deployment 🚀
