

/**
 * Process notification jobs
 */
notificationQueue.process('budget-alert', async (job) => {
  const { companyId, agentId, message } = job.data
  const company = await prisma.company.findUnique({
    where: { id: companyId },
    include: { owner: true }
  })
  
  if (company) {
    await notificationService.notifyUser(company.ownerId, {
      title: '💸 Budget Alert',
      message,
      type: 'warning'
    })
  }
})

notificationQueue.process('ceo-report', async (job) => {
  const { companyId, report } = job.data
  const company = await prisma.company.findUnique({
    where: { id: companyId },
    include: { owner: true }
  })
  
  if (company) {
    await notificationService.notifyUser(company.ownerId, {
      title: `📊 Daily Report: ${company.name}`,
      message: report,
      type: 'info'
    })
  }
})

notificationQueue.process('task-completed', async (job) => {
  const { companyId, taskTitle, result } = job.data
  await notificationService.sendTaskCompleted(companyId, taskTitle, result)
})

notificationQueue.process('revenue', async (job) => {
  const { companyId, amount } = job.data
  await notificationService.sendRevenueNotification(companyId, amount)
})

notificationQueue.process('agent-error', async (job) => {
  const { companyId, agentName, error } = job.data
  await notificationService.sendAgentError(companyId, agentName, error)
})

notificationQueue.process('weekly-summary', async (job) => {
  const { userId } = job.data
  await notificationService.sendWeeklySummary(userId)
})

console.log('📬 Notification Queue initialized')
