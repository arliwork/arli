import { prisma } from '.'

async function main() {
  console.log('🌱 Seeding database...')

  // Создаем демо пользователя
  const user = await prisma.user.upsert({
    where: { email: 'demo@arli.ai' },
    update: {},
    create: {
      email: 'demo@arli.ai',
      name: 'Demo User',
    },
  })

  // Создаем демо компанию
  const company = await prisma.company.upsert({
    where: { slug: 'demo-agency' },
    update: {},
    create: {
      name: 'Demo Content Agency',
      slug: 'demo-agency',
      description: 'AI-powered content marketing agency',
      template: 'CONTENT_AGENCY',
      niche: 'fitness',
      credits: 10000,
      status: 'ACTIVE',
      ownerId: user.id,
    },
  })

  // Создаем агентов
  const agents = await Promise.all([
    prisma.agent.upsert({
      where: { id: 'ceo-agent' },
      update: {},
      create: {
        id: 'ceo-agent',
        name: 'CEO Agent',
        role: 'CEO',
        description: 'Strategic planning and oversight',
        adapter: 'CLAUDE',
        config: { model: 'claude-3-opus' },
        companyId: company.id,
      },
    }),
    prisma.agent.upsert({
      where: { id: 'content-agent' },
      update: {},
      create: {
        id: 'content-agent',
        name: 'Content Creator',
        role: 'SPECIALIST',
        description: 'Creates viral content for TikTok',
        adapter: 'CLAUDE',
        config: { model: 'claude-3-sonnet' },
        companyId: company.id,
      },
    }),
    prisma.agent.upsert({
      where: { id: 'scheduler-agent' },
      update: {},
      create: {
        id: 'scheduler-agent',
        name: 'Post Scheduler',
        role: 'WORKER',
        description: 'Schedules and publishes content',
        adapter: 'HTTP',
        config: { endpoints: ['postiz.io'] },
        companyId: company.id,
      },
    }),
  ])

  // Создаем sample skills
  const skills = await Promise.all([
    prisma.skill.upsert({
      where: { name: 'TikTok Trend Hunter' },
      update: {},
      create: {
        name: 'TikTok Trend Hunter',
        description: 'Finds trending sounds and hashtags',
        category: 'CONTENT',
        price: 500,
        authorId: 'system',
        authorName: 'ARLI Team',
        content: '# TikTok Trend Hunter\n\nFind viral trends...',
      },
    }),
    prisma.skill.upsert({
      where: { name: 'UGC Script Writer' },
      update: {},
      create: {
        name: 'UGC Script Writer',
        description: 'Writes scripts for user-generated content',
        category: 'MARKETING',
        price: 1000,
        authorId: 'system',
        authorName: 'ARLI Team',
        content: '# UGC Script Writer\n\nCreate engaging scripts...',
      },
    }),
  ])

  // Создаем sample ticket
  await prisma.ticket.upsert({
    where: { id: 'sample-ticket' },
    update: {},
    create: {
      id: 'sample-ticket',
      title: 'Find trending fitness hashtags',
      description: 'Research top 10 trending hashtags for fitness niche',
      status: 'PENDING',
      priority: 'HIGH',
      goal: 'Increase reach by 50%',
      companyId: company.id,
      assignedToId: agents[1].id, // Content Creator
    },
  })

  console.log('✅ Seed completed:')
  console.log(`  - User: ${user.email}`)
  console.log(`  - Company: ${company.name}`)
  console.log(`  - Agents: ${agents.length}`)
  console.log(`  - Skills: ${skills.length}`)
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })