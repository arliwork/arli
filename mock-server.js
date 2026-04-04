// Mock API Server for ARLI Demo
const http = require('http');
const url = require('url');

const PORT = 3100;

// Mock data
const companies = [
  {
    id: '1',
    name: 'My Marketing Agency',
    template: 'agency-scalr',
    status: 'ACTIVE',
    description: 'Full-service marketing agency with AI automation',
    config: {
      channels: ['google', 'meta', 'linkedin'],
      budget_minimum: 3000
    },
    createdAt: new Date().toISOString(),
    agents: [
      {
        id: 'agent-1',
        name: 'Campaign Architect Agent',
        role: 'media_planner',
        status: 'ACTIVE',
        description: 'Generates media plans based on goals and budget',
        skills: ['media_planning', 'budget_allocation', 'channel_mix_optimization'],
        lastRun: new Date().toISOString(),
        tasksCompleted: 156
      },
      {
        id: 'agent-2',
        name: 'Creative Testing Agent',
        role: 'creative_strategist',
        status: 'ACTIVE',
        description: 'A/B test concepts without design teams',
        skills: ['creative_generation', 'a_b_testing', 'performance_prediction'],
        lastRun: new Date().toISOString(),
        tasksCompleted: 89
      },
      {
        id: 'agent-3',
        name: 'Performance Reporter Agent',
        role: 'analytics_specialist',
        status: 'ACTIVE',
        description: 'Automated dashboards and anomaly detection',
        skills: ['dashboard_automation', 'anomaly_detection', 'insight_generation'],
        lastRun: new Date().toISOString(),
        tasksCompleted: 432
      },
      {
        id: 'agent-4',
        name: 'Client Communication Agent',
        role: 'account_manager',
        status: 'ACTIVE',
        description: 'Proactive updates and client Q&A',
        skills: ['client_communication', 'update_automation', 'satisfaction_monitoring'],
        lastRun: new Date().toISOString(),
        tasksCompleted: 267
      },
      {
        id: 'agent-5',
        name: 'Opportunity Spotter Agent',
        role: 'business_development',
        status: 'ACTIVE',
        description: 'Finds upsell gaps and expansion opportunities',
        skills: ['account_analysis', 'upsell_detection', 'proposal_generation'],
        lastRun: new Date().toISOString(),
        tasksCompleted: 45
      }
    ]
  }
];

const templates = [
  {
    id: 'agency-scalr',
    name: 'Agency Scalr',
    description: 'Marketing Agency Automation',
    icon: '📈',
    category: 'marketing',
    agentCount: 5,
    metrics: {
      accountsPerManager: '3x',
      retentionImprovement: '+17%',
      upsellIncrease: '+30%'
    }
  },
  {
    id: 'commerce-intel',
    name: 'Commerce Intel',
    description: 'E-commerce Intelligence Platform',
    icon: '🛒',
    category: 'retail',
    agentCount: 5,
    metrics: {
      marginImprovement: '+5-15%',
      stockoutReduction: '-30%',
      roasImprovement: '+25%'
    }
  },
  {
    id: 'saas-growth-lab',
    name: 'SaaS Growth Lab',
    description: 'Subscription Business Intelligence',
    icon: '🚀',
    category: 'saas',
    agentCount: 5,
    metrics: {
      nrrTarget: '>120%',
      churnReduction: '-30%',
      expansionGrowth: '+20%'
    }
  },
  {
    id: 'clinic-flow',
    name: 'Clinic Flow',
    description: 'Healthcare Operations Automation',
    icon: '🏥',
    category: 'healthcare',
    agentCount: 5,
    metrics: {
      throughputIncrease: '+25%',
      noShowReduction: '-40%',
      claimApproval: '+20%'
    }
  },
  {
    id: 'property-pulse',
    name: 'Property Pulse',
    description: 'Real Estate Automation Platform',
    icon: '🏠',
    category: 'real_estate',
    agentCount: 5,
    metrics: {
      leadsPerAgent: '3x',
      daysOnMarket: '-20%',
      conversionRate: '+150%'
    }
  },
  {
    id: 'legal-synth',
    name: 'Legal Synth',
    description: 'Law Firm Automation',
    icon: '⚖️',
    category: 'legal',
    agentCount: 5,
    metrics: {
      reviewSpeedup: '+400%',
      researchReduction: '-70%',
      timeCapture: '+15%'
    }
  },
  {
    id: 'ledger-minds',
    name: 'Ledger Minds',
    description: 'Accounting & Advisory Automation',
    icon: '📊',
    category: 'accounting',
    agentCount: 5,
    metrics: {
      closeSpeedup: '-60%',
      categorizationAccuracy: '85%+',
      taxSavings: '+20%'
    }
  },
  {
    id: 'learning-foundry',
    name: 'Learning Foundry',
    description: 'EdTech Content Automation',
    icon: '🎓',
    category: 'education',
    agentCount: 5,
    metrics: {
      contentSpeed: '10x',
      completionRate: '+30%',
      retentionRate: '+40%'
    }
  },
  {
    id: 'hospitality-hive',
    name: 'Hospitality Hive',
    description: 'Restaurant & Hotel Operations',
    icon: '🏨',
    category: 'hospitality',
    agentCount: 5,
    metrics: {
      laborCost: '-15%',
      occupancyRate: '+10%',
      spoilage: '-20%'
    }
  },
  {
    id: 'manufacturing-mind',
    name: 'Manufacturing Mind',
    description: 'Production Intelligence',
    icon: '🏭',
    category: 'manufacturing',
    agentCount: 5,
    metrics: {
      oeeImprovement: '+20%',
      downtimeReduction: '-70%',
      defectRate: '-80%'
    }
  }
];

