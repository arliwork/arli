// API Response types
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

// Pagination
export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

// Company types
export interface CreateCompanyInput {
  name: string
  slug: string
  description?: string
  template?: string
  niche?: string
  initialCredits?: number
}

export interface CompanySettings {
  heartbeatInterval: number
  autoScale: boolean
  notificationPreferences: {
    email: boolean
    telegram?: string
  }
}

// Agent types
export interface CreateAgentInput {
  name: string
  role: string
  description?: string
  adapter: string
  config: Record<string, any>
  monthlyBudget: number
}

export interface AgentConfig {
  model?: string
  apiKey?: string
  temperature?: number
  maxTokens?: number
  endpoints?: string[]
  customPrompt?: string
}

// Ticket types
export interface CreateTicketInput {
  title: string
  description?: string
  priority?: string
  goal?: string
  context?: Record<string, any>
}

export interface TicketExecutionResult {
  success: boolean
  result?: string
  error?: string
  cost: number
  duration: number // в секундах
}

// Credit system
export interface CreditPackage {
  id: string
  name: string
  credits: number
  priceUsd: number
  bonusCredits?: number
}

export const CREDIT_PACKAGES: CreditPackage[] = [
  { id: 'starter', name: 'Starter', credits: 1000, priceUsd: 10 },
  { id: 'growth', name: 'Growth', credits: 5000, priceUsd: 45, bonusCredits: 500 },
  { id: 'scale', name: 'Scale', credits: 20000, priceUsd: 150, bonusCredits: 3000 },
  { id: 'enterprise', name: 'Enterprise', credits: 100000, priceUsd: 500, bonusCredits: 25000 },
]

// Revenue share
export interface RevenueShareCalculation {
  grossRevenue: number
  platformFee: number
  platformFeeRate: number
  netRevenue: number
  skillRoyalties: number
  ownerPayout: number
}

export function calculateRevenueShare(
  grossRevenue: number,
  platformFeeRate: number = 0.10
): RevenueShareCalculation {
  const platformFee = Math.floor(grossRevenue * platformFeeRate)
  const skillRoyalties = Math.floor(grossRevenue * 0.05) // 5% на skills
  const netRevenue = grossRevenue - platformFee - skillRoyalties
  
  return {
    grossRevenue,
    platformFee,
    platformFeeRate,
    netRevenue,
    skillRoyalties,
    ownerPayout: netRevenue,
  }
}

// Heartbeat
export interface HeartbeatConfig {
  intervalMinutes: number
  maxConcurrentTasks: number
  retryAttempts: number
  backoffMultiplier: number
}

// Skills
export interface SkillManifest {
  name: string
  version: string
  description: string
  category: string
  author: string
  price: number
  isSubscription: boolean
  dependencies?: string[]
  compatibleAdapters: string[]
}

// Analytics
export interface CompanyAnalytics {
  totalRevenue: number
  totalSpent: number
  roi: number
  ticketsCompleted: number
  ticketsFailed: number
  averageTicketCost: number
  activeAgents: number
  monthlyGrowth: number
}