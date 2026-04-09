#!/usr/bin/env python3
"""
ARLI Memory System - Real Usage Example
Shows how backend-dev agent uses memory to learn from past tasks
"""

from runtime import AgentRuntime

def main():
    print("🧠 ARLI Agent Memory - Real World Example")
    print("=" * 60)
    
    # Create backend-dev agent with memory
    agent = AgentRuntime("backend-dev", workspace=".", enable_memory=True)
    
    print("\n📋 Agent: backend-dev")
    print("🎯 Task: Implement user authentication API")
    
    # Task 1: First authentication implementation
    print("\n" + "=" * 60)
    print("TASK 1: Build auth endpoint")
    print("=" * 60)
    
    agent.start_task("Build JWT authentication endpoint", "coding")
    
    # Simulate work
    agent.write_file("auth.py", """
import jwt
from datetime import datetime, timedelta

def create_token(user_id):
    # BUG: No expiration!
    return jwt.encode({'user_id': user_id}, 'secret', algorithm='HS256')
""")
    
    agent.execute_shell("python3 -c 'import auth; print(auth.create_token(123))'")
    
    agent.end_task(
        result="success",
        lessons=[
            "JWT tokens need expiration timestamps",
            "Use bcrypt for password hashing, not plain text",
            "Always validate token signature"
        ]
    )
    
    print("✅ Task 1 complete - lessons learned saved to memory")
    
    # Task 2: Similar task - should recall lessons!
    print("\n" + "=" * 60)
    print("TASK 2: Create login API")
    print("=" * 60)
    
    # Before starting, show what agent remembers
    print("\n🧠 Agent recalls similar tasks:")
    context = agent.get_memory_context("Create login API with JWT")
    print(context)
    
    agent.start_task("Create login API with JWT authentication", "coding")
    
    # Now agent uses lessons from memory
    agent.write_file("login.py", """
import jwt
import bcrypt
from datetime import datetime, timedelta

def create_token(user_id):
    # FIXED: Added expiration based on past lesson
    exp = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode({'user_id': user_id, 'exp': exp}, 'secret', algorithm='HS256')

def hash_password(password):
    # FIXED: Using bcrypt from lesson
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
""")
    
    agent.end_task(
        result="success",
        lessons=[
            "Rate limiting prevents brute force attacks",
            "Refresh tokens improve UX"
        ]
    )
    
    print("✅ Task 2 complete - applied lessons from Task 1")
    
    # Task 3: Different agent uses shared knowledge
    print("\n" + "=" * 60)
    print("TASK 3: DevOps deploys auth service")
    print("=" * 60)
    
    devops = AgentRuntime("devops", workspace=".", enable_memory=True)
    
    # DevOps sees what backend-dev learned
    print("\n🤝 DevOps checks shared knowledge:")
    shared_context = devops.get_memory_context("Deploy authentication service")
    print(shared_context)
    
    devops.start_task("Deploy auth service with JWT", "deployment")
    
    devops.write_file("docker-compose.yml", """
services:
  auth:
    image: auth-service:latest
    environment:
      - JWT_SECRET=${JWT_SECRET}  # From shared knowledge
      - TOKEN_EXPIRY=24h
    ports:
      - "8080:8080"
""")
    
    devops.end_task(
        result="success",
        lessons=["Use secrets management for JWT keys", "Enable HTTPS in production"]
    )
    
    # Share knowledge across agents
    devops.share_knowledge("JWT Deployment", "Always rotate secrets monthly")
    
    print("✅ Task 3 complete - knowledge shared with team")
    
    # Final stats
    print("\n" + "=" * 60)
    print("MEMORY STATISTICS")
    print("=" * 60)
    
    print("\n📊 backend-dev:")
    stats = agent.get_memory_stats()
    print(f"   Total episodes: {stats['episodic']['total_episodes']}")
    print(f"   Success rate: {stats['episodic']['success_rate']:.0%}")
    print(f"   Patterns learned: {stats['episodic']['patterns_learned']}")
    
    print("\n📊 devops:")
    stats = devops.get_memory_stats()
    print(f"   Total episodes: {stats['episodic']['total_episodes']}")
    print(f"   Patterns learned: {stats['episodic']['patterns_learned']}")
    
    print("\n" + "=" * 60)
    print("✅ Memory system working! Agents learn and share knowledge.")
    print("=" * 60)

if __name__ == "__main__":
    main()
