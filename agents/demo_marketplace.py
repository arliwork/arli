#!/usr/bin/env python3
"""
ARLI Skills Marketplace - Live Demo
Creating, publishing, and using real skills
"""

import sys
sys.path.insert(0, '/home/paperclip/arli')

from agents.skills_marketplace import (
    SkillPackage, Marketplace, SkillInstaller, 
    SkillMetadata, SkillCategory, SkillStatus
)
from agents.runtime import AgentRuntime
import json
from pathlib import Path

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def create_real_skills():
    """Create several real, working skills"""
    print_section("1. СОЗДАНИЕ СКИЛЛОВ")
    
    packager = SkillPackage()
    skills = []
    
    # Skill 1: Web Scraper Pro
    print("\n🕷️  Creating 'Web Scraper Pro'...")
    path1 = packager.create_skill_template("Web Scraper Pro", "ScrapeMaster")
    
    # Update with real implementation
    skill_py = path1 / "skill.py"
    skill_py.write_text('''#!/usr/bin/env python3
"""Web Scraper Pro - Advanced web scraping with anti-detection"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time

class Skill:
    def __init__(self, runtime):
        self.runtime = runtime
        self.name = "Web Scraper Pro"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def execute(self, url: str, selector: str, extract_type: str = "text") -> Dict:
        """
        Scrape data from any website
        
        Args:
            url: Target website URL
            selector: CSS selector (e.g., '.price', 'h1', '.product-title')
            extract_type: 'text', 'html', 'links', or 'images'
        
        Returns:
            Dict with scraped data
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            elements = soup.select(selector)
            
            results = []
            for elem in elements:
                if extract_type == "text":
                    results.append(elem.get_text(strip=True))
                elif extract_type == "html":
                    results.append(str(elem))
                elif extract_type == "links":
                    if elem.name == 'a' and elem.get('href'):
                        results.append({
                            'text': elem.get_text(strip=True),
                            'url': elem['href']
                        })
                elif extract_type == "images":
                    if elem.name == 'img' and elem.get('src'):
                        results.append(elem['src'])
            
            return {
                "success": True,
                "data": results,
                "count": len(results),
                "url": url
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_capabilities(self):
        return ["web_scraping", "data_extraction", "content_analysis"]

def create_skill(runtime):
    return Skill(runtime)
''')
    
    skill_json = path1 / "skill.json"
    metadata = SkillMetadata(
        skill_id="scrapemaster.web_scraper_pro",
        name="Web Scraper Pro",
        version="1.0.0",
        description="Advanced web scraping with CSS selectors. Extract text, links, images from any website.",
        category=SkillCategory.WEB_SCRAPING,
        author="ScrapeMaster",
        author_id="scrapemaster",
        price=49.99,
        dependencies=["requests", "beautifulsoup4"]
    )
    skill_json.write_text(json.dumps(metadata.__dict__, indent=2, default=str))
    skills.append(("Web Scraper Pro", path1, 49.99))
    print(f"   ✅ Created at: {path1}")
    
    # Skill 2: Database Optimizer
    print("\n🗄️  Creating 'Database Optimizer'...")
    path2 = packager.create_skill_template("Database Optimizer", "DBExpert")
    
    skill_py = path2 / "skill.py"
    skill_py.write_text('''#!/usr/bin/env python3
"""Database Optimizer - Analyze and optimize PostgreSQL/MySQL"""

import re
from typing import Dict, List

class Skill:
    def __init__(self, runtime):
        self.runtime = runtime
        self.name = "Database Optimizer"
    
    def execute(self, schema_sql: str = None, query: str = None, 
                operation: str = "analyze") -> Dict:
        """
        Optimize database performance
        
        Args:
            schema_sql: Database schema DDL
            query: SQL query to optimize
            operation: 'analyze', 'suggest_indexes', 'optimize_query'
        
        Returns:
            Optimization recommendations
        """
        recommendations = []
        
        if operation == "analyze" and schema_sql:
            # Check for missing indexes on foreign keys
            fk_pattern = r'FOREIGN KEY \((\w+)\)'
            fks = re.findall(fk_pattern, schema_sql, re.IGNORECASE)
            
            for fk in fks:
                recommendations.append({
                    "type": "index",
                    "priority": "high",
                    "sql": f"CREATE INDEX idx_{fk} ON table_name({fk});",
                    "reason": f"Foreign key '{fk}' should be indexed"
                })
            
            # Check for proper data types
            if 'VARCHAR(255)' in schema_sql:
                recommendations.append({
                    "type": "schema",
                    "priority": "medium",
                    "suggestion": "Consider TEXT instead of VARCHAR(255) for PostgreSQL",
                    "reason": "No performance difference, TEXT is more flexible"
                })
        
        elif operation == "optimize_query" and query:
            # Analyze query
            if "SELECT *" in query.upper():
                recommendations.append({
                    "type": "query",
                    "priority": "high",
                    "suggestion": "Replace SELECT * with specific columns",
                    "reason": "Reduces I/O and memory usage"
                })
            
            if "LIKE '%" in query:
                recommendations.append({
                    "type": "query",
                    "priority": "medium",
                    "suggestion": "Consider full-text search instead of LIKE '%text%'",
                    "reason": "Leading wildcard prevents index usage"
                })
        
        return {
            "success": True,
            "recommendations": recommendations,
            "score": max(0, 100 - len(recommendations) * 10),
            "summary": f"Found {len(recommendations)} optimization opportunities"
        }
    
    def get_capabilities(self):
        return ["database_optimization", "sql_analysis", "performance_tuning"]

def create_skill(runtime):
    return Skill(runtime)
''')
    
    skill_json = path2 / "skill.json"
    metadata = SkillMetadata(
        skill_id="dbexpert.database_optimizer",
        name="Database Optimizer",
        version="1.2.0",
        description="Analyze PostgreSQL/MySQL schemas and queries. Get optimization recommendations.",
        category=SkillCategory.DATA_ANALYSIS,
        author="DBExpert",
        author_id="dbexpert",
        price=29.99
    )
    skill_json.write_text(json.dumps(metadata.__dict__, indent=2, default=str))
    skills.append(("Database Optimizer", path2, 29.99))
    print(f"   ✅ Created at: {path2}")
    
    # Skill 3: API Security Scanner
    print("\n🔒 Creating 'API Security Scanner'...")
    path3 = packager.create_skill_template("API Security Scanner", "SecurIT")
    
    skill_py = path3 / "skill.py"
    skill_py.write_text('''#!/usr/bin/env python3
"""API Security Scanner - Find vulnerabilities in REST APIs"""

import re
from typing import Dict, List

class Skill:
    def __init__(self, runtime):
        self.runtime = runtime
        self.name = "API Security Scanner"
    
    def execute(self, openapi_spec: str = None, code: str = None) -> Dict:
        """
        Scan API for security vulnerabilities
        
        Args:
            openapi_spec: OpenAPI/Swagger specification
            code: API source code to analyze
        
        Returns:
            Security issues found
        """
        vulnerabilities = []
        
        if code:
            # Check for hardcoded secrets
            secret_patterns = [
                (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
                (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
                (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
                (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
            ]
            
            for pattern, issue in secret_patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    vulnerabilities.append({
                        "severity": "critical",
                        "issue": issue,
                        "recommendation": "Use environment variables or secret management"
                    })
            
            # Check for SQL injection risks
            if re.search(r'execute\s*\(\s*["\'].*%s', code):
                vulnerabilities.append({
                    "severity": "critical",
                    "issue": "Potential SQL injection",
                    "recommendation": "Use parameterized queries"
                })
            
            # Check for missing auth
            if 'authentication' not in code.lower() and 'auth' not in code.lower():
                vulnerabilities.append({
                    "severity": "high",
                    "issue": "No authentication detected",
                    "recommendation": "Add authentication middleware"
                })
        
        if openapi_spec:
            # Check for HTTPS
            if 'http://' in openapi_spec and 'https://' not in openapi_spec:
                vulnerabilities.append({
                    "severity": "high",
                    "issue": "HTTP instead of HTTPS",
                    "recommendation": "Use HTTPS for all endpoints"
                })
        
        risk_score = sum(10 if v["severity"] == "critical" else 5 for v in vulnerabilities)
        
        return {
            "success": True,
            "vulnerabilities": vulnerabilities,
            "risk_score": min(100, risk_score),
            "passed": len(vulnerabilities) == 0,
            "summary": f"Found {len(vulnerabilities)} security issues"
        }
    
    def get_capabilities(self):
        return ["security_scanning", "vulnerability_detection", "api_security"]

def create_skill(runtime):
    return Skill(runtime)
''')
    
    skill_json = path3 / "skill.json"
    metadata = SkillMetadata(
        skill_id="securit.api_security_scanner",
        name="API Security Scanner",
        version="2.0.0",
        description="Scan REST APIs for security vulnerabilities. Detect hardcoded secrets, SQL injection, missing auth.",
        category=SkillCategory.SECURITY,
        author="SecurIT",
        author_id="securit",
        price=79.99
    )
    skill_json.write_text(json.dumps(metadata.__dict__, indent=2, default=str))
    skills.append(("API Security Scanner", path3, 79.99))
    print(f"   ✅ Created at: {path3}")
    
    # Skill 4: Content Generator
    print("\n✍️  Creating 'AI Content Generator'...")
    path4 = packager.create_skill_template("AI Content Generator", "ContentKing")
    
    skill_py = path4 / "skill.py"
    skill_py.write_text('''#!/usr/bin/env python3
"""AI Content Generator - Create marketing copy, blogs, emails"""

import random
from typing import Dict, List

class Skill:
    def __init__(self, runtime):
        self.runtime = runtime
        self.name = "AI Content Generator"
    
    def execute(self, content_type: str, topic: str, tone: str = "professional",
               length: str = "medium") -> Dict:
        """
        Generate marketing content
        
        Args:
            content_type: 'blog', 'email', 'social', 'ad'
            topic: What to write about
            tone: 'professional', 'casual', 'persuasive', 'funny'
            length: 'short', 'medium', 'long'
        
        Returns:
            Generated content
        """
        templates = {
            "blog": {
                "intro": [
                    f"In today's fast-paced world, {topic} has become essential...",
                    f"Are you struggling with {topic}? You're not alone...",
                    f"Discover the secret to mastering {topic}..."
                ],
                "body": [
                    f"First, let's understand why {topic} matters...",
                    f"The key to success with {topic} is consistency...",
                    f"Experts agree that {topic} drives results..."
                ],
                "conclusion": [
                    f"Ready to transform your approach to {topic}? Start today!",
                    f"Don't wait - implement these {topic} strategies now."
                ]
            },
            "email": {
                "subject": [
                    f"Boost your {topic} results by 300%",
                    f"Quick question about {topic}",
                    f"Your {topic} strategy needs this"
                ],
                "body": [
                    f"Hi there,\\n\\nI noticed you're interested in {topic}...",
                    f"Quick win: improve your {topic} in just 5 minutes..."
                ]
            },
            "social": {
                "twitter": [
                    f"🚀 {topic} tip: Focus on what matters! #growth",
                    f"💡 Did you know? {topic} can 10x your results!"
                ],
                "linkedin": [
                    f"Just published an article about {topic}. Here's what I learned...",
                    f"{topic} is changing how we work. Here's why:"
                ]
            }
        }
        
        if content_type not in templates:
            return {"error": f"Unknown content type: {content_type}"}
        
        # Generate content
        content_parts = []
        
        if content_type == "blog":
            content_parts.append(random.choice(templates["blog"]["intro"]))
            for _ in range(3 if length == "medium" else 5):
                content_parts.append(random.choice(templates["blog"]["body"]))
            content_parts.append(random.choice(templates["blog"]["conclusion"]))
            
        elif content_type == "email":
            content_parts.append("Subject: " + random.choice(templates["email"]["subject"]))
            content_parts.append("\\n" + random.choice(templates["email"]["body"]))
            content_parts.append("\\nBest regards,")
            
        elif content_type == "social":
            platform = random.choice(["twitter", "linkedin"])
            content_parts.append(random.choice(templates["social"][platform]))
        
        content = "\\n\\n".join(content_parts)
        
        # Adjust tone
        if tone == "casual":
            content = content.replace("essential", "super important").replace("discover", "check out")
        elif tone == "persuasive":
            content = content.replace("can", "will").replace("might", "definitely")
        
        word_count = len(content.split())
        
        return {
            "success": True,
            "content": content,
            "content_type": content_type,
            "tone": tone,
            "word_count": word_count,
            "topic": topic
        }
    
    def get_capabilities(self):
        return ["content_generation", "marketing", "copywriting"]

def create_skill(runtime):
    return Skill(runtime)
''')
    
    skill_json = path4 / "skill.json"
    metadata = SkillMetadata(
        skill_id="contentking.ai_content_generator",
        name="AI Content Generator",
        version="1.5.0",
        description="Generate marketing copy, blog posts, emails, social media content. Multiple tones and lengths.",
        category=SkillCategory.CONTENT,
        author="ContentKing",
        author_id="contentking",
        price=39.99
    )
    skill_json.write_text(json.dumps(metadata.__dict__, indent=2, default=str))
    skills.append(("AI Content Generator", path4, 39.99))
    print(f"   ✅ Created at: {path4}")
    
    return skills

