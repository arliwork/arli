import { FastifyInstance } from 'fastify'
import { prisma } from '@arli/database'
import { calculateRevenueShare, CREDIT_PACKAGES } from '@arli/types'
import { verifyAuth } from '../middleware/auth'
import { stripeService } from '../services/stripe'

export async function billingRoutes(app: FastifyInstance) {
  // All billing routes require auth
  app.addHook('preHandler', verifyAuth)

  // GET /api/billing/packages - Get credit packages
  app.get('/packages', async () => {
    return {
      success: true,
      data: CREDIT_PACKAGES
    }
  })

  // POST /api/billing/checkout - Create Stripe checkout session
  app.post('/checkout', async (request, reply) => {
    try {
      const { companyId, packageId } = request.body as { 
        companyId: string
        packageId: string 
      }
      
      if (!companyId || !packageId) {
        return reply.status(400).send({
          success: false,
          error: 'Company ID and package ID required'
        })
      }

      // Verify company belongs to user
      const company = await prisma.company.findFirst({
        where: { 
          id: companyId,
          ownerId: request.user!.id
        }
      })

      if (!company) {
        return reply.status(404).send({
          success: false,
          error: 'Company not found'
        })
      }

      const session = await stripeService.createCheckoutSession(
        companyId,
        packageId,
        request.user!.id
      )

      return {
        success: true,
        url: session.url
      }
    } catch (error: any) {
      console.error('Checkout error:', error)
      return reply.status(500).send({
        success: false,
        error: error.message || 'Failed to create checkout'
      })
    }
  })

  // POST /api/billing/portal - Create Stripe customer portal session
  app.post('/portal', async (request, reply) => {
    try {
      // Get user's first company with Stripe customer ID
      const company = await prisma.company.findFirst({
        where: { ownerId: request.user!.id },
        where: { stripeCustomerId: { not: null } }
      })

      if (!company?.stripeCustomerId) {
        return reply.status(400).send({
          success: false,
          error: 'No billing history found'
        })
      }

      const session = await stripeService.createPortalSession(company.stripeCustomerId)

      return {
        success: true,
        url: session.url
      }
    } catch (error: any) {
      console.error('Portal error:', error)
      return reply.status(500).send({
        success: false,
        error: error.message || 'Failed to create portal session'
      })
    }
  })

  // GET /api/billing/balance - Get company balance
  app.get('/balance', async (request, reply) => {
    const { companyId } = request.query as { companyId: string }
    
    if (!companyId) {
      return reply.status(400).send({
        success: false,
        error: 'Company ID required'
      })
    }

    // Verify ownership
    const company = await prisma.company.findFirst({
      where: { 
        id: companyId,
        ownerId: request.user!.id
      },
      select: { credits: true, totalSpent: true, totalRevenue: true }
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

  // POST /api/billing/purchase - Direct credit purchase (admin only)
  app.post('/purchase', async (request, reply) => {
    const { companyId, packageId } = request.body as { companyId: string, packageId: string }
    
    const package_ = CREDIT_PACKAGES.find(p => p.id === packageId)
    
    if (!package_) {
      return reply.status(400).send({
        success: false,
        error: 'Invalid package'
      })
    }

    // Verify ownership
    const company = await prisma.company.findFirst({
      where: { 
        id: companyId,
        ownerId: request.user!.id
      }
    })

    if (!company) {
      return reply.status(404).send({
        success: false,
        error: 'Company not found'
      })
    }
    
    const totalCredits = package_.credits + (package_.bonusCredits || 0)
    
    const updated = await prisma.company.update({
      where: { id: companyId },
      data: {
        credits: { increment: totalCredits }
      }
    })
    
    // Create transaction record
    await prisma.transaction.create({
      data: {
        type: 'CREDIT_PURCHASE',
        amount: totalCredits,
        description: `Purchase: ${package_.name}`,
        companyId
      }
    })
    
    return {
      success: true,
      data: {
        credits: updated.credits,
        purchased: totalCredits,
        cost: package_.priceUsd
      },
      message: `Added ${totalCredits} credits`
    }
  })

  // POST /api/billing/revenue - Record revenue (for revenue share)
  app.post('/revenue', async (request, reply) => {
    const { companyId, amount, source } = request.body as { 
      companyId: string
      amount: number
      source: string
    }
    
    const company = await prisma.company.findFirst({
      where: { 
        id: companyId,
        ownerId: request.user!.id
      }
    })
    
    if (!company) {
      return reply.status(404).send({
        success: false,
        error: 'Company not found'
      })
    }
    
    // Calculate revenue share
    const calculation = calculateRevenueShare(amount, company.platformFeeRate)
    
    // Create revenue log
    await prisma.revenueLog.create({
      data: {
        companyId,
        amount,
        platformFee: calculation.platformFee,
        netAmount: calculation.netRevenue
      }
    })
    
    // Update company totals
    await prisma.company.update({
      where: { id: companyId },
      data: {
        totalRevenue: { increment: amount }
      }
    })
    
    return {
      success: true,
      data: calculation
    }
  })

  // GET /api/billing/transactions - Get transaction history
  app.get('/transactions', async (request, reply) => {
    const { companyId } = request.query as { companyId: string }
    
    // Verify ownership
    const company = await prisma.company.findFirst({
      where: { 
        id: companyId,
        ownerId: request.user!.id
      }
    })

    if (!company) {
      return reply.status(404).send({
        success: false,
        error: 'Company not found'
      })
    }
    
    const transactions = await prisma.transaction.findMany({
      where: { companyId },
      orderBy: { createdAt: 'desc' },
      take: 50
    })
    
    return {
      success: true,
      data: transactions
    }
  })
}
