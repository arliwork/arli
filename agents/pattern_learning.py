#!/usr/bin/env python3
"""
ARLI Pattern Learning System
Analyzes episodes to extract reusable patterns and anti-patterns
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import Counter


@dataclass
class Pattern:
    """Extracted pattern from episodes"""
    pattern_id: str
    pattern_type: str  # 'success', 'failure', 'workflow'
    context: str  # e.g., 'authentication', 'database', 'api'
    description: str
    frequency: int  # how many times seen
    success_rate: float
    first_seen: str
    last_seen: str
    source_episodes: List[str]  # episode IDs


class PatternLearner:
    """
    Learns patterns from agent episodes
    - Extracts common successful approaches
    - Identifies anti-patterns (things that fail)
    - Builds workflow templates
    """
    
    def __init__(self, agent_id: str, memory_path: str = ".arli/memory"):
        self.agent_id = agent_id
        self.memory_path = Path(memory_path)
        self.patterns_file = self.memory_path / "agents" / agent_id / "extracted_patterns.json"
        self.patterns: List[Pattern] = []
        
        self._load_patterns()
    
    def _load_patterns(self):
        """Load existing patterns"""
        if self.patterns_file.exists():
            try:
                data = json.loads(self.patterns_file.read_text())
                self.patterns = [Pattern(**p) for p in data.get("patterns", [])]
            except:
                self.patterns = []
    
    def _save_patterns(self):
        """Save patterns to disk"""
        self.patterns_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "pattern_type": p.pattern_type,
                    "context": p.context,
                    "description": p.description,
                    "frequency": p.frequency,
                    "success_rate": p.success_rate,
                    "first_seen": p.first_seen,
                    "last_seen": p.last_seen,
                    "source_episodes": p.source_episodes
                }
                for p in self.patterns
            ]
        }
        self.patterns_file.write_text(json.dumps(data, indent=2))
    
    def analyze_episodes(self, episodes: List[Dict]) -> List[Pattern]:
        """
        Analyze episodes and extract patterns
        Returns newly discovered patterns
        """
        new_patterns = []
        
        # Group episodes by task type
        by_type = {}
        for ep in episodes:
            task_type = ep.get("task_type", "general")
            if task_type not in by_type:
                by_type[task_type] = []
            by_type[task_type].append(ep)
        
        # Analyze each task type
        for task_type, type_episodes in by_type.items():
            # Extract lessons patterns
            lessons_patterns = self._extract_lessons_patterns(type_episodes)
            
            # Extract workflow patterns
            workflow_patterns = self._extract_workflow_patterns(type_episodes)
            
            # Extract tool usage patterns
            tool_patterns = self._extract_tool_patterns(type_episodes)
            
            new_patterns.extend(lessons_patterns)
            new_patterns.extend(workflow_patterns)
            new_patterns.extend(tool_patterns)
        
        # Merge with existing patterns
        self._merge_patterns(new_patterns)
        self._save_patterns()
        
        return new_patterns
    
    def _extract_lessons_patterns(self, episodes: List[Dict]) -> List[Pattern]:
        """Extract patterns from lessons learned"""
        patterns = []
        
        # Collect all lessons by similarity
        all_lessons = []
        for ep in episodes:
            for lesson in ep.get("lessons_learned", []):
                all_lessons.append({
                    "lesson": lesson,
                    "success": ep.get("result") == "success",
                    "episode_id": ep.get("episode_id"),
                    "timestamp": ep.get("timestamp"),
                    "task": ep.get("task", "")
                })
        
        # Group similar lessons
        grouped = self._group_similar_lessons(all_lessons)
        
        for group in grouped:
            if len(group) >= 2:  # Need at least 2 occurrences
                description = group[0]["lesson"]
                successes = sum(1 for g in group if g["success"])
                
                pattern = Pattern(
                    pattern_id=f"pat_{len(self.patterns) + len(patterns)}",
                    pattern_type="success" if successes / len(group) > 0.5 else "failure",
                    context=self._extract_context(description),
                    description=description,
                    frequency=len(group),
                    success_rate=successes / len(group),
                    first_seen=min(g["timestamp"] for g in group),
                    last_seen=max(g["timestamp"] for g in group),
                    source_episodes=[g["episode_id"] for g in group]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _extract_workflow_patterns(self, episodes: List[Dict]) -> List[Pattern]:
        """Extract common action sequences"""
        patterns = []
        
        # Extract action sequences
        sequences = []
        for ep in episodes:
            actions = ep.get("actions", [])
            sequence = [a.get("tool") for a in actions if a.get("tool")]
            if len(sequence) >= 2:
                sequences.append({
                    "sequence": " → ".join(sequence),
                    "success": ep.get("result") == "success",
                    "episode_id": ep.get("episode_id"),
                    "timestamp": ep.get("timestamp")
                })
        
        # Find common sequences
        sequence_counts = Counter(s["sequence"] for s in sequences)
        
        for seq, count in sequence_counts.most_common(5):
            if count >= 2:
                seq_episodes = [s for s in sequences if s["sequence"] == seq]
                successes = sum(1 for s in seq_episodes if s["success"])
                
                pattern = Pattern(
                    pattern_id=f"wf_{len(self.patterns) + len(patterns)}",
                    pattern_type="workflow",
                    context="execution_flow",
                    description=f"Common workflow: {seq}",
                    frequency=count,
                    success_rate=successes / len(seq_episodes),
                    first_seen=min(s["timestamp"] for s in seq_episodes),
                    last_seen=max(s["timestamp"] for s in seq_episodes),
                    source_episodes=[s["episode_id"] for s in seq_episodes]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _extract_tool_patterns(self, episodes: List[Dict]) -> List[Pattern]:
        """Extract successful tool combinations"""
        patterns = []
        
        tool_success = {}
        for ep in episodes:
            success = ep.get("result") == "success"
            for action in ep.get("actions", []):
                tool = action.get("tool", "")
                if tool not in tool_success:
                    tool_success[tool] = {"success": 0, "total": 0}
                tool_success[tool]["total"] += 1
                if success:
                    tool_success[tool]["success"] += 1
        
        for tool, stats in tool_success.items():
            if stats["total"] >= 2:
                success_rate = stats["success"] / stats["total"]
                
                pattern = Pattern(
                    pattern_id=f"tool_{len(self.patterns) + len(patterns)}",
                    pattern_type="success" if success_rate > 0.7 else "failure",
                    context="tool_usage",
                    description=f"Tool '{tool}' has {success_rate:.0%} success rate",
                    frequency=stats["total"],
                    success_rate=success_rate,
                    first_seen="",
                    last_seen="",
                    source_episodes=[]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _group_similar_lessons(self, lessons: List[Dict]) -> List[List[Dict]]:
        """Group similar lessons together"""
        groups = []
        used = set()
        
        for i, lesson1 in enumerate(lessons):
            if i in used:
                continue
            
            group = [lesson1]
            used.add(i)
            
            for j, lesson2 in enumerate(lessons[i+1:], start=i+1):
                if j in used:
                    continue
                
                if self._lessons_similar(lesson1["lesson"], lesson2["lesson"]):
                    group.append(lesson2)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _lessons_similar(self, l1: str, l2: str) -> bool:
        """Check if two lessons are similar"""
        # Simple keyword matching
        words1 = set(l1.lower().split())
        words2 = set(l2.lower().split())
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "to", "of", "in", "and", "for"}
        words1 -= stop_words
        words2 -= stop_words
        
        if not words1 or not words2:
            return False
        
        # Jaccard similarity
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) > 0.5
    
    def _extract_context(self, description: str) -> str:
        """Extract context from description"""
        contexts = {
            "auth": ["auth", "login", "password", "jwt", "token"],
            "database": ["database", "db", "sql", "query", "schema"],
            "api": ["api", "endpoint", "rest", "graphql"],
            "frontend": ["react", "component", "ui", "css", "html"],
            "devops": ["deploy", "docker", "ci", "pipeline", "server"],
            "testing": ["test", "jest", "pytest", "spec"]
        }
        
        desc_lower = description.lower()
        for context, keywords in contexts.items():
            if any(kw in desc_lower for kw in keywords):
                return context
        
        return "general"
    
    def _merge_patterns(self, new_patterns: List[Pattern]):
        """Merge new patterns with existing"""
        for new_pat in new_patterns:
            # Check if similar pattern exists
            existing = self._find_similar_pattern(new_pat)
            
            if existing:
                # Update existing
                existing.frequency += new_pat.frequency
                existing.success_rate = (
                    (existing.success_rate * (existing.frequency - new_pat.frequency) +
                     new_pat.success_rate * new_pat.frequency) / existing.frequency
                )
                existing.last_seen = max(existing.last_seen, new_pat.last_seen)
                existing.source_episodes.extend(new_pat.source_episodes)
            else:
                # Add new
                self.patterns.append(new_pat)
    
    def _find_similar_pattern(self, pattern: Pattern) -> Optional[Pattern]:
        """Find similar existing pattern"""
        for existing in self.patterns:
            if (existing.pattern_type == pattern.pattern_type and
                existing.context == pattern.context and
                self._lessons_similar(existing.description, pattern.description)):
                return existing
        return None
    
    def get_patterns_for_context(self, context: str, min_confidence: float = 0.6) -> List[Pattern]:
        """Get patterns relevant to a context"""
        relevant = [
            p for p in self.patterns
            if p.context == context or context in p.description.lower()
        ]
        
        # Sort by success rate and frequency
        relevant.sort(key=lambda p: (p.success_rate, p.frequency), reverse=True)
        
        return [p for p in relevant if p.success_rate >= min_confidence]
    
    def get_recommendations(self, task: str, task_type: str) -> List[str]:
        """Get pattern-based recommendations for a task"""
        recommendations = []
        
        # Extract context from task
        context = self._extract_context(task)
        
        # Get patterns for this context
        patterns = self.get_patterns_for_context(context)
        
        # Get patterns for this task type
        type_patterns = [p for p in self.patterns if p.context == task_type]
        
        all_patterns = patterns + type_patterns
        
        for pattern in all_patterns[:5]:  # Top 5
            icon = "✅" if pattern.pattern_type == "success" else "⚠️"
            recommendations.append(f"{icon} {pattern.description}")
        
        return recommendations
    
    def get_stats(self) -> Dict:
        """Get learning statistics"""
        return {
            "total_patterns": len(self.patterns),
            "success_patterns": len([p for p in self.patterns if p.pattern_type == "success"]),
            "failure_patterns": len([p for p in self.patterns if p.pattern_type == "failure"]),
            "workflow_patterns": len([p for p in self.patterns if p.pattern_type == "workflow"]),
            "contexts": list(set(p.context for p in self.patterns)),
            "avg_success_rate": sum(p.success_rate for p in self.patterns) / len(self.patterns) if self.patterns else 0
        }


# Example usage
if __name__ == "__main__":
    print("🧠 ARLI Pattern Learning System Test")
    print("=" * 60)
    
    learner = PatternLearner("backend-dev")
    
    # Simulate episodes
    episodes = [
        {
            "episode_id": "ep1",
            "task_type": "coding",
            "result": "success",
            "timestamp": "2026-04-09T10:00:00",
            "lessons_learned": ["Always use bcrypt for passwords", "Add rate limiting"],
            "actions": [{"tool": "read_file"}, {"tool": "write_file"}]
        },
        {
            "episode_id": "ep2",
            "task_type": "coding",
            "result": "success",
            "timestamp": "2026-04-09T11:00:00",
            "lessons_learned": ["Use bcrypt for password hashing", "Validate input"],
            "actions": [{"tool": "read_file"}, {"tool": "write_file"}]
        },
        {
            "episode_id": "ep3",
            "task_type": "coding",
            "result": "failure",
            "timestamp": "2026-04-09T12:00:00",
            "lessons_learned": ["Never store passwords in plain text"],
            "actions": [{"tool": "write_file"}, {"tool": "shell"}]
        }
    ]
    
    print("\n1. Analyzing episodes...")
    new_patterns = learner.analyze_episodes(episodes)
    print(f"   Extracted {len(new_patterns)} new patterns")
    
    print("\n2. Extracted patterns:")
    for pat in new_patterns[:3]:
        print(f"   • [{pat.pattern_type.upper()}] {pat.description[:60]}...")
        print(f"     Frequency: {pat.frequency}, Success: {pat.success_rate:.0%}")
    
    print("\n3. Recommendations for auth task:")
    recs = learner.get_recommendations("Build authentication", "coding")
    for rec in recs:
        print(f"   {rec}")
    
    print("\n4. Learning stats:")
    stats = learner.get_stats()
    print(f"   Total patterns: {stats['total_patterns']}")
    print(f"   Success patterns: {stats['success_patterns']}")
    print(f"   Avg success rate: {stats['avg_success_rate']:.0%}")
    
    print("\n✅ Pattern Learning tests complete!")
