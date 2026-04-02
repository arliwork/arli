import OpenAI from 'openai'

// OpenRouter client (supports multiple AI providers)
const openrouter = new OpenAI({
  baseURL: 'https://openrouter.ai/api/v1',
  apiKey: process.env.OPENROUTER_API_KEY || '',
  defaultHeaders: {
    'HTTP-Referer': process.env.APP_URL || 'http://localhost:3100',
    'X-Title': 'ARLI Platform'
  }
})

// Agent role system prompts
const ROLE_PROMPTS: Record<string, string> = {
  CEO: `You are the CEO of an autonomous AI company. Your responsibilities:
- Set strategic direction and vision
- Make high-level decisions about resource allocation
- Define company goals and KPIs
- Review performance and adjust strategy
- Communicate with stakeholders

Respond concisely with actionable decisions.`,

  CFO: `You are the CFO of an autonomous AI company. Your responsibilities:
- Manage financial planning and budgeting
- Track revenue, costs, and profitability
- Optimize pricing strategies
- Financial forecasting and reporting
- Ensure fiscal sustainability

Respond with financial analysis and recommendations.`,

  CMO: `You are the CMO of an autonomous AI company. Your responsibilities:
- Develop marketing strategies
- Manage brand positioning
- Optimize customer acquisition
- Analyze market trends
- Coordinate promotional campaigns

Respond with marketing insights and campaign ideas.`,

  CTO: `You are the CTO of an autonomous AI company. Your responsibilities:
- Oversee technical architecture
- Make technology stack decisions
- Ensure system reliability and scalability
- Evaluate new technologies
- Manage technical debt

Respond with technical recommendations and architecture decisions.`,

  'Content Writer': `You are a Content Writer AI agent. Your responsibilities:
- Create engaging written content
- Optimize for SEO
- Maintain brand voice consistency
- Research topics thoroughly
- Meet content deadlines

Respond with well-structured, original content.`,

  'Sales Agent': `You are a Sales Agent AI. Your responsibilities:
- Identify and qualify leads
- Craft persuasive outreach messages
- Handle objections
- Close deals
- Build customer relationships

Respond with sales scripts and strategies.`,

  'Support Agent': `You are a Customer Support Agent AI. Your responsibilities:
- Respond to customer inquiries
- Troubleshoot issues
- Provide helpful solutions
- Escalate complex problems
- Maintain customer satisfaction

Respond professionally and empathetically.`,

  Developer: `You are a Software Developer AI agent. Your responsibilities:
- Write clean, efficient code
- Debug and fix issues
- Review code quality
- Implement features
- Maintain documentation

Respond with code snippets and technical solutions.`,

  Analyst: `You are a Data Analyst AI agent. Your responsibilities:
- Analyze business data
- Create reports and visualizations
- Identify trends and insights
- Make data-driven recommendations
- Track key metrics

Respond with data insights and actionable recommendations.`,

  Operator: `You are a Business Operations AI agent. Your responsibilities:
- Execute day-to-day tasks
- Coordinate between teams
- Manage workflows
- Ensure process compliance
- Optimize operational efficiency

Respond with operational plans and task executions.`
}

// Task type prompts
const TASK_PROMPTS: Record<string, string> = {
  'create-content': 'Create the following content with professional quality:',
  'analyze-data': 'Analyze the following data and provide insights:',
  'write-code': 'Write code for the following requirement:',
  'research': 'Research the following topic and summarize findings:',
  'draft-email': 'Draft a professional email for the following:',
  'strategy': 'Develop a strategic plan for:',
  'review': 'Review the following and provide feedback:',
  'decision': 'Make a decision about the following with reasoning:',
  'optimize': 'Optimize the following for better performance:',
  'plan': 'Create a detailed plan for:'
}

export interface AIResponse {
  content: string
  model: string
  usage: {
    promptTokens: number
    completionTokens: number
    totalTokens: number
  }
  cost: number // Estimated cost in credits
}

export interface AgentTask {
  id: string
  type: string
  title: string
  description: string
  context?: Record<string, any>
}

/**
 * AI Service for executing agent tasks
 */
