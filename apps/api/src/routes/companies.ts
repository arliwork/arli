import { FastifyInstance } from 'fastify'
import { prisma } from '@arli/database'
import { z } from 'zod'
import { createCompanyFromTemplate, listTemplates, COMPANY_TEMPLATES } from '../services/templates'

const createCompanySchema = z.object({
  name: z.string().min(3).max(100),
  slug: z.string().min(3).max(50).regex(/^[a-z0-9-]+$/),
  description: z.string().optional(),
  template: z.enum(['CUSTOM', 'CONTENT_AGENCY', 'DROPSHIPPING', 'SAAS', 'TRADING_BOT', 'AFFILIATE_MARKETING']).default('CUSTOM'),
  niche: z.string().optional(),
  initialCredits: z.number().int().min(0).default(1000),
  useTemplate: z.string().optional(), // Template ID for quick setup
})

export async function companyRoutes(app: FastifyInstance) {
  // GET /api/companies/templates - List available templates
  app.get('/templates', async () => {
    return {
      success: true,
      data: listTemplates()
    }
  })

  // GET /api/companies - List all companies for user
  app.get('/', async (request, reply) => {
    // TODO: Get userId from JWT
    const userId = 'demo-user-id' // Placeholder
    
    const companies = await prisma.company.findMany({
      where: { ownerId: userId },
      include: {
        _count: {
          select: { agents: true, tickets: true }
        }
      },
      orderBy: { createdAt: 'desc' }
    })
    
    return {
      success: true,
      data: companies
    }
  })

  // GET /api/companies/:id - Get company details
  app.get('/:id', async (request, reply) => {
    const { id } = request.params as { id: string }
    
    const company = await prisma.company.findUnique({
      where: { id },
      include: {
        agents: true,
        tickets: {
          orderBy: { createdAt: 'desc' },
          take: 10
        },
        _count: {
          select: { agents: true, tickets: true }
        }
      }
    })
    
    if (!company) {
      return reply.status(404).send({
        success: false,
        error: 'Company not found'
      })
    }
    
    return {
      success: true,
      data: company
    }
  })

  // POST /api/companies - Create new company
  app.post('/', async (request, reply) => {
    try {
      const data = createCompanySchema.parse(request.body)
      // TODO: Get userId from JWT
      const userId = 'demo-user-id' // Placeholder
      
      // Check if slug is unique
      const existing = await prisma.company.findUnique({
        where: { slug: data.slug }
      })
      
      if (existing) {
        return reply.status(400).send({
          success: false,
          error: 'Company slug already exists'
        })
      }

      // If using a template, use template creation
      if (data.useTemplate && COMPANY_TEMPLATES[data.useTemplate]) {
        const result = await createCompanyFromTemplate(
          userId,
          data.useTemplate,
          {
            name: data.name,
            slug: data.slug,
            niche: data.niche
          }
        )

        return {
          success: true,
          data: result.company,
          agents: result.agents,
          setupFee: result.setupFee,
          message: `Company created from ${data.useTemplate} template`
        }
      }
      
      // Otherwise, create custom company
      const company = await prisma.company.create({
        data: {
          ...data,
          ownerId: userId,
          status: 'ACTIVE',
        }
      })
      
      // Create default agents based on template
      await createDefaultAgents(company.id, company.template)
      
      return {
        success: true,
        data: company,
        message: 'Company created successfully'
      }
    } catch (error) {
      if (error instanceof z.ZodError) {
        return reply.status(400).send({
          success: false,
          error: 'Validation error',
          details: error.errors
        })
      }
      throw error
    }
  })

  // PATCH /api/companies/:id - Update company
  app.patch('/:id', async (request, reply) => {
    const { id } = request.params as { id: string }
    const updateSchema = createCompanySchema.partial()
    
    try {
      const data = updateSchema.parse(request.body)
      
      const company = await prisma.company.update({
        where: { id },
        data
      })
      
      return {
        success: true,
        data: company
      }
    } catch (error) {
      if (error instanceof z.ZodError) {
        return reply.status(400).send({
          success: false,
          error: 'Validation error',
          details: error.errors
        })
      }
      throw error
    }
  })

  // DELETE /api/companies/:id - Delete company
  app.delete('/:id', async (request, reply) => {
    const { id } = request.params as { id: string }
    
    await prisma.company.delete({
      where: { id }
    })
    
    return {
      success: true,
      message: 'Company deleted successfully'
    }
  })

  // POST /api/companies/:id/pause - Pause company
  app.post('/:id/pause', async (request, reply) => {
    const { id } = request.params as { id: string }
    
    const company = await prisma.company.update({
      where: { id },
      data: { status: 'PAUSED' }
    })
    
    return {
      success: true,
      data: company,
      message: 'Company paused'
    }
  })

  // POST /api/companies/:id/resume - Resume company
  app.post('/:id/resume', async (request, reply) => {
    const { id } = request.params as { id: string }
    
    const company = await prisma.company.update({
      where: { id },
      data: { status: 'ACTIVE' }
    })
    
    return {
      success: true,
      data: company,
      message: 'Company resumed'
    }
  })
}

// Helper function to create default agents based on template
async function createDefaultAgents(companyId: string, template: string) {
  const defaultAgents: Record<string, Array<{name: string, role: string, adapter: string, description: string}>> = {
    CONTENT_AGENCY: [
      { name: 'CEO Agent', role: 'CEO', adapter: 'CLAUDE', description: 'Strategic planning and oversight' },
      { name: 'Content Creator', role: 'SPECIALIST', adapter: 'CLAUDE', description: 'Creates viral content' },
      { name: 'Trend Researcher', role: 'WORKER', adapter: 'HTTP', description: 'Finds trending topics' },
      { name: 'Scheduler', role: 'WORKER', adapter: 'HTTP', description: 'Schedules posts' },
    ],
    DROPSHIPPING: [
      { name: 'CEO Agent', role: 'CEO', adapter: 'CLAUDE', description: 'Business strategy' },
      { name: 'Product Hunter', role: 'SPECIALIST', adapter: 'HTTP', description: 'Finds winning products' },
      { name: 'Ad Manager', role: 'SPECIALIST', adapter: 'HTTP', description: 'Manages ad campaigns' },
      { name: 'Support Agent', role: 'WORKER', adapter: 'CLAUDE', description: 'Customer support' },
    ],
    SAAS: [
      { name: 'CEO Agent', role: 'CEO', adapter: 'CLAUDE', description: 'Product strategy' },
      { name: 'Dev Agent', role: 'SPECIALIST', adapter: 'CODEX', description: 'Full-stack development' },
      { name: 'Marketing Agent', role: 'SPECIALIST', adapter: 'CLAUDE', description: 'Growth marketing' },
    ],
    CUSTOM: [
      { name: 'CEO Agent', role: 'CEO', adapter: 'CLAUDE', description: 'Strategic oversight' },
    ]
  }
  
  const agents = defaultAgents[template] || defaultAgents.CUSTOM
  
  await Promise.all(
    agents.map(agent => 
      prisma.agent.create({
        data: {
          ...agent,
          companyId,
          config: {},
          monthlyBudget: 1000,
        }
      })
    )
  )
}