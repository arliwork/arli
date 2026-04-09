#!/usr/bin/env python3
"""
ARLI Agent Runtime - Real Task Execution
This module allows agents to execute actual work using Hermes tools
Now with integrated Memory System!
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Import memory system
try:
    from memory import AgentMemory
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    print("[Runtime] Memory system not available, running without persistence")

class AgentRuntime:
    """Runtime environment for autonomous agents with memory"""
    
    def __init__(self, agent_id: str, workspace: str = ".", enable_memory: bool = True):
        self.agent_id = agent_id
        self.workspace = Path(workspace).resolve()
        self.session_id = f"{agent_id}-{int(datetime.now().timestamp())}"
        self.logs = []
        
        # Initialize memory system
        self.memory = None
        if enable_memory and MEMORY_AVAILABLE:
            try:
                self.memory = AgentMemory(agent_id, workspace=str(self.workspace))
                print(f"[Runtime] Memory enabled for {agent_id}")
            except Exception as e:
                print(f"[Runtime] Memory init failed: {e}")
                self.memory = None
        
    def log(self, action: str, details: str):
        """Log agent action"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
            "action": action,
            "details": details
        }
        self.logs.append(entry)
        
        # Also log to memory system
        if self.memory and self.memory.current_episode:
            self.memory.record_action(action, details, "", True)
    
    def start_task(self, task: str, task_type: str = "general") -> Dict:
        """Start a new task with memory tracking"""
        if self.memory:
            episode = self.memory.start_episode(task, task_type)
            self.log("task_start", f"{task_type}: {task[:80]}")
            return {"success": True, "episode_id": episode.episode_id}
        return {"success": False, "error": "Memory not available"}
    
    def end_task(self, result: str, lessons: List[str] = None) -> Dict:
        """End current task and save to memory"""
        if self.memory and self.memory.current_episode:
            episode = self.memory.end_episode(result, lessons or [])
            self.log("task_end", f"Result: {result}, Lessons: {len(lessons or [])}")
            return {
                "success": True,
                "episode_id": episode.episode_id,
                "duration": episode.duration_seconds
            }
        return {"success": False, "error": "No active episode"}
    
    def get_memory_context(self, task: str) -> str:
        """Get relevant memory context for a task"""
        if self.memory:
            return self.memory.format_context_for_prompt(task)
        return ""
    
    def share_knowledge(self, topic: str, content: str) -> Dict:
        """Share knowledge with all agents"""
        if self.memory:
            success = self.memory.share_knowledge(topic, content)
            return {"success": success}
        return {"success": False, "error": "Memory not available"}
        
    def execute_shell(self, command: str, timeout: int = 300) -> Dict:
        """Execute shell command safely"""
        self.log("shell_execute", command)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            
            # Track in memory
            if self.memory:
                output = result.stdout[:200] if success else result.stderr[:200]
                self.memory.record_action("shell", command[:100], output, success)
            
            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            if self.memory:
                self.memory.record_action("shell", command[:100], f"Timeout after {timeout}s", False)
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
                "stdout": "",
                "stderr": ""
            }
        except Exception as e:
            if self.memory:
                self.memory.record_action("shell", command[:100], str(e)[:100], False)
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    def write_file(self, path: str, content: str) -> Dict:
        """Write file to workspace"""
        self.log("file_write", path)
        
        try:
            file_path = self.workspace / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            
            # Track in memory
            if self.memory:
                self.memory.remember_file(path)
                self.memory.record_action("write_file", path, f"{len(content)} bytes", True)
            
            return {
                "success": True,
                "path": str(file_path),
                "bytes_written": len(content)
            }
            
        except Exception as e:
            if self.memory:
                self.memory.record_action("write_file", path, str(e), False)
            return {
                "success": False,
                "error": str(e)
            }
    
    def read_file(self, path: str) -> Dict:
        """Read file from workspace"""
        self.log("file_read", path)
        
        try:
            file_path = self.workspace / path
            
            if not file_path.exists():
                if self.memory:
                    self.memory.record_action("read_file", path, "File not found", False)
                return {
                    "success": False,
                    "error": f"File not found: {path}"
                }
            
            content = file_path.read_text()
            
            # Track in memory
            if self.memory:
                self.memory.record_action("read_file", path, f"{len(content)} bytes", True)
            
            return {
                "success": True,
                "path": str(file_path),
                "content": content,
                "size": len(content)
            }
            
        except Exception as e:
            if self.memory:
                self.memory.record_action("read_file", path, str(e), False)
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_files(self, pattern: str, path: str = ".") -> Dict:
        """Search files using grep/ripgrep"""
        self.log("file_search", f"{pattern} in {path}")
        
        try:
            search_path = self.workspace / path
            
            # Try ripgrep first, fall back to grep
            if subprocess.run(["which", "rg"], capture_output=True).returncode == 0:
                cmd = f"rg -n '{pattern}' {search_path}"
            else:
                cmd = f"grep -r -n '{pattern}' {search_path}"
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )
            
            matches = result.stdout.split("\n") if result.stdout else []
            count = len([l for l in matches if l.strip()])
            
            # Track in memory
            if self.memory:
                self.memory.record_action("search_files", f"'{pattern}' in {path}", f"{count} matches", True)
            
            return {
                "success": True,
                "matches": matches,
                "count": count
            }
            
        except Exception as e:
            if self.memory:
                self.memory.record_action("search_files", f"'{pattern}' in {path}", str(e), False)
            return {
                "success": False,
                "error": str(e)
            }
    
    def patch_file(self, path: str, old_string: str, new_string: str) -> Dict:
        """Apply patch to file"""
        self.log("file_patch", path)
        
        try:
            file_path = self.workspace / path
            
            if not file_path.exists():
                if self.memory:
                    self.memory.record_action("patch_file", path, "File not found", False)
                return {
                    "success": False,
                    "error": f"File not found: {path}"
                }
            
            content = file_path.read_text()
            
            if old_string not in content:
                if self.memory:
                    self.memory.record_action("patch_file", path, "Old string not found", False)
                return {
                    "success": False,
                    "error": "Old string not found in file"
                }
            
            new_content = content.replace(old_string, new_string, 1)
            file_path.write_text(new_content)
            
            # Track in memory
            if self.memory:
                self.memory.remember_file(path)
                self.memory.record_action("patch_file", path, "1 replacement", True)
            
            return {
                "success": True,
                "path": str(file_path),
                "replacements": 1
            }
            
        except Exception as e:
            if self.memory:
                self.memory.record_action("patch_file", path, str(e), False)
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_hermes_task(self, task_description: str, system_prompt: str = "") -> Dict:
        """Execute task using Hermes Agent"""
        self.log("hermes_execute", task_description[:100])
        
        try:
            # Create temporary script for Hermes
            script_content = f"""#!/bin/bash
cd {self.workspace}

# Run hermes-agent with the task
hermes-agent --system "{system_prompt}" --prompt "{task_description}" --max-turns 50
"""
            
            script_path = f"/tmp/hermes_task_{self.session_id}.sh"
            with open(script_path, "w") as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)
            
            # Execute
            result = subprocess.run(
                ["bash", script_path],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes max
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Hermes task timed out after 10 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def report_result(self, task_id: str, result: Dict, lessons: List[str] = None):
        """Report task completion"""
        report = {
            "task_id": task_id,
            "agent_id": self.agent_id,
            "completed_at": datetime.now().isoformat(),
            "result": result,
            "logs": self.logs
        }
        
        # Write to completed tasks
        result_path = self.workspace / "tasks" / "completed" / f"{task_id}_result.json"
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(json.dumps(report, indent=2))
        
        # Also save to memory if active episode
        if self.memory and self.memory.current_episode:
            success = "success" if result.get("success") else "failure"
            self.memory.end_episode(success, lessons or [])
        
        return report
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        if self.memory:
            return self.memory.get_stats()
        return {"error": "Memory not enabled"}
    
    def improve_memory(self, dry_run: bool = True) -> Dict:
        """
        Run self-improvement analysis on agent memory
        Consolidates episodes, validates patterns, extracts insights
        """
        if self.memory:
            return self.memory.run_self_improvement(dry_run=dry_run)
        return {"error": "Memory not enabled"}
    
    def get_learning_insights(self) -> Dict:
        """Get meta-learning insights about this agent"""
        if self.memory:
            return self.memory.get_learning_insights()
        return {"error": "Memory not enabled"}

# Example usage and testing
if __name__ == "__main__":
    print("🚀 ARLI Agent Runtime Test")
    print("=" * 50)
    
    runtime = AgentRuntime("test-agent", ".", enable_memory=True)
    
    # Test 1: Start task with memory
    print("\n1. Starting task with memory tracking...")
    result = runtime.start_task("Test file operations", "testing")
    print(f"Episode started: {result.get('episode_id', 'N/A')}")
    
    # Test 2: Execute shell
    print("\n2. Testing shell execution...")
    result = runtime.execute_shell("echo 'Hello from ARLI Agent Runtime!'")
    print(f"Success: {result['success']}")
    print(f"Output: {result['stdout'].strip()}")
    
    # Test 3: Write file
    print("\n3. Testing file write...")
    result = runtime.write_file("test_output.txt", "This file was created by an ARLI agent!")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Written to: {result['path']}")
    
    # Test 4: Read file
    print("\n4. Testing file read...")
    result = runtime.read_file("test_output.txt")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Content: {result['content']}")
    
    # Test 5: Search
    print("\n5. Testing file search...")
    result = runtime.search_files("AgentRuntime", ".")
    print(f"Success: {result['success']}")
    print(f"Found {result.get('count', 0)} matches")
    
    # Test 6: End task and save to memory
    print("\n6. Ending task and saving to memory...")
    result = runtime.end_task(
        result="success",
        lessons=["File operations work correctly", "Memory tracking is functional"]
    )
    print(f"Episode saved: {result.get('episode_id', 'N/A')}")
    print(f"Duration: {result.get('duration', 0)} seconds")
    
    # Test 7: Get memory stats
    print("\n7. Memory statistics:")
    stats = runtime.get_memory_stats()
    print(f"   Agent: {stats.get('agent_id')}")
    print(f"   Total episodes: {stats.get('episodic', {}).get('total_episodes', 0)}")
    print(f"   Success rate: {stats.get('episodic', {}).get('success_rate', 0)}")
    
    # Test 8: Get memory context
    print("\n8. Memory context for similar task:")
    context = runtime.get_memory_context("File operations test")
    print(context[:500] + "..." if len(context) > 500 else context)
    
    print("\n✅ Runtime tests complete!")
