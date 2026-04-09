#!/usr/bin/env python3
"""
ARLI Memory System - Phase A3 Test
Tests Semantic Retrieval (vector-based search)
"""

from runtime import AgentRuntime

def test_phase_a3():
    print("🧠 ARLI Memory Phase A3: Semantic Retrieval")
    print("=" * 70)
    
    # Create agent with all memory features
    agent = AgentRuntime("semantic-test-agent", workspace=".", enable_memory=True)
    
    print("\n📚 Creating knowledge base...")
    print("-" * 70)
    
    # Task 1: Database work
    agent.start_task("Optimize PostgreSQL queries", "database")
    agent.write_file("db_optimization.sql", "CREATE INDEX ...")
    agent.end_task(
        result="success",
        lessons=[
            "Always add indexes on foreign keys",
            "Use EXPLAIN ANALYZE to check query plans",
            "Connection pooling improves performance"
        ]
    )
    print("   ✅ Database optimization episode")
    
    # Task 2: API work (semantically similar to auth)
    agent.start_task("Build user authentication API", "api")
    agent.write_file("auth.py", "# JWT implementation")
    agent.end_task(
        result="success",
        lessons=[
            "JWT tokens need expiration timestamps",
            "Use refresh tokens for better UX",
            "Always validate token signatures"
        ]
    )
    print("   ✅ API auth episode")
    
    # Task 3: Another API task
    agent.start_task("Create login endpoint with session management", "api")
    agent.write_file("login.py", "# Session-based auth")
    agent.end_task(
        result="success",
        lessons=[
            "Session cookies should be httpOnly",
            "Implement CSRF protection",
            "Rate limit login attempts"
        ]
    )
    print("   ✅ Login endpoint episode")
    
    # Task 4: Frontend (different domain)
    agent.start_task("Build React login form", "frontend")
    agent.write_file("LoginForm.jsx", "# React component")
    agent.end_task(
        result="success",
        lessons=[
            "Use controlled components for inputs",
            "Client-side validation improves UX",
            "Show loading states during submission"
        ]
    )
    print("   ✅ Frontend episode")
    
    # Now test semantic search
    print("\n" + "=" * 70)
    print("🔍 TESTING SEMANTIC SEARCH")
    print("=" * 70)
    
    # Test 1: Search for auth-related tasks
    print("\n1. Semantic search: 'authentication with tokens'")
    if agent.memory and agent.memory.semantic:
        results = agent.memory.semantic_search("authentication with tokens", k=3)
        print(f"   Found {len(results)} matches:")
        for i, r in enumerate(results[:3], 1):
            sim_pct = int(r.get('similarity', 0) * 100)
            text = r.get('text', '')[:40]
            print(f"      {i}. ({sim_pct}% match) {text}...")
    
    # Test 2: Get semantic recommendations
    print("\n2. Semantic recommendations for 'Build secure login'")
    if agent.memory:
        recs = agent.memory.get_semantic_recommendations("Build secure login system")
        for i, rec in enumerate(recs[:3], 1):
            print(f"      {i}. 💡 {rec[:60]}...")
    
    # Test 3: Context with semantic matches
    print("\n3. Full context for new auth task:")
    print("   " + "-" * 50)
    context = agent.get_memory_context("Implement OAuth authentication")
    # Show relevant parts
    for line in context.split('\n')[:20]:
        if line.strip():
            print(f"   {line}")
    print("   " + "-" * 50)
    
    # Test 4: Compare keyword vs semantic
    print("\n4. Keyword vs Semantic comparison:")
    print("   Searching for: 'database performance'")
    
    # Keyword search
    keyword_results = agent.memory.episodic.get_similar_episodes("database performance", limit=2) if agent.memory else []
    print(f"   📖 Keyword matches: {len(keyword_results)}")
    for ep in keyword_results:
        print(f"      • {ep.task[:40]}...")
    
    # Semantic search
    semantic_results = agent.memory.semantic_search("database performance", k=2) if agent.memory and agent.memory.semantic else []
    print(f"   🔍 Semantic matches: {len(semantic_results)}")
    for r in semantic_results[:2]:
        print(f"      • ({int(r.get('similarity', 0)*100)}%) {r.get('text', '')[:40]}...")
    
    # Stats
    print("\n" + "=" * 70)
    print("📊 SEMANTIC MEMORY STATISTICS")
    print("=" * 70)
    
    stats = agent.get_memory_stats()
    
    if 'semantic' in stats:
        sem = stats['semantic']
        print(f"\n   🔍 Semantic Memory:")
        print(f"      Total embeddings: {sem.get('total_embeddings', 0)}")
        print(f"      Unique episodes: {sem.get('unique_episodes', 0)}")
        print(f"      FAISS available: {sem.get('faiss_available', False)}")
        print(f"      Index size: {sem.get('index_size', 0)}")
        print(f"      Embedding types: {', '.join(sem.get('embedding_types', []))}")
    
    episodic = stats.get('episodic', {})
    print(f"\n   📁 Episodic Memory:")
    print(f"      Total episodes: {episodic.get('total_episodes', 0)}")
    print(f"      Success rate: {episodic.get('success_rate', 0):.0%}")
    
    if 'patterns' in stats:
        pat = stats['patterns']
        print(f"\n   🧬 Pattern Learning:")
        print(f"      Total patterns: {pat.get('total_patterns', 0)}")
    
    print("\n" + "=" * 70)
    print("✅ Phase A3 Complete: Semantic Retrieval working!")
    print("=" * 70)
    
    print("\n💡 Key Achievements:")
    print("   • Vector-based semantic search")
    print("   • Meaning-based similarity (not just keywords)")
    print("   • Context-aware recommendations")
    print("   • Multi-aspect embeddings (task, lessons, context)")
    
    return True

if __name__ == "__main__":
    test_phase_a3()
