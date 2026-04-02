import { FastifyInstance } from 'fastify'
import { prisma } from '@arli/database'

export async function analyticsRoutes(app: FastifyInstance) {
  // GET /api/analytics/company/:id - Company analytics
  app.get('/company/:id', async (request, reply) => {
    const { id } = request.params as { id: string }
    
    const company = await prisma.company.findUnique({
      where: { id },
      include: {
        _count: {
          select: { agents: true, tickets: true }
        },
        tickets: {
          where: { status: 'COMPLETED' },
          select: { cost: true }
        },
        revenueLogs: {
          select: { amount: true, createdAt: true },
          orderBy: { createdAt: 'desc' },
          take: 30
        }
      }
    })
    
    if (!company) {
      return reply.status(404).send({
        success: false,
        error: 'Company not found'
      })
    }
    
    // Calculate metrics
    const totalSpent = company.tickets.reduce((sum, t) => sum + (t.cost || 0), 0)
    const ticketsCompleted = company.tickets.length
    const averageTicketCost = ticketsCompleted > 0 ? Math.round(totalSpent / ticketsCompleted) : 0
    
    // Revenue metrics
    const monthlyRevenue = company.revenueLogs.reduce((sum, r) => sum + r.amount, 0)
    const roi = totalSpent > 0 ? ((company.totalRevenue - totalSpent) / totalSpent * 100).toFixed(2) : '0'
    
    return {
      success: true,
      data: {
        company: {
          name: company.name,
          status: company.status,
          credits: company.credits
        },
        metrics: {
          totalRevenue: company.totalRevenue,
          totalSpent,
          roi: `${roi}%`,
          ticketsCompleted,
          averageTicketCost,
          activeAgents: company._count.agents,
          monthlyRevenue
        },
        recentRevenue: company.revenueLogs
      }
    }
  })

  // GET /api/analytics/platform - Platform-wide stats (admin)
  app.get('/platform', async () => {
    const stats = await prisma.$transaction([
      prisma.company.count(),
      prisma.company.count({ where: { status: 'ACTIVE' } }),
      prisma.agent.count(),
      prisma.ticket.count(),
      prisma.ticket.count({ where: { status: 'COMPLETED' } }),
      prisma.transaction.aggregate({
        where: { type: 'CREDIT_PURCHASE' },
        _sum: { amount: true }
      }),
      prisma.revenueLog.aggregate({
        _sum: { platformFee: true }
      })
    ])
    
    return {
      success: true,
      data: {
        totalCompanies: stats[0],
        activeCompanies: stats[1],
        totalAgents: stats[2],
        totalTickets: stats[3],
        completedTickets: stats[4],
        totalCreditsPurchased: stats[5]._sum.amount || 0,
        totalPlatformRevenue: stats[6]._sum.platformFee || 0
      }
    }
  })
}