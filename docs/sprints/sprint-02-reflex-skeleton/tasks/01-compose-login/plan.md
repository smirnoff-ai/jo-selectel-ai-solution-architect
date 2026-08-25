# Task 01: Compose + логин

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/backend-2-skeleton`
> **Spec:** [api-contracts.md](../../../../concept/api-contracts.md), [architecture.md](../../../../concept/architecture.md)
>
> Self-review: ✅ (2026-08-25)

---

## Цель

Каркас `backend/` и `frontend/`, корневой compose, cookie-логин, fail-fast Settings.

---

## Состав работ

- [x] uv backend: Settings, `/health`, login/logout/me
- [x] Next.js login + тёмная тема по умолчанию, стол-заглушка
- [x] docker-compose: mock, postgres, langfuse, backend, frontend
- [x] Секреты из Keychain в make, в git только `.env.example`
- [x] pytest логина; браузерный вход

## Skills

Read: fastapi-templates, modern-python, uv-package-manager, python-testing-patterns, nextjs-app-router-patterns, shadcn, frontend-design, docker-expert.

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | login/me/logout по контракту | `make test-backend` |
| 2 | Lint backend | ruff |
| 3 | Вход в браузере | MCP browser |

---

## Scope

**Трогаем:** `backend/`, `frontend/`, compose, Makefile, sprint docs, `.env.example`.

**НЕ трогаем:** агент, обращения, мок-контракт.
