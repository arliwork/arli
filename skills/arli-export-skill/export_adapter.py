"""
Arli Export Adapter
Универсальный модуль для экспорта агентов в формат Arli
"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
import os


@dataclass
class Capability:
    """Умение агента"""
    name: str
    category: str
    proficiency: float = 0.5  # 0.0 - 1.0
    execution_count: int = 0
    success_rate: float = 0.5
    avg_execution_time: float = 0.0
    description: str = ""


@dataclass
class Session:
    """Сессия/задача агента"""
    task: str
    success: bool
    xp_earned: int = 10
    date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    duration: float = 0.0
    error: Optional[str] = None


@dataclass
class Insight:
    """Инсайт/стратегия агента"""
    content: str
    source: str = "unknown"  # pattern, learning, decision
    confidence: float = 0.5
    date: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ArliExporter:
    """Универсальный экспортёр агентов"""
    
    def __init__(
        self,
        agent_name: str,
        agent_id: str,
        source_system: str = "unknown",
        description: str = ""
    ):
        self.agent_name = agent_name
        self.agent_id = agent_id
        self.source_system = source_system
        self.description = description
        self.created_at = datetime.utcnow().isoformat()
        
        # Данные для заполнения
        self.capabilities: List[Capability] = []
        self.sessions: List[Session] = []
        self.insights: List[Insight] = []
        self.preferences: Dict[str, Any] = {}
        self.additional_data: Dict[str, Any] = {}
        
        # Генерируем Arli ID
        self.arli_id = self._generate_arli_id()
    
    def _generate_arli_id(self) -> str:
        """Генерирует уникальный Arli ID"""
        hash_input = f"{self.source_system}:{self.agent_id}:{self.created_at}"
        return f"arli_{hashlib.md5(hash_input.encode()).hexdigest()[:16]}"
    
    def add_capability(
        self,
        name: str,
        category: str = "general",
        proficiency: float = 0.5,
        execution_count: int = 0,
        success_rate: float = 0.5,
        avg_execution_time: float = 0.0,
        description: str = ""
    ) -> "ArliExporter":
        """Добавляет умение"""
        self.capabilities.append(Capability(
            name=name,
            category=category,
            proficiency=proficiency,
            execution_count=execution_count,
            success_rate=success_rate,
            avg_execution_time=avg_execution_time,
            description=description
        ))
        return self
    
    def add_session(
        self,
        task: str,
        success: bool,
        xp_earned: int = 10,
        date: Optional[str] = None,
        duration: float = 0.0,
        error: Optional[str] = None
    ) -> "ArliExporter":
        """Добавляет сессию"""
        self.sessions.append(Session(
            task=task,
            success=success,
            xp_earned=xp_earned,
            date=date or datetime.utcnow().isoformat(),
            duration=duration,
            error=error
        ))
        return self
    
    def add_insight(
        self,
        content: str,
        source: str = "unknown",
        confidence: float = 0.5
    ) -> "ArliExporter":
        """Добавляет инсайт"""
        self.insights.append(Insight(
            content=content,
            source=source,
            confidence=confidence
        ))
        return self
    
    def add_preference(self, key: str, value: Any) -> "ArliExporter":
        """Добавляет предпочтение"""
        self.preferences[key] = value
        return self
    
    def add_data(self, key: str, value: Any) -> "ArliExporter":
        """Добавляет произвольные данные"""
        self.additional_data[key] = value
        return self
    
    def _calculate_xp(self) -> int:
        """Вычисляет общий XP"""
        xp = 0
        # XP за сессии
        for session in self.sessions:
            xp += session.xp_earned
        # XP за умения
        for cap in self.capabilities:
            xp += int(cap.execution_count * 0.5)
        return xp
    
    def _calculate_level(self, xp: int) -> int:
        """Вычисляет уровень из XP"""
        level = 1
        xp_needed = 100
        while xp >= xp_needed:
            xp -= xp_needed
            level += 1
            xp_needed = int(xp_needed * 1.2)
        return min(level, 100)
    
    def _determine_tier(self, level: int) -> str:
        """Определяет тир"""
        if level >= 80:
            return "LEGENDARY"
        elif level >= 60:
            return "EPIC"
        elif level >= 40:
            return "RARE"
        elif level >= 20:
            return "UNCOMMON"
        return "COMMON"
    
    def _calculate_market_value(self) -> float:
        """Оценивает рыночную стоимость"""
        value = 10.0  # Базовая стоимость
        
        # За умения
        for cap in self.capabilities:
            value += cap.proficiency * 5
            value += cap.execution_count * 0.1
            value += cap.success_rate * 10
        
        # За опыт
        total_tasks = len(self.sessions)
        successful_tasks = sum(1 for s in self.sessions if s.success)
        value += total_tasks * 0.5
        if total_tasks > 0:
            value += (successful_tasks / total_tasks) * 50
        
        # За инсайты
        value += len(self.insights) * 2
        high_confidence_insights = sum(1 for i in self.insights if i.confidence > 0.7)
        value += high_confidence_insights * 5
        
        return round(value, 2)
    
    def _calculate_uniqueness(self) -> float:
        """Вычисляет уникальность"""
        uniqueness = 0.3  # Базовая
        
        # Уникальные комбинации умений
        categories = set(cap.category for cap in self.capabilities)
        uniqueness += len(categories) * 0.1
        
        # Уникальные инсайты
        uniqueness += len(self.insights) * 0.05
        
        # Опыт
        if len(self.sessions) > 100:
            uniqueness += 0.2
        
        return min(uniqueness, 1.0)
    
    def _build_trajectory(self) -> Dict[str, Any]:
        """Строит объект траектории"""
        total_tasks = len(self.sessions)
        successful_tasks = sum(1 for s in self.sessions if s.success)
        failed_tasks = total_tasks - successful_tasks
        xp_gained = self._calculate_xp()
        
        # Level progression
        level_progression = []
        cumulative_xp = 0
        current_level = 1
        for session in self.sessions[:20]:  # Last 20 sessions max
            cumulative_xp += session.xp_earned
            new_level = self._calculate_level(cumulative_xp)
            if new_level > current_level:
                level_progression.append({
                    "level": new_level,
                    "xp": cumulative_xp,
                    "date": session.date,
                    "milestone": f"Level {new_level} reached"
                })
                current_level = new_level
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "xp_gained": xp_gained,
            "level_progression": level_progression,
            "skill_acquisition": [
                {"skill": cap.name, "proficiency": cap.proficiency}
                for cap in self.capabilities
            ],
            "behavioral_patterns": self._extract_patterns()
        }
    
    def _extract_patterns(self) -> List[str]:
        """Извлекает поведенческие паттерны"""
        patterns = []
        
        # Паттерны из категорий
        categories = {}
        for cap in self.capabilities:
            categories[cap.category] = categories.get(cap.category, 0) + 1
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            patterns.append(f"Frequent {cat}: {count} capabilities")
        
        # Паттерны успеха
        if self.sessions:
            success_rate = sum(1 for s in self.sessions if s.success) / len(self.sessions)
            if success_rate > 0.8:
                patterns.append("High reliability agent")
            elif success_rate < 0.5:
                patterns.append("Experimental/high-risk agent")
        
        return patterns[:5]
    
    def _build_memory(self) -> Dict[str, Any]:
        """Строит объект памяти"""
        successful_strategies = [
            i.content for i in self.insights
            if i.confidence > 0.6
        ]
        
        failure_patterns = [
            s.error for s in self.sessions
            if not s.success and s.error
        ]
        
        preferred_tools = list(set(
            cap.name for cap in self.capabilities
            if cap.execution_count > 10
        ))
        
        return {
            "key_insights": [i.content for i in self.insights[:10]],
            "common_patterns": self._extract_patterns(),
            "preferred_tools": preferred_tools[:5],
            "successful_strategies": successful_strategies[:10],
            "failure_patterns": list(set(failure_patterns))[:5],
            "context_preferences": self.preferences
        }
    
    def export(self) -> Dict[str, Any]:
        """Генерирует финальный пакет"""
        xp = self._calculate_xp()
        level = self._calculate_level(xp)
        
        return {
            "name": self.agent_name,
            "source_system": self.source_system,
            "original_id": self.agent_id,
            "arli_id": self.arli_id,
            "description": self.description,
            "level": level,
            "xp": xp,
            "tier": self._determine_tier(level),
            "capabilities": [asdict(cap) for cap in self.capabilities],
            "trajectory": self._build_trajectory(),
            "memory": self._build_memory(),
            "created_at": self.created_at,
            "conversion_date": datetime.utcnow().isoformat(),
            "estimated_market_value": self._calculate_market_value(),
            "uniqueness_score": self._calculate_uniqueness(),
            "conversion_quality_score": self._assess_quality(),
            "additional_data": self.additional_data
        }
    
    def _assess_quality(self) -> float:
        """Оценивает качество экспорта"""
        quality = 0.3
        if self.capabilities:
            quality += 0.2
        if len(self.sessions) > 5:
            quality += 0.2
        if self.insights:
            quality += 0.15
        if self.preferences:
            quality += 0.15
        return min(quality, 1.0)
    
    def save(self, filepath: Optional[str] = None) -> str:
        """Сохраняет пакет в файл"""
        if filepath is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filepath = f"arli_export_{self.agent_name.replace(' ', '_')}_{timestamp}.json"
        
        package = self.export()
        with open(filepath, 'w') as f:
            json.dump(package, f, indent=2, default=str)
        
        return filepath
    
    def get_summary(self) -> str:
        """Возвращает текстовое summary"""
        package = self.export()
        
        lines = [
            "=" * 60,
            f"📦 AR EXPORT: {package['name']}",
            "=" * 60,
            f"   Arli ID: {package['arli_id']}",
            f"   Level: {package['level']} ({package['tier']})",
            f"   XP: {package['xp']}",
            f"",
            f"🎯 Capabilities: {len(package['capabilities'])}",
            f"📈 Sessions: {package['trajectory']['total_tasks']}",
            f"🧠 Insights: {len(package['memory']['key_insights'])}",
            f"",
            f"💰 Market Value: ${package['estimated_market_value']}",
            f"🦄 Uniqueness: {package['uniqueness_score']:.0%}",
            f"✅ Quality: {package['conversion_quality_score']:.0%}",
            "=" * 60
        ]
        
        return "\n".join(lines)


class HermesAutoScanner:
    """Авто-сканер для Hermes агентов"""
    
    def __init__(self):
        self.exporter: Optional[ArliExporter] = None
    
    def scan(
        self,
        fabric_path: str = "~/.hermes/fabric/",
        sessions_path: str = "~/.hermes/sessions/",
        config_path: str = "~/.hermes/config.yaml"
    ) -> ArliExporter:
        """Сканирует Hermes данные и создаёт экспортёр"""
        
        fabric_path = os.path.expanduser(fabric_path)
        
        # Создаём экспортёр
        self.exporter = ArliExporter(
            agent_name="Hermes Agent",
            agent_id=f"hermes_{datetime.utcnow().strftime('%Y%m%d')}",
            source_system="hermes"
        )
        
        # Сканируем fabric (если есть)
        if os.path.exists(fabric_path):
            self._scan_fabric(fabric_path)
        
        # Добавляем стандартные навыки Hermes
        self._add_hermes_capabilities()
        
        return self.exporter
    
    def _scan_fabric(self, fabric_path: str):
        """Сканирует fabric entries"""
        try:
            import glob
            fabric_files = glob.glob(os.path.join(fabric_path, "**/*.json"), recursive=True)
            
            for filepath in fabric_files[:50]:  # Max 50 entries
                try:
                    with open(filepath, 'r') as f:
                        entry = json.load(f)
                    
                    # Извлекаем инсайты из high-value entries
                    if entry.get('training_value') == 'high' or entry.get('outcome'):
                        content = entry.get('content', '') or entry.get('summary', '')
                        if content:
                            self.exporter.add_insight(
                                content=content[:200],
                                source=entry.get('type', 'fabric'),
                                confidence=0.8 if entry.get('outcome') else 0.5
                            )
                    
                    # Добавляем сессию
                    if entry.get('type') == 'task' and entry.get('status'):
                        self.exporter.add_session(
                            task=entry.get('summary', 'Unknown task'),
                            success=entry.get('status') == 'completed',
                            xp_earned=50 if entry.get('status') == 'completed' else 10
                        )
                        
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Warning: Could not scan fabric: {e}")
    
    def _add_hermes_capabilities(self):
        """Добавляет стандартные Hermes capabilities"""
        hermes_tools = [
            ("terminal", "code", 0.9),
            ("web_search", "web", 0.85),
            ("browser_navigate", "web", 0.88),
            ("execute_code", "code", 0.92),
            ("read_file", "file", 0.95),
            ("write_file", "file", 0.90),
            ("patch", "file", 0.85),
            ("search_files", "file", 0.88),
        ]
        
        for tool_name, category, proficiency in hermes_tools:
            self.exporter.add_capability(
                name=tool_name,
                category=category,
                proficiency=proficiency,
                execution_count=100,  # Placeholder
                success_rate=0.85
            )
    
    def scan_and_export(
        self,
        fabric_path: str = "~/.hermes/fabric/",
        sessions_path: str = "~/.hermes/sessions/"
    ) -> Dict[str, Any]:
        """Сканирует и экспортирует"""
        exporter = self.scan(fabric_path, sessions_path)
        return exporter.export()


# CLI интерфейс
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Export agent to Arli format")
    parser.add_argument("--name", required=True, help="Agent name")
    parser.add_argument("--id", required=True, help="Agent ID")
    parser.add_argument("--system", default="unknown", help="Source system")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--hermes", action="store_true", help="Auto-scan Hermes data")
    
    args = parser.parse_args()
    
    if args.hermes:
        print("🔍 Scanning Hermes data...")
        scanner = HermesAutoScanner()
        exporter = scanner.scan()
        print(f"✅ Scanned {len(exporter.sessions)} sessions")
    else:
        exporter = ArliExporter(
            agent_name=args.name,
            agent_id=args.id,
            source_system=args.system
        )
    
    # Export
    package = exporter.export()
    filepath = exporter.save(args.output)
    
    print(exporter.get_summary())
    print(f"\n💾 Saved to: {filepath}")
    print(f"\n🚀 Upload to Arli:")
    print(f"   curl -X POST https://api.arli.ai/agents -d @{filepath}")


if __name__ == "__main__":
    main()
