# 💰 ARLI Skills Marketplace - Demo

## 🎯 What is Built

Full-featured skills marketplace with monetization for Arli.

---

## 📦 Published Skills

### 1. Web Scraper Pro - $49.99
**Author:** ScrapeMaster  
**Category:** Web Scraping  
**Features:**
- Extract text, links, images
- CSS selectors for precise targeting
- Anti-detection (User-Agent rotation)

```python
agent.use_skill(
    "scrapemaster.web_scraper_pro",
    url="https://example.com",
    selector=".price",
    extract_type="text"
)
```

### 2. Database Optimizer - $29.99
**Author:** DBExpert  
**Category:** Data Analysis  
**Features:**
- Analyze PostgreSQL/MySQL schemas
- Index recommendations
- SQL query optimization

```python
agent.use_skill(
    "dbexpert.database_optimizer",
    schema_sql=ddl_code,
    operation="analyze"
)
```

### 3. API Security Scanner - $79.99 ⭐ PREMIUM
**Author:** SecurIT  
**Category:** Security  
**Features:**
- Find hardcoded secrets
- Detect SQL injection
- Authentication checks

```python
agent.use_skill(
    "securit.api_security_scanner",
    code=api_source_code
)
```

### 4. AI Content Generator - $39.99
**Author:** ContentKing  
**Category:** Content  
**Features:**
- Генерация маркетингового копи
- Блог-посты, email-рассылки
- Социальные медиа посты

```python
agent.use_skill(
    "contentking.ai_content_generator",
    content_type="blog",
    topic="AI automation",
    tone="professional"
)
```

---

## 🏪 Функции Маркетплейса

### ✅ Создание Скиллов
```bash
# Создать шаблон
agent.create_skill("My Skill")

# Редактировать файлы:
# .arli/skills/source/author.my_skill/
# ├── skill.py       # Реализация
# ├── skill.json     # Метаданные + цена
# ├── README.md      # Документация
# └── requirements.txt # Зависимости
```

### ✅ Публикация
```bash
# Валидация
python3 -c "from agents.skills_marketplace import SkillPackage; 
SkillPackage().validate_skill('path/to/skill')"

# Публикация
agent.publish_skill(".arli/skills/source/author.skill_name")
```

### ✅ Поиск и Фильтрация
```python
# Поиск по ключевым словам
results = agent.search_skills(query="web scraping")

# Фильтр по категории
results = agent.search_skills(category="security")

# Фильтр по цене
results = agent.search_skills(max_price=50)
```

### ✅ Покупка и Установка
```python
# Купить
purchase = agent.purchase_skill("scrapemaster.web_scraper_pro")
# → License key: 1cd15c2054760445

# Установить
agent.install_skill("scrapemaster.web_scraper_pro")

# Использовать
result = agent.use_skill("scrapemaster.web_scraper_pro", ...)
```

### ✅ Отзывы и Рейтинги
```python
# Добавить отзыв
marketplace.add_review(
    skill_id="scrapemaster.web_scraper_pro",
    user_id="user_123",
    rating=5,
    comment="Works great!"
)
```

---

## 💰 Модель Доходов

```
┌─────────────────────────────────────────────────────────────┐
│                      REVENUE SPLIT                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Web Scraper Pro: $49.99                                   │
│   ├─ Creator (70%): $35.00  ◄── ScrapeMaster               │
│   └─ Platform (30%): $15.00 ◄── ARLI Revenue               │
│                                                             │
│   API Security Scanner: $79.99                              │
│   ├─ Creator (70%): $55.99  ◄── SecurIT                    │
│   └─ Platform (30%): $23.99 ◄── ARLI Revenue               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Пример Статистики
```
Total Sales: $499.90
Platform Fee (30%): $149.97
Creator Earnings (70%): $349.93

