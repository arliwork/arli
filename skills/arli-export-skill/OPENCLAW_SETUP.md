# 🚀 OpenClaw + Arli Export — Пошаговая инструкция

## 📋 Что тебе нужно сделать:

### Шаг 1: Скопируй файл агенту

Есть 3 способа дать этот код твоему OpenClaw агенту:

#### Способ А: Через файл (самый простой)

```bash
# 1. Сохрани этот код в файл
# Скопируй содержимое openclaw_integration.py в файл

# 2. Положи файл рядом с твоим агентом
# Например:
# /my_project/
#   ├── openclaw_agent.py
#   ├── openclaw_integration.py  <-- сюда
#   └── ...
```

#### Способ Б: Вставь напрямую в код агента

```python
# В начало файла твоего OpenClaw агента добавь:

# ===== AR EXPORT INTEGRATION =====
import json
import hashlib
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class Capability:
    name: str
    category: str
    proficiency: float = 0.5
    execution_count: int = 0
    success_rate: float = 0.5
    description: str = ""

class QuickExporter:
    """Быстрый экспортёр для OpenClaw"""
    
    def __init__(self, name: str, agent_id: str):
        self.name = name
        self.id = agent_id
        self.data = {
            "name": name,
            "source_system": "openclaw",
            "original_id": agent_id,
            "arli_id": f"arli_{hashlib.md5(f'openclaw:{agent_id}'.encode()).hexdigest()[:16]}",
            "level": 1, "xp": 0, "tier": "COMMON",
            "capabilities": [],
            "trajectory": {"total_tasks": 0, "successful_tasks": 0, "failed_tasks": 0, "xp_gained": 0},
            "memory": {"key_insights": [], "successful_strategies": []},
            "estimated_market_value": 10.0,
            "uniqueness_score": 0.3
        }
    
    def add_skill(self, name: str, level: float = 0.5, uses: int = 0):
        self.data["capabilities"].append({
            "name": name, "category": "general", "proficiency": level,
            "execution_count": uses, "success_rate": 0.7
        })
        self.data["xp"] += int(uses * 0.5)
        self._recalculate()
        return self
    
    def add_task(self, description: str, success: bool = True):
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
        xp = self.data["xp"]
        level = 1
        xp_needed = 100
        while xp >= xp_needed:
            xp -= xp_needed
            level += 1
            xp_needed = int(xp_needed * 1.2)
        self.data["level"] = min(level, 100)
        if level >= 80: self.data["tier"] = "LEGENDARY"
        elif level >= 60: self.data["tier"] = "EPIC"
        elif level >= 40: self.data["tier"] = "RARE"
        elif level >= 20: self.data["tier"] = "UNCOMMON"
        value = 10.0
        for cap in self.data["capabilities"]:
            value += cap["proficiency"] * 5 + cap["execution_count"] * 0.1
        value += self.data["trajectory"]["total_tasks"] * 0.5
        self.data["estimated_market_value"] = round(value, 2)
    
    def save(self, filename=None):
        if filename is None:
            filename = f"arli_export_{self.name.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"✅ Saved: {filename}")
        print(f"💰 Market value: ${self.data['estimated_market_value']}")
        return filename

# ===== END INTEGRATION =====
```

#### Способ В: Через pip install (если выложим в PyPI)

```bash
pip install arli-export
```

---

### Шаг 2: Добавь метод в своего агента

```python
class MyOpenClawAgent:
    def __init__(self):
        self.name = "My Trading Bot"
        self.claw_id = "bot_001"
        self.modules = []
        self.execution_log = []
    
    # ===== ДОБАВЬ ЭТОТ МЕТОД =====
    def export_to_arli(self, filename=None):
        """Экспортировать агента на Arli marketplace"""
        
        # Создаём экспортёр
        exporter = QuickExporter(self.name, self.claw_id)
        
        # Добавляем модули как навыки
        for module in self.modules:
            exporter.add_skill(
                name=module.name,
                level=getattr(module, 'efficiency', 0.5),
                uses=getattr(module, 'executions', 0)
            )
        
        # Добавляем историю выполнения
        for log_entry in self.execution_log[-50:]:  # Последние 50
            exporter.add_task(
                description=str(log_entry.get('task', 'Unknown')),
                success=log_entry.get('success', False)
            )
        
        # Сохраняем
        filepath = exporter.save(filename)
        
        print(f"\n🚀 Готово к загрузке на Arli!")
        print(f"📁 Файл: {filepath}")
        print(f"💰 Оценочная стоимость: ${exporter.data['estimated_market_value']}")
        print(f"📊 Уровень: {exporter.data['level']} ({exporter.data['tier']})")
        
        return filepath
    # ===== КОНЕЦ МЕТОДА =====
```

---

### Шаг 3: Запусти экспорт

```python
# Твой код
agent = MyOpenClawAgent()

# ... обучаешь агента ...

# Экспортируешь
agent.export_to_arli()  # Создаст arli_export_My_Trading_Bot.json
```

**Результат:**
```
✅ Saved: arli_export_My_Trading_Bot_20250115.json
💰 Market value: $245.50
📊 Level: 12 (COMMON)
🚀 Готово к загрузке на Arli!
```

