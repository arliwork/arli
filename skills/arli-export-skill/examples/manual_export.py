"""
Example: Manual Export for Any Agent System
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from export_adapter import ArliExporter


def export_openclaw_agent():
    """
    Пример экспорта OpenClaw агента
    """
    exporter = ArliExporter(
        agent_name="OpenClaw Trading Bot",
        agent_id="claw_trader_001",
        source_system="openclaw",
        description="Automated crypto trading with technical analysis"
    )
    
    # Добавляем умения
    exporter.add_capability(
        name="technical_analysis",
        category="trading",
        proficiency=0.88,
        execution_count=2341,
        success_rate=0.74,
        avg_execution_time=2.5,
        description="RSI, MACD, Bollinger Bands analysis"
    )
    
    exporter.add_capability(
        name="risk_management",
        category="trading",
        proficiency=0.92,
        execution_count=1567,
        success_rate=0.89,
        description="Position sizing, stop-loss, take-profit"
    )
    
    exporter.add_capability(
        name="binance_api",
        category="integration",
        proficiency=0.85,
        execution_count=890,
        success_rate=0.95,
        description="Binance spot and futures trading"
    )
    
    # Добавляем сессии (последние сделки)
    sessions_data = [
        ("BTC long entry at $65k", True, 120),
        ("ETH scalp trade", True, 80),
        ("SOL swing trade", False, 20),
        ("ADA breakout", True, 100),
        ("Market neutral arb", True, 150),
    ]
    
    for task, success, xp in sessions_data:
        exporter.add_session(
            task=task,
            success=success,
            xp_earned=xp
        )
    
    # Добавляем инсайты
    exporter.add_insight(
        content="BTC shows 78% probability of rise after 3 red candles on 4h",
        source="pattern_analysis",
        confidence=0.82
    )
    
    exporter.add_insight(
        content="High volatility periods correlate with funding rate spikes",
        source="correlation_analysis",
        confidence=0.76
    )
    
    exporter.add_insight(
        content="Best entry time for alts: 04:00-06:00 UTC",
        source="time_analysis",
        confidence=0.71
    )
    
    # Добавляем предпочтения
    exporter.add_preference("preferred_exchange", "binance")
    exporter.add_preference("risk_level", "moderate")
    exporter.add_preference("max_position_size", "5%")
    exporter.add_preference("timeframe", "4h")
    
    # Экспортируем
    package = exporter.export()
    filepath = exporter.save()
    
    print(exporter.get_summary())
    print(f"\n💾 Saved: {filepath}")
    
    return package


def export_autogen_agent():
    """
    Пример экспорта AutoGen агента
    """
    exporter = ArliExporter(
        agent_name="AutoGen Research Assistant",
        agent_id="autogen_research_042",
        source_system="autogen",
        description="Multi-agent research system with synthesis"
    )
    
    # Умения
    exporter.add_capability(
        name="web_research",
        category="research",
        proficiency=0.90,
        execution_count=567,
        success_rate=0.88
    )
    
    exporter.add_capability(
        name="paper_summarization",
        category="analysis",
        proficiency=0.85,
        execution_count=234,
        success_rate=0.92
    )
    
    exporter.add_capability(
        name="multi_agent_coordination",
        category="orchestration",
        proficiency=0.78,
        execution_count=89,
        success_rate=0.81
    )
    
    # Сессии
    for i in range(20):
        exporter.add_session(
            task=f"Research task #{i+1}",
            success=i % 5 != 0,  # 80% success
            xp_earned=50 if i % 5 != 0 else 10
        )
    
    # Инсайты
    exporter.add_insight(
        content="Multi-agent debate improves research quality by 34%",
        source="experiment",
        confidence=0.88
    )
    
    package = exporter.export()
    print(exporter.get_summary())
    
    return package


def export_custom_agent():
    """
    Пример экспорта кастомного агента (минимальные данные)
    """
    exporter = ArliExporter(
        agent_name="My Custom Bot",
        agent_id="custom_001",
        source_system="custom"
    )
    
    # Минимум - только одно умение
    exporter.add_capability(
        name="data_processing",
        category="data",
        proficiency=0.7,
        execution_count=10
    )
    
    package = exporter.export()
    print(exporter.get_summary())
    
    return package


if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: OpenClaw Trading Bot")
    print("=" * 60)
    export_openclaw_agent()
    
    print("\n" + "=" * 60)
    print("Example 2: AutoGen Research Assistant")
    print("=" * 60)
    export_autogen_agent()
    
    print("\n" + "=" * 60)
    print("Example 3: Custom Agent (minimal)")
    print("=" * 60)
    export_custom_agent()
