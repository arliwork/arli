#!/usr/bin/env python3
"""
ARLI Agent Memory System
Unified memory management for autonomous agents

Features:
- Episodic memory (task history)
- Semantic memory (knowledge base)  
- Procedural memory (learned patterns)
- Company context (shared knowledge)
- Context injection for prompts
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from episodic_store import EpisodicStore, SharedMemoryStore, Episode

try:
    from pattern_learning import PatternLearner
    PATTERN_LEARNING_AVAILABLE = True
except ImportError:
    PATTERN_LEARNING_AVAILABLE = False

try:
    from semantic_memory import SemanticMemoryStore
    SEMANTIC_MEMORY_AVAILABLE = True
except ImportError:
    SEMANTIC_MEMORY_AVAILABLE = False

try:
    from self_improvement import SelfImprovementEngine
    SELF_IMPROVEMENT_AVAILABLE = True
except ImportError:
    SELF_IMPROVEMENT_AVAILABLE = False


class AgentMemory:
    """
    Unified memory system for ARLI agents
    
    Combines:
    - Short-term: Current session context
    - Long-term: Past episodes and learned patterns  
    - Shared: Company-wide knowledge and failures
    """
    
    def __init__(self, agent_id: str, company_id: str = "default", workspace: str = "."):
        self.agent_id = agent_id
        self.company_id = company_id
        self.workspace = Path(workspace)
        
        # Memory stores
        self.episodic = EpisodicStore(agent_id, base_path=str(self.workspace / ".arli" / "memory" / "agents"))
        self.shared = SharedMemoryStore(company_id, base_path=str(self.workspace / ".arli" / "memory" / "shared"))
        
        # Pattern learner
        self.learner = None
        if PATTERN_LEARNING_AVAILABLE:
            try:
                self.learner = PatternLearner(agent_id, memory_path=str(self.workspace / ".arli" / "memory"))
            except Exception as e:
                print(f"[AgentMemory] Pattern learner init failed: {e}")
        
        # Semantic memory
        self.semantic = None
        if SEMANTIC_MEMORY_AVAILABLE:
            try:
                self.semantic = SemanticMemoryStore(
                    agent_id,
                    base_path=str(self.workspace / ".arli" / "memory")
                )
                print(f"[AgentMemory] Semantic memory enabled for {agent_id}")
            except Exception as e:
                print(f"[AgentMemory] Semantic memory init failed: {e}")
        
        # Self-improvement engine
        self.improvement = None
        if SELF_IMPROVEMENT_AVAILABLE:
            try:
                self.improvement = SelfImprovementEngine(
                    agent_id,
                    workspace=str(self.workspace)
                )
                print(f"[AgentMemory] Self-improvement enabled for {agent_id}")
            except Exception as e:
                print(f"[AgentMemory] Self-improvement init failed: {e}")
        
        # Company context
        self.company_context = self._load_company_context()
        
        # Current episode (if any)
        self.current_episode: Optional[Episode] = None
        
        # Session context (short-term memory)
        self.session_context: Dict[str, Any] = {}
        
    def _load_company_context(self) -> Dict[str, Any]:
        """Load company context from COMPANY.md and config"""
        context = {
            "company_name": "Unknown",
            "company_type": "general",
            "agents": [],
            "workflows": [],
            "recent_projects": []
        }
        
        # Try to load COMPANY.md
        company_md = self.workspace / "COMPANY.md"
        if company_md.exists():
            content = company_md.read_text()
            # Parse basic info
            for line in content.split("\n"):
                if line.startswith("**Name:**"):
                    context["company_name"] = line.replace("**Name:**", "").strip()
                elif line.startswith("**Type:**"):
                    context["company_type"] = line.replace("**Type:**", "").strip()
        
        # Try to load config
        config_yaml = self.workspace / ".arli" / "config.yaml"
        if config_yaml.exists():
            try:
                import yaml
                config = yaml.safe_load(config_yaml.read_text())
                if config and "company" in config:
                    context["company_name"] = config["company"].get("name", context["company_name"])
                if config and "agents" in config:
                    context["agents"] = list(config["agents"].keys())
            except:
                pass
        
        return context
    
    def start_episode(self, task: str, task_type: str = "general") -> Episode:
        """Start a new episode for tracking"""
        self.current_episode = Episode.create(self.agent_id, task, task_type)
        self.session_context["current_task"] = task
        self.session_context["start_time"] = datetime.now().isoformat()
        return self.current_episode
    
    def record_action(self, tool: str, input_data: str, output_data: str, success: bool = True):
        """Record an action in the current episode"""
        if self.current_episode:
            self.current_episode.actions.append({
                "timestamp": datetime.now().isoformat(),
                "tool": tool,
                "input": input_data[:200],  # Truncate for storage
                "output": output_data[:500],  # Truncate for storage
                "success": success
            })
    
    def end_episode(self, result: str, lessons: List[str] = None, duration: int = 0):
        """End current episode and save to memory"""
        if not self.current_episode:
            return
        
        self.current_episode.result = result
        self.current_episode.lessons_learned = lessons or []
        
        # Calculate duration if not provided
        if duration == 0 and "start_time" in self.session_context:
            try:
                start = datetime.fromisoformat(self.session_context["start_time"])
                self.current_episode.duration_seconds = int((datetime.now() - start).total_seconds())
            except:
                pass
        else:
            self.current_episode.duration_seconds = duration
        
        # Add company context
        self.current_episode.context = {
            "company": self.company_context.get("company_name"),
            "workspace": str(self.workspace),
            "files_touched": self.session_context.get("files_touched", [])
        }
        
        # Save episode
        self.episodic.save_episode(self.current_episode)
        
        # Add to semantic memory
        if self.semantic:
            self.semantic.add_episode(self.current_episode.to_dict())
        
        # Extract and save patterns from lessons
        for lesson in (lessons or []):
            if result == "success":
                self.episodic.save_pattern(lesson, "success")
            else:
                self.episodic.save_pattern(lesson, "failure")
        
        # Share failures with all agents
        if result == "failure" and lessons:
            self.shared.log_failure(
                self.current_episode.task,
                lessons[0],
                self.agent_id
            )
        
        # Clear current episode
        episode = self.current_episode
        self.current_episode = None
        self.session_context = {}
        
        return episode
    
    def get_relevant_context(self, task: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get relevant memory context for a new task
        Returns structured context for prompt injection
        Uses both keyword and semantic search
        """
        context = {
            "company": self.company_context,
            "similar_episodes": [],
            "semantic_matches": [],
            "learned_patterns": [],
            "common_failures": [],
            "shared_knowledge": []
        }
        
        # Try semantic search first (more accurate)
        if self.semantic:
            semantic_context = self.semantic.get_contextual_memory(task)
            context["semantic_matches"] = semantic_context.get("similar_tasks", [])[:limit]
            context["relevant_lessons"] = semantic_context.get("relevant_lessons", [])[:limit]
        
        # Fallback to keyword search
        similar = self.episodic.get_similar_episodes(task, limit=limit)
        context["similar_episodes"] = [
            {
                "task": ep.task,
                "result": ep.result,
                "lessons": ep.lessons_learned,
                "duration": ep.duration_seconds
            }
            for ep in similar
        ]
        
        # Load learned patterns
        patterns = self.episodic.load_patterns("success")
        context["learned_patterns"] = patterns[-limit:]
        
        # Load failures to avoid
        failures = self.shared.get_common_failures(limit=3)
        context["common_failures"] = [
            {"task": f["task"], "error": f["error"]} 
            for f in failures
        ]
        
        # Load relevant shared knowledge
        # Extract keywords from task
        keywords = task.lower().split()
        all_knowledge = self.shared.get_knowledge(limit=50)
        relevant = [
            k for k in all_knowledge 
            if any(kw in k.get("topic", "").lower() for kw in keywords)
        ]
        context["shared_knowledge"] = relevant[:limit]
        
        return context
    
    def format_context_for_prompt(self, task: str) -> str:
        """
        Format memory context as string for system prompt injection
        Includes semantic search results
        """
        ctx = self.get_relevant_context(task)
        
        lines = [
            "## 📚 Your Memory Context",
            "",
            f"**Company:** {ctx['company'].get('company_name', 'Unknown')}",
            f"**Type:** {ctx['company'].get('company_type', 'general')}",
            ""
        ]
        
        # Pattern-based recommendations
        if self.learner:
            recs = self.learner.get_recommendations(task, "general")
            if recs:
                lines.append("### 🎓 AI Recommendations:")
                for rec in recs[:3]:
                    lines.append(f"{rec}")
                lines.append("")
        
        # Semantic matches (most relevant)
        if ctx.get("semantic_matches"):
            lines.append("### 🔍 Semantically Similar Tasks:")
            for i, match in enumerate(ctx["semantic_matches"][:3], 1):
                sim_pct = int(match.get('similarity', 0) * 100)
                result_icon = "✅" if match.get('result') == 'success' else "❌"
                lines.append(f"{i}. {result_icon} ({sim_pct}% match) {match.get('description', '')[:50]}...")
            lines.append("")
        
        # Relevant lessons from semantic search
        if ctx.get("relevant_lessons"):
            lines.append("### 💡 Relevant Lessons:")
            for lesson in ctx["relevant_lessons"][:3]:
                lines.append(f"• {lesson[:100]}")
            lines.append("")
        
        # Similar past tasks (keyword-based fallback)
        if ctx["similar_episodes"]:
            lines.append("### 📖 Similar Past Tasks:")
            for i, ep in enumerate(ctx["similar_episodes"][:2], 1):
                status = "✅" if ep["result"] == "success" else "❌"
                lines.append(f"{i}. {status} {ep['task'][:50]}...")
                if ep["lessons"]:
                    lines.append(f"   💡 {ep['lessons'][0][:60]}")
            lines.append("")
        
        # Learned patterns
        if ctx["learned_patterns"]:
            lines.append("### 🎯 Patterns You Know:")
            for pattern in ctx["learned_patterns"][:3]:
                lines.append(f"• {pattern[:100]}")
            lines.append("")
        
        # Failures to avoid
        if ctx["common_failures"]:
            lines.append("### ⚠️ Avoid These Mistakes:")
            for f in ctx["common_failures"][:2]:
                lines.append(f"• {f['error'][:60]}...")
            lines.append("")
        
        # Shared knowledge
        if ctx["shared_knowledge"]:
            lines.append("### 👥 Team Knowledge:")
            for k in ctx["shared_knowledge"][:2]:
                lines.append(f"• {k['topic']}: {k['content'][:60]}...")
            lines.append("")
        
        lines.append("---")
        return "\n".join(lines)
    
    def share_knowledge(self, topic: str, content: str) -> bool:
        """Share knowledge with all company agents"""
        return self.shared.add_knowledge(topic, content, self.agent_id)
    
    def analyze_patterns(self) -> Dict:
        """Analyze all episodes and extract patterns"""
        if not self.learner:
            return {"error": "Pattern learner not available"}
        
        episodes = self.episodic.load_episodes(limit=1000)
        episodes_dict = [ep.to_dict() for ep in episodes]
        
        new_patterns = self.learner.analyze_episodes(episodes_dict)
        
        return {
            "episodes_analyzed": len(episodes_dict),
            "new_patterns": len(new_patterns),
            "total_patterns": len(self.learner.patterns),
            "patterns": [
                {
                    "type": p.pattern_type,
                    "context": p.context,
                    "description": p.description[:80],
                    "success_rate": p.success_rate
                }
                for p in new_patterns[:5]
            ]
        }
    
    def semantic_search(self, query: str, k: int = 5) -> List[Dict]:
        """Search semantic memory for relevant episodes"""
        if not self.semantic:
            return []
        return self.semantic.search(query, k=k)
    
    def get_semantic_recommendations(self, task: str) -> List[str]:
        """Get recommendations based on semantic similarity"""
        if not self.semantic:
            return []
        return self.semantic.get_similar_lessons(task, k=5)
    
    def run_self_improvement(self, dry_run: bool = True) -> Dict:
        """
        Run full self-improvement analysis
        Consolidates memory, validates patterns, extracts insights
        """
        if not self.improvement:
            return {"error": "Self-improvement engine not available"}
        
        return self.improvement.run_full_analysis(dry_run=dry_run)
    
    def get_learning_insights(self) -> Dict:
        """Get meta-learning insights"""
        if not self.improvement:
            return {"error": "Self-improvement not available"}
        
        return self.improvement.meta_learner.generate_insights_report()
    
    def consolidate_memory(self, dry_run: bool = True) -> Dict:
        """Consolidate similar episodes"""
        if not self.improvement:
            return {"error": "Self-improvement not available"}
        
        return self.improvement.consolidator.run_consolidation(dry_run=dry_run)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        stats = {
            "agent_id": self.agent_id,
            "company": self.company_context.get("company_name"),
            "episodic": self.episodic.get_stats(),
            "current_episode": self.current_episode is not None
        }
        
        if self.learner:
            stats["patterns"] = self.learner.get_stats()
        
        if self.semantic:
            stats["semantic"] = self.semantic.get_stats()
        
        if self.improvement:
            stats["self_improvement"] = {"enabled": True}
        
        return stats
    
    def remember_file(self, file_path: str):
        """Track that agent touched a file"""
        if "files_touched" not in self.session_context:
            self.session_context["files_touched"] = []
        self.session_context["files_touched"].append(file_path)


