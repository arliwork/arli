# 🚀 ARLI - Autonomous Revenue & Labor Intelligence

**Create and run AI-powered autonomous companies**

ARLI is a platform where anyone can create fully autonomous companies that operate 24/7 with AI agents. Think of it as "AWS for AI Companies" - you bring the business idea, ARLI provides the AI workforce, infrastructure, and monetization.

## 🎯 Vision

The future of work is autonomous. ARLI enables:
- **AI-powered companies** that run without human intervention
- **Revenue sharing** model where platform earns 10% of company revenue
- **Skills marketplace** for buying/selling agent capabilities
- **Company templates** for instant business launch

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        ARLI PLATFORM                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🎨 FRONTEND (Next.js 14)                                  │
│  ├── Landing page                                          │
│  ├── Dashboard                                             │
│  ├── Company Builder                                       │
│  └── Skills Marketplace                                    │
│                                                             │
│  ⚡ BACKEND (Fastify + Node.js)                            │
│  ├── Company Service (CRUD, orchestration)                 │
│  ├── Agent Runtime (heartbeat, execution)                  │
│  ├── Billing Service (credits, Stripe)                     │
│  └── Revenue Share Engine                                  │
│                                                             │
│  🗄️ DATABASE (PostgreSQL + Prisma)                         │
│  ├── Companies, Agents, Tickets                            │
│  ├── Transactions, Revenue Logs                            │
│  └── Skills Registry                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 💰 Business Model

### Revenue Streams:
1. **Platform Fee (10%)** - On every transaction in autonomous companies
2. **Compute Credits** - Users buy credits to run agents ($1 = 100 credits)
3. **Skills Marketplace** - 30% commission on skill sales
4. **Premium Templates** - One-time setup fees ($199-499)

### Unit Economics:
- User pays: $100 for 10,000 credits
- AWS cost: $20 (compute)
- **Gross margin: 80%**

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- pnpm 9+
- PostgreSQL 15+

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/arli.git
cd arli

# Install dependencies
pnpm install

# Setup database
cp packages/database/.env.example packages/database/.env
# Edit DATABASE_URL in .env
pnpm db:migrate
pnpm db:seed

# Setup API
cp apps/api/.env.example apps/api/.env
# Edit environment variables

# Run development servers
pnpm dev
```

### Services:
- **Web**: http://localhost:3000
- **API**: http://localhost:3100
- **API Docs**: http://localhost:3100/docs

## 📁 Project Structure

```
arli/
├── apps/
│   ├── api/           # Fastify backend API
│   └── web/           # Next.js frontend
├── packages/
│   ├── database/      # Prisma schema & client
│   └── types/         # Shared TypeScript types
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

## 🛠️ Development

### Commands:
```bash
# Run everything
pnpm dev

# Database operations
pnpm db:migrate      # Run migrations
pnpm db:studio       # Open Prisma Studio
pnpm db:seed         # Seed database

# Build for production
pnpm build

# Type checking
pnpm typecheck
```

## 📊 Database Schema

### Core Entities:
- **User** - Platform users (company owners)
- **Company** - Autonomous AI companies
- **Agent** - AI workers with specific roles
- **Ticket** - Tasks assigned to agents
- **Skill** - Reusable capabilities for agents
- **Transaction** - Credit purchases and usage
- **RevenueLog** - Revenue tracking for fees

## 🎯 Roadmap

### Phase 1: MVP (Month 1-2)
- [x] Project structure
- [x] Database schema
- [x] Basic API endpoints
- [x] Landing page
- [x] Dashboard UI
- [ ] Heartbeat system
- [ ] Claude Code integration
- [ ] Stripe payments

### Phase 2: Beta (Month 3)
- [ ] Skills marketplace
- [ ] Company templates
- [ ] Mobile app
- [ ] Analytics dashboard
- [ ] 100 beta users

### Phase 3: Scale (Month 4-6)
- [ ] ICP integration (blockchain)
- [ ] Tokenization
- [ ] Governance (DAO)
- [ ] 1000+ companies

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md)

## 📄 License

MIT © 2026 ARLI

---

**Built for the autonomous future.** 🚀