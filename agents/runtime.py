#!/usr/bin/env python3
"""
ARLI Agent Runtime - Real Task Execution
This module allows agents to execute actual work using Hermes tools
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class AgentRuntime:
    """Runtime environment for autonomous agents"""
    
    def __init__(self, agent_id: str, workspace: str = "."):
        self.agent_id = agent_id
        self.workspace = Path(workspace).resolve()
        self.session_id = f"{agent_id}-{int(datetime.now().timestamp())}"
        self.logs = []
        
    def log(self, action: str, details: str):
        """Log agent action"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
            "action": action,
            "details": details
        }
        self.logs.append(entry)
        
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
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
                "stdout": "",
                "stderr": ""
            }
        except Exception as e:
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
            
            return {
                "success": True,
                "path": str(file_path),
                "bytes_written": len(content)
            }
            
        except Exception as e:
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
                return {
                    "success": False,
                    "error": f"File not found: {path}"
                }
            
            content = file_path.read_text()
            
            return {
                "success": True,
                "path": str(file_path),
                "content": content,
                "size": len(content)
            }
            
        except Exception as e:
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
            
            return {
                "success": True,
                "matches": result.stdout.split("\n") if result.stdout else [],
                "count": len([l for l in result.stdout.split("\n") if l.strip()])
            }
            
        except Exception as e:
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
                return {
                    "success": False,
                    "error": f"File not found: {path}"
                }
            
            content = file_path.read_text()
            
            if old_string not in content:
                return {
                    "success": False,
                    "error": "Old string not found in file"
                }
            
            new_content = content.replace(old_string, new_string, 1)
            file_path.write_text(new_content)
            
            return {
                "success": True,
                "path": str(file_path),
                "replacements": 1
            }
            
        except Exception as e:
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
    
    def report_result(self, task_id: str, result: Dict):
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
        
        return report

# Example usage and testing
if __name__ == "__main__":
    print("🚀 ARLI Agent Runtime Test")
    print("=" * 50)
    
    runtime = AgentRuntime("test-agent", ".")
    
    # Test 1: Execute shell
    print("\n1. Testing shell execution...")
    result = runtime.execute_shell("echo 'Hello from ARLI Agent Runtime!'")
    print(f"Success: {result['success']}")
    print(f"Output: {result['stdout'].strip()}")
    
    # Test 2: Write file
    print("\n2. Testing file write...")
    result = runtime.write_file("test_output.txt", "This file was created by an ARLI agent!")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Written to: {result['path']}")
    
    # Test 3: Read file
    print("\n3. Testing file read...")
    result = runtime.read_file("test_output.txt")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Content: {result['content']}")
    
    # Test 4: Search
    print("\n4. Testing file search...")
    result = runtime.search_files("AgentRuntime", ".")
    print(f"Success: {result['success']}")
    print(f"Found {result.get('count', 0)} matches")
    
    print("\n✅ Runtime tests complete!")
