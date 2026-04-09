# 🤝 ARLI Multi-Agent Collaboration

Agent-to-agent task delegation and communication system.

## Overview

ARLI agents can now collaborate by:
- **Delegating tasks** to other agents based on capabilities
- **Handing off context** between agents
- **Working in parallel** on different parts of a project
- **Aggregating results** from multiple agents

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 COLLABORATION ORCHESTRATOR                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📋 AGENT REGISTRY           📋 TASK BOARD                 │
│  ├── Agent profiles          ├── Pending tasks             │
│  ├── Capabilities            ├── Assigned tasks            │
│  ├── Status tracking         ├── Subtasks                  │
│  └── Match scoring           └── Results                   │
│                                                             │
│  🔄 COLLABORATION PATTERNS                                  │
│  ├── Sequential: A → B → C                                  │
│  ├── Parallel: A → [B, C] → D                               │
│  └── Hierarchical: Manager → Workers                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Components

### AgentRegistry

Central registry of all agents and their capabilities.

```python
from collaboration import AgentRegistry

registry = AgentRegistry()

# Find agents by capability
db_agents = registry.find_agents_by_capability("database")

# Find best agent for task
best = registry.find_best_agent(task)

# Update agent status
registry.update_agent_status("backend-dev", "busy", task_id="abc123")
```

### TaskBoard

Central task management system.

```python
from collaboration import TaskBoard, DelegatedTask

board = TaskBoard()

# Create task
task = board.create_task(
    title="Build API",
    description="Create REST endpoints",
    task_type="coding",
    required_capabilities=["api-development"],
    creator="architect"
)

# Assign task
board.assign_task(task.task_id, "backend-dev")

# Update status
board.update_task_status(task.task_id, TaskStatus.COMPLETED, result={"url": "/api"})
```

### CollaborationOrchestrator

Main orchestrator that ties everything together.

```python
from collaboration import CollaborationOrchestrator, CollaborationPattern

orchestrator = CollaborationOrchestrator()

# Simple delegation
task = orchestrator.create_and_delegate(
    title="Build auth",
    description="Implement JWT auth",
    task_type="coding",
    required_capabilities=["api-development"],
    from_agent="architect",
    to_agent="backend-dev"
)

# Execute collaboration pattern
tasks = orchestrator.execute_collaboration_pattern(
    pattern=CollaborationPattern.SEQUENTIAL,
    initial_task=feature_task,
    agent_sequence=["architect", "backend-dev", "devops"]
)
```

## Usage

### Basic Task Delegation

```python
from runtime import AgentRuntime

# Create CEO agent
ceo = AgentRuntime("ceo", workspace=".", enable_memory=True)

# Delegate to architect automatically (finds best match)
result = ceo.delegate_task(
    title="Design payment system",
    description="Create architecture for Stripe integration",
    task_type="design",
    required_capabilities=["system-design"],
    priority=5
)

print(f"Task delegated to: {result['assignee']}")
```

### Sequential Workflow

```python
# CEO delegates to Architect
arch_task = ceo.delegate_task(
    title="Design API",
    description="Create API specification",
    task_type="design",
    required_capabilities=["system-design"],
    to_agent="architect"
)

# Architect delegates to Backend
backend_task = architect.delegate_task(
    title="Implement API",
    description="Build endpoints based on design",
    task_type="coding",
    required_capabilities=["api-development"],
    to_agent="backend-dev"
)

# Backend delegates to DevOps
deploy_task = backend.delegate_task(
    title="Deploy API",
    description="Deploy to production",
    task_type="deployment",
    required_capabilities=["deployment"],
    to_agent="devops"
)
```

### Parallel Workflow

```python
# Architect creates parallel tasks
backend_task = architect.delegate_task(
    title="Build API",
    description="Create REST endpoints",
    task_type="coding",
    required_capabilities=["api-development"],
    to_agent="backend-dev"
)

frontend_task = architect.delegate_task(
    title="Build UI",
    description="Create React components",
    task_type="coding",
    required_capabilities=["ui-development"],
    to_agent="frontend-dev"
)

# Both work in parallel!
```

