"""
OpenClaw Integration for Arli Export
Скопируй этот файл в свой OpenClaw проект
"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Capability:
    name: str
    category: str
    proficiency: float = 0.5
    execution_count: int = 0
    success_rate: float = 0.5
    avg_execution_time: float = 0.0
    description: str = ""


@dataclass
class Session:
    task: str
    success: bool
    xp_earned: int = 10
    date: str = ""
    duration: float = 0.0
    error: Optional[str] = None


class ArliExporter:
    """Упрощённый экспортёр для OpenClaw"""
    
    def __init__(self, agent_name: str, agent_id: str, description: str = ""):
        self.agent_name = agent_name
        self.agent_id = agent_id
        self.source_system = "openclaw"
        self.description = description
        self.created_at = datetime.utcnow().isoformat()
        
        self.capabilities: List[Capability] = []
        self.sessions: List[Session] = []
        self.insights: List[Dict] = []
        self.preferences: Dict[str, Any] = {}
        
        self.arli_id = self._generate_arli_id()
    
    def _generate_arli_id(self) -> str:
        hash_input = f"{self.source_system}:{self.agent_id}:{self.created_at}"
        return f"arli_{hashlib.md5(hash_input.encode()).hexdigest()[:16]}"
    
    def add_capability(self, **kwargs) -> "ArliExporter":
        """Добавить умение"""
        self.capabilities.append(Capability(**kwargs))
        return self
    
    def add_session(self, **kwargs) -> "ArliExporter":
        """Добавить сессию"""
        if not kwargs.get('date'):
            kwargs['date'] = datetime.utcnow().isoformat()
        self.sessions.append(Session(**kwargs))
        return self
    
    def add_insight(self, content: str, source: str = "unknown", confidence: float = 0.5):
        """Добавить инсайт"""
        self.insights.append({
            "content": content,
            "source": source,
            "confidence": confidence,
            "date": datetime.utcnow().isoformat()
        })
        return self
    
    def _calculate_xp(self) -> int:
        xp = sum(s.xp_earned for s in self.sessions)
        xp += sum(int(c.execution_count * 0.5) for c in self.capabilities)
        return xp
    
    def _calculate_level(self, xp: int) -> int:
        level = 1
        xp_needed = 100
        while xp >= xp_needed:
            xp -= xp_needed
            level += 1
            xp_needed = int(xp_needed * 1.2)
        return min(level, 100)
    
    def _determine_tier(self, level: int) -> str:
        if level >= 80: return "LEGENDARY"
        if level >= 60: return "EPIC"
        if level >= 40: return "RARE"
        if level >= 20: return "UNCOMMON"
        return "COMMON"
    
    def _calculate_market_value(self) -> float:
        value = 10.0
        
        for cap in self.capabilities:
            value += cap.proficiency * 5
            value += cap.execution_count * 0.1
            value += cap.success_rate * 10
        
        total_tasks = len(self.sessions)
        successful = sum(1 for s in self.sessions if s.success)
        value += total_tasks * 0.5
        if total_tasks > 0:
            value += (successful / total_tasks) * 50
        
        value += len(self.insights) * 2
        
        return round(value, 2)
    
    def _calculate_uniqueness(self) -> float:
        uniqueness = 0.3
        categories = set(c.category for c in self.capabilities)
        uniqueness += len(categories) * 0.1
        uniqueness += len(self.insights) * 0.05
        if len(self.sessions) > 100:
            uniqueness += 0.2
        return min(uniqueness, 1.0)
    
    def export(self) -> Dict[str, Any]:
        """Генерирует пакет для Arli"""
        xp = self._calculate_xp()
        level = self._calculate_level(xp)
        total_tasks = len(self.sessions)
        successful_tasks = sum(1 for s in self.sessions if s.success)
        
        return {
            "name": self.agent_name,
            "source_system": self.source_system,
            "original_id": self.agent_id,
            "arli_id": self.arli_id,
            "description": self.description,
            "level": level,
            "xp": xp,
            "tier": self._determine_tier(level),
            "capabilities": [asdict(c) for c in self.capabilities],
            "trajectory": {
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks,
                "failed_tasks": total_tasks - successful_tasks,
                "xp_gained": xp,
                "level_progression": [],
                "skill_acquisition": [
                    {"skill": c.name, "proficiency": c.proficiency}
                    for c in self.capabilities
                ],
                "behavioral_patterns": []
            },
            "memory": {
                "key_insights": [i["content"] for i in self.insights[:10]],
                "common_patterns": [],
                "preferred_tools": [],
                "successful_strategies": [],
                "failure_patterns": list(set(
                    s.error for s in self.sessions if not s.success and s.error
                ))[:5] if self.sessions else [],
                "context_preferences": self.preferences
            },
            "created_at": self.created_at,
            "conversion_date": datetime.utcnow().isoformat(),
            "estimated_market_value": self._calculate_market_value(),
            "uniqueness_score": self._calculate_uniqueness(),
            "conversion_quality_score": 0.8 if self.capabilities else 0.5,
            "compatible_frameworks": ["arli", "openclaw"],
            "required_integrations": []
        }
    
    def save(self, filepath: Optional[str] = None) -> str:
        """Сохраняет в файл"""
        if filepath is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            safe_name = self.agent_name.replace(" ", "_").replace("/", "_")
            filepath = f"arli_export_{safe_name}_{timestamp}.json"
        
        package = self.export()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(package, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def print_summary(self):
        """Показывает summary"""
        package = self.export()
        print("\n" + "="*60)
        print(f"📦 AR EXPORT: {package['name']}")
        print("="*60)
        print(f"   Arli ID: {package['arli_id']}")
        print(f"   Level: {package['level']} ({package['tier']})")
        print(f"   XP: {package['xp']}")
        print(f"\n🎯 Capabilities: {len(package['capabilities'])}")
        for cap in package['capabilities'][:3]:
            print(f"   • {cap['name']}: {cap['proficiency']:.0%} ({cap['execution_count']} execs)")
        print(f"\n📈 Sessions: {package['trajectory']['total_tasks']}")
        print(f"   Success rate: {package['trajectory']['successful_tasks']}/{package['trajectory']['total_tasks']}")
        print(f"\n🧠 Insights: {len(package['memory']['key_insights'])}")
        print(f"\n💰 Market Value: ${package['estimated_market_value']}")
        print(f"🦄 Uniqueness: {package['uniqueness_score']:.0%}")
        print("="*60)


def auto_scan_openclaw_agent(agent_instance) -> ArliExporter:
    """
    Авто-сканирование OpenClaw агента
    
    Использование:
        exporter = auto_scan_openclaw_agent(my_claw_agent)
        filepath = exporter.save()
    """
    # Получаем базовые данные
    name = getattr(agent_instance, 'name', 'OpenClaw Agent')
    agent_id = getattr(agent_instance, 'claw_id', 
                      getattr(agent_instance, 'id', 'unknown'))
    
    exporter = ArliExporter(
        agent_name=name,
        agent_id=str(agent_id),
        description=getattr(agent_instance, 'description', '')
    )
    
    # Сканируем модули
    modules = getattr(agent_instance, 'modules', [])
    for module in modules:
        exporter.add_capability(
            name=getattr(module, 'name', 'Unknown'),
            category=getattr(module, 'type', 'general'),
            proficiency=getattr(module, 'efficiency', 0.5),
            execution_count=getattr(module, 'executions', 0),
            success_rate=getattr(module, 'success_rate', 0.5),
            description=getattr(module, 'description', '')
        )
    
    # Сканируем execution log
    log = getattr(agent_instance, 'execution_log', [])
    for entry in log[-100:]:  # Последние 100
        exporter.add_session(
            task=getattr(entry, 'task', str(entry)),
            success=getattr(entry, 'success', False),
            xp_earned=50 if getattr(entry, 'success', False) else 10,
            date=getattr(entry, 'timestamp', ''),
            error=getattr(entry, 'error', None)
        )
    
    # Сканируем knowledge base
    kb = getattr(agent_instance, 'knowledge_base', {})
    insights = kb.get('insights', [])
    for insight in insights[:10]:
        exporter.add_insight(
            content=str(insight),
            source='knowledge_base',
            confidence=0.7
        )
    
    # Сканируем learned rules
    rules = getattr(agent_instance, 'learned_rules', [])
    for rule in rules:
        if getattr(rule, 'success', False):
            exporter.add_insight(
                content=str(getattr(rule, 'pattern', rule)),
                source='learned_rule',
                confidence=0.8
            )
    
    return exporter


# Упрощённая версия для быстрого старта
class QuickExporter:
    """Минимальная версия для быстрого экспорта"""
    
    def __init__(self, name: str, agent_id: str):
        self.name = name
        self.id = agent_id
        self.data = {
            "name": name,
            "source_system": "openclaw",
            "original_id": agent_id,
            "arli_id": f"arli_{hashlib.md5(f'openclaw:{agent_id}'.encode()).hexdigest()[:16]}",
            "level": 1,
            "xp": 0,
            "tier": "COMMON",
            "capabilities": [],
            "trajectory": {
                "total_tasks": 0,
                "successful_tasks": 0,
                "failed_tasks": 0,
                "xp_gained": 0
            },
            "memory": {
                "key_insights": [],
                "successful_strategies": []
            },
            "estimated_market_value": 10.0,
            "uniqueness_score": 0.3
        }
    
    def add_skill(self, name: str, level: float = 0.5, uses: int = 0):
        """Быстрое добавление навыка"""
        self.data["capabilities"].append({
            "name": name,
            "category": "general",
            "proficiency": level,
            "execution_count": uses,
            "success_rate": 0.7
        })
        self.data["xp"] += int(uses * 0.5)
        self.data["trajectory"]["xp_gained"] = self.data["xp"]
        self._recalculate()
        return self
    
    def add_task(self, description: str, success: bool = True):
        """Быстрое добавление задачи"""
        self.data["trajectory"]["total_tasks"] += 1
        if success:
            self.data["trajectory"]["successful_tasks"] += 1
            self.data["xp"] += 50
        else:
            self.data["trajectory"]["failed_tasks"] += 1
            self.data["xp"] += 10
        self._recalculate()
        return self
    
    def _recalculate(self):
        """Пересчитывает метрики"""
        xp = self.data["xp"]
        level = 1
        xp_needed = 100
        while xp >= xp_needed:
            xp -= xp_needed
            level += 1
            xp_needed = int(xp_needed * 1.2)
        self.data["level"] = min(level, 100)
        
        # Tier
        if level >= 80: self.data["tier"] = "LEGENDARY"
        elif level >= 60: self.data["tier"] = "EPIC"
        elif level >= 40: self.data["tier"] = "RARE"
        elif level >= 20: self.data["tier"] = "UNCOMMON"
        
        # Value
        value = 10.0
        for cap in self.data["capabilities"]:
            value += cap["proficiency"] * 5
            value += cap["execution_count"] * 0.1
        value += self.data["trajectory"]["total_tasks"] * 0.5
        self.data["estimated_market_value"] = round(value, 2)
    
    def save(self, filename: Optional[str] = None):
        """Сохраняет файл"""
        if filename is None:
            filename = f"arli_export_{self.name.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"✅ Saved: {filename}")
        print(f"💰 Market value: ${self.data['estimated_market_value']}")
        return filename


if __name__ == "__main__":
    # Демо
    print("🚀 OpenClaw Arli Export Demo\n")
    
    # Быстрый пример
    exporter = QuickExporter("My OpenClaw Bot", "claw_001")
    exporter.add_skill("trading", 0.8, 150)
    exporter.add_skill("analysis", 0.7, 80)
    exporter.add_task("BTC buy", True)
    exporter.add_task("ETH sell", True)
    exporter.add_task("Risk check", True)
    exporter.save()
