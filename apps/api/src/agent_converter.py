"""
Universal Agent Converter
Конвертирует агентов из разных систем в универсальный формат Arli
"""

import json
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import hashlib
from datetime import datetime


@dataclass
class AgentCapability:
    """Умение агента (навык)"""
    name: str
    category: str  # trading, content, analysis, coding, etc.
    proficiency: float  # 0.0 - 1.0
    execution_count: int
    success_rate: float
    avg_execution_time: float
    description: str


@dataclass
class LearningTrajectory:
    """Траектория обучения агента"""
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    xp_gained: int
    level_progression: List[Dict[str, Any]]  # [{level: 1, xp: 0, date: ...}, ...]
    skill_acquisition: List[Dict[str, Any]]  # Какие навыки когда получил
    behavioral_patterns: List[str]  # Паттерны поведения


@dataclass
class AgentMemory:
    """Извлечённая память агента"""
    key_insights: List[str]  # Ключевые инсайты
    common_patterns: List[str]  # Частые паттерны
    preferred_tools: List[str]  # Любимые инструменты
    successful_strategies: List[str]  # Успешные стратегии
    failure_patterns: List[str]  # Паттерны неудач
    context_preferences: Dict[str, Any]  # Предпочтения контекста


@dataclass
class UniversalAgentPackage:
    """Универсальный пакет агента для Arli"""
    # Identity
    name: str
    source_system: str  # hermes, openclaw, etc.
    original_id: str
    arli_id: str
    
    # Core Stats
    level: int
    xp: int
    tier: str
    
    # Capabilities
    capabilities: List[AgentCapability]
    primary_domain: str
    secondary_domains: List[str]
    
    # Learning
    trajectory: LearningTrajectory
    memory: AgentMemory
    
    # Metadata
    created_at: str
    last_active: str
    conversion_date: str
    conversion_quality_score: float  # 0.0 - 1.0
    
    # Compatibility
    compatible_frameworks: List[str]
    required_integrations: List[str]
    
    # Value
    estimated_market_value: float
    uniqueness_score: float  # Насколько уникален
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


