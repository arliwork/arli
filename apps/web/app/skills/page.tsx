'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

interface Skill {
  id: string
  name: string
  description: string
  category: string
  price: number
  author: string
  author_id: string
  rating: number
  review_count: number
  downloads: number
  version: string
}

const CATEGORIES = [
  { id: 'all', name: 'All Skills', icon: '🎯' },
  { id: 'coding', name: 'Coding', icon: '💻' },
  { id: 'data_analysis', name: 'Data Analysis', icon: '📊' },
  { id: 'web_scraping', name: 'Web Scraping', icon: '🕷️' },
  { id: 'automation', name: 'Automation', icon: '⚙️' },
  { id: 'integration', name: 'Integration', icon: '🔗' },
  { id: 'content', name: 'Content', icon: '✍️' },
  { id: 'security', name: 'Security', icon: '🔒' },
  { id: 'devops', name: 'DevOps', icon: '🚀' },
  { id: 'other', name: 'Other', icon: '📦' },
]

export default function SkillsMarketplaceReal() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [purchasing, setPurchasing] = useState<string | null>(null)
  const [purchaseSuccess, setPurchaseSuccess] = useState<string | null>(null)

  useEffect(() => {
    fetchSkills()
  }, [selectedCategory, searchQuery])

  const fetchSkills = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (selectedCategory !== 'all') params.append('category', selectedCategory)
      if (searchQuery) params.append('search', searchQuery)
      
      const res = await fetch(`${API_URL}/skills/?${params}`)
      if (!res.ok) throw new Error('Failed to fetch skills')
      
      const data = await res.json()
      setSkills(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const purchaseSkill = async (skillId: string) => {
    setPurchasing(skillId)
    try {
      const res = await fetch(`${API_URL}/skills/${skillId}/purchase`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'demo_user_123' })
      })
      
      if (!res.ok) throw new Error('Purchase failed')
      
      const data = await res.json()
      setPurchaseSuccess(`Purchased! License: ${data.license_key.substring(0, 16)}...`)
      fetchSkills() // Refresh to update download count
      
      setTimeout(() => setPurchaseSuccess(null), 5000)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Purchase failed')
    } finally {
      setPurchasing(null)
    }
  }

  const filteredSkills = skills

  if (loading && skills.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading skills...</div>
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
              <span className="text-xl font-bold">ARLI Skills</span>
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
            <Link href="/companies" className="text-gray-600 hover:text-gray-900">
              Companies
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Skills Marketplace
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Supercharge your AI agents with specialized skills. Buy once, use forever.
            Revenue split: <span className="font-bold text-green-600">90% Creator / 10% Platform</span>
          </p>
        </div>

        {/* Success Message */}
        {purchaseSuccess && (
          <div className="max-w-2xl mx-auto mb-6 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
            ✅ {purchaseSuccess}
          </div>
        )}

        {/* Search */}
        <div className="max-w-2xl mx-auto mb-8">
          <input
            type="text"
            placeholder="Search skills..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Categories */}
        <div className="flex flex-wrap justify-center gap-2 mb-12">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-4 py-2 rounded-full font-medium transition-colors ${
                selectedCategory === cat.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span className="mr-2">{cat.icon}</span>
              {cat.name}
            </button>
          ))}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-6 mb-12 max-w-2xl mx-auto">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{skills.length}</div>
            <div className="text-gray-600">Skills Available</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {skills.reduce((acc, s) => acc + s.downloads, 0)}
            </div>
            <div className="text-gray-600">Downloads</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {skills.length > 0 
                ? (skills.reduce((acc, s) => acc + s.rating, 0) / skills.length).toFixed(1)
                : '0.0'}
            </div>
            <div className="text-gray-600">Average Rating</div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="text-center py-12">
            <p className="text-red-500">Error: {error}</p>
            <button 
              onClick={fetchSkills}
              className="mt-4 text-blue-600 hover:underline"
            >
              Retry
            </button>
          </div>
        )}

        {/* Skills Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredSkills.map((skill) => (
            <SkillCard 
              key={skill.id} 
              skill={skill} 
              onPurchase={() => purchaseSkill(skill.id)}
              purchasing={purchasing === skill.id}
            />
          ))}
        </div>

        {filteredSkills.length === 0 && !error && (
          <div className="text-center py-12">
            <p className="text-gray-500">No skills found matching your criteria</p>
          </div>
        )}

        {/* Become a Creator CTA */}
        <div className="mt-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white text-center">
          <h2 className="text-2xl font-bold mb-2">Become a Skill Creator</h2>
          <p className="mb-6">
            Create and sell your own skills. Keep <span className="font-bold">90%</span> of all sales.
            We take only 10% to maintain the platform.
          </p>
          <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
            Start Creating
          </button>
        </div>
      </main>
    </div>
  )
}

function SkillCard({ 
  skill, 
  onPurchase,
  purchasing 
}: { 
  skill: Skill
  onPurchase: () => void
  purchasing: boolean
}) {
  const categoryColors: Record<string, string> = {
    'coding': 'bg-blue-100 text-blue-800',
    'data_analysis': 'bg-yellow-100 text-yellow-800',
    'web_scraping': 'bg-purple-100 text-purple-800',
    'automation': 'bg-gray-100 text-gray-800',
    'integration': 'bg-green-100 text-green-800',
    'content': 'bg-indigo-100 text-indigo-800',
    'security': 'bg-red-100 text-red-800',
    'devops': 'bg-orange-100 text-orange-800',
    'other': 'bg-gray-100 text-gray-600',
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${categoryColors[skill.category] || 'bg-gray-100'}`}>
          {skill.category.replace('_', ' ').toUpperCase()}
        </span>
        <span className="text-xs text-gray-500">v{skill.version}</span>
      </div>

      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {skill.name}
      </h3>
      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
        {skill.description}
      </p>

      <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
        <span>👤 {skill.author}</span>
        <span>⬇️ {skill.downloads}</span>
        <span>⭐ {skill.rating.toFixed(1)} ({skill.review_count})</span>
      </div>

      <div className="flex items-center justify-between pt-4 border-t">
        <div>
          <span className="text-2xl font-bold text-gray-900">
            ${skill.price.toFixed(2)}
          </span>
          <span className="text-gray-500 ml-1">USD</span>
        </div>
        <button 
          onClick={onPurchase}
          disabled={purchasing}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {purchasing ? 'Processing...' : 'Buy Now'}
        </button>
      </div>
    </div>
  )
}
