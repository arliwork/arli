'use client'

import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

interface RevenueChartProps {
  data: { date: string; revenue: number; costs: number }[]
}

export function RevenueChart({ data }: RevenueChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="colorCosts" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
        <YAxis stroke="#6b7280" fontSize={12} />
        <Tooltip 
          contentStyle={{ background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb' }}
          formatter={(value: number) => `$${value.toFixed(2)}`}
        />
        <Legend />
        <Area type="monotone" dataKey="revenue" stroke="#3b82f6" fillOpacity={1} fill="url(#colorRevenue)" name="Revenue" />
        <Area type="monotone" dataKey="costs" stroke="#ef4444" fillOpacity={1} fill="url(#colorCosts)" name="Costs" />
      </AreaChart>
    </ResponsiveContainer>
  )
}

interface TasksChartProps {
  data: { date: string; completed: number; pending: number }[]
}

export function TasksChart({ data }: TasksChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
        <YAxis stroke="#6b7280" fontSize={12} />
        <Tooltip 
          contentStyle={{ background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb' }}
        />
        <Legend />
        <Bar dataKey="completed" fill="#10b981" name="Completed" radius={[4, 4, 0, 0]} />
        <Bar dataKey="pending" fill="#f59e0b" name="Pending" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

interface CreditsChartProps {
  data: { date: string; balance: number; spent: number }[]
}

export function CreditsChart({ data }: CreditsChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
        <YAxis stroke="#6b7280" fontSize={12} />
        <Tooltip 
          contentStyle={{ background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb' }}
        />
        <Legend />
        <Line type="monotone" dataKey="balance" stroke="#3b82f6" strokeWidth={2} name="Balance" dot={false} />
        <Line type="monotone" dataKey="spent" stroke="#ef4444" strokeWidth={2} name="Spent" dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}

interface AgentsChartProps {
  data: { name: string; tasks: number; revenue: number }[]
}

export function AgentsChart({ data }: AgentsChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" horizontal={false} />
        <XAxis type="number" stroke="#6b7280" fontSize={12} />
        <YAxis dataKey="name" type="category" stroke="#6b7280" fontSize={12} width={100} />
        <Tooltip 
          contentStyle={{ background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb' }}
        />
        <Legend />
        <Bar dataKey="tasks" fill="#3b82f6" name="Tasks" radius={[0, 4, 4, 0]} />
        <Bar dataKey="revenue" fill="#10b981" name="Revenue ($)" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

interface DistributionChartProps {
  data: { name: string; value: number }[]
}

export function DistributionChart({ data }: DistributionChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip 
          contentStyle={{ background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb' }}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}

interface StatsCardProps {
  title: string
  value: string | number
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
  icon?: React.ReactNode
}

export function StatsCard({ title, value, change, changeType = 'neutral', icon }: StatsCardProps) {
  const changeColors = {
    positive: 'text-green-600 bg-green-50',
    negative: 'text-red-600 bg-red-50',
    neutral: 'text-gray-600 bg-gray-50'
  }

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>
      {change && (
        <div className="mt-4">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${changeColors[changeType]}`}>
            {changeType === 'positive' && '↑ '}
            {changeType === 'negative' && '↓ '}
            {change}
          </span>
        </div>
      )}
    </div>
  )
}