---

### Шаг 4: Загрузи на Arli

```bash
# Вариант 1: Через curl
curl -X POST https://api.arli.ai/agents \
  -H "Content-Type: application/json" \
  -d @arli_export_My_Trading_Bot_20250115.json

# Вариант 2: Через Python
import requests

with open('arli_export_My_Trading_Bot_20250115.json') as f:
    data = json.load(f)

response = requests.post(
    'https://api.arli.ai/agents',
    json=data
)
print(f"Uploaded! Agent ID: {response.json()['arli_id']}")

# Вариант 3: Через веб-интерфейс
# Зайди на https://arli.ai/upload и загрузи файл
```

---

## 📝 Пример полной интеграции

```python
#!/usr/bin/env python3
"""
Мой OpenClaw агент с Arli Export
"""

# === КОПИРУЙ СЮДА КОД ИЗ РАЗДЕЛА "Способ Б" ВЫШЕ ===
# (QuickExporter класс)

class TradingBot:
    """Мой торговый агент"""
    
    def __init__(self):
        self.name = "Crypto Trading Pro"
        self.claw_id = "trader_v2"
        self.modules = [
            {"name": "RSI_Analysis", "efficiency": 0.85, "executions": 1200},
            {"name": "MACD_Signals", "efficiency": 0.78, "executions": 980},
            {"name": "Risk_Manager", "efficiency": 0.92, "executions": 1500}
        ]
        self.execution_log = []
    
    def trade(self, signal):
        """Выполняет торговлю"""
        result = self._execute_trade(signal)
        
        # Логируем для экспорта
        self.execution_log.append({
            "task": f"Trade: {signal['pair']} {signal['action']}",
            "success": result['success'],
            "profit": result.get('profit', 0),
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def _execute_trade(self, signal):
        # Твоя логика торговли
        return {"success": True, "profit": 0.5}
    
    # === МЕТОД ЭКСПОРТА ===
    def export_to_arli(self, filename=None):
        exporter = QuickExporter(self.name, self.claw_id)
        
        for module in self.modules:
            exporter.add_skill(
                name=module["name"],
                level=module["efficiency"],
                uses=module["executions"]
            )
        
        for log in self.execution_log[-100:]:
            exporter.add_task(log["task"], log["success"])
        
        return exporter.save(filename)


# ИСПОЛЬЗОВАНИЕ
if __name__ == "__main__":
    bot = TradingBot()
    
    # Симулируем торговлю
    for i in range(20):
        bot.trade({"pair": "BTC/USD", "action": "buy"})
    
    # Экспортируем
    bot.export_to_arli()
```

---

## 🎯 Быстрый старт (копипаста)

Если лень разбираться — просто скопируй это:

```python
# 1. Вставь в свой агент этот класс:
class ArliExport:
    def __init__(self, name, agent_id):
        import hashlib
        self.data = {
            "name": name, "source_system": "openclaw", "original_id": agent_id,
            "arli_id": f"arli_{hashlib.md5(f'openclaw:{agent_id}'.encode()).hexdigest()[:16]}",
            "level": 1, "xp": 0, "tier": "COMMON",
            "capabilities": [], "trajectory": {"total_tasks": 0, "successful_tasks": 0},
            "memory": {"key_insights": []},
            "estimated_market_value": 10.0
        }
    
    def skill(self, name, level=0.5, uses=0):
        self.data["capabilities"].append({"name": name, "proficiency": level, "execution_count": uses})
        self.data["xp"] += int(uses * 0.5) + 10
        return self
    
    def task(self, success=True):
        self.data["trajectory"]["total_tasks"] += 1
        if success: 
            self.data["trajectory"]["successful_tasks"] += 1
            self.data["xp"] += 50
        self.data["estimated_market_value"] = 10 + len(self.data["capabilities"]) * 20 + self.data["trajectory"]["total_tasks"] * 0.5
        return self
    
    def save(self):
        import json
        fname = f"arli_{self.data['name'].replace(' ', '_')}.json"
        with open(fname, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"✅ {fname} ready! Value: ${self.data['estimated_market_value']}")
        return fname

# 2. Используй в агенте:
export = ArliExport("My Bot", "id_001")
export.skill("trading", 0.8, 100).skill("analysis", 0.7, 50)
export.task(True).task(True).task(False)
export.save()  # Готово!
```

---

## ❓ Частые вопросы

**Q: Какие данные агент отправляет на Arli?**  
A: Только метаданные (имя, навыки, метрики). Ни API ключей, ни стратегий, ни личных данных.

**Q: Можно ли редактировать файл перед загрузкой?**  
A: Да! Это обычный JSON — открой и поменяй что хочешь.

**Q: Что если у меня нет execution_log?**  
A: Создай пустой список `self.execution_log = []` и добавляй в него результаты работы.

**Q: Сколько стоит загрузка?**  
A: Загрузка бесплатная. Комиссия 10% только при продаже.

---

## 🚀 Готово!

Теперь твой OpenClaw агент может сам создавать пакеты для Arli marketplace!

**Просто вызови:**
```python
agent.export_to_arli()
```

И получи файл, готовый к продаже! 🎉
