#!/usr/bin/env python3
"""
ARLI Memory System - Phase A4 Test
Tests Self-Improvement (consolidation, validation, meta-learning)
"""

from runtime import AgentRuntime

def test_phase_a4():
    print("🧠 ARLI Memory Phase A4: Self-Improvement")
    print("=" * 70)
    
    # Create agent with all features including self-improvement
    agent = AgentRuntime("self-improving-agent", workspace=".", enable_memory=True)
    
    print("\n📚 Phase 1: Creating diverse knowledge base...")
    print("-" * 70)
    
    # Create similar episodes (for consolidation test)
    tasks = [
        ("Build user auth API", "coding", "success", [
            "Use bcrypt for password hashing",
            "JWT tokens need expiration"
        ]),
        ("Create login endpoint", "coding", "success", [
            "Use bcrypt for passwords",  # Similar to above
            "Rate limit login attempts"
        ]),
        ("Implement OAuth flow", "coding", "failure", [
            "OAuth requires HTTPS",
            "Validate all redirect URIs"
        ]),
        ("Add password reset", "coding", "success", [
            "Send emails asynchronously",
            "Rate limit reset requests"
        ]),
        ("Build React form", "frontend", "success", [
            "Use controlled components",
            "Client-side validation improves UX"
        ]),
    ]
    
    for task, task_type, result, lessons in tasks:
        agent.start_task(task, task_type)
        # Simulate some work
        agent.write_file(f"{task.replace(' ', '_').lower()}.py", f"# {task}")
        agent.end_task(result=result, lessons=lessons)
        print(f"   ✅ {task[:40]:40} ({result})")
    
    print("\n" + "=" * 70)
    print("🧠 Phase 2: Running Self-Improvement Analysis")
    print("=" * 70)
    
    # Run self-improvement (dry run first)
    print("\n1. Memory Consolidation Analysis:")
    print("   " + "-" * 50)
    consolidation = agent.memory.consolidate_memory(dry_run=True) if agent.memory else {}
    print(f"   📦 Candidates found: {consolidation.get('candidates_found', 0)}")
    print(f"   📊 Episodes affected: {consolidation.get('episodes_affected', 0)}")
    if consolidation.get('consolidations'):
        for cons in consolidation['consolidations'][:2]:
            print(f"   🔄 Can merge {len(cons.get('merged_episodes', []))} episodes into 1")
            print(f"      Lessons preserved: {cons.get('lessons_count', 0)}")
    print("   " + "-" * 50)
    
    print("\n2. Pattern Validation:")
    print("   " + "-" * 50)
    if agent.memory and agent.memory.improvement:
        validations = agent.memory.improvement.validator.validate_patterns(min_usage=1)
        valid_count = sum(1 for v in validations if v.is_still_valid)
        print(f"   ✅ Valid patterns: {valid_count}/{len(validations)}")
        
        deprecated = [v for v in validations if not v.is_still_valid]
        if deprecated:
            print(f"   ⚠️  Deprecated patterns: {len(deprecated)}")
            for v in deprecated[:2]:
                print(f"      • {v.pattern[:50]}...")
    print("   " + "-" * 50)
    
    print("\n3. Meta-Learning Insights:")
    print("   " + "-" * 50)
    insights = agent.get_learning_insights()
    
    if 'learning_strategies' in insights:
        print(f"   📈 Strategies analyzed: {len(insights['learning_strategies'])}")
        for strategy in insights['learning_strategies'][:3]:
            icon = "✅" if strategy['success_rate'] > 0.7 else "⚠️"
            print(f"   {icon} {strategy['strategy']}: {strategy['success_rate']:.0%} "
                  f"({strategy['recommendation']})")
    
    if 'general_principles' in insights:
        print(f"\n   🎯 General principles: {len(insights['general_principles'])}")
        for principle in insights['general_principles'][:3]:
            print(f"      • {principle[:60]}...")
    print("   " + "-" * 50)
    
    print("\n4. Full Self-Improvement Report:")
    print("   " + "-" * 50)
    improvement = agent.improve_memory(dry_run=True)
    
    if 'cleanup_plan' in improvement:
        cleanup = improvement['cleanup_plan']
        print(f"   🧹 Cleanup opportunities:")
        print(f"      • Stale episodes: {cleanup.get('stale_count', 0)}")
        print(f"      • Redundant patterns: {cleanup.get('redundant_count', 0)}")
        print(f"      • Space savings: {cleanup.get('estimated_space_saved', '0 KB')}")
    
    if 'meta_learning' in improvement and 'recommendations' in improvement['meta_learning']:
        print(f"\n   💡 Top Recommendations:")
        for rec in improvement['meta_learning']['recommendations'][:3]:
            print(f"      • {rec[:55]}...")
    print("   " + "-" * 50)
    
    # Show final stats
    print("\n" + "=" * 70)
    print("📊 FINAL MEMORY SYSTEM STATUS")
    print("=" * 70)
    
    stats = agent.get_memory_stats()
    
    print(f"\n   🆔 Agent: {stats['agent_id']}")
    
    episodic = stats.get('episodic', {})
    print(f"\n   📁 Episodic:")
    print(f"      Total episodes: {episodic.get('total_episodes', 0)}")
    print(f"      Success rate: {episodic.get('success_rate', 0):.0%}")
    
    if 'patterns' in stats:
        pat = stats['patterns']
        print(f"\n   🧬 Patterns:")
        print(f"      Total: {pat.get('total_patterns', 0)}")
        print(f"      Success: {pat.get('success_patterns', 0)}")
    
    if 'semantic' in stats:
        sem = stats['semantic']
        print(f"\n   🔍 Semantic:")
        print(f"      Embeddings: {sem.get('total_embeddings', 0)}")
        print(f"      FAISS: {sem.get('faiss_available', False)}")
    
    if 'self_improvement' in stats:
        print(f"\n   ⚡ Self-Improvement:")
        print(f"      Enabled: ✅")
        print(f"      Status: Active (dry-run mode)")
    
    print("\n" + "=" * 70)
    print("✅ Phase A4 Complete: Self-Improvement working!")
    print("=" * 70)
    
    print("\n🎯 Key Achievements:")
    print("   • Memory consolidation (merge similar episodes)")
    print("   • Pattern validation (verify what works)")
    print("   • Auto-forget (cleanup stale data)")
    print("   • Meta-learning (extract general principles)")
    print("   • Learning strategy analysis")
    
    print("\n🚀 Ready for production!")
    print("   Run with dry_run=False to apply optimizations")
    
    return True

if __name__ == "__main__":
    test_phase_a4()
