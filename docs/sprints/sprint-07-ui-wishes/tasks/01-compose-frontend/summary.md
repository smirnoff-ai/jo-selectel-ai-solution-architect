# Summary: Task 01 — Образ frontend / `make up`

> **План:** [plan.md](./plan.md)  
> **Дата закрытия:** 2026-08-25

---

## Что реализовано

- `frontend/Dockerfile` — runtime-пользователь uid 1001; Corepack берёт pnpm с npmmirror; Playwright браузеры не качает

---

## Отклонения от плана

Нет. `.dockerignore`, `next.config.ts`, `docker-compose.yml` не трогали — образ стартовал без них.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| uid 1001, не 1000 | в `node:22-alpine` 1000 занят пользователем `node` | — |
| `COREPACK_NPM_REGISTRY=https://registry.npmmirror.com` | как `.npmrc`; npmjs.org в сборке обрывал TLS | — |
| `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1` | браузеры в образе UI не нужны | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| `adduser: uid '1000' in use` | группа/пользователь 1001 |
| Corepack → `registry.npmjs.org`, `ECONNRESET` | зеркало + `corepack prepare pnpm@11.18.0` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Образ собирается | ✅ `docker compose build frontend` |
| 2 | UI на `:3000` из compose | ✅ логин «Рефлекс» |
| 3 | Backend health | ✅ `{"status":"ok"}` |
| 4 | Не через `make dev-frontend` | ✅ контейнер `frontend` |

---

## Что дальше

- Задача 02: `create_agent` + стрим + Langfuse — после явного «ок» на её plan.md
