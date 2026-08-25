# Summary: Task 01 — Compose + логин

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-08-25

---

## Что реализовано

- `backend/` — Settings fail-fast, `/health`, login/logout/me, cookie
- `frontend/` — `/login`, стол-заглушка, тёмная тема, переключатель
- `docker-compose.yml` — postgres, langfuse, mock, backend, frontend
- `scripts/write-env-from-keychain.sh` + `.env.example`
- pytest логина; вход в браузере на `localhost:3000`

---

## Отклонения от плана

Langfuse в compose есть, ключи пилота локальные (`pk-lf-local`). Трассы агента — спринт 04.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Cookie itsdangerous, один логин из Settings | контракт, без SSO |
| Rewrite `/api` на backend | cookie same-origin |
| Секреты из Keychain в `.env` через make | не коммитить секреты |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| pypi.org / npmjs TLS | зеркала Tsinghua / npmmirror |
| Next блокирует 127.0.0.1 для `/_next` | `allowedDevOrigins` + проверка через localhost |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | login/me/logout | ✅ 7 pytest |
| 2 | Lint backend | ✅ ruff |
| 3 | Вход в браузере | ✅ стол, logout на /login |

---

## Что дальше

- Sprint 03: обращения в Postgres