const tasks = [
  {
    id: 'task-1',
    agentId: 'agent-1',
    type: 'media_plan_generation',
    status: 'COMPLETED',
    input: { client: 'TechCorp', budget: 10000, goal: 'lead_generation' },
    output: { channels: { google: 4000, meta: 3500, linkedin: 2500 }, expectedCpl: 45 },
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    completedAt: new Date().toISOString()
  },
  {
    id: 'task-2',
    agentId: 'agent-3',
    type: 'anomaly_detection',
    status: 'COMPLETED',
    input: { metric: 'cpa', campaign: 'Q2_Lead_Gen' },
    output: { anomaly: true, change: '+45%', recommendation: 'Switch to long-tail keywords' },
    createdAt: new Date(Date.now() - 7200000).toISOString(),
    completedAt: new Date(Date.now() - 7000000).toISOString()
  },
  {
    id: 'task-3',
    agentId: 'agent-5',
    type: 'opportunity_detection',
    status: 'RUNNING',
    input: { clientId: 'ecommerce-store' },
    createdAt: new Date(Date.now() - 1800000).toISOString()
  }
];

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization'
};

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  const method = req.method;

  // Set CORS headers
  Object.entries(corsHeaders).forEach(([key, value]) => {
    res.setHeader(key, value);
  });

  // Handle preflight
  if (method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Set content type
  res.setHeader('Content-Type', 'application/json');

  console.log(`${method} ${path}`);

  // Health check
  if (path === '/health' && method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }));
    return;
  }

  // Get all companies
  if (path === '/api/companies' && method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({ companies }));
    return;
  }

  // Get company by ID
  if (path.match(/\/api\/companies\/[^/]+$/) && method === 'GET') {
    const id = path.split('/').pop();
    const company = companies.find(c => c.id === id);
    if (company) {
      res.writeHead(200);
      res.end(JSON.stringify({ company }));
    } else {
      res.writeHead(404);
      res.end(JSON.stringify({ error: 'Company not found' }));
    }
    return;
  }

  // Get templates
  if (path === '/api/templates' && method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({ templates }));
    return;
  }

  // Get template by ID
  if (path.match(/\/api\/templates\/[^/]+$/) && method === 'GET') {
    const id = path.split('/').pop();
    const template = templates.find(t => t.id === id);
    if (template) {
      res.writeHead(200);
      res.end(JSON.stringify({ template }));
    } else {
      res.writeHead(404);
      res.end(JSON.stringify({ error: 'Template not found' }));
    }
    return;
  }

  // Get agents for company
  if (path.match(/\/api\/companies\/[^/]+\/agents$/) && method === 'GET') {
    const companyId = path.split('/')[3];
    const company = companies.find(c => c.id === companyId);
    if (company) {
      res.writeHead(200);
      res.end(JSON.stringify({ agents: company.agents }));
    } else {
      res.writeHead(404);
      res.end(JSON.stringify({ error: 'Company not found' }));
    }
    return;
  }

  // Get tasks
  if (path === '/api/tasks' && method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({ tasks }));
    return;
  }

  // Create company from template
  if (path === '/api/companies' && method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      const data = JSON.parse(body);
      const newCompany = {
        id: String(companies.length + 1),
        name: data.name,
        template: data.templateId,
        status: 'ACTIVE',
        description: data.description || '',
        config: data.config || {},
        createdAt: new Date().toISOString(),
        agents: [] // Would be populated from template
      };
      companies.push(newCompany);
      res.writeHead(201);
      res.end(JSON.stringify({ company: newCompany }));
    });
    return;
  }

  // 404 for unknown routes
  res.writeHead(404);
  res.end(JSON.stringify({ error: 'Not found', path, method }));
});

server.listen(PORT, () => {
  console.log('✅ ARLI Mock API Server running');
  console.log(`   URL: http://localhost:${PORT}`);
  console.log('');
  console.log('Available endpoints:');
  console.log('  GET  /health              - Health check');
  console.log('  GET  /api/companies       - List companies');
  console.log('  GET  /api/companies/:id   - Get company');
  console.log('  POST /api/companies       - Create company');
  console.log('  GET  /api/templates       - List templates');
  console.log('  GET  /api/templates/:id   - Get template');
  console.log('  GET  /api/tasks           - List tasks');
  console.log('');
  console.log('Press Ctrl+C to stop');
});
