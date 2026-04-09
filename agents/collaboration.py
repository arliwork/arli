#!/usr/bin/env python3
"""
ARLI Multi-Agent Collaboration System
Agent-to-agent task delegation and communication

Features:
- Agent Registry: discover available agents and their capabilities
- Task Delegation: assign tasks to best-suited agents
- Handoff Protocol: transfer context between agents
- Collaboration Patterns: sequential, parallel, hierarchical
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import yaml


class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DELEGATED = "delegated"


class CollaborationPattern(Enum):
    SEQUENTIAL = "sequential"  # Agent A → Agent B → Agent C
    PARALLEL = "parallel"      # Agent A → [Agent B, Agent C] → Agent D
    HIERARCHICAL = "hierarchical"  # CEO → CTO → [Backend, Frontend, DevOps]


@dataclass
class AgentCapability:
    """What an agent can do"""
    name: str
    description: str
    keywords: List[str]  # For task matching
    tools: List[str]     # Available tools
    success_rate: float = 0.0
    avg_completion_time: int = 0  # seconds


@dataclass
class AgentProfile:
    """Agent registration info"""
    agent_id: str
    name: str
    role: str
    capabilities: List[AgentCapability]
    status: str = "available"  # available, busy, offline
    current_task: Optional[str] = None
    load: int = 0  # Number of concurrent tasks
    max_load: int = 3
    
    def can_accept_task(self) -> bool:
        return self.status == "available" and self.load < self.max_load


@dataclass
class DelegatedTask:
    """Task that can be delegated between agents"""
    task_id: str
    title: str
    description: str
    task_type: str
    required_capabilities: List[str]
    status: TaskStatus
    creator: str  # Agent who created the task
    assignee: Optional[str] = None  # Agent who is working on it
    parent_task: Optional[str] = None  # For subtasks
    subtasks: List[str] = None
    context: Dict[str, Any] = None  # Shared context
    result: Any = None
    created_at: str = None
    assigned_at: Optional[str] = None
    completed_at: Optional[str] = None
    priority: int = 1  # 1-5, higher = more important
    estimated_duration: int = 3600  # seconds
    
    def __post_init__(self):
        if self.subtasks is None:
            self.subtasks = []
        if self.context is None:
            self.context = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class AgentRegistry:
    """
    Registry of all agents in the company
    Manages agent discovery and capability matching
    """
    
    def __init__(self, company_id: str = "default", workspace: str = "."):
        self.company_id = company_id
        self.workspace = Path(workspace)
        self.registry_path = self.workspace / ".arli" / "agents" / "registry.json"
        self.agents: Dict[str, AgentProfile] = {}
        
        self._load_registry()
    
    def _load_registry(self):
        """Load agent registry from disk"""
        if self.registry_path.exists():
            try:
                data = json.loads(self.registry_path.read_text())
                for agent_id, profile_data in data.get("agents", {}).items():
                    caps = [AgentCapability(**c) for c in profile_data.get("capabilities", [])]
                    self.agents[agent_id] = AgentProfile(
                        agent_id=agent_id,
                        name=profile_data["name"],
                        role=profile_data["role"],
                        capabilities=caps,
                        status=profile_data.get("status", "available"),
                        current_task=profile_data.get("current_task"),
                        load=profile_data.get("load", 0),
                        max_load=profile_data.get("max_load", 3)
                    )
            except Exception as e:
                print(f"[AgentRegistry] Error loading: {e}")
                self._init_default_agents()
        else:
            self._init_default_agents()
    
    def _init_default_agents(self):
        """Initialize default agents from config"""
        config_path = self.workspace / ".arli" / "config.yaml"
        if not config_path.exists():
            return
        
        try:
            config = yaml.safe_load(config_path.read_text())
            for agent_id, agent_config in config.get("agents", {}).items():
                caps = self._extract_capabilities(agent_config)
                self.agents[agent_id] = AgentProfile(
                    agent_id=agent_id,
                    name=agent_config.get("name", agent_id),
                    role=agent_config.get("role", "general"),
                    capabilities=caps
                )
        except Exception as e:
            print(f"[AgentRegistry] Error loading config: {e}")
    
    def _extract_capabilities(self, agent_config: Dict) -> List[AgentCapability]:
        """Extract capabilities from agent config"""
        caps = []
        
        for cap_name in agent_config.get("capabilities", []):
            caps.append(AgentCapability(
                name=cap_name,
                description=f"Can perform {cap_name}",
                keywords=[cap_name],
                tools=[]
            ))
        
        return caps
    
    def register_agent(self, profile: AgentProfile) -> bool:
        """Register or update an agent"""
        self.agents[profile.agent_id] = profile
        self._save_registry()
        return True
    
    def get_agent(self, agent_id: str) -> Optional[AgentProfile]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def find_agents_by_capability(self, capability: str) -> List[AgentProfile]:
        """Find all agents with specific capability"""
        matching = []
        for agent in self.agents.values():
            for cap in agent.capabilities:
                if capability.lower() in cap.name.lower() or \
                   any(capability.lower() in kw.lower() for kw in cap.keywords):
                    matching.append(agent)
                    break
        return matching
    
    def find_best_agent(self, task: DelegatedTask) -> Optional[AgentProfile]:
        """
        Find best agent for a task based on:
        1. Capability match
        2. Availability
        3. Current load
        4. Historical success rate
        """
        candidates = []
        
        for agent in self.agents.values():
            # Check availability
            if not agent.can_accept_task():
                continue
            
            # Check capability match
            match_score = self._calculate_match_score(agent, task)
            if match_score > 0:
                candidates.append((agent, match_score))
        
        if not candidates:
            return None
        
        # Sort by match score (descending)
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    
    def _calculate_match_score(self, agent: AgentProfile, task: DelegatedTask) -> float:
        """Calculate how well agent matches task (0-1)"""
        if not task.required_capabilities:
            return 0.5  # Generic match
        
        agent_capabilities = set()
        for cap in agent.capabilities:
            agent_capabilities.add(cap.name.lower())
            agent_capabilities.update(kw.lower() for kw in cap.keywords)
        
        matches = 0
        for req_cap in task.required_capabilities:
            req_lower = req_cap.lower()
            if req_lower in agent_capabilities:
                matches += 1
            else:
                # Check partial matches
                for agent_cap in agent_capabilities:
                    if req_lower in agent_cap or agent_cap in req_lower:
                        matches += 0.5
                        break
        
        return matches / len(task.required_capabilities)
    
    def update_agent_status(self, agent_id: str, status: str, current_task: Optional[str] = None):
        """Update agent status"""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            self.agents[agent_id].current_task = current_task
            if status == "busy":
                self.agents[agent_id].load += 1
            elif status == "available":
                self.agents[agent_id].load = max(0, self.agents[agent_id].load - 1)
            self._save_registry()
    
    def _save_registry(self):
        """Save registry to disk"""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "company_id": self.company_id,
            "updated_at": datetime.now().isoformat(),
            "agents": {
                agent_id: {
                    "name": agent.name,
                    "role": agent.role,
                    "capabilities": [
                        {
                            "name": cap.name,
                            "description": cap.description,
                            "keywords": cap.keywords,
                            "tools": cap.tools
                        }
                        for cap in agent.capabilities
                    ],
                    "status": agent.status,
                    "current_task": agent.current_task,
                    "load": agent.load,
                    "max_load": agent.max_load
                }
                for agent_id, agent in self.agents.items()
            }
        }
        self.registry_path.write_text(json.dumps(data, indent=2))


class TaskBoard:
    """
    Central task board for all delegated tasks
    """
    
    def __init__(self, workspace: str = "."):
        self.workspace = Path(workspace)
        self.board_path = self.workspace / ".arli" / "tasks" / "delegated"
        self.board_path.mkdir(parents=True, exist_ok=True)
        
        self.tasks: Dict[str, DelegatedTask] = {}
        self._load_tasks()
    
    def _load_tasks(self):
        """Load all tasks from disk"""
        for task_file in self.board_path.glob("*.json"):
            try:
                data = json.loads(task_file.read_text())
                task = DelegatedTask(**data)
                self.tasks[task.task_id] = task
            except:
                pass
    
    def create_task(self, title: str, description: str, task_type: str,
                   required_capabilities: List[str], creator: str,
                   priority: int = 1, parent_task: Optional[str] = None) -> DelegatedTask:
        """Create new task on the board"""
        task = DelegatedTask(
            task_id=str(uuid.uuid4())[:8],
            title=title,
            description=description,
            task_type=task_type,
            required_capabilities=required_capabilities,
            status=TaskStatus.PENDING,
            creator=creator,
            parent_task=parent_task
        )
        
        self.tasks[task.task_id] = task
        self._save_task(task)
        
        return task
    
    def assign_task(self, task_id: str, assignee: str) -> bool:
        """Assign task to an agent"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.assignee = assignee
        task.status = TaskStatus.ASSIGNED
        task.assigned_at = datetime.now().isoformat()
        
        self._save_task(task)
        return True
    
    def update_task_status(self, task_id: str, status: TaskStatus, result: Any = None) -> bool:
        """Update task status and optionally set result"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = status
        
        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now().isoformat()
            task.result = result
        elif status == TaskStatus.DELEGATED:
            # Task was delegated to subtasks
            pass
        
        self._save_task(task)
        return True
    
    def add_subtask(self, parent_id: str, subtask_id: str) -> bool:
        """Add subtask to parent task"""
        if parent_id not in self.tasks:
            return False
        
        self.tasks[parent_id].subtasks.append(subtask_id)
        self._save_task(self.tasks[parent_id])
        return True
    
    def get_task(self, task_id: str) -> Optional[DelegatedTask]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_pending_tasks(self) -> List[DelegatedTask]:
        """Get all pending tasks"""
        return [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
    
    def get_agent_tasks(self, agent_id: str) -> List[DelegatedTask]:
        """Get all tasks assigned to or created by agent"""
        return [
            t for t in self.tasks.values()
            if t.assignee == agent_id or t.creator == agent_id
        ]
    
    def _save_task(self, task: DelegatedTask):
        """Save task to disk"""
        task_file = self.board_path / f"{task.task_id}.json"
        task_file.write_text(json.dumps(asdict(task), indent=2, default=str))


class CollaborationOrchestrator:
    """
    Main orchestrator for multi-agent collaboration
    Handles task delegation, handoffs, and result aggregation
    """
    
    def __init__(self, workspace: str = "."):
        self.workspace = Path(workspace)
        self.registry = AgentRegistry(workspace=workspace)
        self.task_board = TaskBoard(workspace=workspace)
        
        # Callbacks for agent notification
        self._delegation_callbacks: Dict[str, Callable] = {}
    
    def register_delegation_callback(self, agent_id: str, callback: Callable):
        """Register callback for when agent receives task"""
        self._delegation_callbacks[agent_id] = callback
    
    def delegate_task(self, task: DelegatedTask, from_agent: str, 
                     to_agent: Optional[str] = None) -> Optional[DelegatedTask]:
        """
        Delegate task to another agent
        If to_agent not specified, find best match
        """
        # Update task creator
        task.creator = from_agent
        
        # Find agent if not specified
        if to_agent is None:
            best_agent = self.registry.find_best_agent(task)
            if not best_agent:
                print(f"[Collaboration] No suitable agent found for task: {task.title}")
                return None
            to_agent = best_agent.agent_id
        
        # Assign task
        task.assignee = to_agent
        task.status = TaskStatus.ASSIGNED
        task.assigned_at = datetime.now().isoformat()
        
        # Save to board
        self.task_board.tasks[task.task_id] = task
        self.task_board._save_task(task)
        
        # Update agent status
        self.registry.update_agent_status(to_agent, "busy", task.task_id)
        
        # Notify agent (if callback registered)
        if to_agent in self._delegation_callbacks:
            self._delegation_callbacks[to_agent](task)
        
        print(f"[Collaboration] Task '{task.title}' delegated from {from_agent} to {to_agent}")
        
        return task
    
    def create_and_delegate(self, title: str, description: str, task_type: str,
                           required_capabilities: List[str], from_agent: str,
                           to_agent: Optional[str] = None, priority: int = 1,
                           parent_task: Optional[str] = None) -> Optional[DelegatedTask]:
        """Create task and immediately delegate"""
        task = self.task_board.create_task(
            title=title,
            description=description,
            task_type=task_type,
            required_capabilities=required_capabilities,
            creator=from_agent,
            priority=priority,
            parent_task=parent_task
        )
        
        return self.delegate_task(task, from_agent, to_agent)
    
    def handoff_context(self, from_agent: str, to_agent: str, 
                       context: Dict[str, Any]) -> bool:
        """
        Hand off context from one agent to another
        Preserves memory and state across agents
        """
        # Save handoff context
        handoff_path = self.workspace / ".arli" / "handoffs" / f"{from_agent}_to_{to_agent}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        
        handoff_data = {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        
        handoff_path.write_text(json.dumps(handoff_data, indent=2))
        
        # In production: notify receiving agent
        print(f"[Collaboration] Context handed off from {from_agent} to {to_agent}")
        
        return True
    
    def aggregate_results(self, parent_task_id: str) -> Dict[str, Any]:
        """
        Aggregate results from all subtasks
        Returns combined result
        """
        parent = self.task_board.get_task(parent_task_id)
        if not parent:
            return {"error": "Parent task not found"}
        
        results = {
            "parent_task": parent_task_id,
            "subtasks_completed": 0,
            "subtasks_failed": 0,
            "results": {}
        }
        
        for subtask_id in parent.subtasks:
            subtask = self.task_board.get_task(subtask_id)
            if not subtask:
                continue
            
            if subtask.status == TaskStatus.COMPLETED:
                results["subtasks_completed"] += 1
                results["results"][subtask_id] = {
                    "title": subtask.title,
                    "result": subtask.result,
                    "assignee": subtask.assignee
                }
            elif subtask.status == TaskStatus.FAILED:
                results["subtasks_failed"] += 1
        
        return results
    
    def execute_collaboration_pattern(self, pattern: CollaborationPattern,
                                    initial_task: DelegatedTask,
                                    agent_sequence: List[str]) -> List[DelegatedTask]:
        """
        Execute a collaboration pattern
        Returns list of created tasks
        """
        tasks = []
        
        if pattern == CollaborationPattern.SEQUENTIAL:
            # Chain: Agent A → Agent B → Agent C
            current_task = initial_task
            for i, agent_id in enumerate(agent_sequence):
                if i == 0:
                    # First agent gets initial task
                    task = self.delegate_task(current_task, "orchestrator", agent_id)
                else:
                    # Subsequent agents get new tasks with context
                    task = self.create_and_delegate(
                        title=f"Continue: {initial_task.title}",
                        description=f"Continue work from previous agent. Context: {current_task.title}",
                        task_type=initial_task.task_type,
                        required_capabilities=initial_task.required_capabilities,
                        from_agent=agent_sequence[i-1],
                        to_agent=agent_id,
                        parent_task=initial_task.task_id
                    )
                
                if task:
                    tasks.append(task)
                    current_task = task
        
        elif pattern == CollaborationPattern.PARALLEL:
            # Fan out: Agent A → [Agent B, Agent C, Agent D]
            # Then aggregate
            for agent_id in agent_sequence:
                task = self.create_and_delegate(
                    title=f"Part of: {initial_task.title}",
                    description=f"Parallel work on: {initial_task.description}",
                    task_type=initial_task.task_type,
                    required_capabilities=initial_task.required_capabilities,
                    from_agent=initial_task.creator,
                    to_agent=agent_id,
                    parent_task=initial_task.task_id
                )
                if task:
                    tasks.append(task)
        
        elif pattern == CollaborationPattern.HIERARCHICAL:
            # Manager delegates to workers
            if agent_sequence:
                manager = agent_sequence[0]
                workers = agent_sequence[1:]
                
                # Manager gets oversight task
                manager_task = self.delegate_task(initial_task, "orchestrator", manager)
                if manager_task:
                    tasks.append(manager_task)
                
                # Manager delegates to workers
                for worker in workers:
                    subtask = self.create_and_delegate(
                        title=f"Subtask for: {initial_task.title}",
                        description=f"Work assigned by {manager}",
                        task_type=initial_task.task_type,
                        required_capabilities=initial_task.required_capabilities,
                        from_agent=manager,
                        to_agent=worker,
                        parent_task=initial_task.task_id
                    )
                    if subtask:
                        tasks.append(subtask)
                        self.task_board.add_subtask(initial_task.task_id, subtask.task_id)
        
        return tasks
    
    def get_collaboration_summary(self) -> Dict[str, Any]:
        """Get summary of all collaboration activity"""
        return {
            "registered_agents": len(self.registry.agents),
            "total_tasks": len(self.task_board.tasks),
            "pending_tasks": len(self.task_board.get_pending_tasks()),
            "agents_by_status": {
                "available": len([a for a in self.registry.agents.values() if a.status == "available"]),
                "busy": len([a for a in self.registry.agents.values() if a.status == "busy"])
            }
        }


# Example usage
if __name__ == "__main__":
    print("🚀 ARLI Multi-Agent Collaboration Test")
    print("=" * 60)
    
    # Create orchestrator
    orchestrator = CollaborationOrchestrator(".")
    
    print("\n1. Registered Agents:")
    for agent_id, agent in orchestrator.registry.agents.items():
        caps = ", ".join(c.name for c in agent.capabilities[:3])
        print(f"   • {agent.name} ({agent_id}): {caps}")
    
    print("\n2. Creating and delegating tasks:")
    
    # CEO creates a feature request
    task1 = orchestrator.create_and_delegate(
        title="Build user authentication system",
        description="Complete auth system with login, signup, password reset",
        task_type="feature",
        required_capabilities=["system-design", "api-development"],
        from_agent="ceo",
        priority=5
    )
    
    if task1:
        print(f"   ✅ Created: {task1.title} → {task1.assignee}")
    
    # Sequential delegation example
    print("\n3. Sequential pattern (Architect → Backend → Frontend):")
    design_task = orchestrator.create_and_delegate(
        title="Design API architecture",
        description="Create API specs and database schema",
        task_type="design",
        required_capabilities=["system-design"],
        from_agent="ceo",
        to_agent="architect"
    )
    
    if design_task:
        print(f"   ✅ Architect designing: {design_task.title}")
        
        # Architect delegates implementation
        impl_task = orchestrator.create_and_delegate(
            title="Implement auth API",
            description=f"Based on design: {design_task.task_id}",
            task_type="coding",
            required_capabilities=["api-development"],
            from_agent="architect",
            to_agent="backend-dev"
        )
        
        if impl_task:
            print(f"   ✅ Backend implementing: {impl_task.title}")
    
    print("\n4. Collaboration Summary:")
    summary = orchestrator.get_collaboration_summary()
    print(f"   Agents: {summary['registered_agents']}")
    print(f"   Tasks: {summary['total_tasks']}")
    print(f"   Pending: {summary['pending_tasks']}")
    
    print("\n✅ Collaboration tests complete!")
