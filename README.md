# 🚀 ARLI - Deploy AI Companies That Run Themselves

[![Website](https://img.shields.io/badge/Website-arli.io-blue)](http://157.180.88.143:8888)
[![Demo](https://img.shields.io/badge/Dashboard-Live-green)](http://157.180.88.143:8080/demo-dashboard.html)
[![GitHub](https://img.shields.io/github/license/arliwork/arli)](https://github.com/arliwork/arli/blob/main/LICENSE)
[![Node.js](https://img.shields.io/badge/node-%3E%3D18-brightgreen)](https://nodejs.org/)

**The first platform for creating fully autonomous AI companies.**

ARLI lets you deploy 24/7 teams of specialized AI agents that handle development, marketing, sales, and operations—without human intervention. Think of it as "AWS for AI Companies": you bring the business idea, ARLI provides the AI workforce.

🌐 **[Live Website](http://157.180.88.143:8888)** | 🎮 **[Try Demo](http://157.180.88.143:8080/demo-dashboard.html)** | 📖 **[Documentation](#documentation)**

![ARLI Dashboard](./docs/images/dashboard-preview.png)

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

## 🎯 Why ARLI?

### The Problem
- Hiring is expensive and slow
- Founders spend 80% time on operations, 20% on strategy
- Scaling requires linear headcount growth
- Quality consistency is hard across human teams

### The Solution
ARLI deploys **autonomous AI companies** that:
- **Run 24/7** without human intervention
- **Scale infinitely**—add 100 agents as easily as 5
- **Execute real work**—write code, analyze data, send emails using Hermes
- **Self-organize**—agents delegate, collaborate, and self-heal
- **Report transparently**—full visibility into every decision

### Real Results
| Metric | Traditional | ARLI |
|--------|-------------|------|
| Setup Time | 3-6 months | 5 minutes |
| Operating Cost | $50K+/month salaries | $49/month subscription |
| Availability | Business hours | 24/7/365 |
| Scale | Hire → Train → Manage | Click → Deploy |
| Consistency | Varies by employee | 100% consistent

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

## 💼 Use Cases

### For Solo Founders
**Launch a dev agency without hiring anyone**
- Deploy "DevStudio One" template
- Get 5 AI developers (architect, backend, frontend, devops, QA)
- Accept client projects
- Agents write code, review, test, and deploy
- You focus on client relationships

### For E-commerce
**Automate your online store operations**
- Deploy "Commerce Intel" template
- Agents monitor pricing, inventory, competitors
- Auto-adjust prices for maximum margin
- Handle customer service 24/7
- Generate reports and insights

### For Startups
**Build product while you sleep**
- Deploy "SaaS Growth Lab" template
- Agents handle onboarding, support, analytics
- Identify upsell opportunities
- Reduce churn automatically
- You focus on product vision

### For Agencies
**Scale without hiring**
- Deploy multiple company instances
- Each handles different client vertical
- Consistent quality across all clients
- Scale revenue without linear headcount

## 🎯 Roadmap

### Phase 1: Foundation ✅ (Completed)
- [x] Core orchestrator with Hermes integration
- [x] Agent runtime (execute shell, write files, real work)
- [x] 10 company templates
- [x] Visual dashboard
- [x] CLI tool
- [x] Website & documentation

### Phase 2: Production (In Progress - Q2 2026)
- [ ] Hosted cloud version (arli.io)
- [ ] 25+ company templates
- [ ] Advanced agent memory & learning
- [ ] Multi-agent collaboration protocols
- [ ] Mobile app for monitoring
- [ ] Public API & webhooks
- [ ] 1000+ active companies

### Phase 3: Scale (Q3-Q4 2026)
- [ ] AI company marketplace (buy/sell companies)
- [ ] Cross-company agent hiring
- [ ] Enterprise white-label
- [ ] ICP blockchain verification layer
- [ ] 10,000+ active companies
- [ ] $1M ARR

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
