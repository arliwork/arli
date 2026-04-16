'use client'

import { useEffect, useState } from 'react'
// Clerk removed - using safe auth
import Link from 'next/link'
import { useAuthSafe } from '../hooks/useAuthSafe'
import toast from 'react-hot-toast'
import { 
  RevenueChart, 
  TasksChart, 
  CreditsChart, 
  AgentsChart,
  StatsCard 
} from '../components/Charts'
import { DollarSign, TrendingUp, CheckCircle, Users } from 'lucide-react'

interface AnalyticsData {
  revenue: { date: string; revenue: number; costs: number }[]
  tasks: { date: string; completed: number; pending: number }[]
  credits: { date: string; balance: number; spent: number }[]
  agents: { name: string; tasks: number; revenue: number }[]
  stats: {
    totalRevenue: number
    totalTasks: number
    activeAgents: number
    avgTaskCost: number
  }
}

export default function AnalyticsPage() {
  const { isLoaded, token, getToken } = useAuthSafe()
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('7d')

  useEffect(() => {
    if (token) {
      fetchAnalytics()
    }
  }, [token, timeRange])

  const fetchAnalytics = async () => {
    try {
      const authToken = await getToken()
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/analytics?range=${timeRange}`,
        { headers: { 'Authorization': `Bearer ${authToken}` } }
      )
      
      if (!response.ok) throw new Error('Failed to fetch analytics')
      
      const result = await response.json()
      setData(result.data)
    } catch (error) {
      toast.error('Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading analytics...</div>
      </div>
    )
  }

  // Mock data for demo
  const mockData: AnalyticsData = {
    revenue: [
      { date: 'Mon', revenue: 1200, costs: 400 },
      { date: 'Tue', revenue: 1800, costs: 500 },
      { date: 'Wed', revenue: 2400, costs: 600 },
      { date: 'Thu', revenue: 2100, costs: 550 },
      { date: 'Fri', revenue: 3200, costs: 800 },
      { date: 'Sat', revenue: 2800, costs: 700 },
      { date: 'Sun', revenue: 3500, costs: 900 },
    ],
    tasks: [
      { date: 'Mon', completed: 12, pending: 3 },
      { date: 'Tue', completed: 18, pending: 5 },
      { date: 'Wed', completed: 24, pending: 2 },
      { date: 'Thu', completed: 21, pending: 4 },
      { date: 'Fri', completed: 32, pending: 6 },
      { date: 'Sat', completed: 28, pending: 3 },
      { date: 'Sun', completed: 35, pending: 2 },
    ],
    credits: [
      { date: 'Mon', balance: 5000, spent: 400 },
      { date: 'Tue', balance: 4800, spent: 500 },
      { date: 'Wed', balance: 4600, spent: 600 },
      { date: 'Thu', balance: 4400, spent: 550 },
      { date: 'Fri', balance: 4200, spent: 800 },
      { date: 'Sat', balance: 4000, spent: 700 },
      { date: 'Sun', balance: 3800, spent: 900 },
    ],
    agents: [
      { name: 'CEO Agent', tasks: 45, revenue: 5000 },
      { name: 'Content Writer', tasks: 120, revenue: 3200 },
      { name: 'Sales Agent', tasks: 85, revenue: 8500 },
      { name: 'Analyst', tasks: 60, revenue: 1800 },
    ],
    stats: {
      totalRevenue: 17000,
      totalTasks: 160,
      activeAgents: 4,
      avgTaskCost: 45
    }
  }

  const displayData = data || mockData

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
              <span className="text-xl font-bold">Analytics</span>
            </Link>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
            <Link href="/billing" className="text-gray-600 hover:text-gray-900">
              Billing
            </Link>
            <div className="w-8 h-8 bg-gray-200 rounded-full"/>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Time Range Selector */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
          <div className="flex gap-2">
            {['24h', '7d', '30d', '90d'].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  timeRange === range
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                {range === '24h' ? 'Last 24h' : `Last ${range}`}
              </button>
            ))}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Revenue"
            value={`$${displayData.stats.totalRevenue.toLocaleString()}`}
            change="+23%"
            changeType="positive"
            icon={<DollarSign className="w-6 h-6" />}
          />
          <StatsCard
            title="Total Tasks"
            value={displayData.stats.totalTasks}
            change="+12"
            changeType="positive"
            icon={<CheckCircle className="w-6 h-6" />}
          />
          <StatsCard
            title="Active Agents"
            value={displayData.stats.activeAgents}
            change="0"
            changeType="neutral"
            icon={<Users className="w-6 h-6" />}
          />
          <StatsCard
            title="Avg Task Cost"
            value={`${displayData.stats.avgTaskCost} credits`}
            change="-5%"
            changeType="positive"
            icon={<TrendingUp className="w-6 h-6" />}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Revenue Chart */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue vs Costs</h3>
            <RevenueChart data={displayData.revenue} />
          </div>

          {/* Tasks Chart */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Completion</h3>
            <TasksChart data={displayData.tasks} />
          </div>

          {/* Credits Chart */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Credits Usage</h3>
            <CreditsChart data={displayData.credits} />
          </div>

          {/* Agents Chart */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Performance</h3>
            <AgentsChart data={displayData.agents} />
          </div>
        </div>
      </main>
    </div>
  )
}
