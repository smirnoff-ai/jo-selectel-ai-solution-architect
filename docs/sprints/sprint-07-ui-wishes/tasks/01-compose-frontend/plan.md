# Task 01: Образ frontend / `make up`

> **Sprint:** [../../README.md](../../README.md)  
> **Тип:** fix  
> **Ветка:** `fix/frontend-7-compose-image`  
> **Spec:** без spec · [architecture.md](../../../../concept/architecture.md) § compose

---

## Цель

`make up` собирает образ frontend и отдаёт UI на `http://localhost:3000` без ручного `make dev-frontend`.

---

## Состав работ

- [x] Воспроизвести падение `docker compose build frontend` / `make up`, зафиксировать ошибку в ходе работы
- [x] Починить [frontend/Dockerfile](../../../../../frontend/Dockerfile) (standalone Next: lockfile, corepack, `public` / `.next/static`, `BACKEND_URL` на build)
- [x] Если дыра в compose или `next.config` — только то, без чего образ не стартует
- [x] Самопроверка по DoD
- [x] (после «ок») `summary.md`, строка задачи в sprint README

## Skills

Read: `docker-expert`.

MCP: не обязателен; при сомнении по Next standalone — Context7 / Next docs.

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Образ frontend собирается | `docker compose build frontend` |
| 2 | Стек поднимается, UI на `:3000` | `make up` → открыть логин |
| 3 | Backend жив | `curl -sf http://127.0.0.1:8000/health` |
| 4 | Фронт не через `make dev-frontend` | в проверке только compose |

> Те же команды — для самостоятельной проверки.

---

## Артефакты

- `frontend/Dockerfile` — сборка runtime
- `frontend/.dockerignore` — если мешает контекст (создать/править только если надо)
- `frontend/next.config.ts` — только если standalone/rewrites ломают образ
- `docker-compose.yml` — только сервис `frontend`, если без этого не стартует
- `docs/sprints/sprint-07-ui-wishes/tasks/01-compose-frontend/summary.md` — после «ок»

---

## Scope

**Трогаем:** только файлы из «Артефакты».

**НЕ трогаем:** агент, Langfuse SDK, UI-компоненты, `complete_catalog`, промпт.

---

## Риски и допущения

- Rewrite `/api` в контейнере должен бить в `http://backend:8000`, не в localhost хоста.
- Не тащить ClickHouse / Langfuse v3 «заодно».

---

## Открытые вопросы

- Нет. Стартовать можно.
