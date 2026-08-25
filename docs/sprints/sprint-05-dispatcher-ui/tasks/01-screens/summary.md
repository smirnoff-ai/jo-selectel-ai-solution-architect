# Summary: Task 01 — Экраны диспетчера

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-08-25

---

## Что реализовано

- `frontend/src/app/` — стол, журнал, форма, карточка `R-{id}`
- `frontend/src/components/` — оболочка, документ карточки, чат, SSE
- shadcn-примитивы вручную (CLI `shadcn@latest` падает на zod/`@modelcontextprotocol/sdk`)
- `backend/src/backend/agent/loop.py` — события SSE во время тулов

---

## Отклонения от плана

CLI shadcn не запустился. Компоненты — тот же API (Button, Field, Badge, Table) и семантические токены.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Client pages + `/api` rewrite | cookie same-origin, EventSource |
| Именованные SSE `addEventListener` | `event:` не попадает в `onmessage` |
| Emit тулов из цикла | иначе карточка 45 с пустая |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| shadcn CLI ERR_PACKAGE_PATH_NOT_EXPORTED | свои примитивы + `cn`/`cva` |
| eslint set-state-in-effect | убрали лишний reset в эффектах |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Стол, форма, карточка | ✅ login → форма S2 → R-1, clarify, две площадки |
| 2 | Журнал и назад | ✅ строка «Нужно уточнение»; стол виджет count=1 |
| 3 | Lint | ✅ `pnpm lint`, tsc |

---

## Что дальше

- Sprint 06: S1–S4, Langfuse, README задания, demo
