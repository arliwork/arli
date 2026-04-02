import { FastifyInstance } from 'fastify'
import { prisma } from '@arli/database'

export async function skillRoutes(app: FastifyInstance) {
  // GET /api/skills - List all skills
  app.get('/', async (request, reply) => {
    const { category } = request.query as { category?: string }
    
    const skills = await prisma.skill.findMany({
      where: category ? { category } : undefined,
      orderBy: { downloads: 'desc' },
      take: 100
    })
    
    return {
      success: true,
      data: skills
    }
  })

  // GET /api/skills/:id - Get skill details
  app.get('/:id', async (request, reply) => {
    const { id } = request.params as { id: string }
    
    const skill = await prisma.skill.findUnique({
      where: { id }
    })
    
    if (!skill) {
      return reply.status(404).send({
        success: false,
        error: 'Skill not found'
      })
    }
    
    return {
      success: true,
      data: skill
    }
  })

  // POST /api/skills - Create skill (for developers)
  app.post('/', async (request, reply) => {
    // TODO: Auth check for developers
    const skill = await prisma.skill.create({
      data: request.body as any
    })
    
    return {
      success: true,
      data: skill
    }
  })

  // POST /api/skills/:id/purchase - Purchase skill for agent
  app.post('/:id/purchase', async (request, reply) => {
    const { id } = request.params as { id: string }
    const { agentId } = request.body as { agentId: string }
    
    const skill = await prisma.skill.findUnique({
      where: { id }
    })
    
    if (!skill) {
      return reply.status(404).send({
        success: false,
        error: 'Skill not found'
      })
    }
    
    const agent = await prisma.agent.findUnique({
      where: { id: agentId },
      include: { company: true }
    })
    
    if (!agent) {
      return reply.status(404).send({
        success: false,
        error: 'Agent not found'
      })
    }
    
    // Check if already purchased
    const existing = await prisma.agentSkill.findUnique({
      where: {
        agentId_skillId: {
          agentId,
          skillId: id
        }
      }
    })
    
    if (existing) {
      return reply.status(400).send({
        success: false,
        error: 'Skill already purchased for this agent'
      })
    }
    
    // Check credits
    if (agent.company.credits < skill.price) {
      return reply.status(400).send({
        success: false,
        error: 'Insufficient credits'
      })
    }
    
    // Deduct credits
    await prisma.company.update({
      where: { id: agent.companyId },
      data: {
        credits: { decrement: skill.price }
      }
    })
    
    // Create purchase record
    await prisma.agentSkill.create({
      data: {
        agentId,
        skillId: id,
        expiresAt: skill.isSubscription ? new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) : null
      }
    })
    
    // Update skill downloads
    await prisma.skill.update({
      where: { id },
      data: { downloads: { increment: 1 } }
    })
    
    // Revenue share (70% to author, 30% to platform)
    const authorShare = Math.floor(skill.price * 0.7)
    const platformShare = skill.price - authorShare
    
    // TODO: Transfer to author
    
    return {
      success: true,
      message: 'Skill purchased successfully',
      data: {
        skill: skill.name,
        cost: skill.price,
        remainingCredits: agent.company.credits - skill.price
      }
    }
  })
}