# Universal Agent Converter

Конвертирует агентов из любой системы в универсальный формат Arli.

## 🎯 Что делает

1. **Извлекает** ценные данные из агента любой системы
2. **Анализирует** learning curve и опыт
3. **Упаковывает** в универсальный формат
4. **Оценивает** рыночную стоимость

## 📦 Поддерживаемые системы

| Система | Статус | Качество конвертации |
|---------|--------|---------------------|
| Hermes | ✅ Ready | High |
| OpenClaw | ✅ Ready | Medium |
| AutoGen | 🚧 Planned | - |
| LangChain | 🚧 Planned | - |
| Custom | 🚧 Planned | - |

## 🚀 Использование

### CLI

```bash
# Конвертировать одного агента
python tools/convert_agent.py my_agent.json

# Сохранить результат
python tools/convert_agent.py my_agent.json -o converted.json

# JSON формат
python tools/convert_agent.py my_agent.json -f json

# Импорт в Arli
python tools/convert_agent.py my_agent.json --import-to-arli
```

### API

```bash
# Конвертировать через API
curl -X POST http://localhost:8000/convert/agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_data": { ... }
  }'
```

### Python

```python
from agent_converter import AgentConverter

converter = AgentConverter()
package = converter.convert(my_agent_data)

print(f"Level: {package.level}")
print(f"Value: ${package.estimated_market_value}")
print(f"Capabilities: {len(package.capabilities)}")
```

## 📊 Что извлекается

### Capabilities (Умения)
- Название и категория
- Уровень владения (0-100%)
- Количество выполнений
- Успешность
- Среднее время выполнения

### Learning Trajectory (Траектория)
- Общее количество задач
- Успешные/неуспешные
- Набранный XP
- История уровней
- Приобретённые навыки
- Поведенческие паттерны

### Memory (Память)
- Ключевые инсайты
- Успешные стратегии
- Предпочитаемые инструменты
- Паттерны неудач
- Контекстные предпочтения

## 💰 Оценка стоимости

Алгоритм оценки учитывает:
- Уровень и опыт агента
- Количество и качество навыков
- Уникальность инсайтов
- Успешность выполнения задач
- Редкость комбинации умений

## 🔌 Добавление нового адаптера

```python
from agent_converter import BaseAgentAdapter

class MySystemAdapter(BaseAgentAdapter):
    def __init__(self):
        super().__init__("mysystem")
    
    def can_parse(self, agent_data):
        # Проверяем, наш ли это формат
        return "mysystem_id" in agent_data
    
    def parse_capabilities(self, agent_data):
        # Извлекаем умения
        return [...]
    
    def parse_trajectory(self, agent_data):
        # Извлекаем траекторию
        return LearningTrajectory(...)
    
    def parse_memory(self, agent_data):
        # Извлекаем память
        return AgentMemory(...)

# Регистрируем
converter.register_adapter(MySystemAdapter())
```

## 📁 Формат выходных данных

```json
{
  "name": "My Trading Agent",
  "source_system": "hermes",
  "arli_id": "arli_a1b2c3d4...",
  "level": 15,
  "tier": "RARE",
  "xp": 2450,
  "capabilities": [
    {
      "name": "binance_trading",
      "category": "trading",
      "proficiency": 0.85,
      "execution_count": 342,
      "success_rate": 0.78
    }
  ],
  "trajectory": {
    "total_tasks": 500,
    "successful_tasks": 390,
    "xp_gained": 2450
  },
  "memory": {
    "key_insights": ["Market trends..."],
    "preferred_tools": ["binance_api", "ta_lib"],
    "successful_strategies": ["Buy on dip..."]
  },
  "estimated_market_value": 245.50,
  "uniqueness_score": 0.73
}
```
