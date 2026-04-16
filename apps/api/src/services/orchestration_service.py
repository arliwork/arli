"""
ARLI Autonomous Company Orchestration Service
Coordinates the full pipeline: CEO → Architect → Backend → Frontend → DevOps
"""
import os
import sys
import json
import uuid
import asyncio
from services.llm_client import get_llm_client, LLMResponse
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add agents to path
ARLI_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ARLI_ROOT / "agents"))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import ARLI agent systems
try:
    from collaboration import CollaborationOrchestrator, DelegatedTask
    COLLAB_AVAILABLE = True
except ImportError:
    COLLAB_AVAILABLE = False

try:
    from runtime import AgentRuntime
    RUNTIME_AVAILABLE = True
except ImportError:
    RUNTIME_AVAILABLE = False

from models import Workflow, Task, Agent

# Agent role definitions for the autonomous company
# Company templates for 1-click launch
COMPANY_TEMPLATES = {
    "sales": {
        "name": "Sales Company",
        "description": "AI-powered sales team for lead generation and outreach",
        "pipeline_type": "plan-feature",
        "agents": [
            {"role": "ceo", "name": "Sales Director", "capabilities": ["strategy", "planning", "delegation"]},
            {"role": "researcher", "name": "Lead Researcher", "capabilities": ["research", "data-analysis", "linkedin-scraping"]},
            {"role": "backend-dev", "name": "Outreach Agent", "capabilities": ["email-automation", "crm-integration", "personalization"]},
            {"role": "devops", "name": "CRM Manager", "capabilities": ["salesforce", "hubspot", "reporting"]},
        ],
    },
    "dev": {
        "name": "Dev Agency",
        "description": "Full-stack AI development team",
        "pipeline_type": "plan-feature",
        "agents": [
            {"role": "ceo", "name": "Tech Lead", "capabilities": ["strategy", "planning", "delegation"]},
            {"role": "architect", "name": "System Architect", "capabilities": ["system-design", "architecture-review"]},
            {"role": "backend-dev", "name": "Backend Engineer", "capabilities": ["api-development", "database", "testing"]},
            {"role": "frontend-dev", "name": "Frontend Engineer", "capabilities": ["ui-development", "react", "styling"]},
            {"role": "devops", "name": "DevOps Engineer", "capabilities": ["deployment", "ci-cd", "monitoring"]},
        ],
    },
    "trading": {
        "name": "Trading Desk",
        "description": "AI-powered crypto and forex trading desk",
        "pipeline_type": "plan-feature",
        "agents": [
            {"role": "ceo", "name": "Fund Manager", "capabilities": ["strategy", "risk-management", "delegation"]},
            {"role": "researcher", "name": "Market Analyst", "capabilities": ["technical-analysis", "on-chain-analysis", "research"]},
            {"role": "backend-dev", "name": "Trading Agent", "capabilities": ["trading", "api-integration", "binance"]},
            {"role": "devops", "name": "Risk Manager", "capabilities": ["monitoring", "alerts", "reporting"]},
        ],
    },
    "content": {
        "name": "Content Studio",
        "description": "AI-powered content creation and distribution studio",
        "pipeline_type": "plan-feature",
        "agents": [
            {"role": "ceo", "name": "Creative Director", "capabilities": ["strategy", "planning", "delegation"]},
            {"role": "researcher", "name": "Trend Researcher", "capabilities": ["research", "trend-analysis", "seo"]},
            {"role": "backend-dev", "name": "Content Writer", "capabilities": ["content_creation", "copywriting", "storytelling"]},
            {"role": "frontend-dev", "name": "Designer", "capabilities": ["design", "branding", "visual-content"]},
            {"role": "devops", "name": "Publisher", "capabilities": ["scheduling", "social-media", "distribution"]},
        ],
    },
}

COMPANY_AGENTS = {
    "ceo": {
        "role": "ceo",
        "capabilities": ["strategy", "planning", "delegation"],
        "description": "CEO agent that analyzes tasks and creates execution plans",
    },
    "architect": {
        "role": "architect",
        "capabilities": ["system-design", "architecture-review"],
        "description": "CTO/Architect agent that designs technical solutions",
    },
    "backend-dev": {
        "role": "backend-dev",
        "capabilities": ["api-development", "database", "testing"],
        "description": "Backend developer that implements APIs and business logic",
    },
    "frontend-dev": {
        "role": "frontend-dev",
        "capabilities": ["ui-development", "react", "styling"],
        "description": "Frontend developer that builds user interfaces",
    },
    "devops": {
        "role": "devops",
        "capabilities": ["deployment", "ci-cd", "monitoring"],
        "description": "DevOps engineer that deploys and monitors systems",
    },
}