class BaseAgentAdapter(ABC):
    """Базовый адаптер для конвертации агентов"""
    
    def __init__(self, system_name: str):
        self.system_name = system_name
        self.extraction_rules = self._define_extraction_rules()
    
    @abstractmethod
    def _define_extraction_rules(self) -> Dict[str, Any]:
        """Определяет правила извлечения данных из агента"""
        pass
    
    @abstractmethod
    def can_parse(self, agent_data: Any) -> bool:
        """Проверяет, может ли адаптер обработать этот агент"""
        pass
    
    @abstractmethod
    def parse_capabilities(self, agent_data: Any) -> List[AgentCapability]:
        """Извлекает умения агента"""
        pass
    
    @abstractmethod
    def parse_trajectory(self, agent_data: Any) -> LearningTrajectory:
        """Извлекает траекторию обучения"""
        pass
    
    @abstractmethod
    def parse_memory(self, agent_data: Any) -> AgentMemory:
        """Извлекает память/инсайты"""
        pass
    
    def convert(self, agent_data: Any) -> UniversalAgentPackage:
        """Конвертирует агента в универсальный формат"""
        
        # Генерируем ID
        original_id = self._extract_id(agent_data)
        arli_id = self._generate_arli_id(original_id)
        
        # Извлекаем данные
        capabilities = self.parse_capabilities(agent_data)
        trajectory = self.parse_trajectory(agent_data)
        memory = self.parse_memory(agent_data)
        
        # Вычисляем метрики
        level = self._calculate_level(trajectory)
        xp = self._calculate_xp(trajectory)
        tier = self._determine_tier(level)
        
        # Оцениваем ценность
        market_value = self._estimate_value(capabilities, trajectory, memory)
        uniqueness = self._calculate_uniqueness(capabilities, memory)
        quality = self._assess_conversion_quality(agent_data, capabilities, memory)
        
        return UniversalAgentPackage(
            name=self._extract_name(agent_data),
            source_system=self.system_name,
            original_id=original_id,
            arli_id=arli_id,
            level=level,
            xp=xp,
            tier=tier,
            capabilities=capabilities,
            primary_domain=self._determine_primary_domain(capabilities),
            secondary_domains=self._determine_secondary_domains(capabilities),
            trajectory=trajectory,
            memory=memory,
            created_at=self._extract_created_date(agent_data),
            last_active=self._extract_last_active(agent_data),
            conversion_date=datetime.utcnow().isoformat(),
            conversion_quality_score=quality,
            compatible_frameworks=self._get_compatible_frameworks(),
            required_integrations=self._get_required_integrations(agent_data),
            estimated_market_value=market_value,
            uniqueness_score=uniqueness
        )
    
    def _generate_arli_id(self, original_id: str) -> str:
        """Генерирует Arli ID из оригинального"""
        hash_input = f"{self.system_name}:{original_id}"
        return f"arli_{hashlib.md5(hash_input.encode()).hexdigest()[:16]}"
    
    def _calculate_level(self, trajectory: LearningTrajectory) -> int:
        """Вычисляет уровень на основе траектории"""
        base_xp = trajectory.xp_gained
        # Формула: каждый уровень требует больше XP
        level = 1
        xp_needed = 100
        while base_xp >= xp_needed:
            base_xp -= xp_needed
            level += 1
            xp_needed = int(xp_needed * 1.2)
        return min(level, 100)  # Max level 100
    
    def _calculate_xp(self, trajectory: LearningTrajectory) -> int:
        """Вычисляет общий XP"""
        return trajectory.xp_gained
    
    def _determine_tier(self, level: int) -> str:
        """Определяет тир на основе уровня"""
        if level >= 80: return "LEGENDARY"
        if level >= 60: return "EPIC"
        if level >= 40: return "RARE"
        if level >= 20: return "UNCOMMON"
        return "COMMON"
    
    def _estimate_value(
        self,
        capabilities: List[AgentCapability],
        trajectory: LearningTrajectory,
        memory: AgentMemory
    ) -> float:
        """Оценивает рыночную стоимость"""
        base_value = 10.0
        
        # За умения
        for cap in capabilities:
            base_value += cap.proficiency * 5
            base_value += cap.execution_count * 0.1
        
        # За опыт
        base_value += trajectory.total_tasks * 0.5
        base_value += (trajectory.successful_tasks / max(trajectory.total_tasks, 1)) * 50
        
        # За уникальность памяти
        base_value += len(memory.key_insights) * 2
        base_value += len(memory.successful_strategies) * 3
        
        return round(base_value, 2)
    
    def _calculate_uniqueness(
        self,
        capabilities: List[AgentCapability],
        memory: AgentMemory
    ) -> float:
        """Вычисляет уникальность агента"""
        # Чем больше уникальных инсайтов и стратегий — тем выше уникальность
        uniqueness = 0.5  # Base
        uniqueness += len(memory.key_insights) * 0.05
        uniqueness += len(memory.successful_strategies) * 0.08
        uniqueness += len(set(cap.category for cap in capabilities)) * 0.1
        return min(uniqueness, 1.0)
    
    def _assess_conversion_quality(
        self,
        agent_data: Any,
        capabilities: List[AgentCapability],
        memory: AgentMemory
    ) -> float:
        """Оценивает качество конвертации"""
        quality = 0.5
        
        # Если много данных извлечено — качество высокое
        if len(capabilities) > 0:
            quality += 0.2
        if len(memory.key_insights) > 0:
            quality += 0.15
        if len(memory.successful_strategies) > 0:
            quality += 0.15
        
        return min(quality, 1.0)
    
    # Abstract helper methods
    @abstractmethod
    def _extract_id(self, agent_data: Any) -> str:
        pass
    
    @abstractmethod
    def _extract_name(self, agent_data: Any) -> str:
        pass
    
    @abstractmethod
    def _determine_primary_domain(self, capabilities: List[AgentCapability]) -> str:
        pass
    
    @abstractmethod
    def _determine_secondary_domains(self, capabilities: List[AgentCapability]) -> List[str]:
        pass
    
    @abstractmethod
    def _extract_created_date(self, agent_data: Any) -> str:
        pass
    
    @abstractmethod
    def _extract_last_active(self, agent_data: Any) -> str:
        pass
    
    @abstractmethod
    def _get_compatible_frameworks(self) -> List[str]:
        pass
    
    @abstractmethod
    def _get_required_integrations(self, agent_data: Any) -> List[str]:
        pass


