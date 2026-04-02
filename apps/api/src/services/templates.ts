import { prisma } from '@arli/database'
import { CreateCompanyInput } from '@arli/types'

/**
 * Company Templates
 * Pre-configured company setups for instant launch
 */
export interface CompanyTemplate {
  id: string
  name: string
  description: string
  category: string
  setupFee: number
  recommendedCredits: number
  agents: Array<{
    name: string
    role: string
    adapter: string
    description: string
    skills: string[]
    monthlyBudget: number
  }>
  initialTickets: Array<{
    title: string
    description: string
    priority: string
    goal: string
  }>
  config: {
    heartbeatInterval: number
    niche: string
  }
}

export const COMPANY_TEMPLATES: Record<string, CompanyTemplate> = {
  'content-agency': {
    id: 'content-agency',
    name: 'AI Content Agency',
    description: 'Create viral TikTok and Instagram content on autopilot',
    category: 'Marketing',
    setupFee: 199,
    recommendedCredits: 5000,
    agents: [
      {
        name: 'CEO Agent',
        role: 'CEO',
        adapter: 'CLAUDE',
        description: 'Strategic planning, content calendar, and quality control',
        skills: ['strategy-planning', 'content-calendar'],
        monthlyBudget: 2000
      },
      {
        name: 'Trend Hunter',
        role: 'SPECIALIST',
        adapter: 'HTTP',
        description: 'Finds viral trends, sounds, and hashtags',
        skills: ['trend-research', 'hashtag-optimization'],
        monthlyBudget: 1000
      },
      {
        name: 'Content Creator',
        role: 'SPECIALIST',
        adapter: 'CLAUDE',
        description: 'Writes scripts and creates content ideas',
        skills: ['script-writing', 'content-ideation', 'viral-formulas'],
        monthlyBudget: 3000
      },
      {
        name: 'Post Scheduler',
        role: 'WORKER',
        adapter: 'HTTP',
        description: 'Schedules posts on TikTok, Instagram, and other platforms',
        skills: ['postiz-scheduling', 'buffer-posting'],
        monthlyBudget: 500
      },
      {
        name: 'Analytics Expert',
        role: 'SPECIALIST',
        adapter: 'CLAUDE',
        description: 'Analyzes performance and suggests optimizations',
        skills: ['analytics-review', 'performance-optimization'],
        monthlyBudget: 1000
      }
    ],
    initialTickets: [
      {
        title: 'Research trending hashtags in niche',
        description: 'Find top 20 trending hashtags related to the selected niche',
        priority: 'HIGH',
        goal: 'Build hashtag strategy'
      },
      {
        title: 'Create content calendar',
        description: 'Plan 30 days of content with themes and topics',
        priority: 'HIGH',
        goal: 'Establish posting schedule'
      },
      {
        title: 'Write 5 viral scripts',
        description: 'Create scripts following viral content formulas',
        priority: 'MEDIUM',
        goal: 'Build content library'
      }
    ],
    config: {
      heartbeatInterval: 30,
      niche: 'general'
    }
  },

  'dropshipping': {
    id: 'dropshipping',
    name: 'Dropshipping Store',
    description: 'Automated product hunting, ad management, and order fulfillment',
    category: 'E-commerce',
    setupFee: 299,
    recommendedCredits: 10000,
    agents: [
      {
        name: 'CEO Agent',
        role: 'CEO',
        adapter: 'CLAUDE',
        description: 'Business strategy, store optimization, and profit analysis',
        skills: ['business-strategy', 'profit-analysis'],
        monthlyBudget: 2000
      },
      {
        name: 'Product Hunter',
        role: 'SPECIALIST',
        adapter: 'HTTP',
        description: 'Finds winning products using data analysis',
        skills: ['product-research', 'trend-analysis', 'competitor-analysis'],
        monthlyBudget: 3000
      },
      {
        name: 'Ad Manager',
        role: 'SPECIALIST',
        adapter: 'HTTP',
        description: 'Manages Facebook and TikTok ad campaigns',
        skills: ['facebook-ads', 'tiktok-ads', 'budget-optimization'],
        monthlyBudget: 5000
      },
      {
        name: 'Store Manager',
        role: 'MANAGER',
        adapter: 'HTTP',
        description: 'Manages Shopify store, listings, and inventory',
        skills: ['shopify-management', 'product-listing', 'inventory-sync'],
        monthlyBudget: 2000
      },
      {
        name: 'Customer Support',
        role: 'WORKER',
        adapter: 'CLAUDE',
        description: 'Handles customer inquiries and support tickets',
        skills: ['customer-support', 'email-handling', 'dispute-resolution'],
        monthlyBudget: 1500
      },
      {
        name: 'Fulfillment Coordinator',
        role: 'WORKER',
        adapter: 'HTTP',
        description: 'Coordinates with suppliers for order fulfillment',
        skills: ['order-processing', 'supplier-management'],
        monthlyBudget: 1000
      }
    ],
    initialTickets: [
      {
        title: 'Set up Shopify store',
        description: 'Configure store settings, payment gateways, and basic design',
        priority: 'HIGH',
        goal: 'Store ready for products'
      },
      {
        title: 'Find first winning product',
        description: 'Research and identify a product with high potential',
        priority: 'HIGH',
        goal: 'Launch first product'
      },
      {
        title: 'Create ad campaign structure',
        description: 'Set up Facebook Business Manager and campaign structure',
        priority: 'HIGH',
        goal: 'Ready for advertising'
      }
    ],
    config: {
      heartbeatInterval: 60,
      niche: 'general'
    }
  },

  'saas-micro': {
    id: 'saas-micro',
    name: 'Micro-SaaS Builder',
    description: 'Build and launch micro-SaaS products from scratch',
    category: 'Technology',
    setupFee: 499,
    recommendedCredits: 8000,
    agents: [
      {
        name: 'CEO Agent',
        role: 'CEO',
        adapter: 'CLAUDE',
        description: 'Product strategy, market research, and roadmap planning',
        skills: ['product-strategy', 'market-research', 'roadmap-planning'],
        monthlyBudget: 2000
      },
      {
        name: 'Full-Stack Developer',
        role: 'SPECIALIST',
        adapter: 'CODEX',
        description: 'Builds the entire application frontend and backend',
        skills: ['nextjs', 'typescript', 'postgresql', 'deployment'],
        monthlyBudget: 5000
      },
      {
        name: 'UI/UX Designer',
        role: 'SPECIALIST',
        adapter: 'CLAUDE',
        description: 'Designs interfaces and user experiences',
        skills: ['ui-design', 'ux-research', 'design-systems'],
        monthlyBudget: 2000
      },
      {
        name: 'Growth Marketer',
        role: 'SPECIALIST',
        adapter: 'CLAUDE',
        description: 'Marketing strategy, content, and user acquisition',
        skills: ['growth-marketing', 'content-strategy', 'seo'],
        monthlyBudget: 2000
      },
      {
        name: 'DevOps Engineer',
        role: 'SPECIALIST',
        adapter: 'BASH',
        description: 'Deployment, CI/CD, and infrastructure',
        skills: ['docker', 'aws', 'ci-cd', 'monitoring'],
        monthlyBudget: 1500
      }
    ],
    initialTickets: [
      {
        title: 'Validate product idea',
        description: 'Research market demand and competition analysis',
        priority: 'HIGH',
        goal: 'Validate market fit'
      },
      {
        title: 'Create MVP specification',
        description: 'Write detailed spec for minimum viable product',
        priority: 'HIGH',
        goal: 'Ready for development'
      },
      {
        title: 'Set up development environment',
        description: 'Initialize project repo, CI/CD, and deployment pipeline',
        priority: 'HIGH',
        goal: 'Ready to code'
      }
    ],
    config: {
      heartbeatInterval: 60,
      niche: 'saas'
    }
  }
}