class MemoryEnhancedRuntime:
    """
    Wrapper that adds memory to AgentRuntime
    This will be integrated into the main runtime
    """
    
    def __init__(self, runtime, memory: AgentMemory):
        self.runtime = runtime
        self.memory = memory
        self._wrap_methods()
    
    def _wrap_methods(self):
        """Wrap runtime methods to track in memory"""
        # Store original methods
        self._original_execute_shell = self.runtime.execute_shell
        self._original_write_file = self.runtime.write_file
        self._original_read_file = self.runtime.read_file
        self._original_search_files = self.runtime.search_files
        self._original_patch_file = self.runtime.patch_file
        
        # Wrap with memory tracking
        self.runtime.execute_shell = self._track_shell
        self.runtime.write_file = self._track_write
        self.runtime.read_file = self._track_read
        self.runtime.search_files = self._track_search
        self.runtime.patch_file = self._track_patch
    
    def _track_shell(self, command: str, timeout: int = 300):
        result = self._original_execute_shell(command, timeout)
        self.memory.record_action(
            "shell",
            command[:100],
            result.get("stdout", "")[:200] if result.get("success") else result.get("error", "")[:200],
            result.get("success", False)
        )
        return result
    
    def _track_write(self, path: str, content: str):
        result = self._original_write_file(path, content)
        if result.get("success"):
            self.memory.remember_file(path)
        self.memory.record_action("write_file", path, f"{result.get('bytes_written', 0)} bytes", result.get("success"))
        return result
    
    def _track_read(self, path: str):
        result = self._original_read_file(path)
        self.memory.record_action("read_file", path, f"{result.get('size', 0)} bytes", result.get("success"))
        return result
    
    def _track_search(self, pattern: str, path: str = "."):
        result = self._original_search_files(pattern, path)
        matches = result.get("count", 0)
        self.memory.record_action("search_files", f"'{pattern}' in {path}", f"{matches} matches", result.get("success"))
        return result
    
    def _track_patch(self, path: str, old_string: str, new_string: str):
        result = self._original_patch_file(path, old_string, new_string)
        if result.get("success"):
            self.memory.remember_file(path)
        self.memory.record_action("patch_file", path, f"{result.get('replacements', 0)} changes", result.get("success"))
        return result


