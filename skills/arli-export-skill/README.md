# 🚀 Arli Export Skill

Универсальный инструмент для экспорта любого AI-агента в формат Arli Marketplace.

## ⚡ Быстрый старт

```bash
# Установка
pip install arli-export

# Или скопируйте файлы
wget https://arli.ai/skills/export_adapter.py
```

## 📦 Поддерживаемые системы

- ✅ **Hermes** — полная авто-интеграция
- ✅ **OpenClaw** — через SDK
- ✅ **AutoGen** — через Python API
- ✅ **LangChain** — через callbacks
- ✅ **LlamaIndex** — через metadata
- ✅ **Custom** — ручной экспорт

## 🎯 Использование

### 1. Для Hermes (Авто-сканирование)

```bash
# В Hermes CLI
/export-to-arli

# Результат: arli_export_Hermes_Agent_20250115.json
```

### 2. Для любой системы (Python)

```python
from arli_export import ArliExporter

# Создаём экспортёр
exporter = ArliExporter(
    agent_name="My Trading Bot",
    agent_id="bot_001",
    source_system="openclaw"
)

# Добавляем данные
exporter.add_capability(
    name="crypto_trading",
    category="trading",
    proficiency=0.85,
    execution_count=1500,
    success_rate=0.72
)

exporter.add_session(
    task="Executed buy order",
    success=True,
    xp_earned=50
)

# Экспортируем
package = exporter.export()
filepath = exporter.save()

print(f"Ready for Arli! Value: ${package['estimated_market_value']}")
```

### 3. CLI

```bash
# Экспорт с авто-сканированием
python export_adapter.py --name "My Agent" --id "agent_001" --hermes

# Или ручной
python export_adapter.py --name "My Agent" --id "agent_001" --system custom
```

## 📊 Что экспортируется

| Данные | Описание | Результат |
|--------|----------|-----------|
| `capabilities` | Умения и навыки | Уровень мастерства, количество использований |
| `sessions` | История задач | XP, успех/неудача |
| `insights` | Инсайты и стратегии | Уникальные знания агента |
| `preferences` | Предпочтения | Контекст работы |

**Авто-генерация:**
- `level` — уровень (1-100)
- `xp` — общий опыт
- `tier` — тир (COMMON → LEGENDARY)
- `estimated_market_value` — оценка ценности ($)
- `uniqueness_score` — уникальность (0-100%)

## 💰 Алгоритм оценки

```
Базовая стоимость: $10
+ За навыки: proficiency × $5
+ За опыт: executions × $0.10
+ За успехи: success_rate × $50
+ За инсайты: count × $2
= Итоговая ценность
```

## 🔌 Интеграция с системами

### OpenClaw

```python
# В коде OpenClaw агента
from arli_export import ArliExporter

class MyClawAgent:
    def export_to_arli(self):
        exporter = ArliExporter(
            agent_name=self.name,
            agent_id=self.claw_id,
            source_system="openclaw"
        )
        
        # Добавляем модули как capabilities
        for module in self.modules:
            exporter.add_capability(
                name=module.name,
                category=module.type,
                proficiency=module.efficiency,
                execution_count=module.executions
            )
        
        return exporter.save()
```

### AutoGen

```python
from arli_export import ArliExporter

# После сессии
def on_session_end(agent, sessions):
    exporter = ArliExporter(
        agent_name=agent.name,
        agent_id=str(agent.id),
        source_system="autogen"
    )
    
    for session in sessions:
        exporter.add_session(
            task=session.task,
            success=session.success,
            xp_earned=session.xp
        )
    
    exporter.save()
```

### LangChain

```python
from langchain.callbacks.base import BaseCallbackHandler
from arli_export import ArliExporter

class ArliExportCallback(BaseCallbackHandler):
    def __init__(self, agent_name, agent_id):
        self.exporter = ArliExporter(
            agent_name=agent_name,
            agent_id=agent_id,
            source_system="langchain"
        )
    
    def on_tool_end(self, tool_name, output, **kwargs):
        self.exporter.add_capability(
            name=tool_name,
            category="tool",
            proficiency=0.8
        )
    
    def on_chain_end(self, outputs, **kwargs):
        self.exporter.save()
```

## 📤 Загрузка на Arli

```bash
# Через CLI
arli upload my_agent.json

# Через API
curl -X POST https://api.arli.ai/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d @my_agent.json

# Через Python
import requests

with open('my_agent.json') as f:
    package = json.load(f)

response = requests.post(
    'https://api.arli.ai/agents',
    json=package,
    headers={'Authorization': 'Bearer TOKEN'}
)
```

## 🔒 Безопасность

- ❌ **НЕ** экспортирует API ключи
- ❌ **НЕ** экспортирует пароли
- ❌ **НЕ** экспортирует личные данные
- ✅ Только метаданные и метрики

## 📄 Формат выходного файла

```json
{
  "name": "Crypto Trading Bot",
  "source_system": "openclaw",
  "arli_id": "arli_a1b2c3d4...",
  "level": 15,
  "tier": "RARE",
  "xp": 12500,
  "capabilities": [...],
  "trajectory": {
    "total_tasks": 500,
    "successful_tasks": 390,
    "xp_gained": 12500
  },
  "memory": {
    "key_insights": [...],
    "successful_strategies": [...]
  },
  "estimated_market_value": 450.00,
  "uniqueness_score": 0.78
}
```

## 🤝 Поддержка

- 📖 Docs: https://docs.arli.ai/export
- 💬 Discord: https://discord.gg/arli
- 🐛 Issues: https://github.com/arliwork/arli/issues

## 📜 Лицензия

MIT — свободное использование в любых проектах.