/**
 * Create company from template
 */
export async function createCompanyFromTemplate(
  userId: string,
  templateId: string,
  customizations: {
    name: string
    slug: string
    niche?: string
  }
) {
  const template = COMPANY_TEMPLATES[templateId]
  
  if (!template) {
    throw new Error('Template not found')
  }

  // Create company
  const company = await prisma.company.create({
    data: {
      name: customizations.name,
      slug: customizations.slug,
      description: template.description,
      template: templateId.toUpperCase().replace('-', '_') as any,
      niche: customizations.niche || template.config.niche,
      heartbeatInterval: template.config.heartbeatInterval,
      credits: template.recommendedCredits,
      status: 'ACTIVE',
      ownerId: userId
    }
  })

  // Create agents from template
  const createdAgents = await Promise.all(
    template.agents.map(agent => 
      prisma.agent.create({
        data: {
          name: agent.name,
          role: agent.role as any,
          adapter: agent.adapter as any,
          description: agent.description,
          config: {},
          monthlyBudget: agent.monthlyBudget,
          companyId: company.id,
          isActive: true
        }
      })
    )
  )

  // Create initial tickets
  await Promise.all(
    template.initialTickets.map(ticket =>
      prisma.ticket.create({
        data: {
          title: ticket.title,
          description: ticket.description,
          priority: ticket.priority as any,
          goal: ticket.goal,
          status: 'PENDING',
          companyId: company.id,
          assignedToId: createdAgents[0]?.id // Assign to CEO
        }
      })
    )
  )

  return {
    company,
    agents: createdAgents,
    setupFee: template.setupFee,
    recommendedCredits: template.recommendedCredits
  }
}

/**
 * List all templates
 */
export function listTemplates() {
  return Object.values(COMPANY_TEMPLATES).map(t => ({
    id: t.id,
    name: t.name,
    description: t.description,
    category: t.category,
    setupFee: t.setupFee,
    recommendedCredits: t.recommendedCredits,
    agentCount: t.agents.length
  }))
}