def publish_to_marketplace(skills):
    """Publish skills to marketplace"""
    print_section("2. ПУБЛИКАЦИЯ В МАРКЕТПЛЕЙС")
    
    marketplace = Marketplace()
    published = []
    
    for name, path, price in skills:
        print(f"\n📦 Publishing '{name}' (${price})...")
        
        # Validate
        packager = SkillPackage()
        validation = packager.validate_skill(path)
        
        if validation["valid"]:
            result = marketplace.publish_skill(path)
            if result["success"]:
                skill_id = result.get("skill_id", "unknown")
                marketplace.approve_skill(skill_id)
                published.append((name, skill_id, price))
                print(f"   ✅ Published & Approved!")
                print(f"      ID: {skill_id}")
        else:
            print(f"   ❌ Validation failed: {validation['errors']}")
    
    return published, marketplace

def demo_marketplace(marketplace, published_skills):
    """Demo marketplace features"""
    print_section("3. МАРКЕТПЛЕЙС - ПОИСК И ПРОСМОТР")
    
    print("\n🔍 All Published Skills:")
    all_skills = marketplace.search_skills()
    for i, skill in enumerate(all_skills, 1):
        print(f"\n   {i}. {skill.name}")
        print(f"      💰 ${skill.price}")
        print(f"      🏷️  Category: {skill.category.value}")
        print(f"      👤 Author: {skill.author}")
        print(f"      📝 {skill.description[:60]}...")
    
    print("\n🔍 Search: 'security'")
    security_skills = marketplace.search_skills(query="security")
    print(f"   Found {len(security_skills)} security skills")
    for skill in security_skills:
        print(f"   • {skill.name} - ${skill.price}")
    
    print("\n🔍 Filter by price (max $40)")
    affordable = marketplace.search_skills(max_price=40)
    print(f"   Found {len(affordable)} skills under $40")
    for skill in affordable:
        print(f"   • {skill.name} - ${skill.price}")

