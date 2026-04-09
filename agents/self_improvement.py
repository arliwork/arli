#!/usr/bin/env python3
"""
ARLI Self-Improvement System - Phase A4
Agents analyze their own memory to improve future performance

Features:
- Memory Consolidation: merge similar episodes
- Pattern Validation: verify patterns still work
- Automatic Forgetting: remove outdated/irrelevant memory
- Meta-Learning: extract general principles
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

# Import memory components
try:
    from episodic_store import EpisodicStore, Episode
    from semantic_memory import SemanticMemoryStore
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False


@dataclass
class ConsolidationCandidate:
    """Candidate episodes for consolidation"""
    episode_ids: List[str]
    similarity_score: float
    common_context: str
    merged_lessons: List[str]


@dataclass
class PatternValidation:
    """Validation result for a pattern"""
    pattern: str
    times_used: int
    success_count: int
    failure_count: int
    last_used: str
    is_still_valid: bool
    recommendation: str


class MemoryConsolidator:
    """
    Consolidates similar episodes to reduce redundancy
    """
    
    def __init__(self, agent_id: str, memory_path: str = ".arli/memory"):
        self.agent_id = agent_id
        self.memory_path = Path(memory_path)
        self.episodic = EpisodicStore(agent_id, base_path=str(self.memory_path / "agents"))
        
        try:
            self.semantic = SemanticMemoryStore(agent_id, base_path=str(self.memory_path))
        except:
            self.semantic = None
    
    def find_similar_episodes(self, min_similarity: float = 0.7) -> List[ConsolidationCandidate]:
        """
        Find episodes that can be consolidated
        Uses semantic similarity if available, falls back to keyword
        """
        episodes = self.episodic.load_episodes(limit=1000)
        candidates = []
        
        if not episodes:
            return candidates
        
        # Group by task type first
        by_type = defaultdict(list)
        for ep in episodes:
            by_type[ep.task_type].append(ep)
        
        # Find similar within each type
        for task_type, type_episodes in by_type.items():
            if len(type_episodes) < 2:
                continue
            
            # Compare all pairs
            for i, ep1 in enumerate(type_episodes):
                similar_group = [ep1]
                
                for ep2 in type_episodes[i+1:]:
                    similarity = self._calculate_similarity(ep1, ep2)
                    
                    if similarity >= min_similarity:
                        similar_group.append(ep2)
                
                if len(similar_group) >= 2:
                    # Create consolidation candidate
                    all_lessons = []
                    for ep in similar_group:
                        all_lessons.extend(ep.lessons_learned)
                    
                    # Deduplicate lessons
                    unique_lessons = list(set(all_lessons))
                    
                    candidate = ConsolidationCandidate(
                        episode_ids=[ep.episode_id for ep in similar_group],
                        similarity_score=self._calculate_similarity(similar_group[0], similar_group[1]),
                        common_context=task_type,
                        merged_lessons=unique_lessons
                    )
                    
                    # Avoid duplicates
                    if not any(set(c.episode_ids) == set(candidate.episode_ids) for c in candidates):
                        candidates.append(candidate)
        
        return candidates
    
    def _calculate_similarity(self, ep1: Episode, ep2: Episode) -> float:
        """Calculate similarity between two episodes"""
        # Use semantic similarity if available
        if self.semantic:
            # Embed both tasks and compare
            try:
                vec1 = self.semantic.embedder.embed(ep1.task)
                vec2 = self.semantic.embedder.embed(ep2.task)
                return float(np.dot(vec1, vec2))
            except:
                pass
        
        # Fallback: keyword similarity
        words1 = set(ep1.task.lower().split())
        words2 = set(ep2.task.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def consolidate_episodes(self, candidate: ConsolidationCandidate) -> Optional[Dict]:
        """
        Merge similar episodes into one consolidated episode
        """
        # Load all episodes to consolidate
        all_episodes = self.episodic.load_episodes(limit=1000)
        episodes_to_merge = [
            ep for ep in all_episodes 
            if ep.episode_id in candidate.episode_ids
        ]
        
        if len(episodes_to_merge) < 2:
            return None
        
        # Create consolidated episode
        consolidated = {
            "episode_id": f"consolidated_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "task": f"[Consolidated] {episodes_to_merge[0].task} (+{len(episodes_to_merge)-1} similar)",
            "task_type": candidate.common_context,
            "actions": [],  # Simplified
            "result": "success" if all(ep.result == "success" for ep in episodes_to_merge) else "mixed",
            "duration_seconds": sum(ep.duration_seconds for ep in episodes_to_merge),
            "lessons_learned": candidate.merged_lessons,
            "context": {
                "consolidated_from": candidate.episode_ids,
                "consolidation_reason": f"High similarity ({candidate.similarity_score:.2f})",
                "original_count": len(episodes_to_merge)
            }
        }
        
        return consolidated
    
    def run_consolidation(self, dry_run: bool = True) -> Dict:
        """
        Run full consolidation process
        """
        candidates = self.find_similar_episodes(min_similarity=0.7)
        
        results = {
            "candidates_found": len(candidates),
            "episodes_affected": sum(len(c.episode_ids) for c in candidates),
            "consolidations": [],
            "dry_run": dry_run
        }
        
        for candidate in candidates[:5]:  # Limit to top 5
            consolidated = self.consolidate_episodes(candidate)
            
            if consolidated:
                results["consolidations"].append({
                    "new_episode_id": consolidated["episode_id"],
                    "merged_episodes": candidate.episode_ids,
                    "lessons_count": len(consolidated["lessons_learned"])
                })
                
                if not dry_run:
                    # Save consolidated episode
                    from episodic_store import Episode
                    ep = Episode(**consolidated)
                    self.episodic.save_episode(ep)
                    
                    # Mark original episodes as consolidated (don't delete for safety)
                    # In production: move to archive or mark status
        
        return results


class PatternValidator:
    """
    Validates that learned patterns are still effective
    """
    
    def __init__(self, agent_id: str, memory_path: str = ".arli/memory"):
        self.agent_id = agent_id
        self.memory_path = Path(memory_path)
        self.episodic = EpisodicStore(agent_id, base_path=str(self.memory_path / "agents"))
    
    def validate_patterns(self, min_usage: int = 2) -> List[PatternValidation]:
        """
        Check which patterns are actually helping
        """
        # Load all patterns
        patterns = self.episodic.load_patterns("success")
        failures = self.episodic.load_patterns("failure")
        
        # Load all episodes to check usage
        episodes = self.episodic.load_episodes(limit=1000)
        
        validations = []
        
        for pattern in patterns:
            validation = self._validate_single_pattern(pattern, episodes, is_success=True)
            if validation.times_used >= min_usage:
                validations.append(validation)
        
        for pattern in failures:
            validation = self._validate_single_pattern(pattern, episodes, is_success=False)
            if validation.times_used >= min_usage:
                validations.append(validation)
        
        return validations
    
    def _validate_single_pattern(self, pattern: str, episodes: List, is_success: bool) -> PatternValidation:
        """Validate a single pattern against episode history"""
        times_used = 0
        success_count = 0
        failure_count = 0
        last_used = None
        
        pattern_keywords = set(pattern.lower().split())
        
        for ep in episodes:
            # Check if this episode used this pattern
            for lesson in ep.lessons_learned:
                lesson_words = set(lesson.lower().split())
                similarity = len(pattern_keywords & lesson_words) / len(pattern_keywords | lesson_words)
                
                if similarity > 0.5:  # Pattern was used
                    times_used += 1
                    last_used = ep.timestamp
                    
                    if ep.result == "success":
                        success_count += 1
                    else:
                        failure_count += 1
                    break
        
        # Determine if pattern is still valid
        if times_used == 0:
            is_valid = True  # No data, keep it
            recommendation = "Not used yet - monitor"
        elif success_count / times_used > 0.7:
            is_valid = True
            recommendation = "Keep - high success rate"
        elif success_count / times_used < 0.3:
            is_valid = False
            recommendation = "DEPRECATE - consistently fails"
        else:
            is_valid = True
            recommendation = "Review - mixed results"
        
        return PatternValidation(
            pattern=pattern,
            times_used=times_used,
            success_count=success_count,
            failure_count=failure_count,
            last_used=last_used or "never",
            is_still_valid=is_valid,
            recommendation=recommendation
        )
    
    def get_deprecated_patterns(self) -> List[str]:
        """Get patterns that should be removed"""
        validations = self.validate_patterns(min_usage=1)
        return [v.pattern for v in validations if not v.is_still_valid]


class AutoForget:
    """
    Automatically removes outdated/irrelevant memory
    """
    
    def __init__(self, agent_id: str, memory_path: str = ".arli/memory"):
        self.agent_id = agent_id
        self.memory_path = Path(memory_path)
        self.episodic = EpisodicStore(agent_id, base_path=str(self.memory_path / "agents"))
    
    def find_stale_episodes(self, days_threshold: int = 90) -> List[str]:
        """
        Find episodes that haven't been referenced in a while
        """
        episodes = self.episodic.load_episodes(limit=1000)
        stale = []
        
        threshold = datetime.now() - timedelta(days=days_threshold)
        
        for ep in episodes:
            try:
                ep_time = datetime.fromisoformat(ep.timestamp)
                if ep_time < threshold:
                    # Check if this is a failed episode with no lessons
                    if ep.result == "failure" and not ep.lessons_learned:
                        stale.append(ep.episode_id)
            except:
                pass
        
        return stale
    
    def find_redundant_patterns(self) -> List[str]:
        """
        Find patterns that are subsets of other patterns
        """
        patterns = self.episodic.load_patterns("success")
        
        redundant = []
        for i, p1 in enumerate(patterns):
            for p2 in patterns[i+1:]:
                # Check if p1 is subset of p2
                if p1.lower() in p2.lower() and len(p1) < len(p2):
                    redundant.append(p1)
                    break
        
        return redundant
    
    def cleanup_plan(self) -> Dict:
        """
        Generate cleanup plan without executing
        """
        stale = self.find_stale_episodes(days_threshold=90)
        redundant = self.find_redundant_patterns()
        
        return {
            "stale_episodes": stale,
            "stale_count": len(stale),
            "redundant_patterns": redundant,
            "redundant_count": len(redundant),
            "estimated_space_saved": f"{len(stale) * 2 + len(redundant) * 0.5:.1f} KB"
        }


class MetaLearner:
    """
    Extracts general principles from specific episodes
    Learns how to learn better
    """
    
    def __init__(self, agent_id: str, memory_path: str = ".arli/memory"):
        self.agent_id = agent_id
        self.memory_path = Path(memory_path)
        self.episodic = EpisodicStore(agent_id, base_path=str(self.memory_path / "agents"))
    
    def extract_learning_strategies(self) -> List[Dict]:
        """
        Analyze what learning strategies work best
        """
        episodes = self.episodic.load_episodes(limit=1000)
        
        strategies = {
            "quick_iteration": {"success": 0, "total": 0},  # Short episodes
            "thorough_research": {"success": 0, "total": 0},  # Long episodes with many reads
            "experimentation": {"success": 0, "total": 0},  # Many actions
        }
        
        for ep in episodes:
            action_count = len(ep.actions)
            read_count = sum(1 for a in ep.actions if "read" in str(a))
            duration = ep.duration_seconds
            
            # Classify strategy
            if duration < 300:  # < 5 min
                key = "quick_iteration"
            elif read_count > action_count * 0.5:
                key = "thorough_research"
            elif action_count > 10:
                key = "experimentation"
            else:
                continue
            
            strategies[key]["total"] += 1
            if ep.result == "success":
                strategies[key]["success"] += 1
        
        # Calculate effectiveness
        results = []
        for strategy, data in strategies.items():
            if data["total"] > 0:
                success_rate = data["success"] / data["total"]
                results.append({
                    "strategy": strategy,
                    "success_rate": success_rate,
                    "sample_size": data["total"],
                    "recommendation": "Use" if success_rate > 0.7 else "Avoid" if success_rate < 0.3 else "Review"
                })
        
        # Sort by success rate
        results.sort(key=lambda x: x["success_rate"], reverse=True)
        return results
    
    def extract_general_principles(self) -> List[str]:
        """
        Extract general principles from specific lessons
        """
        episodes = self.episodic.load_episodes(limit=1000)
        
        all_lessons = []
        for ep in episodes:
            if ep.result == "success":
                all_lessons.extend(ep.lessons_learned)
        
        # Find common themes
        themes = defaultdict(list)
        
        for lesson in all_lessons:
            lesson_lower = lesson.lower()
            
            # Categorize by keywords
            if any(w in lesson_lower for w in ["test", "validate", "check"]):
                themes["testing"].append(lesson)
            elif any(w in lesson_lower for w in ["security", "auth", "password", "token"]):
                themes["security"].append(lesson)
            elif any(w in lesson_lower for w in ["performance", "speed", "optimize", "cache"]):
                themes["performance"].append(lesson)
            elif any(w in lesson_lower for w in ["error", "exception", "handle", "catch"]):
                themes["error_handling"].append(lesson)
            else:
                themes["general"].append(lesson)
        
        # Extract top principles per theme
        principles = []
        for theme, lessons in themes.items():
            if len(lessons) >= 2:
                principles.append(f"[{theme.upper()}] {lessons[0]}")
        
        return principles
    
    def generate_insights_report(self) -> Dict:
        """
        Generate comprehensive insights about learning
        """
        return {
            "learning_strategies": self.extract_learning_strategies(),
            "general_principles": self.extract_general_principles(),
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        strategies = self.extract_learning_strategies()
        principles = self.extract_general_principles()
        
        recommendations = []
        
        # Strategy recommendations
        for s in strategies:
            if s["success_rate"] > 0.8:
                recommendations.append(f"Use '{s['strategy']}' approach (success: {s['success_rate']:.0%})")
            elif s["success_rate"] < 0.4:
                recommendations.append(f"Avoid '{s['strategy']}' approach (success: {s['success_rate']:.0%})")
        
        # Principle recommendations
        for p in principles[:3]:
            recommendations.append(f"Remember: {p}")
        
        return recommendations


class SelfImprovementEngine:
    """
    Main engine that orchestrates all self-improvement processes
    """
    
    def __init__(self, agent_id: str, workspace: str = "."):
        self.agent_id = agent_id
        self.workspace = Path(workspace)
        self.memory_path = self.workspace / ".arli" / "memory"
        
        self.consolidator = MemoryConsolidator(agent_id, str(self.memory_path))
        self.validator = PatternValidator(agent_id, str(self.memory_path))
        self.auto_forget = AutoForget(agent_id, str(self.memory_path))
        self.meta_learner = MetaLearner(agent_id, str(self.memory_path))
    
    def run_full_analysis(self, dry_run: bool = True) -> Dict:
        """
        Run complete self-improvement analysis
        """
        print(f"\n🧠 Running Self-Improvement Analysis for {self.agent_id}")
        print("=" * 60)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "consolidation": None,
            "pattern_validation": None,
            "cleanup_plan": None,
            "meta_learning": None
        }
        
        # 1. Memory Consolidation
        print("\n📦 1. Memory Consolidation...")
        consolidation = self.consolidator.run_consolidation(dry_run=dry_run)
        results["consolidation"] = consolidation
        print(f"   Found {consolidation['candidates_found']} consolidation candidates")
        print(f"   Can reduce {consolidation['episodes_affected']} episodes to {len(consolidation['consolidations'])} consolidated")
        
        # 2. Pattern Validation
        print("\n✅ 2. Pattern Validation...")
        validations = self.validator.validate_patterns(min_usage=1)
        results["pattern_validation"] = {
            "total_validated": len(validations),
            "valid_patterns": sum(1 for v in validations if v.is_still_valid),
            "deprecated_patterns": [v.pattern[:50] for v in validations if not v.is_still_valid][:5]
        }
        print(f"   Validated {len(validations)} patterns")
        print(f"   {results['pattern_validation']['valid_patterns']} still valid")
        if results["pattern_validation"]["deprecated_patterns"]:
            print(f"   {len(results['pattern_validation']['deprecated_patterns'])} patterns to deprecate")
        
        # 3. Cleanup Plan
        print("\n🧹 3. Cleanup Analysis...")
        cleanup = self.auto_forget.cleanup_plan()
        results["cleanup_plan"] = cleanup
        print(f"   Stale episodes: {cleanup['stale_count']}")
        print(f"   Redundant patterns: {cleanup['redundant_count']}")
        print(f"   Estimated space saved: {cleanup['estimated_space_saved']}")
        
        # 4. Meta-Learning
        print("\n🎯 4. Meta-Learning Insights...")
        insights = self.meta_learner.generate_insights_report()
        results["meta_learning"] = insights
        
        print(f"   Learning strategies analyzed: {len(insights['learning_strategies'])}")
        for s in insights['learning_strategies'][:2]:
            print(f"      • {s['strategy']}: {s['success_rate']:.0%} success ({s['recommendation']})")
        
        print(f"\n   General principles extracted: {len(insights['general_principles'])}")
        for p in insights['general_principles'][:2]:
            print(f"      • {p[:60]}...")
        
        # 5. Recommendations
        print("\n💡 Key Recommendations:")
        for rec in insights['recommendations'][:5]:
            print(f"   • {rec}")
        
        print("\n" + "=" * 60)
        if dry_run:
            print("🔍 DRY RUN - No changes made. Run with dry_run=False to apply.")
        else:
            print("✅ CHANGES APPLIED - Memory optimized!")
        
        return results


# Example usage
if __name__ == "__main__":
    print("🚀 ARLI Self-Improvement System Test")
    print("=" * 60)
    
    engine = SelfImprovementEngine("backend-dev", workspace=".")
    
    # Run analysis
    results = engine.run_full_analysis(dry_run=True)
    
    print("\n✅ Self-Improvement tests complete!")
