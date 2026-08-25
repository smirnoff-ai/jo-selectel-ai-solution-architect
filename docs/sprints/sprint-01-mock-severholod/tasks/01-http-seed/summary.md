# Summary: Task 01 — HTTP + сид

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-08-25

---

## Что реализовано

- `mock-severholod/` — FastAPI-сервис на JSON-сиде, без БД
- `mock-severholod/src/mock_severholod/data/seed.json` — бриф + поля T-884
- Поиск CRM/EAM/договоры/ITSM и dry-run POST/PATCH
- `mock-severholod/tests/` — health, два ХУ-17, пустой поиск, dry-run, ФЛК
- `mock-severholod/Dockerfile` — multi-stage, healthcheck
- Корневой `Makefile` — `mock`, `mock-test`, `mock-lint`

---

## Отклонения от плана

Нет отклонений по контракту. Индекс пакетов в `pyproject.toml` — зеркало Tsinghua: с этой машины `pypi.org` рвёт TLS.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| Память + JSON, не Postgres | Контур мока без БД | ADR 0001 |
| `ALLOW_TICKET_MUTATIONS` default false | Dry-run без флага в теле | контракт мока |
| Роутеры по контурам API | ruff ALL + SoC | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| TLS handshake eof на pypi.org | `uv` через `pypi.tuna.tsinghua.edu.cn` |
| `select = ALL` шумит на FastAPI | игнор CPY/TC/RUF001/S104/PLR0913; роуты разнесены |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Контрактные тесты зелёные | ✅ 13 passed |
| 2 | Lint | ✅ ruff check src tests |
| 3 | `/health` ok (curl) | ✅ |
| 4 | Два ХУ-17 | ✅ A-1001 и A-1002 |
| 5 | Dry-run create T-885, persisted false | ✅ |
| 6 | ФЛК 400 | ✅ чужой актив A-2001 |

---

## Что дальше

- Sprint 02: каркас Рефлекса, compose, логин
