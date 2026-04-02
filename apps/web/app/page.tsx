'use client'

import Link from 'next/link'
import { UserButton, SignedIn, SignedOut, useAuth } from '@clerk/nextjs'

export default function Home() {
  const { isLoaded } = useAuth()

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
            <SignedIn>
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                Dashboard
              </Link>
              <Link href="/companies" className="text-gray-600 hover:text-gray-900">
                My Companies
              </Link>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
            <SignedOut>
              <Link href="/sign-in" className="text-gray-600 hover:text-gray-900">
                Sign In
              </Link>
              <Link href="/sign-up" className="btn-primary">
                Get Started
              </Link>
            </SignedOut>
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
            <Link href="/dashboard" className="btn-primary text-lg px-8 py-3">
              Launch Your Company
            </Link>
            <button className="btn-secondary text-lg px-8 py-3">
              View Demo
            </button>
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

      {/* Templates */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-4">
            Start with a Proven Template
          </h2>
          <p className="text-gray-600 text-center mb-16 max-w-2xl mx-auto">
            Launch in 10 minutes with pre-configured companies
          </p>
          <div className="grid md:grid-cols-3 gap-6">
            <TemplateCard
              name="Content Agency"
              description="AI-powered TikTok and Instagram content creation"
              agents={4}
              price="$49/mo"
            />
            <TemplateCard
              name="Dropshipping Store"
              description="Automated product hunting and ad management"
              agents={5}
              price="$79/mo"
            />
            <TemplateCard
              name="SaaS Micro-Product"
              description="Build and launch micro-SaaS products"
              agents={3}
              price="$99/mo"
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
    <div className="card hover:shadow-md transition-shadow">
      <div className="text-3xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2 text-gray-900">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

function TemplateCard({ name, description, agents, price }: { name: string; description: string; agents: number; price: string }) {
  return (
    <div className="card hover:shadow-lg transition-shadow cursor-pointer border-2 border-transparent hover:border-blue-500">
      <h3 className="text-xl font-semibold mb-2 text-gray-900">{name}</h3>
      <p className="text-gray-600 mb-4">{description}</p>
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-500">{agents} AI agents</span>
        <span className="text-lg font-bold text-blue-600">{price}</span>
      </div>
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