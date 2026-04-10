# ARLI Production Setup

## 🚀 Quick Start

```bash
# 1. Clone and enter directory
cd arli

# 2. Configure environment
cp .env.example .env
# Edit .env with your real API keys and passwords

# 3. Start production
chmod +x start-production.sh
./start-production.sh
```

## 📋 Prerequisites

- Docker & Docker Compose
- Domain name (for SSL)
- API keys:
  - OpenAI API key
  - Anthropic API key (optional)
  - ICP identity (for blockchain)

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Nginx     │────▶│  Next.js    │────▶│  FastAPI    │
│   (SSL)     │     │  Frontend   │     │   API       │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                       ┌─────────────┐         │
                       │  PostgreSQL │◀────────┤
                       │   (Data)    │         │
                       └─────────────┘         │
                                                │
                       ┌─────────────┐         │
                       │    Redis    │◀────────┘
                       │ (Queue/Cache)│
                       └─────────────┘
```

## 📁 Services

| Service | Description | Port |
|---------|-------------|------|
| `postgres` | Main database | 5432 |
| `redis` | Cache & queues | 6379 |
| `api` | FastAPI backend | 8000 |
| `web` | Next.js frontend | 3000 |
| `worker` | Celery task workers | - |
| `nginx` | Reverse proxy | 80/443 |

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
# Required
DB_PASSWORD=secure_password
REDIS_PASSWORD=secure_password
OPENAI_API_KEY=sk-...
JWT_SECRET=random_string_32_chars

# Optional
ANTHROPIC_API_KEY=sk-ant-...
SENTRY_DSN=https://...
```

### SSL Certificates

Place your SSL certificates in `ssl/`:
```bash
ssl/
  ├── arli.crt
  └── arli.key
```

Or use Let's Encrypt:
```bash
certbot --nginx -d arli.io -d www.arli.io
```

## 🗃️ Database

### Migrations

```bash
# Create migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback
docker-compose exec api alembic downgrade -1
```

### Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U arli arli_prod > backup.sql

# Restore
docker-compose exec -T postgres psql -U arli arli_prod < backup.sql
```

## 📊 Monitoring

### Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
```

### Health Checks

```bash
curl http://localhost/health
curl http://localhost/api/health
```

## 🔄 Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up --build -d
```

## 🛡️ Security

- All sensitive data in `.env`
- SSL/TLS enabled
- Rate limiting on API
- No debug mode in production
- Database not exposed externally

## 🆘 Troubleshooting

### Database connection failed
```bash
docker-compose ps
docker-compose logs postgres
```

### API not responding
```bash
docker-compose restart api
docker-compose logs api
```

### Frontend blank page
```bash
docker-compose logs web
# Check browser console for errors
```

## 💰 Production Checklist

- [ ] SSL certificates configured
- [ ] Domain DNS pointing to server
- [ ] `.env` configured with real keys
- [ ] Database migrations applied
- [ ] Firewall configured (ports 80, 443 open)
- [ ] Backups scheduled
- [ ] Monitoring enabled (Sentry)
- [ ] Rate limiting tested

## 📞 Support

- GitHub Issues: https://github.com/arliwork/arli/issues
- Discord: [link]
- Email: support@arli.io
