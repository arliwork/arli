'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

interface Skill {
  id: string
  name: string
  description: string
  category: string
  price: number
  isSubscription: boolean
  subscriptionPrice?: number
  authorName: string
  downloads: number
  rating: number
}

const CATEGORIES = [
  { id: 'all', name: 'All Skills', icon: '🎯' },
  { id: 'MARKETING', name: 'Marketing', icon: '📢' },
  { id: 'SALES', name: 'Sales', icon: '💰' },
  { id: 'DEVELOPMENT', name: 'Development', icon: '💻' },
  { id: 'DESIGN', name: 'Design', icon: '🎨' },
  { id: 'ANALYTICS', name: 'Analytics', icon: '📊' },
  { id: 'AUTOMATION', name: 'Automation', icon: '⚙️' },
  { id: 'CONTENT', name: 'Content', icon: '✍️' },
]

export default function SkillsMarketplace() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchSkills()
  }, [])

  const fetchSkills = async () => {
    try {
      // TODO: Replace with actual API call
      // const res = await fetch('/api/skills')
      // const data = await res.json()
      
      // Mock data
      const mockSkills: Skill[] = [
        {
          id: '1',
          name: 'TikTok Trend Hunter',
          description: 'Automatically finds viral trends, trending sounds, and hashtags on TikTok',
          category: 'CONTENT',
          price: 500,
          isSubscription: false,
          authorName: 'ARLI Team',
          downloads: 1240,
          rating: 4.8
        },
        {
          id: '2',
          name: 'UGC Script Writer Pro',
          description: 'Writes high-converting UGC scripts using proven viral formulas',
          category: 'CONTENT',
          price: 1000,
          isSubscription: false,
          authorName: 'Sarah Chen',
          downloads: 856,
          rating: 4.9
        },
        {
          id: '3',
          name: 'Facebook Ads Optimizer',
          description: 'AI-powered Facebook ad campaign optimization and budget management',
          category: 'MARKETING',
          price: 2000,
          isSubscription: true,
          subscriptionPrice: 200,
          authorName: 'GrowthLab',
          downloads: 2341,
          rating: 4.7
        },
        {
          id: '4',
          name: 'Product Research Bot',
          description: 'Finds winning dropshipping products using data analysis',
          category: 'ANALYTICS',
          price: 1500,
          isSubscription: false,
          authorName: 'Ecom Expert',
          downloads: 1892,
          rating: 4.6
        },
        {
          id: '5',
          name: 'Email Sequence Writer',
          description: 'Creates high-converting email sequences for any niche',
          category: 'MARKETING',
          price: 800,
          isSubscription: false,
          authorName: 'CopyMaster',
          downloads: 678,
          rating: 4.8
        },
        {
          id: '6',
          name: 'Shopify Store Manager',
          description: 'Automates Shopify store operations and inventory management',
          category: 'AUTOMATION',
          price: 1200,
          isSubscription: true,
          subscriptionPrice: 150,
          authorName: 'ARLI Team',
          downloads: 945,
          rating: 4.5
        },
        {
          id: '7',
          name: 'Next.js Full-Stack Dev',
          description: 'Complete full-stack development with Next.js, TypeScript, and PostgreSQL',
          category: 'DEVELOPMENT',
          price: 3000,
          isSubscription: false,
          authorName: 'DevPro',
          downloads: 432,
          rating: 4.9
        },
        {
          id: '8',
          name: 'Brand Identity Designer',
          description: 'Creates complete brand identities including logos and style guides',
          category: 'DESIGN',
          price: 1500,
          isSubscription: false,
          authorName: 'DesignStudio',
          downloads: 567,
          rating: 4.7
        },
        {
          id: '9',
          name: 'SEO Content Optimizer',
          description: 'Optimizes content for search engines with keyword research',
          category: 'ANALYTICS',
          price: 900,
          isSubscription: true,
          subscriptionPrice: 100,
          authorName: 'SEOMaster',
          downloads: 1234,
          rating: 4.6
        },
      ]
      
      setSkills(mockSkills)
    } catch (error) {
      console.error('Failed to fetch skills:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredSkills = skills.filter(skill => {
    const matchesCategory = selectedCategory === 'all' || skill.category === selectedCategory
    const matchesSearch = skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         skill.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  if (loading) {
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
          </p>
        </div>

        {/* Search */}
        <div className="max-w-2xl mx-auto mb-8">
          <input
            type="text"
            placeholder="Search skills..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input text-lg"
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
            <div className="text-3xl font-bold text-blue-600">50+</div>
            <div className="text-gray-600">Skills Available</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">10K+</div>
            <div className="text-gray-600">Downloads</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">4.8</div>
            <div className="text-gray-600">Average Rating</div>
          </div>
        </div>

        {/* Skills Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredSkills.map((skill) => (
            <SkillCard key={skill.id} skill={skill} />
          ))}
        </div>

        {filteredSkills.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No skills found matching your criteria</p>
          </div>
        )}

        {/* Become a Creator CTA */}
        <div className="mt-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white text-center">
          <h2 className="text-2xl font-bold mb-2">Become a Skill Creator</h2>
          <p className="mb-6">
            Create and sell your own skills. Keep 90% of all sales.
          </p>
          <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
            Start Creating
          </button>
        </div>
      </main>
    </div>
  )
}

function SkillCard({ skill }: { skill: Skill }) {
  const categoryColors: Record<string, string> = {
    'MARKETING': 'bg-purple-100 text-purple-800',
    'SALES': 'bg-green-100 text-green-800',
    'DEVELOPMENT': 'bg-blue-100 text-blue-800',
    'DESIGN': 'bg-pink-100 text-pink-800',
    'ANALYTICS': 'bg-yellow-100 text-yellow-800',
    'AUTOMATION': 'bg-gray-100 text-gray-800',
    'CONTENT': 'bg-indigo-100 text-indigo-800',
  }

  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <span className={`badge ${categoryColors[skill.category] || 'bg-gray-100'}`}>
          {skill.category}
        </span>
        {skill.isSubscription && (
          <span className="badge bg-blue-100 text-blue-800">
            Subscription
          </span>
        )}
      </div>

      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {skill.name}
      </h3>
      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
        {skill.description}
      </p>

      <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
        <span>👤 {skill.authorName}</span>
        <span>⬇️ {skill.downloads}</span>
        <span>⭐ {skill.rating}</span>
      </div>

      <div className="flex items-center justify-between pt-4 border-t">
        <div>
          <span className="text-2xl font-bold text-gray-900">
            {skill.price.toLocaleString()}
          </span>
          <span className="text-gray-500 ml-1">credits</span>
          {skill.isSubscription && (
            <div className="text-xs text-gray-500">
              +{skill.subscriptionPrice}/mo
            </div>
          )}
        </div>
        <button className="btn-primary">
          Buy Now
        </button>
      </div>
    </div>
  )
}