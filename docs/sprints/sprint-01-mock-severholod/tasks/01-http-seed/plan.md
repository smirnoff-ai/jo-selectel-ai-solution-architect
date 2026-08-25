# Task 01: HTTP-мок СеверХолода

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/mock-1-http-seed`
> **Spec:** [api-contracts-mock.md](../../../../concept/api-contracts-mock.md)
>
> Self-review: ✅ (2026-08-25)

---

## Цель

Сервис `mock-severholod`: сид JSON, контракт CRM/EAM/договоры/ITSM, тесты, Dockerfile.

---

## Состав работ

- [x] uv-проект, FastAPI, Settings
- [x] Сид из брифа + поля T-884
- [x] Поиски и dry-run
- [x] pytest/httpx
- [x] Dockerfile + healthcheck
- [x] Самопроверка DoD

## Skills

Read: fastapi-templates, modern-python, uv-package-manager, python-testing-patterns, api-design-principles, docker-expert.

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Контрактные тесты зелёные | `cd mock-severholod && uv run pytest` |
| 2 | Lint | `uv run ruff check src tests` |

---

## Scope

**Трогаем:** `mock-severholod/`, sprint docs, корневой Makefile (только цель мока).

**НЕ трогаем:** backend Рефлекса, frontend, агент.
