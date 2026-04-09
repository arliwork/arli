#!/usr/bin/env python3
"""
ARLI Episodic Memory Store
Handles persistent storage of agent episodes (tasks) in JSONL format
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class Episode:
    """Single agent episode (task execution)"""
    episode_id: str
    timestamp: str
    agent_id: str
    task: str
    task_type: str  # 'coding', 'research', 'planning', 'debugging', etc.
    actions: List[Dict[str, Any]]
    result: str  # 'success', 'failure', 'partial'
    duration_seconds: int
    lessons_learned: List[str]
    context: Dict[str, Any]  # company context, files touched, etc.
    
    @classmethod
    def create(cls, agent_id: str, task: str, task_type: str = "general") -> "Episode":
        """Create new episode with auto-generated ID"""
        import uuid
        return cls(
            episode_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            task=task,
            task_type=task_type,
            actions=[],
            result="pending",
            duration_seconds=0,
            lessons_learned=[],
            context={}
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Episode":
        """Create Episode from dictionary"""
        return cls(**data)


class EpisodicStore:
    """JSONL-based episodic memory storage for agents"""
    
    def __init__(self, agent_id: str, base_path: str = ".arli/memory/agents"):
        self.agent_id = agent_id
        self.base_path = Path(base_path)
        self.episodes_path = self.base_path / agent_id / "episodes.jsonl"
        self.patterns_path = self.base_path / agent_id / "patterns.json"
        self.state_path = self.base_path / agent_id / "state.json"
        
        # Ensure directories exist
        self.episodes_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create files if don't exist
        if not self.episodes_path.exists():
            self.episodes_path.touch()
        if not self.patterns_path.exists():
            self.patterns_path.write_text(json.dumps({"patterns": [], "failures": []}, indent=2))
        if not self.state_path.exists():
            self._save_state({"total_episodes": 0, "success_rate": 0.0, "last_active": None})
    
    def save_episode(self, episode: Episode) -> bool:
        """Append episode to JSONL file"""
        try:
            with open(self.episodes_path, "a") as f:
                f.write(json.dumps(episode.to_dict(), ensure_ascii=False) + "\n")
            
            # Update state
            self._update_state(episode)
            return True
        except Exception as e:
            print(f"[EpisodicStore] Error saving episode: {e}")
            return False
    
    def load_episodes(self, limit: int = 100, task_type: Optional[str] = None) -> List[Episode]:
        """Load recent episodes, optionally filtered by type"""
        episodes = []
        
        if not self.episodes_path.exists():
            return episodes
        
        try:
            with open(self.episodes_path, "r") as f:
                lines = f.readlines()
            
            # Parse all valid episodes
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    episode = Episode.from_dict(data)
                    
                    # Filter by task type if specified
                    if task_type and episode.task_type != task_type:
                        continue
                    
                    episodes.append(episode)
                except json.JSONDecodeError:
                    continue
            
            # Return most recent first
            episodes.reverse()
            return episodes[:limit]
            
        except Exception as e:
            print(f"[EpisodicStore] Error loading episodes: {e}")
            return []
    
    def get_similar_episodes(self, task: str, limit: int = 5) -> List[Episode]:
        """Find episodes with similar tasks (simple keyword matching)"""
        episodes = self.load_episodes(limit=1000)
        
        # Simple similarity: count matching keywords
        task_keywords = set(task.lower().split())
        scored = []
        
        for ep in episodes:
            ep_keywords = set(ep.task.lower().split())
            score = len(task_keywords & ep_keywords)
            if score > 0:
                scored.append((score, ep))
        
        # Sort by score and return top
        scored.sort(reverse=True, key=lambda x: x[0])
        return [ep for _, ep in scored[:limit]]
    
    def save_pattern(self, pattern: str, pattern_type: str = "success") -> bool:
        """Save learned pattern (success or failure)"""
        try:
            patterns = json.loads(self.patterns_path.read_text())
            
            entry = {
                "pattern": pattern,
                "type": pattern_type,
                "timestamp": datetime.now().isoformat(),
                "agent_id": self.agent_id
            }
            
            if pattern_type == "success":
                patterns["patterns"].append(entry)
            else:
                patterns["failures"].append(entry)
            
            self.patterns_path.write_text(json.dumps(patterns, indent=2))
            return True
        except Exception as e:
            print(f"[EpisodicStore] Error saving pattern: {e}")
            return False
    
    def load_patterns(self, pattern_type: str = "success") -> List[str]:
        """Load learned patterns"""
        try:
            patterns = json.loads(self.patterns_path.read_text())
            key = "patterns" if pattern_type == "success" else "failures"
            return [p["pattern"] for p in patterns.get(key, [])]
        except Exception as e:
            return []
    
    def _load_state(self) -> Dict:
        """Load agent state"""
        try:
            return json.loads(self.state_path.read_text())
        except:
            return {"total_episodes": 0, "success_rate": 0.0, "last_active": None}
    
    def _save_state(self, state: Dict):
        """Save agent state"""
        self.state_path.write_text(json.dumps(state, indent=2))
    
    def _update_state(self, episode: Episode):
        """Update agent state after new episode"""
        state = self._load_state()
        state["total_episodes"] = state.get("total_episodes", 0) + 1
        state["last_active"] = episode.timestamp
        
        # Calculate rolling success rate
        episodes = self.load_episodes(limit=100)
        if episodes:
            successes = sum(1 for ep in episodes if ep.result == "success")
            state["success_rate"] = round(successes / len(episodes), 2)
        
        self._save_state(state)
    
    def get_stats(self) -> Dict:
        """Get agent memory statistics"""
        state = self._load_state()
        episodes = self.load_episodes(limit=1000)
        
        task_types = {}
        for ep in episodes:
            task_types[ep.task_type] = task_types.get(ep.task_type, 0) + 1
        
        return {
            "agent_id": self.agent_id,
            "total_episodes": state.get("total_episodes", 0),
            "success_rate": state.get("success_rate", 0.0),
            "last_active": state.get("last_active"),
            "task_types": task_types,
            "patterns_learned": len(self.load_patterns("success")),
            "failures_avoided": len(self.load_patterns("failure"))
        }


class SharedMemoryStore:
    """Shared memory across all agents in a company"""
    
    def __init__(self, company_id: str = "default", base_path: str = ".arli/memory/shared"):
        self.company_id = company_id
        self.base_path = Path(base_path)
        self.knowledge_path = self.base_path / "knowledge_base.jsonl"
        self.failures_path = self.base_path / "failures.jsonl"
        self.success_patterns_path = self.base_path / "success_patterns.json"
        
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        for path in [self.knowledge_path, self.failures_path]:
            if not path.exists():
                path.touch()
        
        if not self.success_patterns_path.exists():
            self.success_patterns_path.write_text(json.dumps({"patterns": []}, indent=2))
    
    def add_knowledge(self, topic: str, content: str, source_agent: str) -> bool:
        """Add knowledge to shared knowledge base"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "content": content,
            "source_agent": source_agent
        }
        
        try:
            with open(self.knowledge_path, "a") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return True
        except Exception as e:
            print(f"[SharedMemoryStore] Error adding knowledge: {e}")
            return False
    
    def get_knowledge(self, topic: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get knowledge, optionally filtered by topic"""
        entries = []
        
        if not self.knowledge_path.exists():
            return entries
        
        try:
            with open(self.knowledge_path, "r") as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if topic and topic.lower() not in entry.get("topic", "").lower():
                        continue
                    entries.append(entry)
                except:
                    continue
            
            return entries[-limit:]  # Most recent
        except Exception as e:
            return []
    
    def log_failure(self, task: str, error: str, agent_id: str) -> bool:
        """Log failure for all agents to learn from"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "error": error,
            "agent_id": agent_id
        }
        
        try:
            with open(self.failures_path, "a") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return True
        except:
            return False
    
    def get_common_failures(self, limit: int = 10) -> List[Dict]:
        """Get recent common failures"""
        failures = []
        
        if not self.failures_path.exists():
            return failures
        
        try:
            with open(self.failures_path, "r") as f:
                lines = f.readlines()
            
            for line in lines[-limit:]:
                line = line.strip()
                if line:
                    try:
                        failures.append(json.loads(line))
                    except:
                        continue
            
            return failures
        except:
            return []


