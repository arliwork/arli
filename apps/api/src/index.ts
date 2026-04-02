import Fastify from 'fastify'
import cors from '@fastify/cors'
import swagger from '@fastify/swagger'
import swaggerUi from '@fastify/swagger-ui'
import jwt from '@fastify/jwt'
import { companyRoutes } from './routes/companies'
import { agentRoutes } from './routes/agents'
import { ticketRoutes } from './routes/tickets'
import { billingRoutes } from './routes/billing'
import { skillRoutes } from './routes/skills'
import { analyticsRoutes } from './routes/analytics'
import { heartbeatService } from './services/heartbeat'
import { taskQueue, notificationQueue, revenueQueue } from './services/queue'
import { stripeService } from './services/stripe'

const app = Fastify({
  logger: true,
})

// Register plugins
app.register(cors, {
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
})

// JWT для авторизации
app.register(jwt, {
  secret: process.env.JWT_SECRET || 'super-secret-change-in-production',
})

// Swagger документация
app.register(swagger, {
  swagger: {
    info: {
      title: 'ARLI API',
      description: 'Autonomous Revenue & Labor Intelligence Platform API',
      version: '0.1.0',
    },
    tags: [
      { name: 'companies', description: 'Company management' },
      { name: 'agents', description: 'AI agent management' },
      { name: 'tickets', description: 'Task ticket management' },
      { name: 'billing', description: 'Credits and payments' },
      { name: 'skills', description: 'Skills marketplace' },
      { name: 'analytics', description: 'Analytics and reporting' },
    ],
  },
})

app.register(swaggerUi, {
  routePrefix: '/docs',
})

// Health check
app.get('/health', async () => {
  // Check queue health
  const queueHealth = {
    tasks: await taskQueue.getJobCounts(),
    notifications: await notificationQueue.getJobCounts(),
    revenue: await revenueQueue.getJobCounts()
  }

  return { 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    queues: queueHealth
  }
})

// Stripe webhook (needs raw body)
app.post('/api/stripe/webhook', {
  config: {
    // Disable body parsing for Stripe webhook
    rawBody: true
  }
}, async (request, reply) => {
  try {
    const payload = request.body as string
    const signature = request.headers['stripe-signature'] as string
    
    if (!signature) {
      return reply.status(400).send({ error: 'Missing signature' })
    }
    
    await stripeService.handleWebhook(payload, signature)
    return { received: true }
  } catch (error: any) {
    app.log.error('Webhook error:', error)
    return reply.status(400).send({ error: error.message })
  }
})

// Register routes
app.register(companyRoutes, { prefix: '/api/companies' })
app.register(agentRoutes, { prefix: '/api/agents' })
app.register(ticketRoutes, { prefix: '/api/tickets' })
app.register(billingRoutes, { prefix: '/api/billing' })
app.register(skillRoutes, { prefix: '/api/skills' })
app.register(analyticsRoutes, { prefix: '/api/analytics' })

// Error handler
app.setErrorHandler((error, request, reply) => {
  app.log.error(error)
  reply.status(error.statusCode || 500).send({
    success: false,
    error: error.message || 'Internal Server Error',
  })
})

// Start server
const start = async () => {
  try {
    const port = parseInt(process.env.PORT || '3100')
    
    // Start heartbeat service
    await heartbeatService.start()
    
    await app.listen({ port, host: '0.0.0.0' })
    app.log.info(`🚀 ARLI API running on port ${port}`)
    app.log.info(`📚 Swagger docs at http://localhost:${port}/docs`)
    app.log.info(`🫀 Heartbeat service active`)
    app.log.info(`📬 Task queues initialized`)
  } catch (err) {
    app.log.error(err)
    process.exit(1)
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  app.log.info('SIGTERM received, closing server...')
  await app.close()
  await taskQueue.close()
  await notificationQueue.close()
  await revenueQueue.close()
  process.exit(0)
})

start()