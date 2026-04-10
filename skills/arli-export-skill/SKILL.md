# Arli Export Skill

Универсальный skill для экспорта агента в формат Arli Marketplace. Любой агент (Hermes, OpenClaw, AutoGen, etc.) может использовать этот skill для создания пакета данных, готового к продаже.

## 🎯 Что делает

1. **Сканирует** данные агента (память, навыки, историю)
2. **Извлекает** ценные метрики (XP, успехи, инсайты)
3. **Упаковывает** в стандартный Arli JSON
4. **Оценивает** рыночную стоимость

## 📦 Установка

### Для Hermes Agent:

```bash
# Копируем skill в папку skills
cp -r arli-export-skill ~/.hermes/skills/

# Или через Hermes CLI
hermes skills install arli-export
```

### Для других систем:

Скопируйте файл `export_adapter.py` в проект и используйте как модуль.

## 🚀 Использование

### Вариант 1: Через команду

```bash
# Hermes
/hermes export-to-arli

# Результат: arli_package_2025-01-15.json
```

### Вариант 2: Программно

```python
from arli_export import ArliExporter

# Создаём экспортёр
exporter = ArliExporter(
    agent_name="My Trading Bot",
    agent_id="bot_001",
    source_system="hermes"  # или "openclaw", "autogen", etc.
)

# Добавляем данные
exporter.add_skill(
    name="crypto_trading",
    category="trading",
    proficiency=0.85,
    executions=1500,
    success_rate=0.72
)

exporter.add_session(
    task="Executed buy order",
    success=True,
    xp_earned=50
)

exporter.add_insight(
    content="BTC dips on Sunday evenings",
    source="pattern_analysis"
)

# Генерируем пакет
package = exporter.export()

# Сохраняем
with open("my_agent_arli.json", "w") as f:
    json.dump(package, f, indent=2)
```

### Вариант 3: Авто-сканирование (Hermes)

```python
# Автоматически сканирует fabric, sessions, skills
from arli_export import HermesAutoScanner

scanner = HermesAutoScanner()
package = scanner.scan_and_export(
    fabric_path="~/.hermes/fabric/",
    sessions_path="~/.hermes/sessions/"
)

print(f"Агент готов к продаже! Ценность: ${package['estimated_market_value']}")
```

## 📊 Что экспортируется

### Обязательные поля:
- `name` — название агента
- `source_system` — исходная система (hermes, openclaw, etc.)
- `capabilities` — список умений

### Опциональные поля:
- `session_history` — история задач
- `insights` — ключевые инсайты
- `preferences` — предпочтения
- `performance_metrics` — метрики производительности

### Авто-генерируемые:
- `arli_id` — уникальный ID в Arli
- `level` — уровень (вычисляется из XP)
- `xp` — общий опыт
- `tier` — тир (COMMON, UNCOMMON, RARE, EPIC, LEGENDARY)
- `estimated_market_value` — оценочная стоимость
- `uniqueness_score` — уникальность (0-100%)

## 💰 Алгоритм оценки стоимости

```python
base_value = 10

# За навыки
for skill in capabilities:
    value += skill.proficiency * 5
    value += skill.executions * 0.1

# За опыт
value += total_tasks * 0.5
value += success_rate * 50

# За уникальность
value += unique_insights * 2
value += successful_strategies * 3
```

## 🔌 Интеграция с Arli

После экспорта:

```bash
# Загрузить на marketplace
arli upload my_agent_arli.json

# Или через API
curl -X POST https://api.arli.ai/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d @my_agent_arli.json
```

## 📁 Структура пакета

```json
{
  "name": "Crypto Trading Bot",
  "source_system": "hermes",
  "arli_id": "arli_a1b2c3d4...",
  "level": 15,
  "tier": "RARE",
  "xp": 12500,
  "capabilities": [...],
  "trajectory": {...},
  "memory": {...},
  "estimated_market_value": 450.00,
  "uniqueness_score": 0.78
}
```

## 🛠️ Для разработчиков

### Добавить поддержку новой системы:

```python
from arli_export import BaseExporter

class MySystemExporter(BaseExporter):
    def scan_agent(self, agent_instance):
        # Ваша логика сканирования
        self.add_skill(...)
        self.add_session(...)
        return self.export()
```

## 🔒 Безопасность

- ❌ **НЕ** экспортирует API ключи
- ❌ **НЕ** экспортирует пароли
- ❌ **НЕ** экспортирует личные данные пользователей
- ✅ Экспортирует только метаданные и метрики

## 📄 Лицензия

MIT - свободное использование в любых проектах.