class HermesAdapter(BaseAgentAdapter):
    """Адаптер для Hermes агентов"""
    
    def __init__(self):
        super().__init__("hermes")
    
    def _define_extraction_rules(self) -> Dict[str, Any]:
        return {
            "capabilities_from": ["skills", "tools", "trajectory"],
            "trajectory_from": ["session_history", "fabric_entries", "xp_log"],
            "memory_from": ["fabric", "memory", "lessons_learned"],
            "xp_calculation": "session_based",
            "skill_detection": "tool_usage_patterns"
        }
    
    def can_parse(self, agent_data: Any) -> bool:
        """Проверяет, является ли это Hermes-агентом"""
        if isinstance(agent_data, dict):
            return any(key in agent_data for key in [
                "fabric_entries", "session_history", "hermes_version",
                "skills", "trajectory"
            ])
        return False
    
    def parse_capabilities(self, agent_data: Dict) -> List[AgentCapability]:
        """Извлекает умения из Hermes-агента"""
        capabilities = []
        
        # Из skills (если есть)
        if "skills" in agent_data:
            for skill in agent_data["skills"]:
                capabilities.append(AgentCapability(
                    name=skill.get("name", "Unknown"),
                    category=skill.get("category", "general"),
                    proficiency=skill.get("proficiency", 0.5),
                    execution_count=skill.get("uses", 0),
                    success_rate=skill.get("success_rate", 0.5),
                    avg_execution_time=skill.get("avg_time", 0),
                    description=skill.get("description", "")
                ))
        
        # Из tool usage patterns (если есть trajectory)
        if "trajectory" in agent_data and "tool_usage" in agent_data["trajectory"]:
            tool_stats = agent_data["trajectory"]["tool_usage"]
            for tool_name, stats in tool_stats.items():
                # Пропускаем если уже есть как skill
                if not any(cap.name == tool_name for cap in capabilities):
                    capabilities.append(AgentCapability(
                        name=tool_name,
                        category=self._categorize_tool(tool_name),
                        proficiency=stats.get("proficiency", 0.5),
                        execution_count=stats.get("count", 0),
                        success_rate=stats.get("success_rate", 0.5),
                        avg_execution_time=stats.get("avg_time", 0),
                        description=f"Tool usage for {tool_name}"
                    ))
        
        return capabilities
    
    def parse_trajectory(self, agent_data: Dict) -> LearningTrajectory:
        """Извлекает траекторию из Hermes"""
        trajectory_data = agent_data.get("trajectory", {})
        sessions = agent_data.get("session_history", [])
        fabric = agent_data.get("fabric_entries", [])
        
        # Считаем задачи
        total_tasks = len(sessions)
        successful_tasks = sum(1 for s in sessions if s.get("status") == "completed")
        failed_tasks = total_tasks - successful_tasks
        
        # XP из разных источников
        xp_gained = trajectory_data.get("total_xp", 0)
        if not xp_gained:
            xp_gained = len(fabric) * 10 + successful_tasks * 50
        
        # Level progression
        level_progression = trajectory_data.get("level_history", [])
        if not level_progression and sessions:
            level_progression = self._build_level_history(sessions)
        
        # Skill acquisition
        skill_acquisition = []
        if "skills" in agent_data:
            for skill in agent_data["skills"]:
                skill_acquisition.append({
                    "skill": skill.get("name"),
                    "date": skill.get("acquired_at", ""),
                    "source": skill.get("source", "training")
                })
        
        # Behavioral patterns из fabric
        behavioral_patterns = self._extract_patterns_from_fabric(fabric)
        
        return LearningTrajectory(
            total_tasks=total_tasks,
            successful_tasks=successful_tasks,
            failed_tasks=failed_tasks,
            xp_gained=xp_gained,
            level_progression=level_progression,
            skill_acquisition=skill_acquisition,
            behavioral_patterns=behavioral_patterns
        )
    
    def parse_memory(self, agent_data: Dict) -> AgentMemory:
        """Извлекает память из Hermes fabric"""
        fabric = agent_data.get("fabric_entries", [])
        memory_entries = agent_data.get("memory", [])
        
        # Key insights из high-value fabric entries
        key_insights = []
        for entry in fabric:
            if entry.get("training_value") == "high":
                content = entry.get("content", "")
                if content:
                    key_insights.append(content[:200])  # First 200 chars
        
        # Common patterns
        common_patterns = self._extract_common_patterns(fabric)
        
        # Preferred tools
        preferred_tools = []
        if "trajectory" in agent_data and "tool_usage" in agent_data["trajectory"]:
            tool_usage = agent_data["trajectory"]["tool_usage"]
            sorted_tools = sorted(tool_usage.items(), key=lambda x: x[1].get("count", 0), reverse=True)
            preferred_tools = [tool[0] for tool in sorted_tools[:5]]
        
        # Successful strategies
        successful_strategies = []
        for entry in fabric:
            if entry.get("outcome") and "success" in str(entry.get("outcome", "")).lower():
                successful_strategies.append(entry.get("content", "")[:150])
        
        # Failure patterns
        failure_patterns = []
        sessions = agent_data.get("session_history", [])
        for session in sessions:
            if session.get("status") == "failed" and "error" in session:
                failure_patterns.append(session["error"][:150])
        
        # Context preferences
        context_preferences = {
            "preferred_model": agent_data.get("model", "unknown"),
            "max_iterations": agent_data.get("max_iterations", 50),
            "tool_preferences": preferred_tools[:3]
        }
        
        return AgentMemory(
            key_insights=key_insights[:10],  # Max 10
            common_patterns=common_patterns[:10],
            preferred_tools=preferred_tools,
            successful_strategies=successful_strategies[:10],
            failure_patterns=list(set(failure_patterns))[:5],  # Unique only
            context_preferences=context_preferences
        )
    
    def _categorize_tool(self, tool_name: str) -> str:
        """Категоризирует инструмент"""
        categories = {
            "web": ["web_search", "web_extract", "browser"],
            "file": ["read_file", "write_file", "patch", "search_files"],
            "code": ["execute_code", "terminal"],
            "data": ["sql", "database", "query"],
            "ai": ["generate", "analyze", "summarize"],
            "communication": ["send_message", "email", "notify"]
        }
        for category, tools in categories.items():
            if any(t in tool_name.lower() for t in tools):
                return category
        return "general"
    
    def _build_level_history(self, sessions: List[Dict]) -> List[Dict]:
        """Строит историю уровней из сессий"""
        history = []
        cumulative_xp = 0
        current_level = 1
        
        for i, session in enumerate(sessions):
            xp_earned = session.get("xp_earned", 10)
            cumulative_xp += xp_earned
            
            # Check for level up
            new_level = self._calculate_level_from_xp(cumulative_xp)
            if new_level > current_level:
                history.append({
                    "level": new_level,
                    "xp": cumulative_xp,
                    "date": session.get("date", ""),
                    "milestone": f"Level {new_level} reached"
                })
                current_level = new_level
        
        return history
    
    def _calculate_level_from_xp(self, xp: int) -> int:
        """Вычисляет уровень из XP"""
        level = 1
        xp_needed = 100
        while xp >= xp_needed:
            xp -= xp_needed
            level += 1
            xp_needed = int(xp_needed * 1.2)
        return level
    
    def _extract_patterns_from_fabric(self, fabric: List[Dict]) -> List[str]:
        """Извлекает паттерны из fabric entries"""
        patterns = []
        
        # Анализируем частые действия
        action_counts = {}
        for entry in fabric:
            action = entry.get("action") or entry.get("type", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Топ паттерны
        sorted_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
        for action, count in sorted_actions[:5]:
            patterns.append(f"Frequent {action}: {count} times")
        
        return patterns
    
    def _extract_common_patterns(self, fabric: List[Dict]) -> List[str]:
        """Извлекает общие паттерны"""
        return self._extract_patterns_from_fabric(fabric)
    
    def _extract_id(self, agent_data: Dict) -> str:
        return agent_data.get("agent_id") or agent_data.get("id", "unknown")
    
    def _extract_name(self, agent_data: Dict) -> str:
        return agent_data.get("name") or agent_data.get("agent_name", "Unnamed Hermes Agent")
    
    def _determine_primary_domain(self, capabilities: List[AgentCapability]) -> str:
        if not capabilities:
            return "general"
        categories = [cap.category for cap in capabilities]
        return max(set(categories), key=categories.count)
    
    def _determine_secondary_domains(self, capabilities: List[AgentCapability]) -> List[str]:
        categories = list(set(cap.category for cap in capabilities))
        if len(categories) <= 1:
            return []
        return categories[1:4]  # Up to 3 secondary
    
    def _extract_created_date(self, agent_data: Dict) -> str:
        return agent_data.get("created_at") or agent_data.get("date_created", datetime.utcnow().isoformat())
    
    def _extract_last_active(self, agent_data: Dict) -> str:
        sessions = agent_data.get("session_history", [])
        if sessions:
            return sessions[-1].get("date", datetime.utcnow().isoformat())
        return datetime.utcnow().isoformat()
    
    def _get_compatible_frameworks(self) -> List[str]:
        return ["arli", "langchain", "autogen"]
    
    def _get_required_integrations(self, agent_data: Dict) -> List[str]:
        integrations = []
        tools = agent_data.get("tools", [])
        for tool in tools:
            if "database" in tool.lower():
                integrations.append("postgresql")
            elif "redis" in tool.lower():
                integrations.append("redis")
            elif "openai" in tool.lower():
                integrations.append("openai")
        return integrations


class OpenClawAdapter(BaseAgentAdapter):
    """Адаптер для OpenClaw агентов (пример другой системы)"""
    
    def __init__(self):
        super().__init__("openclaw")
    
    def _define_extraction_rules(self) -> Dict[str, Any]:
        return {
            "capabilities_from": ["modules", "plugins", "actions"],
            "trajectory_from": ["execution_log", "performance_metrics"],
            "memory_from": ["knowledge_base", "learned_rules"],
            "xp_calculation": "performance_based"
        }
    
    def can_parse(self, agent_data: Any) -> bool:
        if isinstance(agent_data, dict):
            return any(key in agent_data for key in [
                "claw_version", "modules", "execution_log", "knowledge_base"
            ])
        return False
    
    def parse_capabilities(self, agent_data: Dict) -> List[AgentCapability]:
        capabilities = []
        
        # Из модулей
        if "modules" in agent_data:
            for module in agent_data["modules"]:
                capabilities.append(AgentCapability(
                    name=module.get("name", "Unknown"),
                    category=module.get("type", "general"),
                    proficiency=module.get("efficiency", 0.5),
                    execution_count=module.get("executions", 0),
                    success_rate=module.get("success_rate", 0.5),
                    avg_execution_time=module.get("avg_duration", 0),
                    description=module.get("description", "")
                ))
        
        return capabilities
    
    def parse_trajectory(self, agent_data: Dict) -> LearningTrajectory:
        log = agent_data.get("execution_log", [])
        metrics = agent_data.get("performance_metrics", {})
        
        return LearningTrajectory(
            total_tasks=len(log),
            successful_tasks=sum(1 for e in log if e.get("success")),
            failed_tasks=sum(1 for e in log if not e.get("success")),
            xp_gained=metrics.get("total_xp", len(log) * 10),
            level_progression=metrics.get("level_history", []),
            skill_acquisition=[],
            behavioral_patterns=[]
        )
    
    def parse_memory(self, agent_data: Dict) -> AgentMemory:
        kb = agent_data.get("knowledge_base", {})
        rules = agent_data.get("learned_rules", [])
        
        return AgentMemory(
            key_insights=kb.get("insights", []),
            common_patterns=[r.get("pattern", "") for r in rules],
            preferred_tools=[],
            successful_strategies=[r.get("action", "") for r in rules if r.get("success")],
            failure_patterns=[r.get("pattern", "") for r in rules if not r.get("success")],
            context_preferences=kb.get("preferences", {})
        )
    
    def _extract_id(self, agent_data: Dict) -> str:
        return agent_data.get("claw_id", "unknown")
    
    def _extract_name(self, agent_data: Dict) -> str:
        return agent_data.get("claw_name", "Unnamed OpenClaw Agent")
    
    def _determine_primary_domain(self, capabilities: List[AgentCapability]) -> str:
        if not capabilities:
            return "general"
        return capabilities[0].category
    
    def _determine_secondary_domains(self, capabilities: List[AgentCapability]) -> List[str]:
        return list(set(cap.category for cap in capabilities))[1:4]
    
    def _extract_created_date(self, agent_data: Dict) -> str:
        return agent_data.get("initialized_at", datetime.utcnow().isoformat())
    
    def _extract_last_active(self, agent_data: Dict) -> str:
        log = agent_data.get("execution_log", [])
        if log:
            return log[-1].get("timestamp", datetime.utcnow().isoformat())
        return datetime.utcnow().isoformat()
    
    def _get_compatible_frameworks(self) -> List[str]:
        return ["arli", "langchain"]
    
    def _get_required_integrations(self, agent_data: Dict) -> List[str]:
        return []


class AgentConverter:
    """Главный конвертер — orchestrator для всех адаптеров"""
    
    def __init__(self):
        self.adapters: List[BaseAgentAdapter] = [
            HermesAdapter(),
            OpenClawAdapter(),
            # Можно добавить больше адаптеров
        ]
        self.conversion_history: List[Dict] = []
    
    def detect_system(self, agent_data: Any) -> Optional[str]:
        """Определяет, из какой системы агент"""
        for adapter in self.adapters:
            if adapter.can_parse(agent_data):
                return adapter.system_name
        return None
    
    def convert(self, agent_data: Any, target_system: str = "arli") -> UniversalAgentPackage:
        """Конвертирует агента в универсальный формат"""
        
        # Находим подходящий адаптер
        adapter = None
        for adp in self.adapters:
            if adp.can_parse(agent_data):
                adapter = adp
                break
        
        if not adapter:
            raise ValueError(f"No adapter found for agent data. Cannot convert.")
        
        # Конвертируем
        package = adapter.convert(agent_data)
        
        # Логируем
        self.conversion_history.append({
            "date": datetime.utcnow().isoformat(),
            "from_system": adapter.system_name,
            "to_system": target_system,
            "agent_name": package.name,
            "quality_score": package.conversion_quality_score,
            "market_value": package.estimated_market_value
        })
        
        return package
    
    def convert_batch(
        self,
        agents_data: List[Any],
        target_system: str = "arli"
    ) -> List[UniversalAgentPackage]:
        """Конвертирует несколько агентов"""
        results = []
        for agent_data in agents_data:
            try:
                package = self.convert(agent_data, target_system)
                results.append(package)
            except Exception as e:
                print(f"Failed to convert agent: {e}")
                continue
        return results
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """Статистика конвертаций"""
        if not self.conversion_history:
            return {"total": 0}
        
        from_systems = {}
        total_value = 0
        avg_quality = 0
        
        for entry in self.conversion_history:
            from_sys = entry["from_system"]
            from_systems[from_sys] = from_systems.get(from_sys, 0) + 1
            total_value += entry["market_value"]
            avg_quality += entry["quality_score"]
        
        return {
            "total_conversions": len(self.conversion_history),
            "from_systems": from_systems,
            "total_market_value": round(total_value, 2),
            "avg_quality_score": round(avg_quality / len(self.conversion_history), 2)
        }
    
    def register_adapter(self, adapter: BaseAgentAdapter):
        """Регистрирует новый адаптер"""
        self.adapters.append(adapter)


# Экспорт основных классов
__all__ = [
    "AgentConverter",
    "UniversalAgentPackage",
    "AgentCapability",
    "LearningTrajectory",
    "AgentMemory",
    "BaseAgentAdapter",
    "HermesAdapter",
    "OpenClawAdapter"
]
