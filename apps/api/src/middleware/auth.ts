import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify'
import { Clerk } from '@clerk/clerk-sdk-node'

const clerk = new Clerk({ secretKey: process.env.CLERK_SECRET_KEY || '' })

/**
 * Verify Clerk JWT token
 */
export async function verifyAuth(
  request: FastifyRequest,
  reply: FastifyReply
) {
  try {
    // Get token from Authorization header
    const authHeader = request.headers.authorization
    
    if (!authHeader?.startsWith('Bearer ')) {
      return reply.status(401).send({
        success: false,
        error: 'Unauthorized - No token provided'
      })
    }

    const token = authHeader.substring(7)
    
    // Verify with Clerk
    const decoded = await clerk.verifyToken(token)
    
    // Attach user info to request
    request.user = {
      id: decoded.sub,
      email: decoded.email as string,
      orgId: decoded.org_id as string | undefined
    }
    
  } catch (error) {
    console.error('Auth error:', error)
    return reply.status(401).send({
      success: false,
      error: 'Unauthorized - Invalid token'
    })
  }
}

/**
 * Optional auth - doesn't fail if no token
 */
export async function optionalAuth(
  request: FastifyRequest,
  reply: FastifyReply
) {
  try {
    const authHeader = request.headers.authorization
    
    if (authHeader?.startsWith('Bearer ')) {
      const token = authHeader.substring(7)
      const decoded = await clerk.verifyToken(token)
      
      request.user = {
        id: decoded.sub,
        email: decoded.email as string,
        orgId: decoded.org_id as string | undefined
      }
    }
  } catch (error) {
    // Ignore errors for optional auth
    console.log('Optional auth failed:', error)
  }
}

// Type augmentation for Fastify
declare module 'fastify' {
  interface FastifyRequest {
    user?: {
      id: string
      email: string
      orgId?: string
    }
  }
}