# Example usage
if __name__ == "__main__":
    print("🧠 ARLI Episodic Store Test")
    print("=" * 50)
    
    # Test episodic store
    store = EpisodicStore("backend-dev")
    
    # Create and save episode
    ep = Episode.create("backend-dev", "Fix authentication bug", "debugging")
    ep.actions = [
        {"tool": "search_files", "input": "auth", "output": "found 3 matches"},
        {"tool": "read_file", "input": "auth.py", "output": "file content"},
        {"tool": "patch_file", "input": "fix bug", "output": "success"}
    ]
    ep.result = "success"
    ep.duration_seconds = 300
    ep.lessons_learned = ["Always check token expiration", "Add logging to auth failures"]
    
    store.save_episode(ep)
    
    # Load episodes
    episodes = store.load_episodes(limit=5)
    print(f"\n1. Saved and loaded {len(episodes)} episodes")
    
    # Save pattern
    store.save_pattern("Use JWT with refresh tokens", "success")
    patterns = store.load_patterns("success")
    print(f"2. Saved and loaded {len(patterns)} patterns")
    
    # Get stats
    stats = store.get_stats()
    print(f"3. Agent stats: {stats}")
    
    # Test shared memory
    shared = SharedMemoryStore()
    shared.add_knowledge("React Best Practices", "Use functional components with hooks", "frontend-dev")
    knowledge = shared.get_knowledge(limit=5)
    print(f"4. Shared knowledge entries: {len(knowledge)}")
    
    print("\n✅ Episodic Store tests complete!")
