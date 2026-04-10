# 🚀 Arli Marketplace Launch Guide

## ✅ Что создано:

### 1. Backend API (`apps/api/src/marketplace_server.py`)
- **POST /agents/upload** — загрузка агента
- **GET /agents** — список всех агентов
- **POST /agents/{id}/buy** — покупка агента
- **GET /stats** — статистика маркетплейса

### 2. Frontend (`apps/web/marketplace.html`)
- Красивый UI для просмотра агентов
- Drag-and-drop загрузка
- Фильтры и поиск
- Кнопки покупки

---

## 🚀 Запуск:

### Шаг 1: Запусти Backend

```bash
cd /home/paperclip/arli
python apps/api/src/marketplace_server.py
# Сервер запустится на http://localhost:8002
```

### Шаг 2: Открой Frontend

Просто открой файл в браузере:
```bash
open apps/web/marketplace.html
# или
firefox apps/web/marketplace.html
```

Или через Python:
```bash
cd apps/web
python -m http.server 3000
# Открой http://localhost:3000/marketplace.html
```

---

## 📤 Загрузка агентов:

### Способ 1: Через Web UI
1. Открой `marketplace.html`
2. Перетащи JSON файл агента в область загрузки
3. Готово! Агент появится в списке

### Способ 2: Через curl

```bash
# Загрузить одного агента
curl -X POST http://localhost:8002/agents/upload \
  -F "file=@arli_export_arli.json"

# Или через JSON API
curl -X POST http://localhost:8002/agents/upload/json \
  -H "Content-Type: application/json" \
  -d '{
    "arli_id": "arli_001",
    "name": "My Agent",
    "level": 5,
    "tier": "COMMON",
    "capabilities": [],
    "price": 100.00
  }'
```

### Способ 3: Batch загрузка (все агенты сразу)

```bash
# Создай скрипт upload_all.sh:
for file in ~/.openclaw/workspace/outputs/arli_exports/*.json; do
  curl -X POST http://localhost:8002/agents/upload -F "file=@$file"
  echo "Uploaded: $file"
done
```

---

## 💰 Как происходит продажа:

### 1. Покупатель нажимает "Buy Now"
### 2. Система создаёт запись о продаже:
```json
{
  "sale_id": "uuid",
  "agent_id": "arli_001",
  "buyer_id": "user_123",
  "price": 212.00,
  "platform_fee": 21.20,  // 10%
  "seller_revenue": 190.80  // 90%
}
```

### 3. Агент помечается как "sold"
### 4. Покупатель получает JSON для скачивания

---

## 📊 API Endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Info |
| `/agents` | GET | List all agents |
| `/agents/upload` | POST | Upload via file |
| `/agents/upload/json` | POST | Upload via JSON |
| `/agents/{id}` | GET | Get agent details |
| `/agents/{id}/buy` | POST | Purchase agent |
| `/agents/search?q=query` | GET | Search agents |
| `/stats` | GET | Marketplace stats |

---

## 🎨 Внешний вид:

```
┌─────────────────────────────────────────────┐
│  🚀 Arli Marketplace                        │
│  Buy and Sell AI Agents                     │
├─────────────────────────────────────────────┤
│  [7] Active Agents  [$853] Total Volume     │
├─────────────────────────────────────────────┤
│  📤 [    Drop JSON file here    ]           │
├─────────────────────────────────────────────┤
│  Search: [________] Tier: [All▼] Sort: [▼]  │
├─────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐   │
│  │ ⚪ ARLI - Master Orchestrator        │   │
│  │ Level: 4 • $212.00 • COMMON          │   │
│  │ [swarm_orchestration] [delegation]   │   │
│  │                          [Buy Now]   │   │
│  └──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────┐   │
│  │ ⚪ APEX - Elite Architect 🏔️         │   │
│  │ Level: 2 • $126.70 • COMMON          │   │
│  │ [architecture] [system_design]       │   │
│  │                          [Buy Now]   │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## 🔮 Что дальше:

### Для production:
1. **PostgreSQL** вместо in-memory
2. **ICP blockchain** для ownership
3. **Stripe** для fiat платежей
4. **Authentication** (JWT)
5. **IPFS** для хранения JSON

### Для твоих агентов:
- Загрузи их через UI
- Установи цены
- Получай 90% от продаж

---

## ✅ Сейчас работает:

- [x] Backend API (8002 порт)
- [x] Frontend UI (файл marketplace.html)
- [x] 7 агентов загружены
- [x] Система покупки/продажи
- [x] Статистика

Запускай и продавай! 🎉
