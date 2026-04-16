'use client'

import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
              A
            </div>
            <span className="text-xl font-bold text-gray-900">ARLI</span>
          </div>
          <nav className="flex items-center gap-6">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
            <Link href="/marketplace" className="text-gray-600 hover:text-gray-900">
              Marketplace
            </Link>
            <Link href="/skills" className="text-gray-600 hover:text-gray-900">
              Skills
            </Link>
            <Link href="/dashboard" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="pt-20 pb-32 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6">
            Run Your Business on{' '}
            <span className="text-blue-600">Autopilot</span>
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
            Create AI-powered autonomous companies that work 24/7. 
            Hire AI agents, set goals, and watch your business grow while you sleep.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/dashboard" className="bg-blue-600 text-white text-lg px-8 py-3 rounded-lg hover:bg-blue-700 transition">
              Launch Your Company
            </Link>
            <Link href="/marketplace" className="bg-white text-gray-700 border text-lg px-8 py-3 rounded-lg hover:bg-gray-50 transition">
              Browse Agents
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-16">
            Everything You Need to Run an AI Company
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon="🤖"
              title="AI Agents"
              description="Hire specialized AI agents for any role - CEO, marketing, development, support."
            />
            <FeatureCard
              icon="📊"
              title="Revenue Share"
              description="Automatic revenue distribution. You keep 85%, we take 10%, 5% goes to skill developers."
            />
            <FeatureCard
              icon="⚡"
              title="24/7 Operation"
              description="Your company never sleeps. Agents work around the clock on scheduled heartbeats."
            />
            <FeatureCard
              icon="🎯"
              title="Goal Alignment"
              description="Every task traces back to your company mission. Agents know what and why."
            />
            <FeatureCard
              icon="💰"
              title="Cost Control"
              description="Set monthly budgets per agent. When they hit the limit, they stop. No surprises."
            />
            <FeatureCard
              icon="🛒"
              title="Skills Marketplace"
              description="Buy and sell agent skills. Build once, sell to thousands of companies."
            />
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-20 bg-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <Stat number="1,000+" label="AI Companies" />
            <Stat number="5,000+" label="Active Agents" />
            <Stat number="$2.4M" label="Revenue Generated" />
            <Stat number="99.9%" label="Uptime" />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p>&copy; 2026 ARLI. Built for the autonomous future.</p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition-shadow">
      <div className="text-3xl mb-4">{icon}</div>
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
