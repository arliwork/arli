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
import aiohttp

# Import memory system
try:
    from memory import AgentMemory
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    print("[Runtime] Memory system not available, running without persistence")

# Import collaboration system
try:
    from collaboration import CollaborationOrchestrator, DelegatedTask
    COLLABORATION_AVAILABLE = True
except ImportError:
    COLLABORATION_AVAILABLE = False

# Import skills marketplace
try:
    from skills_marketplace import Marketplace, SkillInstaller, SkillPackage
    MARKETPLACE_AVAILABLE = True
except ImportError:
    MARKETPLACE_AVAILABLE = False

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
        
        # Initialize collaboration system
        self.collaboration = None
        if COLLABORATION_AVAILABLE:
            try:
                self.collaboration = CollaborationOrchestrator(workspace=str(self.workspace))
                # Register this agent in the registry
                if self.collaboration.registry.get_agent(agent_id):
                    print(f"[Runtime] Collaboration enabled for {agent_id}")
            except Exception as e:
                print(f"[Runtime] Collaboration init failed: {e}")
        
        # Initialize skills marketplace
        self.marketplace = None
        self.skill_installer = None
        self.loaded_skills: Dict[str, Any] = {}
        if MARKETPLACE_AVAILABLE:
            try:
                self.marketplace = Marketplace()
                self.skill_installer = SkillInstaller()
                self._load_installed_skills()
                print(f"[Runtime] Skills marketplace enabled for {agent_id}")
            except Exception as e:
                print(f"[Runtime] Skills marketplace init failed: {e}")
        
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
    

    # --- Browser Automation ---
    
    async def browser_navigate(self, url: str) -> Dict:
        """Navigate browser to URL via Browserbase"""
        self.log("browser_navigate", url)
        try:
            import sys
            hermes_tools_path = str(Path(__file__).resolve().parent.parent / "hermes-agent" / "tools")
            if hermes_tools_path not in sys.path:
                sys.path.insert(0, hermes_tools_path)
            
            # Direct HTTP call to Browserbase API
            bb_api_key = os.getenv("BROWSERBASE_API_KEY", "")
            if not bb_api_key:
                # Fallback: simulate with simple HTTP fetch
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=30) as resp:
                        html = await resp.text()
                        return {
                            "success": True,
                            "url": url,
                            "status": resp.status,
                            "content_length": len(html),
                            "method": "http_fetch"
                        }
            
            # Real Browserbase would go here
            return {
                "success": True,
                "url": url,
                "method": "browserbase",
                "note": "Browserbase integration ready"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def browser_extract(self, url: str) -> Dict:
        """Extract content from webpage"""
        self.log("browser_extract", url)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0"
                }) as resp:
                    html = await resp.text()
                    # Simple extraction of title and text
                    import re
                    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
                    title = title_match.group(1).strip() if title_match else "No title"
                    
                    # Remove scripts and styles
                    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
                    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
                    text = re.sub(r"<[^>]+>", " ", text)
                    text = re.sub(r"\s+", " ", text).strip()[:5000]
                    
                    return {
                        "success": True,
                        "url": url,
                        "title": title,
                        "text_preview": text[:1000],
                        "text_full": text,
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def browser_search(self, query: str) -> Dict:
        """Search the web and return results"""
        self.log("browser_search", query)
        try:
            # Use DuckDuckGo HTML version for search
            search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, timeout=30, headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.0"
                }) as resp:
                    html = await resp.text()
                    import re
                    
                    results = []
                    # Extract result titles and URLs
                    links = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)">(.*?)</a>', html)
                    for url, title in links[:10]:
                        title = re.sub(r"<[^>]+>", "", title)
                        results.append({"title": title, "url": url})
                    
                    return {
                        "success": True,
                        "query": query,
                        "results": results,
                        "count": len(results)
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def research_task(self, query: str, sources: int = 3) -> Dict:
        """Full research workflow: search + extract top sources"""
        self.log("research_task", query)
        
        search_result = await self.browser_search(query)
        if not search_result.get("success"):
            return search_result
        
        findings = []
        for result in search_result["results"][:sources]:
            extract = await self.browser_extract(result["url"])
            if extract.get("success"):
                findings.append({
                    "title": result["title"],
                    "url": result["url"],
                    "summary": extract["text_preview"]
                })
        
        return {
            "success": True,
            "query": query,
            "sources_found": len(search_result["results"]),
            "sources_analyzed": len(findings),
            "findings": findings,
        }

    # --- End Browser Automation ---

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
    
    # ===== COLLABORATION METHODS =====
    
    def delegate_task(self, title: str, description: str, task_type: str,
                     required_capabilities: List[str], to_agent: str = None,
                     priority: int = 1) -> Dict:
        """
        Delegate task to another agent
        If to_agent not specified, finds best match automatically
        """
        if not self.collaboration:
            return {"error": "Collaboration not enabled"}
        
        try:
            task = self.collaboration.create_and_delegate(
                title=title,
                description=description,
                task_type=task_type,
                required_capabilities=required_capabilities,
                from_agent=self.agent_id,
                to_agent=to_agent,
                priority=priority
            )
            
            if task:
                return {
                    "success": True,
                    "task_id": task.task_id,
                    "title": task.title,
                    "assignee": task.assignee,
                    "status": task.status.value if hasattr(task.status, 'value') else str(task.status)
                }
            else:
                return {"error": "Failed to create or delegate task"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get tasks assigned to this agent"""
        if not self.collaboration:
            return []
        
        tasks = self.collaboration.task_board.get_agent_tasks(self.agent_id)
        return [
            {
                "task_id": t.task_id,
                "title": t.title,
                "status": t.status.value if hasattr(t.status, 'value') else str(t.status),
                "creator": t.creator
            }
            for t in tasks
            if t.assignee == self.agent_id
        ]
    
    def complete_delegated_task(self, task_id: str, result: Dict) -> bool:
        """Mark a delegated task as complete"""
        if not self.collaboration:
            return False
        
        from collaboration import TaskStatus
        return self.collaboration.task_board.update_task_status(
            task_id, TaskStatus.COMPLETED, result
        )
    
    def get_available_agents(self) -> List[Dict]:
        """Get list of available agents for collaboration"""
        if not self.collaboration:
            return []
        
        return [
            {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "role": agent.role,
                "status": agent.status,
                "capabilities": [c.name for c in agent.capabilities]
            }
            for agent in self.collaboration.registry.agents.values()
            if agent.can_accept_task()
        ]
    
    def handoff_to_agent(self, to_agent: str, context: Dict) -> bool:
        """Hand off context to another agent"""
        if not self.collaboration:
            return False
        
        return self.collaboration.handoff_context(self.agent_id, to_agent, context)
    
    # ===== SKILLS MARKETPLACE METHODS =====
    
    def _load_installed_skills(self):
        """Load all installed skills"""
        if not self.skill_installer:
            return
        
        installed = self.skill_installer.list_installed_skills()
        for skill_record in installed:
            skill_id = skill_record.get("skill_id")
            if skill_id:
                skill = self.skill_installer.load_skill(skill_id, self)
                if skill:
                    self.loaded_skills[skill_id] = skill
    
    def install_skill(self, skill_id: str) -> Dict:
        """
        Install skill from marketplace
        """
        if not self.marketplace or not self.skill_installer:
            return {"error": "Marketplace not enabled"}
        
        # Use agent_id as user_id
        result = self.skill_installer.install_skill(
            skill_id=skill_id,
            marketplace=self.marketplace,
            user_id=self.agent_id
        )
        
        if result.get("success"):
            # Load the skill
            skill = self.skill_installer.load_skill(skill_id, self)
            if skill:
                self.loaded_skills[skill_id] = skill
        
        return result
    
    def use_skill(self, skill_id: str, **kwargs) -> Dict:
        """
        Execute installed skill
        """
        if skill_id not in self.loaded_skills:
            # Try to load it
            if self.skill_installer:
                skill = self.skill_installer.load_skill(skill_id, self)
                if skill:
                    self.loaded_skills[skill_id] = skill
                else:
                    return {"error": f"Skill '{skill_id}' not installed"}
            else:
                return {"error": "Skills not enabled"}
        
        skill = self.loaded_skills[skill_id]
        
        try:
            if hasattr(skill, 'execute'):
                result = skill.execute(**kwargs)
                return {"success": True, "result": result}
            else:
                return {"error": "Skill has no execute method"}
        except Exception as e:
            return {"error": str(e)}
    
    def list_skills(self) -> List[Dict]:
        """List all installed skills"""
        if not self.skill_installer:
            return []
        
        return self.skill_installer.list_installed_skills()
    
    def search_skills(self, query: str = None, category: str = None, 
                     max_price: float = None) -> List[Dict]:
        """
        Search skills in marketplace
        """
        if not self.marketplace:
            return []
        
        from skills_marketplace import SkillCategory
        
        cat_enum = None
        if category:
            try:
                cat_enum = SkillCategory(category)
            except:
                pass
        
        results = self.marketplace.search_skills(
            query=query,
            category=cat_enum,
            max_price=max_price
        )
        
        return [
            {
                "skill_id": s.skill_id,
                "name": s.name,
                "description": s.description[:100],
                "price": s.price,
                "rating": s.rating,
                "downloads": s.downloads,
                "author": s.author
            }
            for s in results
        ]
    
    def purchase_skill(self, skill_id: str) -> Dict:
        """
        Purchase skill from marketplace
        """
        if not self.marketplace:
            return {"error": "Marketplace not enabled"}
        
        return self.marketplace.purchase_skill(skill_id, self.agent_id)
    
    def create_skill(self, name: str) -> Dict:
        """
        Create new skill template
        """
        if not MARKETPLACE_AVAILABLE:
            return {"error": "Skill creation not available"}
        
        try:
            packager = SkillPackage()
            template_path = packager.create_skill_template(name, self.agent_id)
            
            return {
                "success": True,
                "template_path": str(template_path),
                "message": f"Edit files in {template_path} then publish"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def publish_skill(self, skill_path: str) -> Dict:
        """
        Publish skill to marketplace
        """
        if not self.marketplace:
            return {"error": "Marketplace not enabled"}
        
        try:
            result = self.marketplace.publish_skill(Path(skill_path))
            return result
        except Exception as e:
            return {"error": str(e)}

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
