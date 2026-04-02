import { prisma } from '@arli/database'

/**
 * Notification Service
 * Handles Telegram and Email alerts
 */
export class NotificationService {
  private telegramBotToken: string
  private resendApiKey: string
  private fromEmail: string

  constructor() {
    this.telegramBotToken = process.env.TELEGRAM_BOT_TOKEN || ''
    this.resendApiKey = process.env.RESEND_API_KEY || ''
    this.fromEmail = process.env.FROM_EMAIL || 'notifications@arli.ai'
  }

  /**
   * Send notification to user via all configured channels
   */
  async notifyUser(
    userId: string,
    options: {
      title: string
      message: string
      type: 'info' | 'success' | 'warning' | 'error'
      data?: Record<string, any>
    }
  ) {
    const user = await prisma.user.findUnique({
      where: { id: userId }
    })

    if (!user) {
      console.error(`User ${userId} not found`)
      return
    }

    // Save notification to database
    await prisma.notification.create({
      data: {
        userId,
        title: options.title,
        message: options.message,
        type: options.type,
        data: options.data || {},
        read: false
      }
    })

    // Send via Telegram if configured
    if (user.telegramChatId) {
      await this.sendTelegram(user.telegramChatId, options)
    }

    // Send via Email if configured
    if (user.email) {
      await this.sendEmail(user.email, options)
    }
  }

  /**
   * Send Telegram notification
   */
  async sendTelegram(
    chatId: string,
    options: {
      title: string
      message: string
      type: 'info' | 'success' | 'warning' | 'error'
    }
  ) {
    if (!this.telegramBotToken) {
      console.log('Telegram bot token not configured')
      return
    }

    const emoji = {
      info: 'ℹ️',
      success: '✅',
      warning: '⚠️',
      error: '❌'
    }[options.type]

    const text = `${emoji} <b>${options.title}</b>\n\n${options.message}`

    try {
      const response = await fetch(
        `https://api.telegram.org/bot${this.telegramBotToken}/sendMessage`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            chat_id: chatId,
            text,
            parse_mode: 'HTML'
          })
        }
      )

      if (!response.ok) {
        throw new Error(`Telegram API error: ${response.status}`)
      }

      console.log(`📨 Telegram notification sent to ${chatId}`)
    } catch (error) {
      console.error('Failed to send Telegram notification:', error)
    }
  }

  /**
   * Send Email notification via Resend
   */
  async sendEmail(
    to: string,
    options: {
      title: string
      message: string
      type: 'info' | 'success' | 'warning' | 'error'
    }
  ) {
    if (!this.resendApiKey) {
      console.log('Resend API key not configured')
      return
    }

    const colors = {
      info: '#3b82f6',
      success: '#22c55e',
      warning: '#f59e0b',
      error: '#ef4444'
    }[options.type]

    const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${options.title}</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f3f4f6;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background: #f3f4f6; padding: 40px 20px;">
    <tr>
      <td align="center">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
          <tr>
            <td style="background: ${colors}; padding: 30px; text-align: center;">
              <h1 style="color: white; margin: 0; font-size: 24px; font-weight: 600;">ARLI</h1>
            </td>
          </tr>
          <tr>
            <td style="padding: 40px 30px;">
              <h2 style="color: #111827; margin: 0 0 20px 0; font-size: 20px; font-weight: 600;">${options.title}</h2>
              <p style="color: #4b5563; margin: 0; font-size: 16px; line-height: 1.6;">${options.message.replace(/\n/g, '<br>')}</p>
            </td>
          </tr>
          <tr>
            <td style="padding: 20px 30px; background: #f9fafb; border-top: 1px solid #e5e7eb;">
              <p style="color: #6b7280; margin: 0; font-size: 14px;">
                You're receiving this because you have an ARLI account.<br>
                <a href="https://arli.ai/dashboard" style="color: ${colors}; text-decoration: none;">View Dashboard</a>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`

    try {
      const response = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.resendApiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          from: `ARLI <${this.fromEmail}>`,
          to,
          subject: options.title,
          html
        })
      })

      if (!response.ok) {
        throw new Error(`Resend API error: ${response.status}`)
      }

      console.log(`📧 Email sent to ${to}`)
    } catch (error) {
      console.error('Failed to send email:', error)
    }
  }

  /**
   * Send low credits alert
   */
  async sendLowCreditsAlert(companyId: string, creditsRemaining: number) {
    const company = await prisma.company.findUnique({
      where: { id: companyId },
      include: { owner: true }
    })

    if (!company) return

    await this.notifyUser(company.ownerId, {
      title: '⚠️ Low Credits Alert',
      message: `Your company "${company.name}" is running low on credits.\n\nRemaining: ${creditsRemaining} credits\n\nPurchase more credits to keep your agents running smoothly.`,
      type: 'warning',
      data: { companyId, credits: creditsRemaining }
    })
  }

  /**
   * Send task completed notification
   */
  async sendTaskCompleted(companyId: string, taskTitle: string, result: string) {
    const company = await prisma.company.findUnique({
      where: { id: companyId },
      include: { owner: true }
    })

    if (!company) return

    const truncatedResult = result.length > 200 
      ? result.substring(0, 200) + '...' 
      : result

    await this.notifyUser(company.ownerId, {
      title: '✅ Task Completed',
      message: `Agent completed task: "${taskTitle}"\n\nResult:\n${truncatedResult}`,
      type: 'success',
      data: { companyId, taskTitle }
    })
  }

  /**
   * Send revenue notification
   */
  async sendRevenueNotification(companyId: string, amount: number) {
    const company = await prisma.company.findUnique({
      where: { id: companyId },
      include: { owner: true }
    })

    if (!company) return

    await this.notifyUser(company.ownerId, {
      title: '💰 Revenue Generated',
      message: `Your company "${company.name}" just generated $${amount.toFixed(2)} in revenue!\n\nTotal Revenue: $${company.totalRevenue.toFixed(2)}`,
      type: 'success',
      data: { companyId, amount }
    })
  }

  /**
   * Send agent error notification
   */
  async sendAgentError(companyId: string, agentName: string, error: string) {
    const company = await prisma.company.findUnique({
      where: { id: companyId },
      include: { owner: true }
    })

    if (!company) return

    await this.notifyUser(company.ownerId, {
      title: '❌ Agent Error',
      message: `Agent "${agentName}" in "${company.name}" encountered an error:\n\n${error}`,
      type: 'error',
      data: { companyId, agentName, error }
    })
  }

  /**
   * Send weekly summary
   */
  async sendWeeklySummary(userId: string) {
    const companies = await prisma.company.findMany({
      where: { ownerId: userId },
      include: {
        _count: {
          select: { tickets: true, agents: true }
        }
      }
    })

    if (companies.length === 0) return

    let summary = '📊 Weekly Summary\n\n'
    
    for (const company of companies) {
      const completedTasks = await prisma.ticket.count({
        where: {
          companyId: company.id,
          status: 'COMPLETED',
          completedAt: {
            gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
          }
        }
      })

      summary += `🏢 ${company.name}\n`
      summary += `   Revenue: $${company.totalRevenue.toFixed(2)}\n`
      summary += `   Completed Tasks: ${completedTasks}\n`
      summary += `   Active Agents: ${company._count.agents}\n`
      summary += `   Credits: ${company.credits}\n\n`
    }

    await this.notifyUser(userId, {
      title: '📊 Weekly Summary',
      message: summary,
      type: 'info'
    })
  }
}

// Export singleton
export const notificationService = new NotificationService()
