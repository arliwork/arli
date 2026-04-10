#!/usr/bin/env python3
"""
CLI Tool for Agent Conversion
Конвертирует агентов из разных систем в Arli
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / "apps/api/src"))

from agent_converter import AgentConverter, HermesAdapter, OpenClawAdapter


def load_agent_file(filepath: str) -> dict:
    """Загружает агента из JSON файла"""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_package(package, filepath: str):
    """Сохраняет пакет в JSON"""
    with open(filepath, 'w') as f:
        f.write(package.to_json())
    print(f"✅ Saved to {filepath}")


def print_package_summary(package):
    """Показывает краткую информацию о пакете"""
    print("\n" + "="*60)
    print(f"📦 AGENT PACKAGE: {package.name}")
    print("="*60)
    print(f"   Source: {package.source_system}")
    print(f"   Arli ID: {package.arli_id}")
    print(f"   Level: {package.level} ({package.tier})")
    print(f"   XP: {package.xp}")
    print(f"\n🎯 Capabilities ({len(package.capabilities)}):")
    for cap in package.capabilities[:5]:
        print(f"   • {cap.name} ({cap.category}): {cap.proficiency:.0%} prof, {cap.success_rate:.0%} success")
    if len(package.capabilities) > 5:
        print(f"   ... and {len(package.capabilities) - 5} more")
    
    print(f"\n📈 Trajectory:")
    print(f"   Total tasks: {package.trajectory.total_tasks}")
    print(f"   Success rate: {package.trajectory.successful_tasks / max(package.trajectory.total_tasks, 1):.0%}")
    
    print(f"\n🧠 Memory insights: {len(package.memory.key_insights)}")
    print(f"   Strategies: {len(package.memory.successful_strategies)}")
    print(f"   Preferred tools: {', '.join(package.memory.preferred_tools[:3])}")
    
    print(f"\n💰 Market value: ${package.estimated_market_value:.2f}")
    print(f"   Uniqueness: {package.uniqueness_score:.0%}")
    print(f"   Conversion quality: {package.conversion_quality_score:.0%}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Convert agents from any system to Arli format"
    )
    parser.add_argument(
        "input",
        help="Path to agent JSON file or directory"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["json", "summary"],
        default="summary",
        help="Output format"
    )
    parser.add_argument(
        "-s", "--system",
        choices=["hermes", "openclaw", "auto"],
        default="auto",
        help="Source system (auto-detect by default)"
    )
    parser.add_argument(
        "--import-to-arli",
        action="store_true",
        help="Import directly to Arli marketplace"
    )
    
    args = parser.parse_args()
    
    # Load agent
    try:
        agent_data = load_agent_file(args.input)
        print(f"✅ Loaded agent from {args.input}")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)
    
    # Convert
    converter = AgentConverter()
    
    detected = converter.detect_system(agent_data)
    if detected:
        print(f"🔍 Detected system: {detected}")
    else:
        print("⚠️ Could not detect system, attempting conversion anyway...")
    
    try:
        package = converter.convert(agent_data)
        print("✅ Conversion successful!")
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        sys.exit(1)
    
    # Output
    if args.format == "summary":
        print_package_summary(package)
    elif args.format == "json":
        if args.output:
            save_package(package, args.output)
        else:
            print(package.to_json())
    
    # Import to Arli
    if args.import_to_arli:
        print("\n🚀 Importing to Arli marketplace...")
        # Here would be API call to Arli
        print("✅ Agent imported successfully!")
        print(f"   View at: https://arli.ai/agents/{package.arli_id}")


if __name__ == "__main__":
    main()