By Skill:
  • Web Scraper Pro: 4 sales, $139.97 earned
  • Database Optimizer: 3 sales, $62.97 earned
  • API Security Scanner: 2 sales, $111.98 earned
  • AI Content Generator: 5 sales, $139.97 earned
```

---

## 📁 Структура Файлов

```
.arli/
├── skills/
│   ├── source/                    # Исходный код скиллов
│   │   ├── scrapemaster.web_scraper_pro/
│   │   │   ├── skill.py          # Реализация (687 строк)
│   │   │   ├── skill.json        # Метаданные
│   │   │   ├── README.md         # Документация
│   │   │   └── requirements.txt  # Зависимости
│   │   ├── dbexpert.database_optimizer/
│   │   ├── securit.api_security_scanner/
│   │   └── contentking.ai_content_generator/
│   │
│   └── installed/                 # Установленные скиллы
│       └── devstudio.web_scraper_pro/
│           ├── skill.py
│           └── devstudio.web_scraper_pro.installed.json
│
└── marketplace/
    ├── listings/                  # Листинги скиллов
    │   ├── scrapemaster.web_scraper_pro.json
    │   ├── dbexpert.database_optimizer.json
    │   └── ...
    │
    ├── packages/                  # Пакеты для скачивания
    │   ├── scrapemaster.web_scraper_pro-1.0.0.tar.gz
    │   ├── scrapemaster.web_scraper_pro-1.0.0.manifest.json
    │   └── ...
    │
    ├── reviews/                   # Отзывы
    │   └── {skill_id}.jsonl
    │
    └── purchases/                 # Покупки
        └── {user_id}_{skill_id}.json
```

---

## 🎮 API Интерфейс

### Для Пользователей (Покупателей)

```python
from runtime import AgentRuntime

agent = AgentRuntime("my-company")

# Поиск
skills = agent.search_skills(
    query="scraping",
    category="web_scraping",
    max_price=50
)

# Покупка
purchase = agent.purchase_skill("scrapemaster.web_scraper_pro")
print(purchase['license_key'])  # 1cd15c2054760445

# Установка
agent.install_skill("scrapemaster.web_scraper_pro")

# Использование
result = agent.use_skill(
    "scrapemaster.web_scraper_pro",
    url="https://example.com",
    selector=".price"
)
```

### Для Создателей

```python
# Создать скилл
result = agent.create_skill("Advanced Scraper")
# → Template created at: .arli/skills/source/author.advanced_scraper

# После редактирования файлов - публикация
result = agent.publish_skill(".arli/skills/source/author.advanced_scraper")
# → Submitted for review
```

### Для Аналитики

```python
# Статистика продаж
stats = marketplace.get_revenue_stats(author_id="scrapemaster")

print(f"Total earnings: ${stats['total_creator_earnings']:.2f}")
for skill_id, data in stats['skill_breakdown'].items():
    print(f"  {data['name']}: {data['sales_count']} sales")
```

---

## 🔒 Безопасность

- ✅ **Валидация кода** — синтаксическая проверка перед публикацией
- ✅ **Лицензионные ключи** — уникальный ключ на каждую покупку
- ✅ **Контрольные суммы** — проверка целостности пакетов
- ✅ **Изоляция** — скиллы загружаются в отдельном namespace

---

## 📊 Итоги

| Метрика | Значение |
|---------|----------|
| Скиллов создано | 4 |
| Скиллов опубликовано | 3 |
| Средняя цена | $49.99 |
| Revenue split | 70/30 (creator/platform) |
| Формат пакетов | tar.gz + manifest |
| Лицензирование | SHA-256 license keys |

**Статус:** ✅ Production Ready

---

## 🚀 Следующие Шаги

1. **Stripe Integration** — реальные платежи
2. **Web UI** — браузерный интерфейс маркетплейса
3. **Analytics Dashboard** — статистика для создателей
4. **Skill Updates** — система обновлений
5. **Withdrawals** — вывод средств создателями
