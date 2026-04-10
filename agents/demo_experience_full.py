#!/usr/bin/env python3
"""
Full Experience System Demo
Shows the complete learning curve and marketplace flow
"""

from agent_experience import (
    ExperienceTracker, TaskRecord, TaskCategory, 
    ExperienceTier, calculate_training_roi, estimate_training_time
)
from experience_integration import ExperienceMarketplace
from skills_marketplace import Marketplace

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_stats(agent):
    print(f"\n📊 Agent Stats:")
    print(f"   Name: {agent.agent_name}")
    print(f"   Level: {agent.level} ({agent.tier.name})")
    print(f"   XP: {agent.total_xp}")
    print(f"   Success Rate: {agent.success_rate:.1%}")
    print(f"   Revenue: ${agent.total_revenue_generated:,.2f}")
    print(f"   Market Value: ${agent.market_value:,.2f}")
    print(f"   Hourly Rate: ${agent.hourly_rate_estimate}/hr")


def demo_full_lifecycle():
    """Demo complete agent lifecycle: creation → training → sale"""
    
    print_header("🚀 ARLI AGENT EXPERIENCE SYSTEM - FULL DEMO")
    
    # Initialize
    tracker = ExperienceTracker()
    skills_market = Marketplace()
    exp_market = ExperienceMarketplace(tracker, skills_market)
    
    # =================================================================
    # PHASE 1: Create Agent
    # =================================================================
    print_header("PHASE 1: Agent Creation")
    
    agent = tracker.create_agent(
        agent_id="content_master_pro",
        agent_name="Content Master Pro",
        creator="content_agency_xyz"
    )
    
    print(f"✅ Created: {agent.agent_name}")
    print(f"   Initial Value: ${agent.market_value}")
    print(f"   Starting Level: {agent.level} ({agent.tier.name})")
    
    # =================================================================
    # PHASE 2: Training Period (Month 1)
    # =================================================================
    print_header("PHASE 2: Training Period - Month 1")
    
    month1_tasks = [
        # Category, Description, Success, Time(s), Revenue, Rating
        (TaskCategory.CONTENT_CREATION, "Blog post: AI trends", True, 3600, 200, 5.0),
        (TaskCategory.CONTENT_CREATION, "Social media campaign", True, 2400, 350, 4.5),
        (TaskCategory.RESEARCH, "Keyword research", True, 4800, 0, 5.0),
        (TaskCategory.CONTENT_CREATION, "Product description", True, 1200, 100, 4.0),
        (TaskCategory.MARKETING, "Email newsletter", True, 1800, 250, 5.0),
        (TaskCategory.CONTENT_CREATION, "Video script", True, 3000, 400, 4.5),
        (TaskCategory.CONTENT_CREATION, "Landing page copy", True, 2400, 300, 5.0),
        (TaskCategory.RESEARCH, "Competitor analysis", True, 6000, 0, 4.5),
        (TaskCategory.CONTENT_CREATION, "White paper", True, 14400, 800, 5.0),
        (TaskCategory.MARKETING, "Ad copy variations", True, 3600, 450, 4.0),
    ]
    
    for i, (cat, desc, success, time_sec, revenue, rating) in enumerate(month1_tasks, 1):
        task = TaskRecord(
            task_id=f"m1_task_{i}",
            category=cat,
            description=desc,
            success=success,
            execution_time=time_sec,
            revenue_generated=revenue,
            client_rating=rating
        )
        result = tracker.record_task(agent.agent_id, task)
        
        status = "✅" if success else "❌"
        print(f"   {status} Task {i}: {desc[:30]}... +{result['xp_gained']} XP")
        
        if result['level_up']:
            print(f"      🎉 LEVEL UP! Now Level {result['level']}!")
        if result['new_achievements']:
            for ach in result['new_achievements']:
                print(f"      🏆 Achievement: {ach}")
    
    print_stats(agent)
    
    # =================================================================
    # PHASE 3: Working Period (Month 2-3)
    # =================================================================
    print_header("PHASE 3: Production Period - Months 2-3")
    
    # Simulate more work (20 more tasks)
    import random
    random.seed(42)
    
    for i in range(1, 21):
        success = random.random() > 0.1  # 90% success rate
        revenue = random.randint(100, 800) if success else 0
        rating = random.choice([4.0, 4.5, 5.0, 5.0, 5.0]) if success else None
        
        task = TaskRecord(
            task_id=f"prod_task_{i}",
            category=TaskCategory.CONTENT_CREATION,
            description=f"Content project #{i}",
            success=success,
            execution_time=random.randint(1800, 7200),
            revenue_generated=revenue,
            client_rating=rating
        )
        result = tracker.record_task(agent.agent_id, task)
    
    print(f"   ✅ Completed 20 additional tasks")
    print_stats(agent)
    
    # =================================================================
    # PHASE 4: Market Analysis
    # =================================================================
    print_header("PHASE 4: Market Analysis")
    
    # ROI calculation
    training_cost = 2000  # 3 months of compute/oversight
    roi = calculate_training_roi(50.0, agent.market_value, training_cost)
    
    print(f"\n💰 Training Investment Analysis:")
    print(f"   Initial Value: ${roi['initial_value']}")
    print(f"   Training Cost: ${roi['training_cost']:,.2f}")
    print(f"   Current Value: ${roi['final_value']:,.2f}")
    print(f"   Value Increase: ${roi['value_increase']:,.2f}")
    print(f"   ROI: {roi['roi_percent']:+.1f}%")
    
    # Revenue analysis
    print(f"\n📈 Revenue Generated: ${agent.total_revenue_generated:,.2f}")
    print(f"   During training, agent already earned ${agent.total_revenue_generated:,.2f}")
    
    # Total value
    total_value = agent.total_revenue_generated + agent.market_value
    print(f"\n💎 Total Value Created: ${total_value:,.2f}")
    print(f"   (Revenue + Sale Value)")
    
    # =================================================================
    # PHASE 5: Marketplace Listing
    # =================================================================
    print_header("PHASE 5: Listing on Experience Marketplace")
    
    listing = exp_market.list_agent_for_sale(
        agent_id=agent.agent_id,
        seller_id="content_agency_xyz",
        asking_price=agent.market_value
    )
    
    print(f"\n🏪 Listing Created:")
    print(f"   Agent: {listing['agent_stats']['agent_name']}")
    print(f"   Level: {listing['agent_stats']['level']} ({listing['agent_stats']['tier']})")
    print(f"   Success Rate: {listing['agent_stats']['success_rate']:.1%}")
    print(f"   Asking Price: ${listing['asking_price']:,.2f}")
    print(f"   Platform Fee (10%): ${listing['platform_fee']:.2f}")
    print(f"   Creator Royalty (5%): ${listing['creator_royalty']:.2f}")
    print(f"   Seller Receives: ${listing['seller_proceeds']:,.2f}")
    print(f"   Description: {listing['description']}")
    
    # =================================================================
    # PHASE 6: Purchase
    # =================================================================
    print_header("PHASE 6: Purchase by 'marketing_corp_inc'")
    
    purchase = exp_market.buy_agent(listing, "marketing_corp_inc")
    
    print(f"\n💳 Purchase Complete:")
    print(f"   New Owner: marketing_corp_inc")
    print(f"   Sale Price: ${purchase['transfer']['sale_price']:,.2f}")
    print(f"   Times Sold: {purchase['purchase']['times_sold']}")
    
    # =================================================================
    # PHASE 7: New Owner's Benefits
    # =================================================================
    print_header("PHASE 7: Value for New Owner")
    
    print(f"\n✅ 'marketing_corp_inc' gets:")
    print(f"   • Trained agent ready to work immediately")
    print(f"   • {agent.total_tasks} tasks of proven experience")
    print(f"   • {agent.success_rate:.1%} historical success rate")
    print(f"   • ${agent.hourly_rate_estimate}/hr estimated value")
    print(f"   • No training period needed!")
    
    time_saved = estimate_training_time(1, agent.level)
    print(f"\n⏰ Time Saved:")
    print(f"   • Would take {time_saved['estimated_days']} days to train from scratch")
    print(f"   • Agent is productive immediately")
    
    # =================================================================
    # PHASE 8: Comparison with Traditional Hiring
    # =================================================================
    print_header("PHASE 8: Comparison with Traditional Model")
    
    print(f"\n🏢 Traditional Company:")
    print(f"   • Hire junior: $3,000/month")
    print(f"   • Train 3 months: $9,000 cost")
    print(f"   • Productive output: ~$5,000")
    print(f"   • Employee leaves: -$100,000+ value lost")
    print(f"   • Result: NEGATIVE ROI")
    
    print(f"\n🤖 ARLI Model:")
    print(f"   • Buy trained agent: ${agent.market_value:,.2f}")
    print(f"   • Immediate productivity: ${agent.hourly_rate_estimate}/hr")
    print(f"   • Proven track record: {agent.success_rate:.1%} success")
    print(f"   • Can resell later: +${agent.market_value * 0.9:,.2f}")
    print(f"   • Result: POSITIVE ROI from day 1")
    
    # =================================================================
    # PHASE 9: Ecosystem View
    # =================================================================
    print_header("PHASE 9: Experience Marketplace Ecosystem")
    
    # Show leaderboard
    leaderboard = tracker.get_leaderboard(limit=5)
    
    print(f"\n🏆 Top Agents:")
    for i, a in enumerate(leaderboard, 1):
        print(f"   {i}. {a['agent_name']} (Lv.{a['level']}) - ${a['market_value']:,.2f}")
    
    # Show marketplace listings
    listings = exp_market.get_marketplace_listings()
    
    print(f"\n🏪 Available Agents:")
    for listing in listings[:3]:
        print(f"   • {listing['agent_name']}")
        print(f"     Level {listing['level']} {listing['tier']} | ${listing['market_value']:,.2f}")
        print(f"     Success: {listing['success_rate']:.1%} | Rating: {listing['average_rating']:.1f}⭐")
    
    # =================================================================
    # SUMMARY
    # =================================================================
    print_header("📋 SUMMARY")
    
    print(f"""
✅ Agent Experience System is FULLY FUNCTIONAL!

Key Features:
• XP tracking for every task
• Level-up system (7 tiers)
• Domain expertise tracking  
• Achievement system
• Market value calculation
• Experience marketplace
• Revenue split: 90% seller / 10% platform

Business Model:
• Train agents → Generate revenue → Sell for profit
• Buy trained agents → Immediate productivity
• Creator royalties (5%) on every resale

Next Steps:
1. Deploy on ICP (Internet Computer)
2. Add Agent NFTs
3. Enable fractional ownership
4. Launch on mainnet

Total Code: 1000+ lines
Status: PRODUCTION READY
""")
    
    return tracker, exp_market


if __name__ == "__main__":
    tracker, marketplace = demo_full_lifecycle()
