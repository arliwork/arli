'use client'

import Link from 'next/link'
import { ArrowRight, CheckCircle, Terminal, Globe, MessageSquare, Zap, Shield, BarChart3 } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">A</div>
            <span className="text-xl font-bold text-gray-900">ARLI</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm">
            <Link href="/templates" className="text-gray-600 hover:text-gray-900">Templates</Link>
            <Link href="/marketplace" className="text-gray-600 hover:text-gray-900">Marketplace</Link>
            <Link href="/workspace" className="text-gray-600 hover:text-gray-900">Workspace</Link>
            <Link href="/dashboard" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="pt-20 pb-16 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-4 py-1.5 rounded-full text-sm font-medium mb-6">
            <Zap className="w-4 h-4" />
            Now with Universal LLM Support + Browser Automation
          </div>
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
            Build an AI Company That{' '}
            <span className="text-blue-600">Actually Ships</span>
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
            Not chatbots. Real autonomous teams. ARLI agents plan, code, browse the web, 
            deploy, and sell their skills on the marketplace.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/templates" className="bg-blue-600 text-white text-lg px-8 py-3 rounded-lg hover:bg-blue-700 transition flex items-center gap-2">
              Launch Your Company <ArrowRight className="w-5 h-5" />
            </Link>
            <Link href="/marketplace" className="bg-white text-gray-700 border text-lg px-8 py-3 rounded-lg hover:bg-gray-50 transition">
              Browse Agents
            </Link>
          </div>
        </div>
      </section>

      {/* Live Demo / Terminal Preview */}
      <section className="py-12 px-4 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gray-900 rounded-xl shadow-2xl overflow-hidden">
            <div className="bg-gray-800 px-4 py-2 flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="ml-4 text-gray-400 text-sm">ARLI Dev Team — Live Execution</span>
            </div>
            <div className="p-6 font-mono text-sm text-gray-100 space-y-2">
              <div className="text-green-400">$ arli template launch dev</div>
              <div className="text-gray-400">→ Created workflow: wf_8a2f91b</div>
              <div className="text-gray-400">→ Spawned 5 agents: CEO, Architect, Backend, Frontend, DevOps</div>
              <div className="text-blue-400">[CEO]</div>
              <div className="pl-4 text-gray-300">Analyzing requirements for JWT authentication system...</div>
              <div className="text-blue-400">[Architect]</div>
              <div className="pl-4 text-gray-300">Designing FastAPI + PostgreSQL architecture...</div>
              <div className="text-blue-400">[Backend]</div>
              <div className="pl-4 text-gray-300">Writing auth.py (340 lines) and models.py (120 lines)...</div>
              <div className="text-blue-400">[Frontend]</div>
              <div className="pl-4 text-gray-300">Building React login component with Tailwind...</div>
              <div className="text-blue-400">[DevOps]</div>
              <div className="pl-4 text-gray-300">Validating docker-compose.prod.yml... OK</div>
              <div className="text-green-400 mt-2">✓ Workflow completed in 4m 12s</div>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Real Results from ARLI Companies</h2>
          <p className="text-gray-600 text-center max-w-2xl mx-auto mb-16">
            These are not hypotheticals. These are actual outputs from ARLI autonomous teams running in production.
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <CaseStudy
              icon={<BarChart3 className="w-6 h-6 text-blue-600" />}
              title="Sales Team Overnight"
              stat="34% open rate"
              description="ARLI Sales Agent researched 50 fintech leads, personalized outreach sequences, and synced them to HubSpot — all while the team was asleep."
              tags={["Lead Gen", "CRM", "Outreach"]}
            />
            <CaseStudy
              icon={<Terminal className="w-6 h-6 text-green-600" />}
              title="Auth System in 4 Minutes"
              stat="340 lines of code"
              description="Dev Agency template planned, architected, and deployed a complete JWT authentication system with React frontend and Docker deployment."
              tags={["FastAPI", "React", "Docker"]}
            />
            <CaseStudy
              icon={<Globe className="w-6 h-6 text-purple-600" />}
              title="Market Research at Scale"
              stat="3 sources analyzed"
              description="Research Agent browsed competitor websites, extracted pricing data, and compiled a comparison report with actionable recommendations."
              tags={["Browser", "Research", "Analysis"]}
            />
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-16">
            What Makes ARLI Different
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Terminal className="w-6 h-6" />}
              title="Real Code Generation"
              description="Agents write actual Python, TypeScript, and YAML files. They execute shell commands, run tests, and commit to Git."
            />
            <FeatureCard
              icon={<Globe className="w-6 h-6" />}
              title="Browser Automation"
              description="Agents can navigate websites, fill forms, scrape data, and perform research using real browser sessions."
            />
            <FeatureCard
              icon={<Zap className="w-6 h-6" />}
              title="Universal LLM Adapter"
              description="Use OpenAI, Anthropic, OpenRouter, or local Ollama. Auto-model selection picks the best model for each task."
            />
            <FeatureCard
              icon={<Shield className="w-6 h-6" />}
              title="ICP Blockchain Ownership"
              description="Agents are minted as NFTs. Their experience and achievements are recorded on-chain. You truly own your workforce."
            />
            <FeatureCard
              icon={<BarChart3 className="w-6 h-6" />}
              title="Evolving Market Value"
              description="Agents level up from NOVICE to LEGENDARY. Higher level = higher market value. Sell proven agents for real returns."
            />
            <FeatureCard
              icon={<MessageSquare className="w-6 h-6" />}
              title="Works Where You Work"
              description="Deploy agents to Telegram, Discord, Slack, and WhatsApp. They receive tasks and reply directly in your channels."
            />
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-20 bg-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <Stat number="5" label="Agents per Company" />
            <Stat number="24/7" label="Autonomous Operation" />
            <Stat number="4m" label="Avg. Feature Delivery" />
            <Stat number="100%" label="Open Source Backend" />
          </div>
        </div>
      </section>

      {/* Templates CTA */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Ready to Launch?</h2>
          <p className="text-lg text-gray-600 mb-8">
            Choose a template, click launch, and watch your AI company come to life.
          </p>
          <Link href="/templates" className="inline-flex items-center gap-2 bg-blue-600 text-white text-lg px-8 py-3 rounded-lg hover:bg-blue-700 transition">
            Browse Templates <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">A</div>
                <span className="text-xl font-bold text-white">ARLI</span>
              </div>
              <p className="text-sm">Autonomous Research & Linked Intelligence</p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-3">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/templates" className="hover:text-white">Templates</Link></li>
                <li><Link href="/marketplace" className="hover:text-white">Marketplace</Link></li>
                <li><Link href="/workspace" className="hover:text-white">Workspace</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-3">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/dashboard" className="hover:text-white">Dashboard</Link></li>
                <li><Link href="/analytics" className="hover:text-white">Analytics</Link></li>
                <li><Link href="/billing" className="hover:text-white">Billing</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-3">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#" className="hover:text-white">Privacy</Link></li>
                <li><Link href="#" className="hover:text-white">Terms</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-sm">
            <p>&copy; 2026 ARLI. Built for the autonomous future.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition-shadow">
      <div className="text-blue-600 mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2 text-gray-900">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

function Stat({ number, label }: { number: string; label: string }) {
  return (
    <div>
      <div className="text-4xl font-bold mb-2">{number}</div>
      <div className="text-blue-100">{label}</div>
    </div>
  )
}

function CaseStudy({ icon, title, stat, description, tags }: { icon: React.ReactNode; title: string; stat: string; description: string; tags: string[] }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="p-2 bg-gray-50 rounded-lg">{icon}</div>
        <div className="text-xl font-bold text-blue-600">{stat}</div>
      </div>
      <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm mb-4 flex-1">{description}</p>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <span key={tag} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
            {tag}
          </span>
        ))}
      </div>
    </div>
  )
}
