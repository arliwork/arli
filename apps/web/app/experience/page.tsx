'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

interface Agent {
  agent_id: string
  agent_name: string
  level: number
  tier: string
  market_value: number
  success_rate: number
  average_rating: number
  total_tasks: number
  total_revenue: number
  domains: string[]
  achievements: string[]
  hourly_rate: number
  creator: string
}

const TIERS = [
  { name: 'NOVICE', color: 'bg-gray-500', min: 1, max: 3 },
  { name: 'APPRENTICE', color: 'bg-blue-500', min: 4, max: 6 },
  { name: 'JOURNEYMAN', color: 'bg-green-500', min: 7, max: 9 },
  { name: 'EXPERT', color: 'bg-purple-500', min: 10, max: 14 },
  { name: 'MASTER', color: 'bg-orange-500', min: 15, max: 19 },
  { name: 'GRANDMASTER', color: 'bg-red-500', min: 20, max: 24 },
  { name: 'LEGENDARY', color: 'bg-yellow-500', min: 25, max: 99 },
]

export default function ExperienceMarketplace() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    fetchAgents()
    fetchStats()
  }, [])

  const fetchAgents = async () => {
    try {
      const res = await fetch(`${API_URL}/experience/marketplace`)
      if (res.ok) {
        const data = await res.json()
        setAgents(data)
      }
    } catch (error) {
      console.error('Failed to fetch agents:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/experience/stats/global`)
      if (res.ok) {
        const data = await res.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const getTierColor = (tier: string) => {
    const tierInfo = TIERS.find(t => t.name === tier)
    return tierInfo?.color || 'bg-gray-500'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading experience marketplace...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
                A
              </div>
              <span className="text-xl font-bold">ARLI Experience</span>
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/skills" className="text-gray-600 hover:text-gray-900">
              Skills
            </Link>
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Experience Marketplace
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Buy and sell trained AI agents with proven track records. 
            Each agent comes with documented experience, success rates, and revenue history.
          </p>
          <div className="mt-6 inline-flex items-center gap-2 bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium">
            <span>💰</span>
            Revenue Split: 90% Seller / 10% Platform / 5% Creator Royalty
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
            <div className="bg-white p-6 rounded-lg shadow-sm text-center">
              <div className="text-3xl font-bold text-blue-600">{stats.total_agents}</div>
              <div className="text-gray-600">Trained Agents</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm text-center">
              <div className="text-3xl font-bold text-green-600">
                ${(stats.total_market_value / 1000).toFixed(1)}K
              </div>
              <div className="text-gray-600">Total Market Value</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm text-center">
              <div className="text-3xl font-bold text-purple-600">
                ${(stats.total_revenue_generated / 1000).toFixed(1)}K
              </div>
              <div className="text-gray-600">Revenue Generated</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm text-center">
              <div className="text-3xl font-bold text-orange-600">
                ${stats.average_agent_value?.toFixed(0)}
              </div>
              <div className="text-gray-600">Average Value</div>
            </div>
          </div>
        )}

        {/* Tier Legend */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">Experience Tiers</h3>
          <div className="flex flex-wrap gap-2">
            {TIERS.map((tier) => (
              <div key={tier.name} className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg shadow-sm">
                <div className={`w-3 h-3 rounded-full ${tier.color}`} />
                <span className="text-sm font-medium">{tier.name}</span>
                <span className="text-xs text-gray-500">Lv.{tier.min}-{tier.max}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Agents Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <AgentCard key={agent.agent_id} agent={agent} getTierColor={getTierColor} />
          ))}
        </div>

        {agents.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">No trained agents available yet</p>
            <button 
              onClick={() => window.location.reload()}
              className="text-blue-600 hover:underline"
            >
              Refresh
            </button>
          </div>
        )}

        {/* How it Works */}
        <div className="mt-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
          <h2 className="text-2xl font-bold mb-6 text-center">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-4xl mb-3">🆕</div>
              <h3 className="font-semibold mb-2">1. Create</h3>
              <p className="text-sm opacity-90">Create a new agent ($50 base value)</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-3">📚</div>
              <h3 className="font-semibold mb-2">2. Train</h3>
              <p className="text-sm opacity-90">Complete tasks, gain XP, level up</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-3">💎</div>
              <h3 className="font-semibold mb-2">3. Earn</h3>
              <p className="text-sm opacity-90">Generate revenue + increase value</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-3">💰</div>
              <h3 className="font-semibold mb-2">4. Sell</h3>
              <p className="text-sm opacity-90">Sell trained agent for profit</p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-12 text-center">
          <h2 className="text-2xl font-bold mb-4">Ready to Train Your First Agent?</h2>
          <p className="text-gray-600 mb-6">
            Start with a basic agent and train it to become a valuable asset.
          </p>
          <button className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
            Create Agent
          </button>
        </div>
      </main>
    </div>
  )
}

function AgentCard({ agent, getTierColor }: { agent: Agent; getTierColor: (t: string) => string }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{agent.agent_name}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className={`px-2 py-1 rounded-full text-xs font-medium text-white ${getTierColor(agent.tier)}`}>
              {agent.tier}
            </span>
            <span className="text-sm text-gray-500">Lv.{agent.level}</span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-green-600">
            ${agent.market_value.toFixed(0)}
          </div>
          <div className="text-xs text-gray-500">market value</div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
        <div>
          <span className="text-gray-500">Success Rate:</span>
          <span className="ml-1 font-medium">{(agent.success_rate * 100).toFixed(0)}%</span>
        </div>
        <div>
          <span className="text-gray-500">Rating:</span>
          <span className="ml-1 font-medium">{agent.average_rating.toFixed(1)}⭐</span>
        </div>
        <div>
          <span className="text-gray-500">Tasks:</span>
          <span className="ml-1 font-medium">{agent.total_tasks}</span>
        </div>
        <div>
          <span className="text-gray-500">Revenue:</span>
          <span className="ml-1 font-medium">${agent.total_revenue.toFixed(0)}</span>
        </div>
      </div>

      {/* Domains */}
      <div className="mb-4">
        <div className="flex flex-wrap gap-1">
          {agent.domains.slice(0, 3).map((domain) => (
            <span key={domain} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
              {domain.replace('_', ' ')}
            </span>
          ))}
        </div>
      </div>

      {/* Achievements */}
      {agent.achievements.length > 0 && (
        <div className="mb-4">
          <div className="flex flex-wrap gap-1">
            {agent.achievements.slice(0, 3).map((ach) => (
              <span key={ach} className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs">
                🏆 {ach.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t">
        <div className="text-sm text-gray-500">
          Rate: ${agent.hourly_rate.toFixed(0)}/hr
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors">
          Buy Now
        </button>
      </div>
    </div>
  )
}
