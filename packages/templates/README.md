# ARLI Company Templates

10 production-ready шаблонов AI-компаний для ARLI platform.

## Шаблоны

| Шаблон | Сфера | Основная ценность |
|--------|-------|-------------------|
| 🛒 [Commerce Intel](./commerce-intel) | E-commerce | +5-15% маржа, -30% stockouts |
| 🏠 [Property Pulse](./property-pulse) | Real Estate | 3x лидов на агента |
| 🏥 [Clinic Flow](./clinic-flow) | Healthcare | +25% throughput клиники |
| ⚖️ [Legal Synth](./legal-synth) | Legal | Senior lawyers на strategy |
| 📊 [Ledger Minds](./ledger-minds) | Accounting | Advisory revenue растёт |
| 🎓 [Learning Foundry](./learning-foundry) | EdTech | 10x скорость создания курсов |
| 🏨 [Hospitality Hive](./hospitality-hive) | Hospitality | -15% labor, +10% occupancy |
| 🏭 [Manufacturing Mind](./manufacturing-mind) | Manufacturing | +20% OEE |
| 🚀 [SaaS Growth Lab](./saas-growth-lab) | SaaS | NRR >120% |
| 📈 [Agency Scalr](./agency-scalr) | Marketing | 1 AM = 3x клиентов |

## Структура каждого шаблона

```
template-name/
├── company.yaml       # Конфигурация компании, агенты, интеграции
└── README.md          # Документация, быстрый старт, метрики
```

## Быстрый старт

```bash
# Установка ARLI CLI
npm install -g arliwork

# Создание компании из шаблона
arliwork init my-store --template ~/arli-templates/commerce-intel

# Настройка интеграций
arliwork config --set shopify.store=my-store.myshopify.com

# Запуск
arliwork start
```

## Требования

- ARLI CLI 1.0+
- API ключи для интеграций
- Минимум 4GB RAM для запуска всех агентов

## Стоимость владения

| Расход | Диапазон/мес | Примечание |
|--------|--------------|------------|
| Compute | $150-800 | Зависит от нагрузки |
| API costs | $200-1000 | Интеграции |
| **Итого** | **$350-1800** | ROI обычно 3-10x |

## Поддержка

- Документация: https://arli.work/docs
- Сообщество: https://discord.gg/arli
- Issues: https://github.com/arliwork/arli/issues

## Лицензия

MIT License - используй свободно, модифицируй под свои нужды.