def demo_purchase_and_install(marketplace, published_skills):
    """Demo purchase and installation"""
    print_section("4. ПОКУПКА И УСТАНОВКА СКИЛЛОВ")
    
    installer = SkillInstaller()
    user_id = "devstudio_one"
    
    purchased = []
    
    for name, skill_id, price in published_skills[:3]:  # Buy first 3
        print(f"\n💳 Purchasing '{name}'...")
        
        # Purchase
        purchase = marketplace.purchase_skill(skill_id, user_id)
        if "error" not in purchase:
            print(f"   ✅ Purchased! License: {purchase['license_key']}")
            purchased.append((name, skill_id, purchase['license_key']))
            
            # Install
            print(f"   📥 Installing...")
            install = installer.install_skill(skill_id, marketplace, user_id)
            if install.get("success"):
                print(f"   ✅ Installed to: {install['install_path']}")
        else:
            print(f"   ⚠️  {purchase['error']}")
    
    return purchased

def demo_use_skills(purchased_skills):
    """Demo using installed skills"""
    print_section("5. ИСПОЛЬЗОВАНИЕ СКИЛЛОВ")
    
    # Create agent with skills
    agent = AgentRuntime("demo-agent", workspace=".", enable_memory=True)
    
    print("\n📋 Installed Skills:")
    skills = agent.list_skills()
    for skill in skills:
        print(f"   • {skill['skill_id']} (v{skill['version']})")
    
    # Use Web Scraper Pro
    print("\n🕷️  Using 'Web Scraper Pro':")
    result = agent.use_skill(
        "scrapemaster.web_scraper_pro",
        url="https://example.com",
        selector="h1",
        extract_type="text"
    )
    print(f"   Result: {result}")
    
    # Use Database Optimizer
    print("\n🗄️  Using 'Database Optimizer':")
    schema = """
    CREATE TABLE users (
        id INT PRIMARY KEY,
        email VARCHAR(255),
        FOREIGN KEY (company_id) REFERENCES companies(id)
    );
    """
    result = agent.use_skill(
        "dbexpert.database_optimizer",
        schema_sql=schema,
        operation="analyze"
    )
    if result.get("success"):
        print(f"   Found {len(result['result']['recommendations'])} recommendations")
        for rec in result['result']['recommendations'][:2]:
            print(f"      • {rec['type'].upper()}: {rec['reason']}")
    
    # Use Content Generator
    print("\n✍️  Using 'AI Content Generator':")
    result = agent.use_skill(
        "contentking.ai_content_generator",
        content_type="social",
        topic="AI automation",
        tone="professional"
    )
    if result.get("success"):
        content = result['result']
        print(f"   Generated {content['word_count']} words")
        print(f"   Preview: {content['content'][:100]}...")

