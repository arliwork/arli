# ARLI Platform — Security Audit Checklist

## Pre-Deployment Security Review

### Authentication & Authorization
- [ ] JWT tokens use secure signing (HS256/RS256 with strong secrets)
- [ ] Token expiration set reasonably (access: 15min, refresh: 7d)
- [ ] Password hashing uses bcrypt with salt rounds >= 12
- [ ] Admin endpoints protected with role checks
- [ ] ICP principal verification on wallet-linked operations
- [ ] CORS restricted to known origins only

### Database Security
- [ ] SQL injection prevention via parameterized queries (SQLAlchemy)
- [ ] Sensitive fields encrypted at rest (API keys, private keys)
- [ ] Connection pooling with max connection limits
- [ ] Regular backup strategy configured
- [ ] No hardcoded credentials in source code

### API Security
- [ ] Rate limiting on public endpoints
- [ ] Input validation on all request bodies (Pydantic schemas)
- [ ] Output sanitization to prevent data leakage
- [ ] File upload restrictions (type, size, scan)
- [ ] WebSocket auth handshake before accepting connections

### Smart Contract (Canister) Security
- [ ] Admin authorization checks on mint/transfer/admin ops
- [ ] Reentrancy protection for payment flows
- [ ] Overflow/underflow protection (Rust natively safe)
- [ ] Access control: only experience registry can mint NFTs
- [ ] DDoS protection: compute/memory allocation limits set
- [ ] Cycles management: monitoring + auto-refill

### Infrastructure
- [ ] HTTPS/TLS on all endpoints
- [ ] Secrets managed via environment variables (never committed)
- [ ] Docker images scanned for vulnerabilities
- [ ] Network segmentation: DB not exposed publicly
- [ ] Logging and monitoring (fail2ban, prometheus, alerts)
- [ ] DDoS protection (Cloudflare or equivalent)

### Compliance
- [ ] GDPR: user data deletion endpoint
- [ ] Audit trail for all financial transactions
- [ ] Terms of Service and Privacy Policy pages
- [ ] KYC/AML flow for high-value transactions (if required)

## Deployment Environments

| Environment | Network | Canisters | Purpose |
|-------------|---------|-----------|---------|
| Local | local | all | Development |
| Staging | ic | all | Pre-production testing |
| Production | ic | all | Live users |

## Post-Deployment Monitoring
- [ ] Error tracking (Sentry)
- [ ] Uptime monitoring
- [ ] ICP canister cycle balance alerts
- [ ] Transaction volume anomaly detection
- [ ] Automated security scanning (weekly)
