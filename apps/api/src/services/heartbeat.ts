import { prisma } from '@arli/database'
import { taskQueue } from './queue'

/**
 * Heartbeat Service
 * Manages agent wake-up schedules and task distribution
 */
export class HeartbeatService {
  private static instance: HeartbeatService
  private isRunning: boolean = false
  private intervals: Map<string, NodeJS.Timeout> = new Map()

  static getInstance(): HeartbeatService {
    if (!HeartbeatService.instance) {
      HeartbeatService.instance = new HeartbeatService()
    }
    return HeartbeatService.instance
  }

  /**
   * Start the global heartbeat scheduler
   */
  async start() {
    if (this.isRunning) return
    
    console.log('🫀 Starting Heartbeat Service...')
    this.isRunning = true
    
    // Schedule heartbeats for all active companies
    await this.scheduleAllCompanies()
    
    // Refresh schedules every 5 minutes
    setInterval(() => {
      this.scheduleAllCompanies()
    }, 5 * 60 * 1000)
  }

  /**
   * Schedule heartbeats for all active companies
   */
  private async scheduleAllCompanies() {
    const companies = await prisma.company.findMany({
      where: { 
        status: 'ACTIVE',
        credits: { gt: 0 }  // Only companies with credits
      },
      include: {
        agents: {
          where: { isActive: true }
        }
      }
    })

    for (const company of companies) {
      this.scheduleCompanyHeartbeat(company.id, company.heartbeatInterval)
    }
  }

  /**
   * Schedule heartbeat for a specific company
   */
  private scheduleCompanyHeartbeat(companyId: string, intervalMinutes: number) {
    // Clear existing interval if any
    if (this.intervals.has(companyId)) {
      clearInterval(this.intervals.get(companyId)!)
    }

    // Schedule new heartbeat
    const intervalMs = intervalMinutes * 60 * 1000
    const interval = setInterval(async () => {
      await this.executeCompanyHeartbeat(companyId)
    }, intervalMs)

    this.intervals.set(companyId, interval)
    console.log(`📅 Scheduled heartbeat for company ${companyId} every ${intervalMinutes}min`)
  }

  /**
   * Execute heartbeat for a company
   */
  private async executeCompanyHeartbeat(companyId: string) {
    try {
      console.log(`🫀 Executing heartbeat for company ${companyId}`)

      // Update last heartbeat
      await prisma.company.update({
        where: { id: companyId },
        data: { lastHeartbeat: new Date() }
      })

      // Get all active agents for this company
      const agents = await prisma.agent.findMany({
        where: {
          companyId,
          isActive: true,
          // Check if agent has budget left
          spentThisMonth: { lt: prisma.agent.fields.monthlyBudget }
        }
      })

      // Queue heartbeat tasks for each agent
      for (const agent of agents) {
        await taskQueue.add('agent-heartbeat', {
          agentId: agent.id,
          companyId,
          timestamp: new Date().toISOString()
        }, {
          priority: agent.role === 'CEO' ? 1 : 2,
          attempts: 3,
          backoff: { type: 'exponential', delay: 5000 }
        })
      }

      // Queue CEO strategy review (once per day)
      const ceoAgent = agents.find(a => a.role === 'CEO')
      if (ceoAgent && new Date().getHours() === 9) {
        await taskQueue.add('ceo-strategy-review', {
          agentId: ceoAgent.id,
          companyId
        }, {
          priority: 0,
          delay: 1000
        })
      }

    } catch (error) {
      console.error(`❌ Heartbeat failed for company ${companyId}:`, error)
    }
  }

  /**
   * Manually trigger a heartbeat for a company
   */
  async triggerManualHeartbeat(companyId: string) {
    console.log(`👆 Manual heartbeat triggered for ${companyId}`)
    await this.executeCompanyHeartbeat(companyId)
  }

  /**
   * Stop heartbeat for a company
   */
  stopCompanyHeartbeat(companyId: string) {
    if (this.intervals.has(companyId)) {
      clearInterval(this.intervals.get(companyId)!)
      this.intervals.delete(companyId)
      console.log(`🛑 Stopped heartbeat for company ${companyId}`)
    }
  }

  /**
   * Update heartbeat interval for a company
   */
  async updateHeartbeatInterval(companyId: string, intervalMinutes: number) {
    this.stopCompanyHeartbeat(companyId)
    this.scheduleCompanyHeartbeat(companyId, intervalMinutes)
    
    await prisma.company.update({
      where: { id: companyId },
      data: { heartbeatInterval: intervalMinutes }
    })
  }
}

// Export singleton instance
export const heartbeatService = HeartbeatService.getInstance()