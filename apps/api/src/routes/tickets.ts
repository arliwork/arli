import { FastifyInstance } from 'fastify'
import { prisma } from '@arli/database'
import { z } from 'zod'

const createTicketSchema = z.object({
  title: z.string().min(3).max(200),
  description: z.string().optional(),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']).default('MEDIUM'),
  goal: z.string().optional(),
  context: z.record(z.any()).optional(),
  companyId: z.string(),
  assignedToId: z.string().optional(),
})

export async function ticketRoutes(app: FastifyInstance) {
  // GET /api/tickets - List tickets
  app.get('/', async (request, reply) => {
    const { companyId, status, assignedToId } = request.query as { 
      companyId?: string
      status?: string
      assignedToId?: string
    }
    
    const tickets = await prisma.ticket.findMany({
      where: {
        companyId,
        status: status as any,
        assignedToId
      },
      include: {
        assignedTo: {
          select: { name: true, role: true }
        },
        company: {
          select: { name: true, slug: true }
        }
      },
      orderBy: { createdAt: 'desc' }
    })
    
    return {
      success: true,
      data: tickets
    }
  })

  // POST /api/tickets - Create ticket
  app.post('/', async (request, reply) => {
    try {
      const data = createTicketSchema.parse(request.body)
      
      const ticket = await prisma.ticket.create({
        data: {
          ...data,
          status: 'PENDING'
        }
      })
      
      return {
        success: true,
        data: ticket,
        message: 'Ticket created successfully'
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

  // GET /api/tickets/:id - Get ticket
  app.get('/:id', async (request, reply) => {
    const { id } = request.params as { id: string }
    
    const ticket = await prisma.ticket.findUnique({
      where: { id },
      include: {
        assignedTo: true,
        company: true
      }
    })
    
    if (!ticket) {
      return reply.status(404).send({
        success: false,
        error: 'Ticket not found'
      })
    }
    
    return {
      success: true,
      data: ticket
    }
  })

  // POST /api/tickets/:id/assign - Assign ticket to agent
  app.post('/:id/assign', async (request, reply) => {
    const { id } = request.params as { id: string }
    const { agentId } = request.body as { agentId: string }
    
    const ticket = await prisma.ticket.update({
      where: { id },
      data: { 
        assignedToId: agentId,
        status: 'IN_PROGRESS',
        startedAt: new Date()
      }
    })
    
    return {
      success: true,
      data: ticket
    }
  })

  // POST /api/tickets/:id/complete - Complete ticket
  app.post('/:id/complete', async (request, reply) => {
    const { id } = request.params as { id: string }
    const { result, cost } = request.body as { result: string, cost: number }
    
    const ticket = await prisma.ticket.update({
      where: { id },
      data: { 
        status: 'COMPLETED',
        result,
        cost,
        completedAt: new Date()
      }
    })
    
    // Deduct credits from company
    await prisma.company.update({
      where: { id: ticket.companyId },
      data: {
        credits: { decrement: cost },
        totalSpent: { increment: cost }
      }
    })
    
    return {
      success: true,
      data: ticket
    }
  })
}