### Context Handoff

```python
# Architect completes design, hands off to Backend
architect.handoff_to_agent("backend-dev", {
    "api_spec": "/docs/api.yaml",
    "database_schema": "/docs/schema.sql",
    "lessons_learned": ["Use idempotency keys"]
})
```

### Checking Assigned Tasks

```python
# Backend checks what tasks are assigned
pending = backend.get_pending_tasks()
for task in pending:
    print(f"📋 {task['title']} from {task['creator']}")

# Complete a task
backend.complete_delegated_task(
    task_id="abc123",
    result={"endpoints": ["/auth/login", "/auth/signup"]}
)
```

## Collaboration Patterns

### Sequential
```
CEO → Architect → Backend → DevOps
```
Each step waits for previous to complete.

### Parallel
```
      ┌→ Backend
CEO → |
      └→ Frontend
```
Multiple agents work simultaneously.

### Hierarchical
```
CEO (manager)
  ├→ Architect (lead)
  │  ├→ Backend-dev
  │  └→ Frontend-dev
  └→ DevOps (lead)
     └→ Monitoring-agent
```
Manager delegates to leads, who delegate to workers.

## Task Matching

Agents are matched to tasks based on:
1. **Capability match** - Required vs available capabilities
2. **Availability** - Agent status and current load
3. **Historical success** - Past performance on similar tasks

```python
# Score calculation example
match_score = registry._calculate_match_score(agent, task)
# Returns 0-1 value based on capability overlap
```

## File Structure

```
.arli/
├── agents/
│   ├── registry.json          # Agent profiles
│   └── capabilities/          # Capability definitions
├── tasks/
│   └── delegated/
│       ├── {task_id}.json     # Individual tasks
│       └── board.json         # Task board index
└── handoffs/
    └── {from}_to_{to}_{timestamp}.json
```

## API Reference

### AgentRuntime Collaboration Methods

| Method | Description |
|--------|-------------|
| `delegate_task(title, desc, type, caps, to_agent, priority)` | Delegate task to another agent |
| `get_pending_tasks()` | Get tasks assigned to this agent |
| `complete_delegated_task(task_id, result)` | Mark task as complete |
| `get_available_agents()` | List agents that can accept tasks |
| `handoff_to_agent(to_agent, context)` | Transfer context to agent |

### CollaborationOrchestrator Methods

| Method | Description |
|--------|-------------|
| `create_and_delegate(...)` | Create and delegate task |
| `delegate_task(task, from_agent, to_agent)` | Delegate existing task |
| `execute_collaboration_pattern(pattern, task, agents)` | Run collaboration pattern |
| `handoff_context(from, to, context)` | Hand off context |
| `aggregate_results(parent_task_id)` | Aggregate subtask results |
| `get_collaboration_summary()` | Get collaboration stats |

### AgentRegistry Methods

| Method | Description |
|--------|-------------|
| `register_agent(profile)` | Add agent to registry |
| `get_agent(agent_id)` | Get agent by ID |
| `find_agents_by_capability(cap)` | Find agents with capability |
| `find_best_agent(task)` | Find best agent for task |
| `update_agent_status(id, status, task)` | Update agent status |

## Testing

```bash
cd ~/arli

# Test collaboration system
python3 agents/collaboration.py

# Integration test
python3 agents/test_collaboration.py
```

## Integration with Memory

Collaboration works with the Memory System:

```python
# Agent delegates and remembers
backend = AgentRuntime("backend-dev", enable_memory=True)

# Memory tracks the delegation
backend.start_task("Implement API", "coding")
# ... do work ...
backend.end_task("success", lessons=["Use proper error handling"])

# Delegate to another agent with context
backend.delegate_task(
    title="Add tests",
    description="Write unit tests for API",
    task_type="testing",
    required_capabilities=["testing"],
    to_agent="qa-agent"
)
```

## Next Steps

- [ ] Agent-to-agent communication protocol
- [ ] Conflict resolution when multiple agents want same task
- [ ] Automatic result verification
- [ ] Cross-company agent collaboration
- [ ] Agent reputation system
