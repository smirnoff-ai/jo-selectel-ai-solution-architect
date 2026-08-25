# Task 01: Appeals CRUD

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/backend-3-appeals`
> **Spec:** [api-contracts.md](../../../../concept/api-contracts.md), [data-model.md](../../../../concept/data-model.md)
>
> Self-review: ✅ (2026-08-25)

---

## Цель

Postgres + Alembic, стол/журнал/карточка/реплика без агента.

---

## Состав работ

- [x] Таблицы appeals / messages / events
- [x] Шаблон card из card.md
- [x] REST по контракту; stream — заглушка run_finished
- [x] pytest на живом Postgres

## Skills

Read: postgresql-table-design, fastapi-templates, python-design-patterns, python-testing-patterns.

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | CRUD и стол зелёные | `make test-backend` |
| 2 | Lint | ruff |

---

## Scope

**Трогаем:** `backend/`, Makefile migrate, sprint docs, roadmap.

**НЕ трогаем:** агент, LLM, мок-контракт, полный UI.
