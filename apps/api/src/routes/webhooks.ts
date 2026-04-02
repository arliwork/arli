import { FastifyInstance } from 'fastify'
import { stripeService } from '../services/stripe'

export async function webhookRoutes(app: FastifyInstance) {
  // Stripe webhook endpoint
  app.post('/stripe', {
    config: {
      // Disable body parsing for Stripe webhooks
      rawBody: true
    }
  }, async (request, reply) => {
    try {
      const payload = request.body as string
      const signature = request.headers['stripe-signature'] as string

      if (!signature) {
        return reply.status(400).send({
          success: false,
          error: 'Missing stripe-signature header'
        })
      }

      await stripeService.handleWebhook(payload, signature)

      return { received: true }
    } catch (error: any) {
      console.error('Webhook error:', error)
      return reply.status(400).send({
        success: false,
        error: error.message
      })
    }
  })

  // Clerk webhook for user events
  app.post('/clerk', async (request, reply) => {
    try {
      const payload = request.body as any
      const event = payload.type

      switch (event) {
        case 'user.created':
          console.log('👤 New user created:', payload.data.id)
          // Could create welcome company or send email
          break

        case 'user.updated':
          console.log('👤 User updated:', payload.data.id)
          break

        case 'user.deleted':
          console.log('👤 User deleted:', payload.data.id)
          // Cleanup user data
          break

        case 'organization.created':
          console.log('🏢 New org created:', payload.data.id)
          break

        default:
          console.log('Unhandled Clerk event:', event)
      }

      return { received: true }
    } catch (error: any) {
      console.error('Clerk webhook error:', error)
      return reply.status(400).send({
        success: false,
        error: error.message
      })
    }
  })
}