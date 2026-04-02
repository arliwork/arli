# 🚀 ARLI - Autonomous Revenue & Labor Intelligence

[![npm](https://img.shields.io/npm/v/arliwork)](https://www.npmjs.com/package/arliwork)
[![GitHub](https://img.shields.io/github/license/arliwork/arli)](https://github.com/arliwork/arli/blob/main/LICENSE)
[![Node.js](https://img.shields.io/badge/node-%3E%3D18-brightgreen)](https://nodejs.org/)

**Create and run AI-powered autonomous companies**

ARLI is a platform where anyone can create fully autonomous companies that operate 24/7 with AI agents. Think of it as "AWS for AI Companies" - you bring the business idea, ARLI provides the AI workforce, infrastructure, and monetization.

## 🚀 Quick Start

```bash
# Create new AI company with one command
npx arliwork init my-agency
cd my-agency
arli dev
```

That's it! Your autonomous company platform is running at:
- 🎨 **Web**: http://localhost:3000
- ⚡ **API**: http://localhost:3100
- 📚 **Docs**: http://localhost:3100/docs

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
│  🤖 AI INTEGRATION                                         │
│  ├── OpenRouter (Multi-provider AI)                        │
│  ├── Claude, GPT-4, Gemini, Llama                          │
│  └── Agent task execution                                  │
│                                                             │
│  🗄️ DATABASE (PostgreSQL + Prisma + Redis)                 │
│  ├── Companies, Agents, Tickets                            │
│  ├── Transactions, Revenue Logs                            │
│  └── Bull Task Queues                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 💰 Business Model

### Revenue Streams:
1. **Platform Fee (10%)** - On every transaction in autonomous companies
2. **Compute Credits** - Users buy credits to run agents ($1 = 100 credits)
3. **Skills Marketplace** - 30% commission on skill sales
4. **Premium Templates** - One-time setup fees ($199-499)

## 📦 Installation

### Using CLI (Recommended)

```bash
# Install globally
npm install -g arliwork

# Or use npx (no install)
npx arliwork init my-platform

# Start development
arli dev
```

### Manual Installation

```bash
# Clone the repo
git clone https://github.com/arliwork/arli.git
cd arli

# Install dependencies
pnpm install

# Setup environment
cp apps/web/.env.local.example apps/web/.env.local
cp apps/api/.env.example apps/api/.env
cp packages/database/.env.example packages/database/.env

# Edit environment variables with your API keys

# Run migrations
pnpm db:migrate
pnpm db:seed

# Start development
pnpm dev
```

## 🛠️ CLI Commands

```bash
arli init [project-name]    # Initialize new project
arli dev                    # Start development server
arli start                  # Start production server
arli deploy                 # Deploy to cloud (Railway/Render)
arli db:migrate            # Run database migrations
arli db:seed               # Seed database
arli db:reset              # Reset database (⚠️ destructive)
```

## 📁 Project Structure

```
arli/
├── apps/
│   ├── api/                 # Fastify backend API
│   │   ├── src/routes/      # API endpoints
│   │   ├── src/services/    # Business logic
│   │   └── src/middleware/  # Auth, etc.
│   └── web/                 # Next.js frontend
│       ├── app/             # App router pages
│       └── components/      # React components
├── packages/
│   ├── database/            # Prisma schema & client
│   └── types/               # Shared TypeScript types
├── docker-compose.dev.yml   # Local infrastructure
└── package.json             # Workspace root
```

## 🔧 Configuration

### Required Environment Variables

**Web (.env.local):**
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_API_URL=http://localhost:3100
```

**API (.env):**
```env
CLERK_SECRET_KEY=sk_test_...
STRIPE_SECRET_KEY=sk_test_...
OPENROUTER_API_KEY=sk-or-v1-...
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/arli"
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 📊 Features

- ✅ **Clerk Auth** - Authentication & user management
- ✅ **Stripe Integration** - Payments & billing
- ✅ **Multi-provider AI** - Claude, GPT-4, Gemini via OpenRouter
- ✅ **Task Queue** - Bull + Redis for reliable job processing
- ✅ **Heartbeat System** - Automated agent scheduling
- ✅ **Company Templates** - 3 ready-to-use templates
- ✅ **Skills Marketplace** - Buy/sell agent capabilities
- ✅ **Mobile Responsive** - PWA support
- ✅ **Analytics Charts** - Recharts visualization
- ✅ **Notifications** - Telegram + Email alerts

## 🎯 Roadmap

### Phase 1: MVP ✅
- [x] Core infrastructure
- [x] AI agent runtime
- [x] Billing system
- [x] CLI tool

### Phase 2: Scale (In Progress)
- [ ] More company templates
- [ ] Advanced analytics
- [ ] Mobile app
- [ ] Public API

### Phase 3: Decentralization
- [ ] ICP blockchain integration
- [ ] Token economics
- [ ] DAO governance

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](./CONTRIBUTING.md).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT © 2026 ARLI

---

**Built for the autonomous future.** 🚀

[![GitHub stars](https://img.shields.io/github/stars/arliwork/arli?style=social)](https://github.com/arliwork/arli/stargazers)
