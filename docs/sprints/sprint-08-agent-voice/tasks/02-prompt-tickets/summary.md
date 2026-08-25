# Summary: Task 02 — Промпт, тулы, широкий поиск заявок

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-08-26

---

## Что реализовано

- `docs/requirements/severholod/prompts/system.md` — стоп markdown-отчётом; реплика диспетчера по всему контексту; `grounds` фразами; `search_tickets` по любому одному id
- `backend/src/backend/agent/tools/search_tickets_tool.py` — фильтр `customer_id` / `site_id` / `asset_id` / `contract_id`; пустой вызов → error + `next_actions`
- описания `grounds` в `docs/requirements/severholod/schemas/update_card.py` и runtime-копии
- `docs/concept/agent-harness.md`, `docs/requirements/severholod/harness.md` — контракт тула без обязательного `asset_id`
- `backend/tests/test_system_prompt.py` — нет `Finale`; есть отчёт и диалог
- `backend/tests/test_search_tickets.py` — `customer_id` ок, без фильтра error

---

## Отклонения от плана

В accept (задача 03) промпт ещё ужесточили: `history.resolved` только если `ticket.asset_id` совпал с уже resolved активом; уникальный фрагмент адреса → `resolved`, не `ambiguous`. Это точечные баги агента из прогона, не смена цели задачи.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| Правило работы с контекстом, не список триггеров | Иначе модель ловит фразы и игнорирует карточку | — |
| Один любой identity-фильтр, не обязательный `asset_id` | S2/S4 ищут по клиенту/площадке; мок уже так умеет | — |

---

## Проблемы и решения

Нет на этапе 02. Живые дыры S2/S3 закрыты правками промпта в 03.

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | В промпте нет Finale; есть отчёт и диалог | ✅ |
| 2 | `search_tickets` без обязательного `asset_id` | ✅ |
| 3 | `grounds` — фразы, не пути слотов | ✅ |
| 4 | Lint и тесты backend | ✅ |

---

## Что дальше

- Задача 03: `make accept` и окно

---

## Ссылки

- [system.md](../../../../requirements/severholod/prompts/system.md)
- [harness.md](../../../../requirements/severholod/harness.md) §9
