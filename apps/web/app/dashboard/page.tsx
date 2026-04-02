'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { UserButton, useAuth } from '@clerk/nextjs'
import toast from 'react-hot-toast'

interface Company {
  id: string
  name: string
  slug: string
  status: string
  credits: number
  totalRevenue: number
  _count: {
    agents: number
    tickets: number
  }
}

export default function Dashboard() {
  const router = useRouter()
  const { getToken, userId } = useAuth()
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [stats, setStats] = useState({
    totalRevenue: 0,
    activeAgents: 0,
    completedTasks: 0,
    credits: 0
  })

  useEffect(() => {
    if (userId) {
      fetchCompanies()
    }
  }, [userId])

  const fetchCompanies = async () => {
    try {
      const token = await getToken()
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/companies`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch companies')
      }
      
      const data = await response.json()
      setCompanies(data.companies || [])
      
      // Calculate stats from real data
      const totalRevenue = data.companies?.reduce((sum: number, c: Company) => sum + c.totalRevenue, 0) || 0
      const activeAgents = data.companies?.reduce((sum: number, c: Company) => sum + c._count.agents, 0) || 0
      const credits = data.companies?.reduce((sum: number, c: Company) => sum + c.credits, 0) || 0
      
      setStats({
        totalRevenue,
        activeAgents,
        completedTasks: data.companies?.reduce((sum: number, c: Company) => sum + c._count.tickets, 0) || 0,
        credits
      })
    } catch (error) {
      console.error('Failed to fetch companies:', error)
      toast.error('Failed to load companies')
    } finally {
      setLoading(false)
    }
  }
 
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile Header */}
      <header className="bg-white border-b sticky top-0 z-50 lg:hidden">
        <div className="px-4 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
              A
            </div>
            <span className="text-lg font-bold">ARLI</span>
          </Link>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
        
        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="border-t px-4 py-2 bg-white">
            <Link href="/companies" className="block py-3 text-gray-600">
              My Companies
            </Link>
            <Link href="/skills" className="block py-3 text-gray-600">
              Skills
            </Link>
            <Link href="/billing" className="block py-3 text-gray-600">
              Billing
            </Link>
            <Link href="/companies/new" className="block py-3 text-blue-600 font-medium">
              + New Company
            </Link>
          </div>
        )}
      </header>

      {/* Desktop Header */}
      <header className="bg-white border-b sticky top-0 z-50 hidden lg:block">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
                A
              </div>
              <span className="text-xl font-bold">Dashboard</span>
            </Link>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/companies" className="text-gray-600 hover:text-gray-900">
              Companies
            </Link>
            <Link href="/skills" className="text-gray-600 hover:text-gray-900">
              Skills
            </Link>
            <Link href="/companies/new" className="btn-primary">
              + New Company
            </Link>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 lg:py-8">
        {/* Mobile Stats */}
        <div className="grid grid-cols-2 gap-3 mb-6 lg:hidden">
          <MobileStatCard
            title="Revenue"
            value={`$${(stats.totalRevenue / 1000).toFixed(1)}k`}
            change="+23%"
          />
          <MobileStatCard
            title="Agents"
            value={stats.activeAgents.toString()}
            change="+2"
          />
          <MobileStatCard
            title="Tasks"
            value={stats.completedTasks.toString()}
            change="+45"
          />
          <MobileStatCard
            title="Credits"
            value={(stats.credits / 1000).toFixed(1)}k
            warning
          />
        </div>

        {/* Desktop Stats */}
        <div className="hidden lg:grid md:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Revenue"
            value={`$${stats.totalRevenue.toLocaleString()}`}
            change="+23%"
            positive
          />
          <StatCard
            title="Active Agents"
            value={stats.activeAgents.toString()}
            change="+2"
            positive
          />
          <StatCard
            title="Tasks Completed"
            value={stats.completedTasks.toString()}
            change="+45"
            positive
          />
          <StatCard
            title="Available Credits"
            value={stats.credits.toLocaleString()}
            warning
          />
        </div>

        {/* Companies */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg lg:text-xl font-bold text-gray-900">Your Companies</h2>
            <Link href="/companies" className="text-blue-600 hover:text-blue-700 text-sm">
              View All →
            </Link>
          </div>
          
          <div className="divide-y">
            {companies.map((company) => (
              <div 
                key={company.id} 
                onClick={() => router.push(`/companies/${company.id}`)}
                className="py-4 flex items-center justify-between hover:bg-gray-50 -mx-4 lg:-mx-6 px-4 lg:px-6 transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-3 lg:gap-4">
                  <div className="w-10 h-10 lg:w-12 lg:h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white text-lg lg:text-xl flex-shrink-0">
                    {company.name.charAt(0)}
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-semibold text-gray-900 truncate">{company.name}</h3>
                    <div className="flex items-center gap-2 text-xs lg:text-sm text-gray-500 mt-1 flex-wrap">
                      <span>{company._count.agents} agents</span>
                      <span className="hidden sm:inline">•</span>
                      <span className="hidden sm:inline">{company._count.tickets} tasks</span>
                      <span className="hidden sm:inline">•</span>
                      <StatusBadge status={company.status} />
                    </div>
                  </div>
                </div>
                <div className="text-right flex-shrink-0">
                  <div className="font-semibold text-gray-900">
                    ${(company.totalRevenue / 1000).toFixed(1)}k
                  </div>
                  <div className="text-xs lg:text-sm text-gray-500">
                    {company.credits.toLocaleString()} cr
                  </div>
                </div>
              </div>
            ))}
          </div>

          {companies.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500 mb-4">No companies yet</p>
              <Link href="/companies/new" className="btn-primary">
                Create Your First Company
              </Link>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
          <QuickActionCard
            title="Browse Skills"
            description="Add new capabilities"
            link="/skills"
          />
          <QuickActionCard
            title="Add Credits"
            description="Top up balance"
            link="/billing"
          />
          <QuickActionCard
            title="Analytics"
            description="View reports"
            link="/analytics"
          />
        </div>
      </main>
    </div>
  )
}

function StatCard({ title, value, change, positive, warning }: { 
  title: string
  value: string
  change?: string
  positive?: boolean
  warning?: boolean
}) {
  return (
    <div className="card">
      <p className="text-sm text-gray-600 mb-1">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {change && (
        <p className={`text-sm mt-2 ${positive ? 'text-green-600' : warning ? 'text-yellow-600' : 'text-red-600'}`}>
          {change}
        </p>
      )}
    </div>
  )
}

function MobileStatCard({ title, value, change, warning }: {
  title: string
  value: string
  change?: string
  warning?: boolean
}) {
  return (
    <div className="bg-white rounded-xl p-3 shadow-sm">
      <p className="text-xs text-gray-500 mb-1">{title}</p>
      <p className="text-lg font-bold text-gray-900">{value}</p>
      {change && (
        <p className={`text-xs ${warning ? 'text-yellow-600' : 'text-green-600'}`}>
          {change}
        </p>
      )}
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    ACTIVE: 'bg-green-100 text-green-800',
    PAUSED: 'bg-yellow-100 text-yellow-800',
    SUSPENDED: 'bg-red-100 text-red-800'
  }
  
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
      {status.toLowerCase()}
    </span>
  )
}

function QuickActionCard({ title, description, link }: { title: string; description: string; link: string }) {
  return (
    <Link href={link} className="card hover:shadow-md transition-shadow cursor-pointer block">
      <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </Link>
  )
}