# Example usage
if __name__ == "__main__":
    print("🧠 ARLI Agent Memory System Test")
    print("=" * 50)
    
    # Create memory for backend-dev agent
    memory = AgentMemory("backend-dev", workspace="~/arli")
    
    # Start an episode
    print("\n1. Starting episode...")
    episode = memory.start_episode("Implement user authentication API", "coding")
    print(f"   Episode ID: {episode.episode_id}")
    
    # Simulate some actions
    memory.record_action("read_file", "auth.py", "file content here", True)
    memory.record_action("search_files", "JWT", "3 matches", True)
    memory.record_action("write_file", "auth_new.py", "500 bytes", True)
    memory.remember_file("auth_new.py")
    
    # End episode
    print("\n2. Ending episode...")
    memory.end_episode(
        result="success",
        lessons=["Use bcrypt for password hashing", "Add rate limiting to auth endpoints"],
        duration=1800
    )
    
    # Get context for new task
    print("\n3. Getting context for similar task...")
    context = memory.format_context_for_prompt("Create login API with JWT")
    print(context[:800] + "...")
    
    # Share knowledge
    print("\n4. Sharing knowledge...")
    memory.share_knowledge("JWT Best Practices", "Always validate expiration, use secure cookies")
    
    # Get stats
    print("\n5. Memory stats:")
    stats = memory.get_stats()
    print(f"   Total episodes: {stats['episodic']['total_episodes']}")
    print(f"   Success rate: {stats['episodic']['success_rate']}")
    
    print("\n✅ Memory system tests complete!")
