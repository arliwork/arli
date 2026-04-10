"""
Hermes CLI Integration for Arli Export
Добавляет команду /export-to-arli в Hermes
"""

import os
import sys
import json
from pathlib import Path

# Добавляем путь к export_adapter
sys.path.insert(0, str(Path(__file__).parent))

from export_adapter import ArliExporter, HermesAutoScanner


def export_to_arli_command(agent, args=""):
    """
    Handler for /export-to-arli command
    Используется в Hermes как slash command
    """
    print("🚀 Starting Arli export...")
    
    # Создаём экспортёр
    scanner = HermesAutoScanner()
    
    # Получаем данные из текущей сессии агента
    agent_name = getattr(agent, 'name', 'Hermes Agent')
    agent_id = getattr(agent, 'agent_id', f"hermes_{id(agent)}")
    
    exporter = ArliExporter(
        agent_name=agent_name,
        agent_id=agent_id,
        source_system="hermes"
    )
    
    # Сканируем fabric если доступен
    fabric_path = Path.home() / ".hermes" / "fabric"
    if fabric_path.exists():
        print(f"🔍 Scanning fabric at {fabric_path}...")
        # Здесь логика сканирования fabric
        entries = list(fabric_path.glob("**/*.json"))
        print(f"   Found {len(entries)} entries")
        
        for entry_file in entries[:100]:  # Max 100
            try:
                with open(entry_file, 'r') as f:
                    entry = json.load(f)
                
                # Извлекаем данные
                if entry.get('type') == 'decision' and entry.get('outcome'):
                    exporter.add_insight(
                        content=entry.get('content', '')[:200],
                        source='decision',
                        confidence=0.9
                    )
                elif entry.get('type') == 'learning':
                    exporter.add_insight(
                        content=entry.get('content', '')[:200],
                        source='learning',
                        confidence=0.7
                    )
                elif entry.get('type') == 'task':
                    exporter.add_session(
                        task=entry.get('summary', 'Task'),
                        success=entry.get('status') == 'completed',
                        xp_earned=50 if entry.get('status') == 'completed' else 10
                    )
                    
            except Exception:
                continue
    
    # Добавляем навыки из доступных tools
    tools = getattr(agent, 'tools', [])
    for tool in tools[:20]:  # Max 20 tools
        tool_name = getattr(tool, 'name', str(tool))
        exporter.add_capability(
            name=tool_name,
            category="tool",
            proficiency=0.8,
            execution_count=50,
            success_rate=0.85
        )
    
    # Экспортируем
    package = exporter.export()
    filepath = exporter.save()
    
    # Выводим summary
    print("\n" + exporter.get_summary())
    print(f"\n💾 Export saved: {filepath}")
    print(f"\n🚀 Next steps:")
    print(f"   1. Review the export: cat {filepath}")
    print(f"   2. Upload to Arli: arli upload {filepath}")
    print(f"   3. Set your price: arli price {package['arli_id']} $100")
    
    return f"Export complete: {filepath}"


# Регистрация команды (если используется как Hermes skill)
COMMAND_REGISTRY = {
    "export-to-arli": {
        "handler": export_to_arli_command,
        "description": "Export agent data to Arli marketplace format",
        "args": "[--output path.json]"
    }
}


if __name__ == "__main__":
    # Тест
    class MockAgent:
        name = "Test Agent"
        agent_id = "test_001"
        tools = []
    
    result = export_to_arli_command(MockAgent())
    print(result)
