# 🚀 ARLI - Autonomous Revenue & Labor Intelligence

[![npm](https://img.shields.io/npm/v/arliwork)](https://www.npmjs.com/package/arliwork)
[![GitHub](https://img.shields.io/github/license/arliwork/arli)](https://github.com/arliwork/arli/blob/main/LICENSE)
[![Node.js](https://img.shields.io/badge/node-%3E%3D18-brightgreen)](https://nodejs.org/)

**Create and run AI-powered autonomous companies**

ARLI is a platform where anyone can create fully autonomous companies that operate 24/7 with AI agents. Think of it as "AWS for AI Companies" - you bring the business idea, ARLI provides the AI workforce, infrastructure, and monetization.

## 🚀 Quick Start

### Option 1: Demo Mode (No Setup Required)

```bash
# Clone and run demo
 git clone https://github.com/arliwork/arli.git
 cd arli
 
 # Run demo server
 node mock-server.js &
 python3 -m http.server 8080
```

**Demo URLs:**
- 🎨 **Dashboard**: http://localhost:8080/demo-dashboard.html
- ⚡ **API**: http://localhost:3100

Try it now with pre-configured company: **"My Marketing Agency"** with 5 active AI agents!

### Option 2: Full Development Mode

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

## 🎨 Company Templates

Deploy pre-configured AI companies with one click:

| Template | Description | Agents | Key Metrics |
|----------|-------------|--------|-------------|
| **📈 Agency Scalr** | Marketing Agency Automation | 5 | 3x efficiency, +17% retention |
| **🛒 Commerce Intel** | E-commerce Intelligence | 5 | +5-15% margin, +25% ROAS |
| **🚀 SaaS Growth Lab** | Subscription Business | 5 | >120% NRR, -30% churn |
| **🏥 Clinic Flow** | Healthcare Operations | 5 | +25% throughput, -40% no-shows |
| **🏠 Property Pulse** | Real Estate Automation | 5 | 3x leads, -20% days on market |
| **⚖️ Legal Synth** | Law Firm Automation | 5 | +400% review speed |
| **📊 Ledger Minds** | Accounting & Advisory | 5 | -60% close time, +20% tax savings |
| **🎓 Learning Foundry** | EdTech Content | 5 | 10x content speed, +40% retention |
| **🏨 Hospitality Hive** | Restaurant & Hotel Ops | 5 | -15% labor cost, +10% occupancy |
| **🏭 Manufacturing Mind** | Production Intelligence | 5 | +20% OEE, -70% downtime |

Each template includes specialized AI agents with specific roles, skills, and workflows.

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

- ✅ **Demo Mode** - Try instantly without any setup
- ✅ **10 Company Templates** - Marketing, SaaS, Healthcare, Legal, and more
- ✅ **Visual Dashboard** - Manage companies and agents in real-time
- ✅ **AI Agent Runtime** - Autonomous agents with heartbeat monitoring
- ✅ **Multi-provider AI** - Claude, GPT-4, Gemini via OpenRouter
- ✅ **Task Queue** - Bull + Redis for reliable job processing
- ✅ **Clerk Auth** - Authentication & user management
- ✅ **Stripe Integration** - Payments & billing
- ✅ **Skills Marketplace** - Buy/sell agent capabilities
- ✅ **Mobile Responsive** - Works on all devices
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
