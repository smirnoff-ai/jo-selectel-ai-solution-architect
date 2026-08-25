# Task 01: Экраны диспетчера

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/frontend-5-dispatcher-ui`
> **Spec:** [frontend-ux-logic.md](../../../../concept/frontend-ux-logic.md), [frontend-design.md](../../../../concept/frontend-design.md), [functional-spec.md](../../../../requirements/severholod/functional-spec.md)
>
> Self-review: ✅ (2026-08-25)

---

## Цель

Рабочие экраны диспетчера: стол, журнал, форма, карточка с чатом и SSE.

---

## Состав работ

- [x] shadcn + семантические токены холодного цеха
- [x] оболочка: Стол / Журнал, тема, выход
- [x] стол 2×2, журнал с фильтрами, форма создания
- [x] карточка: документ слева, чат справа, EventSource
- [x] живые SSE-события во время тулов (иначе 45 с пусто)
- [x] проверка в браузере

## Skills

Read: nextjs-app-router-patterns, shadcn, frontend-design, vercel-react-best-practices, web-design-guidelines.

MCP: Context7 Next.js (client fetch / EventSource).

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Стол, форма, карточка | браузер localhost:3000 |
| 2 | Журнал и назад | браузер |
| 3 | Lint | `pnpm lint` в frontend |

---

## Scope

**Трогаем:** `frontend/`, sprint docs, roadmap; точечно `backend/src/backend/agent/loop.py` и `runner.py` (emit во время тула).

**НЕ трогаем:** S1–S4 как приёмка, demo-видео, мок.