def show_revenue_stats(marketplace, published_skills):
    """Show revenue statistics"""
    print_section("6. СТАТИСТИКА ДОХОДОВ")
    
    # Add some reviews
    print("\n⭐ Adding Reviews:")
    reviews_data = [
        ("scrapemaster.web_scraper_pro", 5, "Works great!"),
        ("dbexpert.database_optimizer", 5, "Saved me hours"),
        ("securit.api_security_scanner", 4, "Found real issues"),
        ("contentking.ai_content_generator", 5, "Love the quality"),
    ]
    
    for skill_id, rating, comment in reviews_data:
        marketplace.add_review(skill_id, "user_123", rating, comment)
        print(f"   ✅ {skill_id}: {rating}⭐")
    
    # Show updated listings
    print("\n📊 Updated Marketplace:")
    for name, skill_id, price in published_skills:
        skill = marketplace.get_skill(skill_id)
        if skill:
            print(f"\n   {skill.name}")
            print(f"      💰 ${skill.price}")
            print(f"      ⭐ Rating: {skill.rating:.1f}/5 ({skill.review_count} reviews)")
            print(f"      📥 Downloads: {skill.downloads}")
    
    # Revenue stats
    print("\n💰 Revenue Statistics:")
    
    # Simulate multiple sales
    for i in range(3):  # 3 sales of each
        for name, skill_id, price in published_skills:
            marketplace.purchase_skill(skill_id, f"user_{i}")
    
    stats = marketplace.get_revenue_stats()
    print(f"   Total Sales: ${stats['total_sales']:.2f}")
    print(f"   Platform Fee (30%): ${stats['total_platform_fee']:.2f}")
    print(f"   Creator Earnings (70%): ${stats['total_creator_earnings']:.2f}")
    
    print("\n   By Skill:")
    for skill_id, data in stats['skill_breakdown'].items():
        print(f"      • {data['name']}: {data['sales_count']} sales, "
              f"${data['revenue']:.2f} earned")

