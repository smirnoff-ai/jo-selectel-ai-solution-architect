# Summary: Task 01 — Appeals CRUD

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-08-25

---

## Что реализовано

- `backend/src/backend/models/` — appeals / messages / events
- `backend/src/backend/card_template.py` — пустой card из card.md §8
- `backend/src/backend/repositories/appeal_repository.py` + facade
- `backend/src/backend/routers/appeals.py` — desk, journal, POST, card, replies, SSE-заглушка
- `backend/alembic/` — миграция `0001appeals`
- `backend/tests/test_appeals.py` — живой Postgres
- `Makefile` — `migrate`

---

## Отклонения от плана

Нет. Агент не трогали: `run_status=idle`, stream сразу `run_finished`.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| `ensure_schema=True` по умолчанию | `create_all` на первом старте без обязательного alembic |
| Wipe в тестах отдельным engine | asyncpg не шарит loop с `asyncio.run` |
| `psycopg2-binary` | sync-драйвер для Alembic |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| `text("now()")` в модели Appeal | колонка `text` перекрывала `sqlalchemy.text` → `sa_text` |
| TRUNCATE через session_factory | другой event loop → отдельный engine |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | CRUD и стол зелёные | ✅ 14 pytest |
| 2 | Lint | ✅ ruff |

---

## Что дальше

- Sprint 04: харнес, промпт, пять тулов, живой SSE
