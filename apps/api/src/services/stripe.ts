import Stripe from 'stripe'
import { prisma } from '@arli/database'
import { CREDIT_PACKAGES } from '@arli/types'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', {
  apiVersion: '2023-10-16',
})

/**
 * Stripe Service
 * Handles payments and billing
 */
export class StripeService {
  /**
   * Create a checkout session for credit purchase
   */
  async createCheckoutSession(
    companyId: string,
    packageId: string,
    userId: string
  ) {
    const package_ = CREDIT_PACKAGES.find(p => p.id === packageId)
    
    if (!package_) {
      throw new Error('Invalid package')
    }

    // Create or get Stripe customer
    let company = await prisma.company.findUnique({
      where: { id: companyId }
    })

    let customerId = company?.stripeCustomerId

    if (!customerId) {
      const customer = await stripe.customers.create({
        metadata: {
          companyId,
          userId
        }
      })
      customerId = customer.id

      // Save customer ID
      await prisma.company.update({
        where: { id: companyId },
        data: { stripeCustomerId: customerId }
      })
    }

    // Create checkout session
    const session = await stripe.checkout.sessions.create({
      customer: customerId,
      payment_method_types: ['card'],
      line_items: [
        {
          price_data: {
            currency: 'usd',
            product_data: {
              name: `ARLI Credits - ${package_.name}`,
              description: `${package_.credits.toLocaleString()} credits + ${package_.bonusCredits || 0} bonus`,
            },
            unit_amount: package_.priceUsd * 100, // Convert to cents
          },
          quantity: 1,
        },
      ],
      mode: 'payment',
      success_url: `${process.env.FRONTEND_URL}/billing/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.FRONTEND_URL}/billing/cancel`,
      metadata: {
        companyId,
        packageId,
        userId,
        credits: (package_.credits + (package_.bonusCredits || 0)).toString()
      }
    })

    return session
  }

  /**
   * Handle Stripe webhook
   */
  async handleWebhook(payload: string, signature: string) {
    const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET || ''
    
    let event: Stripe.Event
    
    try {
      event = stripe.webhooks.constructEvent(payload, signature, webhookSecret)
    } catch (error: any) {
      throw new Error(`Webhook signature verification failed: ${error.message}`)
    }

    // Handle the event
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session
        await this.handleCheckoutComplete(session)
        break
      }
      
      case 'invoice.payment_succeeded': {
        // Handle subscription payments if we add them later
        break
      }
      
      case 'invoice.payment_failed': {
        // Handle failed payments
        const invoice = event.data.object as Stripe.Invoice
        console.error(`Payment failed for invoice: ${invoice.id}`)
        break
      }
      
      default:
        console.log(`Unhandled event type: ${event.type}`)
    }

    return { received: true }
  }

  /**
   * Handle completed checkout
   */
  private async handleCheckoutComplete(session: Stripe.Checkout.Session) {
    const { companyId, packageId, credits } = session.metadata || {}

    if (!companyId || !credits) {
      throw new Error('Missing metadata in session')
    }

    const creditsNum = parseInt(credits)

    // Update company credits
    await prisma.company.update({
      where: { id: companyId },
      data: {
        credits: { increment: creditsNum }
      }
    })

    // Create transaction record
    await prisma.transaction.create({
      data: {
        type: 'CREDIT_PURCHASE',
        amount: creditsNum,
        description: `Purchase: ${packageId}`,
        stripePaymentId: session.payment_intent as string,
        companyId
      }
    })

    console.log(`✅ Credited ${creditsNum} credits to company ${companyId}`)
  }

  /**
   * Get customer payment methods
   */
  async getPaymentMethods(customerId: string) {
    const methods = await stripe.paymentMethods.list({
      customer: customerId,
      type: 'card'
    })

    return methods.data
  }

  /**
   * Create a portal session for customer to manage billing
   */
  async createPortalSession(customerId: string) {
    const session = await stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: `${process.env.FRONTEND_URL}/billing`,
    })

    return session
  }

  /**
   * Get Stripe customer ID for company
   */
  async getOrCreateCustomer(companyId: string, email: string) {
    const company = await prisma.company.findUnique({
      where: { id: companyId }
    })

    if (company?.stripeCustomerId) {
      return company.stripeCustomerId
    }

    const customer = await stripe.customers.create({
      email,
      metadata: { companyId }
    })

    await prisma.company.update({
      where: { id: companyId },
      data: { stripeCustomerId: customer.id }
    })

    return customer.id
  }
}

// Export singleton
export const stripeService = new StripeService()