def main():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║           ARLI SKILLS MARKETPLACE - LIVE DEMO              ║
    ║                                                            ║
    ║  Creating → Publishing → Buying → Installing → Using      ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Create skills
    skills = create_real_skills()
    
    # Step 2: Publish to marketplace
    published, marketplace = publish_to_marketplace(skills)
    
    # Step 3: Demo marketplace
    demo_marketplace(marketplace, published)
    
    # Step 4: Purchase and install
    purchased = demo_purchase_and_install(marketplace, published)
    
    # Step 5: Use skills
    demo_use_skills(purchased)
    
    # Step 6: Show revenue
    show_revenue_stats(marketplace, published)
    
    print_section("ДЕМО ЗАВЕРШЕНО")
    print("""
    🎉 Skills Marketplace полностью функционален!
    
    ✅ Создание скиллов с шаблонами
    ✅ Валидация и публикация
    ✅ Поиск и фильтрация
    ✅ Покупка с лицензионными ключами
    ✅ Установка и динамическая загрузка
    ✅ Исполнение скиллов
    ✅ Отзывы и рейтинги
    ✅ Статистика доходов (70/30)
    
    📁 Файлы:
       - Скиллы: .arli/skills/source/
       - Пакеты: .arli/marketplace/packages/
       - Установленные: .arli/skills/installed/
    """)

if __name__ == "__main__":
    main()
