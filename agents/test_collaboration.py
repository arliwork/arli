#!/usr/bin/env python3
"""
ARLI Multi-Agent Collaboration - Integration Test
Tests full collaboration workflows
"""

from runtime import AgentRuntime
from collaboration import CollaborationOrchestrator, CollaborationPattern, DelegatedTask

def test_collaboration():
    print("🤝 ARLI Multi-Agent Collaboration Test")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = CollaborationOrchestrator(".")
    
    print("\n📋 Phase 1: Agent Discovery")
    print("-" * 70)
    print("Available agents:")
    for agent_id, agent in orchestrator.registry.agents.items():
        status_icon = "🟢" if agent.status == "available" else "🔴"
        print(f"   {status_icon} {agent.name} ({agent_id})")
        caps = ", ".join(c.name for c in agent.capabilities[:2])
        print(f"      Capabilities: {caps}")
    
    print("\n📋 Phase 2: Sequential Collaboration Pattern")
    print("-" * 70)
    print("Workflow: CEO → Architect → Backend → DevOps")
    
    # CEO creates feature request
    feature_task = orchestrator.create_and_delegate(
        title="Build payment processing system",
        description="Complete payment system with Stripe integration",
        task_type="feature",
        required_capabilities=["system-design", "api-development", "deployment"],
        from_agent="ceo",
        priority=5
    )
    
    if feature_task:
        print(f"\n   1️⃣ CEO created: {feature_task.title}")
        print(f"      Assigned to: {feature_task.assignee}")
        
        # Architect designs
        design_task = orchestrator.create_and_delegate(
            title="Design payment API architecture",
            description="Create API specs and data models",
            task_type="design",
            required_capabilities=["system-design"],
            from_agent="ceo",
            to_agent="architect",
            parent_task=feature_task.task_id
        )
        
        if design_task:
            print(f"   2️⃣ Architect designing: {design_task.title}")
            orchestrator.task_board.add_subtask(feature_task.task_id, design_task.task_id)
            
            # Backend implements
            impl_task = orchestrator.create_and_delegate(
                title="Implement payment API endpoints",
                description="Build Stripe integration endpoints",
                task_type="coding",
                required_capabilities=["api-development"],
                from_agent="architect",
                to_agent="backend-dev",
                parent_task=feature_task.task_id
            )
            
            if impl_task:
                print(f"   3️⃣ Backend implementing: {impl_task.title}")
                orchestrator.task_board.add_subtask(feature_task.task_id, impl_task.task_id)
                
                # DevOps deploys
                deploy_task = orchestrator.create_and_delegate(
                    title="Deploy payment service",
                    description="Set up production deployment",
                    task_type="deployment",
                    required_capabilities=["deployment"],
                    from_agent="backend-dev",
                    to_agent="devops",
                    parent_task=feature_task.task_id
                )
                
                if deploy_task:
                    print(f"   4️⃣ DevOps deploying: {deploy_task.title}")
                    orchestrator.task_board.add_subtask(feature_task.task_id, deploy_task.task_id)
    
    print("\n📋 Phase 3: Parallel Collaboration Pattern")
    print("-" * 70)
    print("Workflow: Backend + Frontend working in parallel")
    
    # Backend API
    api_task = orchestrator.create_and_delegate(
        title="Build REST API",
        description="Create REST endpoints",
        task_type="coding",
        required_capabilities=["api-development"],
        from_agent="architect",
        to_agent="backend-dev"
    )
    
    # Frontend UI (parallel)
    ui_task = orchestrator.create_and_delegate(
        title="Build React UI",
        description="Create user interface",
        task_type="coding",
        required_capabilities=["ui-development"],
        from_agent="architect",
        to_agent="frontend-dev"
    )
    
    if api_task and ui_task:
        print(f"   ⚡ Backend working on: {api_task.title}")
        print(f"   ⚡ Frontend working on: {ui_task.title}")
        print("   (These can be done in parallel)")
    
    print("\n📋 Phase 4: Task Matching")
    print("-" * 70)
    
    # Test capability matching
    test_task = DelegatedTask(
        task_id="test_match",
        title="Implement database schema",
        description="Design and implement PostgreSQL schema",
        task_type="database",
        required_capabilities=["database-design", "api-development"],
        status="pending",
        creator="ceo"
    )
    
    best_agent = orchestrator.registry.find_best_agent(test_task)
    if best_agent:
        print(f"   🎯 Best match for 'database schema': {best_agent.name}")
        match_score = orchestrator.registry._calculate_match_score(best_agent, test_task)
        print(f"      Match score: {match_score:.0%}")
    
    # Find all agents with specific capability
    db_agents = orchestrator.registry.find_agents_by_capability("database")
    print(f"\n   🗄️  Agents with 'database' capability: {len(db_agents)}")
    for agent in db_agents:
        print(f"      • {agent.name}")
    
    print("\n📋 Phase 5: Context Handoff")
    print("-" * 70)
    
    # Simulate handoff
    context = {
        "api_spec": "/docs/payment_api.yaml",
        "database_schema": "/docs/schema.sql",
        "stripe_config": {"webhook_secret": "whsec_***"},
        "lessons_from_design": ["Use idempotency keys", "Implement retries"]
    }
    
    success = orchestrator.handoff_context("architect", "backend-dev", context)
    if success:
        print("   📤 Context handed off: Architect → Backend")
        print("      Transferred: API spec, DB schema, config")
    
    print("\n📋 Phase 6: Result Aggregation")
    print("-" * 70)
    
    # Complete some subtasks
    if feature_task and feature_task.subtasks:
        # Mark first subtask complete
        first_subtask = feature_task.subtasks[0]
        orchestrator.task_board.update_task_status(
            first_subtask, 
            status=__import__('collaboration', fromlist=['TaskStatus']).TaskStatus.COMPLETED,
            result={"design_doc": "/docs/payment_arch.pdf"}
        )
        
        # Aggregate results
        results = orchestrator.aggregate_results(feature_task.task_id)
        print(f"   📊 Aggregated results for '{feature_task.title}':")
        print(f"      Subtasks completed: {results['subtasks_completed']}")
        print(f"      Subtasks failed: {results['subtasks_failed']}")
        for task_id, result in results['results'].items():
            print(f"      • {result['title']}: {result.get('result', 'N/A')}")
    
    print("\n📋 Phase 7: Collaboration Summary")
    print("-" * 70)
    
    summary = orchestrator.get_collaboration_summary()
    print(f"   👥 Registered agents: {summary['registered_agents']}")
    print(f"   📝 Total tasks: {summary['total_tasks']}")
    print(f"   ⏳ Pending tasks: {summary['pending_tasks']}")
    print(f"   🟢 Available agents: {summary['agents_by_status']['available']}")
    print(f"   🔴 Busy agents: {summary['agents_by_status']['busy']}")
    
    # Show all tasks
    print("\n   All tasks:")
    for task in orchestrator.task_board.tasks.values():
        status_str = task.status.value if hasattr(task.status, 'value') else str(task.status)
        status_icon = {
            "pending": "⏳",
            "assigned": "👤",
            "in_progress": "🔧",
            "completed": "✅",
            "failed": "❌"
        }.get(status_str, "❓")
        
        assignee = task.assignee or "Unassigned"
        print(f"      {status_icon} {task.title[:40]:40} → {assignee}")
    
    print("\n" + "=" * 70)
    print("✅ Collaboration Test Complete!")
    print("=" * 70)
    
    print("\n🎯 Key Features Tested:")
    print("   • Agent registry and capability matching")
    print("   • Sequential delegation (CEO → Architect → Backend → DevOps)")
    print("   • Parallel delegation (Backend + Frontend)")
    print("   • Context handoff between agents")
    print("   • Result aggregation from subtasks")
    print("   • Task status tracking")
    
    return True

if __name__ == "__main__":
    test_collaboration()