WORKFLOW_PIPELINES = {
    "plan-feature": [
        ("ceo", "Analyze feature requirements and create task breakdown"),
        ("architect", "Design system architecture and API contracts"),
        ("backend-dev", "Implement backend APIs and database schema"),
        ("frontend-dev", "Build frontend UI and integrate with backend"),
        ("devops", "Deploy to production and setup monitoring"),
    ],
    "fix-bug": [
        ("ceo", "Prioritize bug and assign resources"),
        ("architect", "Investigate root cause and design fix"),
        ("backend-dev", "Implement backend fix"),
        ("frontend-dev", "Fix UI if needed"),
        ("devops", "Deploy fix and verify"),
    ],
    "refactor": [
        ("architect", "Design refactoring plan"),
        ("backend-dev", "Execute refactoring"),
        ("devops", "Run tests and deploy"),
    ],
}


# Runtime type alias for missing imports
RuntimeType = Any

class OrchestrationService:
    """Service that runs the autonomous company pipeline"""
    
    def __init__(self, workspace: str = "."):
        self.workspace = Path(workspace).resolve()
        self.collaboration = None
        self.runtimes: Dict[str, AgentRuntime] = {}
        
        if COLLAB_AVAILABLE:
            self.collaboration = CollaborationOrchestrator(workspace=str(self.workspace))
        
        if RUNTIME_AVAILABLE:
            for agent_id, config in COMPANY_AGENTS.items():
                self.runtimes[agent_id] = AgentRuntime(
                    agent_id=agent_id,
                    workspace=str(self.workspace),
                    enable_memory=True,
                )
    
    async def create_workflow(self, db: AsyncSession, name: str, description: str, pipeline_type: str, context: Optional[Dict] = None, workflow_id: Optional[str] = None) -> Workflow:
        """Create a new autonomous workflow"""
        steps = WORKFLOW_PIPELINES.get(pipeline_type, [])
        
        workflow = Workflow(
            workflow_id=workflow_id or f"wf_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            total_steps=len(steps),
            context=context or {},
        )
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        
        # Create tasks for each step
        for idx, (role, step_desc) in enumerate(steps):
            task = Task(
                task_id=f"task_{workflow.workflow_id}_{idx}",
                category=pipeline_type,
                description=f"[{role}] {step_desc} for: {description}",
                assigned_role=role,
                workflow_id=workflow.id,
                status="pending",
            )
            db.add(task)
        
        await db.commit()
        await db.refresh(workflow)
        return workflow
    
    async def execute_workflow_step(self, db: AsyncSession, workflow_id: str) -> Dict[str, Any]:
        """Execute the next pending step in a workflow"""
        result = await db.execute(select(Workflow).where(Workflow.workflow_id == workflow_id))
        workflow = result.scalar_one_or_none()
        if not workflow:
            return {"success": False, "error": "Workflow not found"}
        
        if workflow.status in ("completed", "failed"):
            return {"success": False, "error": f"Workflow already {workflow.status}"}
        
        # Find next pending task in order
        result = await db.execute(
            select(Task)
            .where(Task.workflow_id == workflow.id, Task.status == "pending")
            .order_by(Task.created_at.asc())
            .limit(1)
        )
        task = result.scalar_one_or_none()
        
        if not task:
            workflow.status = "completed"
            workflow.completed_at = datetime.now(timezone.utc)
            await db.commit()
            return {"success": True, "message": "Workflow completed", "workflow_id": workflow_id}
        
        # Mark workflow as running
        if workflow.status == "pending":
            workflow.status = "running"
            workflow.started_at = datetime.now(timezone.utc)
        
        # Mark task as running
        task.status = "running"
        task.started_at = datetime.now(timezone.utc)
        await db.commit()
        
        # Execute via agent runtime
        execution_result = await self._execute_task(task)
        
        # Update task with result
        task.status = "completed" if execution_result.get("success") else "failed"
        task.success = execution_result.get("success", False)
        task.result_data = execution_result
        task.completed_at = datetime.now(timezone.utc)
        workflow.current_step += 1
        
        await db.commit()
        
        return {
            "success": execution_result.get("success", False),
            "task_id": task.task_id,
            "role": task.assigned_role,
            "result": execution_result,
            "workflow_status": workflow.status,
            "current_step": workflow.current_step,
            "total_steps": workflow.total_steps,
        }
    
    async def _execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a single task using LLM generation and runtime tools"""
        import re
        from services.llm_client import get_llm_client, LLMResponse
        
        role = task.assigned_role or "backend-dev"
        llm = get_llm_client()
        
        # Get or create runtime for this agent role
        runtime = self.runtimes.get(f"arli_{role}")
        if not runtime and RUNTIME_AVAILABLE:
            runtime = AgentRuntime(agent_id=f"arli_{role}", workspace=str(self.workspace), enable_memory=True)
            self.runtimes[f"arli_{role}"] = runtime
        
        try:
            if role == "ceo":
                messages = [
                    {"role": "system", "content": "You are a strategic CEO of an autonomous AI company. Analyze the task and create a concise execution plan with phases, success criteria, and resource allocation."},
                    {"role": "user", "content": f"Task: {task.description}"},
                ]
                resp = await llm.generate(messages, task_type="reasoning", max_tokens=2000)
                if runtime:
                    runtime.log("plan_created", f"CEO plan for {task.description[:60]}")
                return {
                    "success": True,
                    "output": resp.content,
                    "credits_used": resp.credits_used,
                    "model_used": resp.model,
                    "role": "ceo"
                }
            
            elif role == "architect":
                messages = [
                    {"role": "system", "content": "You are a senior system architect. Design a technical solution. Include architecture overview, tech stack, database recommendations, and API contracts."},
                    {"role": "user", "content": f"Design architecture for: {task.description}"},
                ]
                resp = await llm.generate(messages, task_type="reasoning", max_tokens=3000)
                if runtime:
                    runtime.log("design_created", f"Architecture for {task.description[:60]}")
                return {
                    "success": True,
                    "output": resp.content,
                    "credits_used": resp.credits_used,
                    "model_used": resp.model,
                    "role": "architect"
                }
            
            elif role in ("backend-dev", "frontend-dev", "devops"):
                task_type_code = "coding"
                if role == "backend-dev":
                    system = "You are an expert backend developer. Write clean, production-ready Python code. If creating a file, include the filename as a header comment like: # filename.py"
                    lang = "python" if "frontend" not in task.description.lower() else "typescript"
                elif role == "frontend-dev":
                    system = "You are an expert React/TypeScript frontend developer. Write modern UI code. If creating a component, include the filename as a header comment like: # Component.tsx"
                    lang = "typescript"
                else:
                    system = "You are a DevOps engineer. Write deployment configs, Docker files, CI/CD pipelines. If creating a file, include the filename as a header comment like: # docker-compose.yml"
                    lang = "yaml"
                
                messages = [
                    {"role": "system", "content": system},
                    {"role": "user", "content": task.description},
                ]
                resp = await llm.generate(messages, task_type=task_type_code, max_tokens=4000)
                
                files_modified = []
                if runtime:
                    # Try to extract file blocks and write them
                    file_blocks = re.findall(r'```\w*\n#\s*(\S+)\n(.*?)```', resp.content, re.DOTALL)
                    if not file_blocks:
                        file_blocks = re.findall(r'FILE:\s*(\S+)\s*```\w*\n(.*?)```', resp.content, re.DOTALL)
                    for fname, fcontent in file_blocks:
                        write_result = runtime.write_file(fname.strip(), fcontent.strip())
                        if write_result.get("success"):
                            files_modified.append(fname.strip())
                    runtime.log("code_execution", f"{role} executed {task.description[:60]} using {resp.model}")
                
                return {
                    "success": True,
                    "output": resp.content,
                    "credits_used": resp.credits_used,
                    "model_used": resp.model,
                    "role": role,
                    "files_modified": files_modified,
                }
            
            else:
                messages = [
                    {"role": "system", "content": "You are a helpful AI agent completing tasks efficiently."},
                    {"role": "user", "content": task.description},
                ]
                resp = await llm.generate(messages, task_type="general")
                return {
                    "success": True,
                    "output": resp.content,
                    "credits_used": resp.credits_used,
                    "model_used": resp.model,
                    "role": role
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "role": role,
            }
    

    async def launch_template(
        self,
        db: AsyncSession,
        template_key: str,
        user_id: str,
        custom_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Launch a company from a 1-click template"""
        template = COMPANY_TEMPLATES.get(template_key)
        if not template:
            return {"success": False, "error": f"Unknown template: {template_key}"}
        
        # Create agents for each role in template
        created_agents = []
        from models import Agent
        
        for agent_config in template["agents"]:
            agent = Agent(
                agent_id=f"agent_{agent_config['role']}_{uuid.uuid4().hex[:6]}",
                name=agent_config["name"],
                role=agent_config["role"],
                capabilities=agent_config["capabilities"],
                owner_id=user_id,
                creator_id=user_id,
            )
            db.add(agent)
            created_agents.append(agent)
        
        await db.flush()
        
        # Create workflow
        workflow = await self.create_workflow(
            db=db,
            name=custom_name or template["name"],
            description=template["description"],
            pipeline_type=template["pipeline_type"],
            context={"template": template_key, "agents": [a.agent_id for a in created_agents]},
        )
        
        await db.commit()
        
        return {
            "success": True,
            "template": template_key,
            "workflow_id": workflow.workflow_id,
            "agents": [
                {"id": a.id, "agent_id": a.agent_id, "name": a.name, "role": a.role}
                for a in created_agents
            ],
        }

    async def run_full_workflow(self, db: AsyncSession, workflow_id: str) -> Dict[str, Any]:
        """Run all steps of a workflow sequentially"""
        results = []
        max_steps = 50  # Safety limit
        
        for _ in range(max_steps):
            step_result = await self.execute_workflow_step(db, workflow_id)
            results.append(step_result)
            
            if step_result.get("message") == "Workflow completed":
                break
            if not step_result.get("success"):
                break
        
        return {
            "success": all(r.get("success", False) for r in results),
            "workflow_id": workflow_id,
            "steps_executed": len(results),
            "results": results,
        }


# Singleton instance
_orchestrator: Optional[OrchestrationService] = None

def get_orchestrator() -> OrchestrationService:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestrationService(workspace=str(ARLI_ROOT))
    return _orchestrator
