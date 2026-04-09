# 🧠 ARLI Agent Memory System

**Phase A1+A2+A3+A4: Persistent Memory + Pattern Learning + Semantic Retrieval + Self-Improvement**

## Overview

ARLI agents now have **persistent memory** that survives across sessions. They learn from past tasks, share knowledge, **and continuously improve themselves**.

## Features

### ✅ Phase A1: Basic Persistence

- **Episodic Memory** — каждая задача сохраняется как эпизод
- **JSONL Storage** — append-only, human-readable
- **Action Tracking** — все действия агента логируются
- **Company Context** — загружается из COMPANY.md

### ✅ Phase A2: Pattern Learning

- **Pattern Extraction** — автоматический анализ эпизодов
- **Success/Failure Patterns** — что работает, что нет
- **Workflow Patterns** — типичные последовательности действий
- **Context-Aware** — паттерны группируются по контексту (auth, database, etc.)

### ✅ Phase A3: Semantic Retrieval

- **Vector Embeddings** — тексты преобразуются в векторы
- **Semantic Search** — поиск по смыслу, не по ключевым словам
- **FAISS Integration** — быстрый поиск в больших базах
- **Multi-Aspect Embeddings** — task, lessons, full_context

### ✅ Phase A4: Self-Improvement

- **Memory Consolidation** — объединение похожих эпизодов
- **Pattern Validation** — проверка, что паттерны всё ещё работают
- **Auto-Forget** — автоматическая очистка устаревшего
- **Meta-Learning** — извлечение общих принципов
- **Learning Strategies** — анализ эффективных подходов

## File Structure

```
.arli/memory/
├── agents/{agent_id}/
│   ├── episodes.jsonl           # Все выполненные задачи
│   ├── patterns.json            # Успешные/неуспешные паттерны
│   ├── state.json               # Статистика агента
│   ├── extracted_patterns.json  # AI-извлеченные паттерны
│   └── embeddings/              # Векторные эмбеддинги
│       ├── {agent}_embeddings.npy
│       ├── {agent}_metadata.jsonl
│       └── {agent}_faiss.index
├── shared/
│   ├── knowledge_base.jsonl   # Общие знания компании
│   ├── failures.jsonl         # Ошибки всех агентов
│   └── success_patterns.json  # Успешные подходы
└── embeddings/                # Векторные индексы
```

## Usage

### Basic Usage

```python
from runtime import AgentRuntime

# Create agent with memory
agent = AgentRuntime("backend-dev", workspace=".", enable_memory=True)

# Start task (creates episode)
agent.start_task("Build auth API", "coding")

# Do work...
agent.write_file("auth.py", "...")
agent.execute_shell("pytest")

# End task (saves to memory)
agent.end_task(
    result="success",
    lessons=["Use bcrypt for passwords", "Add rate limiting"]
)

# Get context for new task
context = agent.get_memory_context("Create login endpoint")
print(context)  # Shows similar past tasks + lessons
```

### Pattern Learning

```python
# Analyze all episodes and extract patterns
analysis = agent.memory.analyze_patterns()
print(f"Found {analysis['new_patterns']} new patterns")

# Get recommendations
recs = agent.memory.learner.get_recommendations("Build auth", "coding")
for rec in recs:
    print(rec)  # ✅ Use bcrypt for password hashing...
```

### Sharing Knowledge

```python
# Share with all agents
agent.share_knowledge("React Best Practices", "Use functional components")

# Other agents see this in their context
context = other_agent.get_memory_context("Build React component")
# Shows: 📚 Team Knowledge: React Best Practices: ...
```

### Semantic Search

```python
# Search by meaning (not just keywords)
results = agent.memory.semantic_search("authentication with tokens", k=3)
for r in results:
    print(f"{r['similarity']:.2f}: {r['text']}")

# Get semantically similar lessons
lessons = agent.memory.get_semantic_recommendations("Build secure login")
for lesson in lessons:
    print(f"💡 {lesson}")

# Context automatically includes semantic matches
context = agent.get_memory_context("Create OAuth flow")
# Shows: 🔍 Semantically Similar Tasks: ...
```

### Self-Improvement

```python
# Run full self-improvement analysis (dry run first)
report = agent.improve_memory(dry_run=True)
print(f"Consolidation candidates: {report['consolidation']['candidates_found']}")
print(f"Valid patterns: {report['pattern_validation']['valid_patterns']}")

# Get learning insights
insights = agent.get_learning_insights()
for strategy in insights['learning_strategies']:
    print(f"{strategy['strategy']}: {strategy['success_rate']:.0%}")

for principle in insights['general_principles']:
    print(f"🎯 {principle}")

# Apply optimizations (production)
# agent.improve_memory(dry_run=False)
```

## Memory Context Format

Agents automatically receive this context in prompts:

