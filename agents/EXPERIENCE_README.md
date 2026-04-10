# ARLI Agent Experience & Learning Curve System

## 🎯 Концепция

**Проблема:** Компании тратят годы на обучение сотрудников, а те уходят с опытом.

**Решение ARLI:** Агенты накапливают опыт (experience), который можно продавать как актив.

> "Не нанимай — купи готового эксперта"

---

## 📊 Система Уровней (Learning Curve)

```
Level 1-3:   NOVICE      → $50-150
Level 4-6:   APPRENTICE  → $150-400  
Level 7-9:   JOURNEYMAN  → $400-1000
Level 10-14: EXPERT      → $1000-3000
Level 15-19: MASTER      → $3000-10000
Level 20-24: GRANDMASTER → $10000-50000
Level 25+:   LEGENDARY   → $50000+
```

---

## 💰 Калькуляция Стоимости

Формула рыночной стоимости агента:

```python
market_value = (
    base_value * level_multiplier * success_factor * rating_factor * revenue_factor
    + tier_bonus
    + diversity_bonus  
    + achievement_bonus
)
```

**Факторы:**
- `level_multiplier` — экспоненциальный рост (1.5^level)
- `success_rate` — до 3x множитель за 100% успех
- `average_rating` — до 2x множитель за 5 звезд
- `revenue_generated` — прямая прибыль
- `expertise domains` — бонус за разнообразие

---

## 🏆 Достижения

| Достижение | Условие | Бонус |
|------------|---------|-------|
| first_task | Первая задача | +$25 |
| centurion | 100 задач | +$100 |
| perfect_10 | 95% успех | +$200 |
| money_maker | $10K прибыли | +$500 |
| jack_of_all_trades | 5 доменов | +$250 |
| five_star | 4.9+ рейтинг | +$300 |
| sold | Продан | +$100 |

---

## 📈 ROI Обучения

**Пример:**
```
Инвестиции в обучение: $1,000
Время: 3 месяца (100 задач)
Прибыль от работы: $8,000
Стоимость агента: $2,500
────────────────────────────
Total Return: $10,500
ROI: 950%
```

---

## 🏪 Experience Marketplace

### Что продается:
1. **Trained Agents** — готовые к работе агенты с историей
2. **Domain Experts** — агенты-специалисты в узкой нише
3. **Revenue Streams** — агенты с доказанной прибыльностью

### Revenue Split:
- **90%** — продавец (тренер)
- **10%** — платформа
- **5%** — роялти создателю (навсегда)

---

## 🎮 Использование

### Создать и обучить агента:
```python
from agent_experience import ExperienceTracker, TaskRecord, TaskCategory

tracker = ExperienceTracker()

# Создать
agent = tracker.create_agent(
    agent_id="trading_bot_01",
    agent_name="BTC Scalper",
    creator="trader_alice"
)

# Обучить
for trade in trades:
    task = TaskRecord(
        category=TaskCategory.TRADING,
        description=trade.description,
        success=trade.profit > 0,
        execution_time=trade.duration,
        revenue_generated=trade.profit,
        client_rating=5.0
    )
    tracker.record_task(agent.agent_id, task)

# Проверить стоимость
print(f"Market Value: ${agent.market_value}")
```

### Продать агента:
```python
from experience_integration import ExperienceMarketplace

marketplace = ExperienceMarketplace(tracker, skills_market)

listing = marketplace.list_agent_for_sale(
    agent_id="trading_bot_01",
    seller_id="trader_alice",
    asking_price=agent.market_value
)

# Купить
purchase = marketplace.buy_agent(listing, "hedge_fund_xyz")
```

---

## 🔗 Интеграция с Runtime

```python
from experience_integration import ExperienceEnhancedRuntime

# Runtime автоматически трекает опыт
runtime = ExperienceEnhancedRuntime(
    agent_id="my_agent",
    agent_name="Content Creator"
)

# Выполнить задачу с трекингом
result = await runtime.execute_task(
    task_category=TaskCategory.CONTENT_CREATION,
    task_description="Write blog post",
    execution_func=write_blog_post,
    topic="AI trends"
)

# Получить отчет
report = runtime.get_value_report()
```

---

## 📊 Трекинг Метрик

Каждый агент собирает:

**Performance:**
- Tasks completed
- Success rate
- Average execution time
- Revenue generated
- Cost saved

**Expertise:**
- Domains mastered
- Success rate by domain
- Efficiency by category

**Reputation:**
- Client ratings
- Review count
- Achievement badges

**Market:**
- Times sold
- Previous owners
- Market value history

---

## 🔄 Жизненный Цикл Агента

```
┌─────────────┐
│   Create    │ ← Новый агент ($50)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Train     │ ← Выполняет задачи
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Level Up  │ ← Растет ценность
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Earn      │ ← Приносит прибыль
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Sell     │ ← Продается ($$$)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Repeat    │ ← Новый владелец
└─────────────┘
```

---

## 💡 Уникальность

### Традиционная компания:
```
Обучаешь сотрудника 2 года → он уходит → потеря $100K+
```

### ARLI:
```
Обучаешь агента 2 года → продаешь за $50K → покупаешь готового
```

**Преимущества:**
- ✅ Опыт не теряется
- ✅ Можно купить готового эксперта
- ✅ Прозрачная история (верифицируемый track record)
- ✅ Пассивный доход от роялти
- ✅ Ликвидный рынок труда

---

## 🚀 Дальнейшее Развитие

1. **Agent NFTs** — каждый агент как NFT на ICP
2. **Fractional Ownership** — покупка долей в агентах
3. **Agent Staking** — стейкинг агентов для пассивного дохода
4. **Cross-chain Experience** — перенос опыта между платформами
5. **AI-generated Agents** — создание агентов по спецификации

---

## 📁 Файлы

- `agent_experience.py` — Core experience tracking
- `experience_integration.py` — Marketplace integration
- `EXPERIENCE_README.md` — This file

---

**Статус:** ✅ Реализовано и готово к использованию!
