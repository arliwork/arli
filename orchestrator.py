#!/usr/bin/env python3
"""
ARLI Orchestrator - Real Agent Runtime
Executes tasks using Hermes Agent sub-processes
"""

import os
import json
import time
import yaml
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class ARLIOrchestrator:
    def __init__(self, config_path: str = ".arli/config.yaml"):
        self.config = yaml.safe_load(open(config_path))
        self.company_name = self.config['company']['name']
        self.agents = self.config['agents']
        self.running = False
        self.active_tasks: Dict[str, dict] = {}
        
        # Ensure directories exist
        Path("./tasks/pending").mkdir(parents=True, exist_ok=True)
        Path("./tasks/in-progress").mkdir(parents=True, exist_ok=True)
        Path("./tasks/completed").mkdir(parents=True, exist_ok=True)
        Path("./inbox").mkdir(parents=True, exist_ok=True)
        Path("./logs").mkdir(parents=True, exist_ok=True)
        
    def log(self, message: str, level: str = "info"):
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level.upper()}] {message}"
        print(log_entry)
        
        with open(f"./logs/orchestrator.log", "a") as f:
            f.write(log_entry + "\n")
    
    def scan_pending_tasks(self) -> List[dict]:
        """Scan for new tasks in pending folder"""
        pending_path = Path("./tasks/pending")
        tasks = []
        
        for task_file in pending_path.glob("*.json"):
            try:
                task = json.loads(task_file.read_text())
                task['file_path'] = str(task_file)
                tasks.append(task)
            except Exception as e:
                self.log(f"Error reading task {task_file}: {e}", "error")
                
        return tasks
    
    def find_best_agent(self, task: dict) -> Optional[str]:
        """Find best agent for the task based on required capabilities"""
        required_caps = task.get('required_capabilities', [])
        
        for agent_id, agent_config in self.agents.items():
            agent_caps = agent_config.get('capabilities', [])
            
            # Check if agent has all required capabilities
            if all(cap in agent_caps for cap in required_caps):
                # Check if agent is not busy
                if agent_id not in self.active_tasks:
                    return agent_id
                    
        return None
    
    def execute_task_with_hermes(self, task: dict, agent_id: str) -> dict:
        """Execute task using Hermes Agent sub-process"""
        agent_config = self.agents[agent_id]
        
        self.log(f"Executing task '{task['title']}' with agent '{agent_id}'")
        
        # Prepare the prompt for Hermes
        system_prompt = agent_config['system_prompt']
        task_prompt = f"""
# TASK ASSIGNMENT

Title: {task['title']}
Description: {task['description']}
Priority: {task.get('priority', 'normal')}

## Your Mission
{task.get('instructions', 'Complete this task to the best of your ability.')}

## Context
Company: {self.company_name}
Your Role: {agent_config['name']}

## Deliverables
{task.get('deliverables', '- Complete the task\n- Report results')}

## Working Directory
All work should be done in: {os.getcwd()}

When complete, write results to: ./tasks/completed/{task['id']}_result.json

Start working now.
"""

        # Create a script that will run Hermes with this task
        task_script = f"""#!/bin/bash
export HERMES_QUIET_MODE=1
export HERMES_MAX_ITERATIONS=50

cd {os.getcwd()}

# Run Hermes with the task
hermes-agent --system "{system_prompt}" --prompt "{task_prompt}" --output ./tasks/in-progress/{task['id']}_output.txt

# Mark as completed
echo '{{"status": "completed", "completed_at": "{datetime.now().isoformat()}"}}' > ./tasks/completed/{task['id']}_result.json
"""
        
        script_path = f"./tasks/in-progress/{task['id']}_run.sh"
        with open(script_path, "w") as f:
            f.write(task_script)
        os.chmod(script_path, 0o755)
        
        # Execute the task in background
        try:
            process = subprocess.Popen(
                ["bash", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            return {
                "task_id": task['id'],
                "agent_id": agent_id,
                "process": process,
                "started_at": datetime.now().isoformat(),
                "status": "running"
            }
            
        except Exception as e:
            self.log(f"Failed to execute task: {e}", "error")
            return {
                "task_id": task['id'],
                "agent_id": agent_id,
                "status": "failed",
                "error": str(e)
            }
    
    def assign_task(self, task: dict) -> bool:
        """Assign task to appropriate agent"""
        agent_id = self.find_best_agent(task)
        
        if not agent_id:
            self.log(f"No available agent for task '{task['title']}'", "warning")
            return False
        
        # Move task to in-progress
        old_path = Path(task['file_path'])
        new_path = Path(f"./tasks/in-progress/{task['id']}.json")
        
        task['assigned_to'] = agent_id
        task['assigned_at'] = datetime.now().isoformat()
        task['status'] = 'in-progress'
        
        new_path.write_text(json.dumps(task, indent=2))
        old_path.unlink()
        
        # Execute the task
        execution = self.execute_task_with_hermes(task, agent_id)
        self.active_tasks[agent_id] = execution
        
        self.log(f"Task '{task['title']}' assigned to {agent_id}")
        return True
    
    def check_task_completion(self):
        """Check if any running tasks have completed"""
        completed_agents = []
        
        for agent_id, execution in self.active_tasks.items():
            process = execution.get('process')
            
            if process and process.poll() is not None:
                # Process finished
                stdout, stderr = process.communicate()
                
                task_id = execution['task_id']
                
                # Check if result file exists
                result_path = Path(f"./tasks/completed/{task_id}_result.json")
                
                if result_path.exists():
                    self.log(f"Task {task_id} completed by {agent_id}")
                else:
                    self.log(f"Task {task_id} process finished but no result file", "warning")
                
                completed_agents.append(agent_id)
        
        # Remove completed from active
        for agent_id in completed_agents:
            del self.active_tasks[agent_id]
    
    def run_cycle(self):
        """Run one orchestration cycle"""
        self.log("Running orchestration cycle...")
        
        # Check completed tasks
        self.check_task_completion()
        
        # Scan for new tasks
        pending_tasks = self.scan_pending_tasks()
        
        if pending_tasks:
            self.log(f"Found {len(pending_tasks)} pending tasks")
            
            for task in pending_tasks:
                if len(self.active_tasks) >= self.config['orchestrator']['max_concurrent_tasks']:
                    self.log("Max concurrent tasks reached, waiting...")
                    break
                
                self.assign_task(task)
        else:
            self.log("No pending tasks")
    
    def run(self):
        """Main orchestrator loop"""
        self.running = True
        interval = self.config['orchestrator']['heartbeat_interval']
        
        self.log(f"🚀 ARLI Orchestrator started for '{self.company_name}'")
        self.log(f"Monitoring {len(self.agents)} agents")
        self.log(f"Heartbeat interval: {interval}s")
        
        try:
            while self.running:
                self.run_cycle()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.log("Shutting down...")
            self.running = False
    
    def create_task(self, title: str, description: str, 
                   required_capabilities: List[str],
                   priority: str = "normal",
                   deliverables: str = "") -> str:
        """Create a new task"""
        task_id = f"task-{int(time.time() * 1000)}"
        
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "required_capabilities": required_capabilities,
            "priority": priority,
            "deliverables": deliverables,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "created_by": "user"
        }
        
        task_path = Path(f"./tasks/pending/{task_id}.json")
        task_path.write_text(json.dumps(task, indent=2))
        
        self.log(f"Created task: {title}")
        return task_id
    
    def get_status(self) -> dict:
        """Get current orchestrator status"""
        pending = len(list(Path("./tasks/pending").glob("*.json")))
        in_progress = len(list(Path("./tasks/in-progress").glob("*.json")))
        completed = len(list(Path("./tasks/completed").glob("*.json")))
        
        return {
            "company": self.company_name,
            "agents_total": len(self.agents),
            "agents_active": len(self.active_tasks),
            "tasks_pending": pending,
            "tasks_in_progress": in_progress,
            "tasks_completed": completed,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import sys
    
    orchestrator = ARLIOrchestrator()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            status = orchestrator.get_status()
            print(json.dumps(status, indent=2))
        elif sys.argv[1] == "create-task":
            if len(sys.argv) >= 5:
                task_id = orchestrator.create_task(
                    title=sys.argv[2],
                    description=sys.argv[3],
                    required_capabilities=sys.argv[4].split(","),
                    priority=sys.argv[5] if len(sys.argv) > 5 else "normal"
                )
                print(f"Created task: {task_id}")
            else:
                print("Usage: python orchestrator.py create-task 'Title' 'Description' 'cap1,cap2' [priority]")
        elif sys.argv[1] == "run":
            orchestrator.run()
    else:
        # Default: show status
        status = orchestrator.get_status()
        print(json.dumps(status, indent=2))