```markdown
## 📚 Your Memory Context

**Company:** DevStudio One
**Type:** Software Development Agency

### 🎓 AI Recommendations:
✅ Use bcrypt for password hashing
✅ JWT tokens need expiration timestamps
⚠️ Always validate input

### 🔍 Semantically Similar Tasks:
1. ✅ (85% match) Build user authentication API...
2. ✅ (72% match) Create login endpoint with session...

### 💡 Relevant Lessons:
• JWT tokens need expiration timestamps
• Rate limit login attempts
• Always validate token signatures

### 📖 Similar Past Tasks:
1. ❌ Build JWT authentication endpoint...
   💡 Lesson: JWT tokens must have expiration timestamps
2. ✅ Create secure login API...
   💡 Lesson: Rate limiting prevents brute force

### 🎯 Patterns You Know:
• Use environment variables for secrets
• Always use HTTPS in production

### ⚠️ Avoid These Mistakes:
• Never store passwords in plain text

### 👥 Team Knowledge:
• JWT Best Practices: Always rotate secrets monthly

---
```

## API Reference

### AgentRuntime Methods

| Method | Description |
|--------|-------------|
| `start_task(task, type)` | Start new episode |
| `end_task(result, lessons)` | Save episode with lessons |
| `get_memory_context(task)` | Get relevant context for task |
| `get_memory_stats()` | Get memory statistics |
| `share_knowledge(topic, content)` | Share with all agents |
| `semantic_search(query, k)` | Semantic search episodes |
| `improve_memory(dry_run)` | Run self-improvement analysis |
| `get_learning_insights()` | Get meta-learning insights |

### AgentMemory Methods

| Method | Description |
|--------|-------------|
| `start_episode(task, type)` | Create new episode |
| `record_action(tool, input, output, success)` | Log action |
| `end_episode(result, lessons)` | Finalize episode |
| `analyze_patterns()` | Extract patterns from episodes |
| `get_relevant_context(task)` | Get context for prompt |
| `semantic_search(query, k)` | Vector-based search |
| `get_semantic_recommendations(task)` | Semantic lesson recommendations |

### PatternLearner Methods

| Method | Description |
|--------|-------------|
| `analyze_episodes(episodes)` | Extract patterns |
| `get_recommendations(task, type)` | Get pattern-based advice |
| `get_patterns_for_context(ctx)` | Get patterns for context |
| `get_stats()` | Get learning statistics |

### SemanticMemoryStore Methods

| Method | Description |
|--------|-------------|
| `add_episode(episode)` | Add episode to vector index |
| `search(query, k)` | Semantic search |
| `get_similar_lessons(task, k)` | Find similar lessons |
| `get_contextual_memory(task)` | Get full semantic context |
| `get_stats()` | Get index statistics |

### SelfImprovementEngine Methods

| Method | Description |
|--------|-------------|
| `run_full_analysis(dry_run)` | Complete self-improvement cycle |
| `consolidator.run_consolidation(dry_run)` | Merge similar episodes |
| `validator.validate_patterns(min_usage)` | Check pattern effectiveness |
| `auto_forget.cleanup_plan()` | Find cleanup opportunities |
| `meta_learner.generate_insights_report()` | Extract learning insights |

## Testing

```bash
cd ~/arli

# Individual component tests
python3 agents/runtime.py
python3 agents/pattern_learning.py
python3 agents/semantic_memory.py
python3 agents/self_improvement.py

# Phase integration tests
python3 agents/test_memory_phase_a2.py  # Pattern learning
python3 agents/test_memory_phase_a3.py  # Semantic retrieval
python3 agents/test_memory_phase_a4.py  # Self-improvement

# Real-world example
python3 agents/memory_example.py
```

## All Phases Complete ✅

ARLI Agent Memory System is now **production-ready** with all 4 phases:

- ✅ **A1: Persistence** — Episodes survive across sessions
- ✅ **A2: Pattern Learning** — Auto-extract success patterns  
- ✅ **A3: Semantic Retrieval** — Vector-based meaning search
- ✅ **A4: Self-Improvement** — Auto-consolidate, validate, optimize

## Stats Example

```python
{
  "agent_id": "backend-dev",
  "episodic": {
    "total_episodes": 8,
    "success_rate": 0.8,
    "patterns_learned": 7,
    "failures_avoided": 3
  },
  "patterns": {
    "total_patterns": 12,
    "success_patterns": 6,
    "failure_patterns": 4,
    "avg_success_rate": 0.74,
    "contexts": ["auth", "database", "api"]
  },
  "semantic": {
    "total_embeddings": 40,
    "unique_episodes": 8,
    "faiss_available": True,
    "index_size": 40,
    "embedding_types": ["task", "lesson_0", "lesson_1", "full_context"]
  }
}
```

---

**Built for ARLI** 🚀
