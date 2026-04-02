import { FastifyInstance } from 'fastify'
import { prisma } from '@arli/database'
import { z } from 'zod'

const createAgentSchema = z.object({
  name: z.string().min(2).max(100),
  role: z.enum(['CEO', 'MANAGER', 'WORKER', 'SPECIALIST']),
  description: z.string().optional(),
  adapter: z.enum(['CLAUDE', 'OPENCLAW', 'CODEX', 'CURSOR', 'HTTP', 'BASH']),
  config: z.record(z.any()).default({}),
  monthlyBudget: z.number().int().min(100).default(1000),
  companyId: z.string(),
})

export async function agentRoutes(app: FastifyInstance) {
  // GET /api/agents - List agents (optionally filtered by company)
  app.get('/', async (request, reply) => {
    const { companyId } = request.query as { companyId?: string }
    
    const agents = await prisma.agent.findMany({
      where: companyId ? { companyId } : undefined,
      include: {
        company: {
          select: { name: true, slug: true }
        },
        _count: {
          select: { tickets: true }
        }
      },
      orderBy: { createdAt: 'desc' }
    })
    
    return {
      success: true,
      data: agents
    }
  })

  // GET /api/agents/:id - Get agent details
  app.get('/:id', async (request, reply) => {
    const { id } = request.params as { id: string }
    
    const agent = await prisma.agent.findUnique({
      where: { id },
      include: {
        company: true,
        tickets: {
          orderBy: { createdAt: 'desc' },
          take: 10
        },
        skills: {
          include: { skill: true }
        }
      }
    })
    
    if (!agent) {
      return reply.status(404).send({
        success: false,
        error: 'Agent not found'
      })
    }
    
    return {
      success: true,
      data: agent
    }
  })

  // POST /api/agents - Create new agent
  app.post('/', async (request, reply) => {
    try {
      const data = createAgentSchema.parse(request.body)
      
      // Check if company exists
      const company = await prisma.company.findUnique({
        where: { id: data.companyId }
      })
      
      if (!company) {
        return reply.status(404).send({
          success: false,
          error: 'Company not found'
        })
      }
      
      const agent = await prisma.agent.create({
        data: {
          name: data.name,
          role: data.role,
          description: data.description,
          adapter: data.adapter,
          config: data.config,
          monthlyBudget: data.monthlyBudget,
          companyId: data.companyId,
          isActive: true,
        }
      })
      
      return {
        success: true,
        data: agent,
        message: 'Agent hired successfully'
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

  // PATCH /api/agents/:id - Update agent
  app.patch('/:id', async (request, reply) => {
    const { id } = request.params as { id: string }
    const updateSchema = createAgentSchema.partial().omit({ companyId: true })
    
    try {
      const data = updateSchema.parse(request.body)
      
      const agent = await prisma.agent.update({
        where: { id },
        data
      })
      
      return {
        success: true,
        data: agent
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

  // DELETE /api/agents/:id - Fire agent
  app.delete('/:id', async (request, reply) => {
    const { id } = request.params as { id: string }
    
    await prisma.agent.delete({
      where: { id }
    })
    
    return {
      success: true,
      message: 'Agent fired successfully'
    }
  })

  // POST /api/agents/:id/activate - Activate agent
  app.post('/:id/activate', async (request, reply) => {
    const { id } = request.params as { id: string }
    
    const agent = await prisma.agent.update({
      where: { id },
      data: { isActive: true }
    })
    
    return {
      success: true,
      data: agent,
      message: 'Agent activated'
    }
  })

  // POST /api/agents/:id/deactivate - Deactivate agent
  app.post('/:id/deactivate', async (request, reply) => {
    const { id } = request.params as { id: string }
    
    const agent = await prisma.agent.update({
      where: { id },
      data: { isActive: false }
    })
    
    return {
      success: true,
      data: agent,
      message: 'Agent deactivated'
    }
  })

  // GET /api/agents/:id/heartbeat - Trigger manual heartbeat
  app.post('/:id/heartbeat', async (request, reply) => {
    const { id } = request.params as { id: string }
    
    const agent = await prisma.agent.findUnique({
      where: { id },
      include: { company: true }
    })
    
    if (!agent) {
      return reply.status(404).send({
        success: false,
        error: 'Agent not found'
      })
    }
    
    if (!agent.isActive) {
      return reply.status(400).send({
        success: false,
        error: 'Agent is not active'
      })
    }
    
    // TODO: Implement actual heartbeat logic
    // This would trigger the agent to check for tasks and execute them
    
    await prisma.agent.update({
      where: { id },
      data: { lastRunAt: new Date() }
    })
    
    return {
      success: true,
      message: 'Heartbeat triggered',
      data: {
        agentId: id,
        timestamp: new Date().toISOString()
      }
    }
  })
}