# Summary: Task 01 — Стоп без Finale и без guard

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-08-26

---

## Что реализовано

- `backend/src/backend/agent/factory.py` — `create_agent` без `response_format=ToolStrategy(Finale)`
- `backend/src/backend/agent/runner.py` — после стрима `apply_card_decision`: исход с карточки, ITSM только на create/update, без guard и без синтеза отчёта
- `backend/src/backend/agent/desk_status.py` — статус стола из `outcome`
- `backend/src/backend/agent/ticket_draft.py` — `support_clear` рядом с черновиком заявки
- `backend/src/backend/agent/stream_mapper.py` — без `structured_response` / Finale
- `backend/src/backend/facades/appeal_facade.py` — GET messages без доклейки отчёта
- удалены `finale.py`, `guard.py`, `dispatcher_report.py` и их тесты
- `docs/concept/generation.md` §7, `docs/concept/agent-harness.md`, `docs/requirements/severholod/harness.md`, `docs/adrs/0003-agent-runtime.md`
- тесты: `test_desk_status.py`, `test_ticket_draft.py`, `test_apply_card_decision.py`

---

## Отклонения от плана

Нет отклонений.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| Источник истины — `card.decision`, не structured output | Модель уже пишет исход тулом `update_card` | [0003](../../../../adrs/0003-agent-runtime.md) |
| Примерка ITSM кодом после прогона | Модель не собирает payload и не дергает write | [0002](../../../../adrs/0002-itsm-dry-run.md) |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| `support_clear` жил в `guard.py` | Вынесли в `ticket_draft.py` до удаления guard |
| `message_text` жил в finale | Инлайн в `stream_mapper` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Нет `ToolStrategy(Finale)` | ✅ |
| 2 | Нет синтеза отчёта и guard | ✅ |
| 3 | Lint и тесты backend | ✅ |

---

## Что дальше

- Задача 02: промпт без Finale, широкий `search_tickets`

---

## Ссылки

- [generation.md](../../../../concept/generation.md) §7
- [agent-harness.md](../../../../concept/agent-harness.md)
- [0003-agent-runtime.md](../../../../adrs/0003-agent-runtime.md)
