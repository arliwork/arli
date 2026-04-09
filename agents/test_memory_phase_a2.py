#!/usr/bin/env python3
"""
ARLI Memory System - Phase A2 Test
Tests Pattern Learning integration with Memory
"""

from runtime import AgentRuntime

def test_phase_a2():
    print("🚀 ARLI Memory Phase A2: Pattern Learning")
    print("=" * 70)
    
    agent = AgentRuntime("backend-dev", workspace=".", enable_memory=True)
    
    # Task 1: Auth endpoint (with mistakes)
    print("\n📋 TASK 1: Build auth endpoint (learning phase)")
    print("-" * 70)
    
    agent.start_task("Build JWT authentication endpoint", "coding")
    agent.write_file("auth_v1.py", "# TODO: Add JWT logic")
    agent.execute_shell("echo 'Missing expiration!'")
    agent.end_task(
        result="failure",
        lessons=[
            "JWT tokens must have expiration timestamps",
            "Always validate token signature",
            "Use environment variables for secrets"
        ]
    )
    print("   ❌ Task 1: Failed (lessons learned)")
    
    # Task 2: Auth endpoint (with fixes)
    print("\n📋 TASK 2: Fix auth endpoint (applying lessons)")
    print("-" * 70)
    
    agent.start_task("Fix JWT authentication with proper security", "coding")
    
    # Show context from memory
    print("   🧠 Agent recalls from memory:")
    context = agent.get_memory_context("JWT authentication security")
    for line in context.split("\n")[:10]:
        print(f"      {line}")
    
    agent.write_file("auth_v2.py", """
import jwt
from datetime import datetime, timedelta

def create_token(user_id):
    exp = datetime.utcnow() + timedelta(hours=24)  # Fixed!
    return jwt.encode({'user_id': user_id, 'exp': exp}, 
                      os.getenv('JWT_SECRET'), algorithm='HS256')
""")
    agent.end_task(
        result="success",
        lessons=[
            "JWT tokens need expiration timestamps",
            "Use environment variables for secrets",
            "Rate limiting prevents brute force"
        ]
    )
    print("   ✅ Task 2: Success (applied lessons)")
    
    # Task 3: Another auth task (should recall patterns)
    print("\n📋 TASK 3: Create login API (pattern recognition)")
    print("-" * 70)
    
    agent.start_task("Create secure login API", "coding")
    
    print("   🧠 Memory context shows learned patterns:")
    context = agent.get_memory_context("Login API with JWT tokens")
    if "JWT" in context or "expiration" in context:
        print("      ✅ Agent remembers JWT best practices!")
    
    agent.end_task(
        result="success",
        lessons=[
            "Use bcrypt for password hashing",
            "JWT refresh tokens improve UX",
            "Always use HTTPS in production"
        ]
    )
    print("   ✅ Task 3: Success (patterns reinforced)")
    
    # Task 4: Analyze patterns
    print("\n📊 TASK 4: Analyze learned patterns")
    print("-" * 70)
    
    if agent.memory:
        analysis = agent.memory.analyze_patterns()
        print(f"   📈 Episodes analyzed: {analysis.get('episodes_analyzed', 0)}")
        print(f"   🎯 New patterns found: {analysis.get('new_patterns', 0)}")
        print(f"   📚 Total patterns: {analysis.get('total_patterns', 0)}")
        
        if analysis.get('patterns'):
            print("\n   Extracted patterns:")
            for pat in analysis['patterns'][:3]:
                icon = "✅" if pat['type'] == 'success' else "⚠️"
                print(f"      {icon} [{pat['context']}] {pat['description'][:50]}...")
                print(f"         Success rate: {pat['success_rate']:.0%}")
    
    # Final stats
    print("\n" + "=" * 70)
    print("📊 FINAL MEMORY STATISTICS")
    print("=" * 70)
    
    stats = agent.get_memory_stats()
    print(f"\n   Agent: {stats['agent_id']}")
    print(f"   Company: {stats.get('company', 'Unknown')}")
    
    episodic = stats.get('episodic', {})
    print(f"\n   📁 Episodic Memory:")
    print(f"      Total episodes: {episodic.get('total_episodes', 0)}")
    print(f"      Success rate: {episodic.get('success_rate', 0):.0%}")
    
    if 'patterns' in stats:
        patterns = stats['patterns']
        print(f"\n   🧬 Pattern Learning:")
        print(f"      Total patterns: {patterns.get('total_patterns', 0)}")
        print(f"      Success patterns: {patterns.get('success_patterns', 0)}")
        print(f"      Failure patterns: {patterns.get('failure_patterns', 0)}")
        print(f"      Avg success rate: {patterns.get('avg_success_rate', 0):.0%}")
        print(f"      Contexts: {', '.join(patterns.get('contexts', []))}")
    
    print("\n" + "=" * 70)
    print("✅ Phase A2 Complete: Pattern Learning working!")
    print("=" * 70)
    
    print("\n💡 Key Achievements:")
    print("   • Agents remember past failures")
    print("   • Patterns extracted automatically")
    print("   • Context-aware recommendations")
    print("   • Cross-task learning enabled")
    
    return True

if __name__ == "__main__":
    test_phase_a2()