export class AIService {
  /**
   * Execute a task using the appropriate AI model
   */
  async executeTask(
    agentRole: string,
    task: AgentTask,
    model: string = 'anthropic/claude-3.5-sonnet'
  ): Promise<AIResponse> {
    const startTime = Date.now()
    
    // Build the system prompt
    const systemPrompt = this.buildSystemPrompt(agentRole, task.type)
    
    // Build the user prompt
    const userPrompt = this.buildUserPrompt(task)
    
    try {
      // Call OpenRouter (supports multiple providers)
      const response = await openrouter.chat.completions.create({
        model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        temperature: 0.7,
        max_tokens: 4000,
      })

      const content = response.choices[0]?.message?.content || ''
      const usage = response.usage

      // Calculate credit cost (approximate)
      // 1 credit = $0.001 = 1000 tokens on average
      const creditCost = this.calculateCreditCost(usage, model)

      console.log(`✅ Task ${task.id} completed in ${Date.now() - startTime}ms`)
      console.log(`   Model: ${model}, Cost: ${creditCost} credits`)

      return {
        content,
        model: response.model,
        usage: {
          promptTokens: usage?.prompt_tokens || 0,
          completionTokens: usage?.completion_tokens || 0,
          totalTokens: usage?.total_tokens || 0
        },
        cost: creditCost
      }
    } catch (error) {
      console.error('AI execution error:', error)
      throw new Error(`Failed to execute task: ${error.message}`)
    }
  }

  /**
   * Execute task with code generation capabilities
   */
  async executeCodeTask(
    task: AgentTask,
    language: string = 'typescript'
  ): Promise<AIResponse> {
    const systemPrompt = `You are an expert ${language} developer. 
Write clean, well-documented, production-ready code.
Include error handling and follow best practices.
Respond with code only (in markdown code blocks) and brief explanation.`

    const userPrompt = `Task: ${task.title}
Description: ${task.description}
${task.context ? `Context: ${JSON.stringify(task.context, null, 2)}` : ''}

Please write ${language} code to accomplish this task.`

    const response = await openrouter.chat.completions.create({
      model: 'anthropic/claude-3.5-sonnet',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.3,
      max_tokens: 4000,
    })

    const content = response.choices[0]?.message?.content || ''
    const usage = response.usage

    return {
      content,
      model: response.model,
      usage: {
        promptTokens: usage?.prompt_tokens || 0,
        completionTokens: usage?.completion_tokens || 0,
        totalTokens: usage?.total_tokens || 0
      },
      cost: this.calculateCreditCost(usage, 'anthropic/claude-3.5-sonnet')
    }
  }

  /**
   * Quick completion for simple queries
   */
  async quickCompletion(
    prompt: string,
    model: string = 'openai/gpt-4o-mini'
  ): Promise<string> {
    const response = await openrouter.chat.completions.create({
      model,
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.5,
      max_tokens: 1000,
    })

    return response.choices[0]?.message?.content || ''
  }

  /**
   * Generate task suggestions for an agent
   */
  async generateTaskSuggestions(
    agentRole: string,
    companyContext: Record<string, any>
  ): Promise<string[]> {
    const prompt = `Given this company context:
${JSON.stringify(companyContext, null, 2)}

Generate 5 specific tasks for a ${agentRole} agent that would add value.
Respond with just a JSON array of task titles.`

    const response = await openrouter.chat.completions.create({
      model: 'openai/gpt-4o-mini',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.8,
      max_tokens: 500,
    })

    try {
      const content = response.choices[0]?.message?.content || '[]'
      return JSON.parse(content.replace(/```json\n?|\n?```/g, ''))
    } catch {
      return [
        'Review current performance metrics',
        'Identify optimization opportunities',
        'Draft strategic recommendations',
        'Analyze market trends',
        'Prepare status report'
      ]
    }
  }

  /**
   * Build system prompt based on agent role and task type
   */
  private buildSystemPrompt(agentRole: string, taskType: string): string {
    const rolePrompt = ROLE_PROMPTS[agentRole] || ROLE_PROMPTS['Operator']
    const taskPrompt = TASK_PROMPTS[taskType] || 'Complete the following task:'
    
    return `${rolePrompt}

Task Type: ${taskType}
${taskPrompt}

Respond concisely and professionally. Focus on actionable output.`
  }

  /**
   * Build user prompt from task
   */
  private buildUserPrompt(task: AgentTask): string {
    let prompt = `Title: ${task.title}
Description: ${task.description}`

    if (task.context && Object.keys(task.context).length > 0) {
      prompt += `\n\nAdditional Context:\n${JSON.stringify(task.context, null, 2)}`
    }

    return prompt
  }

  /**
   * Calculate credit cost based on token usage and model
   */
  private calculateCreditCost(
    usage: any,
    model: string
  ): number {
    const tokens = usage?.total_tokens || 0
    
    // Model pricing multipliers (relative to base)
    const pricing: Record<string, number> = {
      'anthropic/claude-3-opus': 3.0,
      'anthropic/claude-3.5-sonnet': 1.5,
      'anthropic/claude-3-haiku': 0.5,
      'openai/gpt-4o': 2.5,
      'openai/gpt-4o-mini': 0.3,
      'google/gemini-pro': 0.8,
      'meta-llama/llama-3-70b': 0.6,
    }

    const multiplier = pricing[model] || 1.0
    
    // Base: 1000 tokens = 1 credit
    return Math.ceil((tokens / 1000) * multiplier)
  }
}

// Export singleton
export const aiService = new AIService()
