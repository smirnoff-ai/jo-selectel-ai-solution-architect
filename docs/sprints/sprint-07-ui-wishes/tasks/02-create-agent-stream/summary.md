# Summary: Task 02 — `create_agent` + стрим + Langfuse

> **План:** [plan.md](./plan.md)  
> **Дата закрытия:** 2026-08-25

---

## Что реализовано

- `backend/src/backend/agent/factory.py` — `ChatOpenRouter`, `streaming=True`, reasoning `effort=high`, без `response_format`
- `backend/src/backend/agent/stream_mapper.py` — `astream_events` v3 → `thought.delta`, `message_delta` / `message_final`, тулы, `context_usage`; `GraphRecursionError` не валит прогон
- `backend/src/backend/agent/runner.py` — `create_agent` + mapper; timeout не стирает карточку
- `backend/src/backend/agent/loop.py` — удалён
- `backend/src/backend/agent/langfuse_trace.py` — SDK 4: `CallbackHandler` + `propagate_attributes`, session = `appeal_id`
- `backend/pyproject.toml` / `uv.lock` — `langchain-openrouter`, `langfuse>=4`
- `docker-compose.yml` — self-host Langfuse v4 (web + worker, ClickHouse, Redis, MinIO, свой Postgres); UI `:3001`
- `docs/concept/agent-harness.md`, `generation.md`, `architecture.md`, `integrations.md`, `docs/adrs/0003-agent-runtime.md`

---

## Отклонения от плана

Self-host изначально держали на `langfuse:2` без ClickHouse. По явной просьбе — актуальный локальный v4 (4.18.0 OSS) и SDK 4.14.5. Те же init-ключи и логин.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| `create_agent` + `astream_events(v3)`, без чекпоинтера | живой стрим на OpenRouter; card в Postgres | [0003](../../../../adrs/0003-agent-runtime.md) |
| `ChatOpenRouter` + reasoning `effort` | `ChatOpenAI` + base_url съедает reasoning | — |
| Langfuse v4 + `propagate_attributes` | актуальный self-host; session на каждом observation | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| `langfuse:2` + SDK 2 ломались о LangChain 1.3 | ушли на v4 server + SDK 4, shim снят |
| Healthcheck web на `127.0.0.1:3000` | Next слушает hostname; `wget http://langfuse:3000/api/public/health` |
| Qwen с `effort=high` часто без текстового финала | дельты мысли в SSE есть; `message_delta` не обязателен в 02 |
| `GraphRecursionError` (limit 20) | mapper отдаёт частичный persist, карточку не сносим |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Нет `run_tool_loop` | ✅ файл удалён |
| 2 | SSE дельтами, не dump | ✅ `event: thought` пачками с 1–3 с (терминал / curl `-N`) |
| 3 | Langfuse session = обращение, generation + tools | ✅ v4.18.0, session `1`, `ChatOpenRouter` + tools |
| 4 | Lint | ✅ `make lint-backend` |
| 5 | Accept не хуже старта (`complete_catalog` жив) | ✅ S1/S2 ок; S3/S4 красные — модель не ищет актив, это 03 |

---

## Что дальше

- Задача 03: финал модели, выкинуть `complete_catalog` — после «ок» на [plan.md](../03-finale-no-catalog/plan.md)
- Окно обращения (04) не начинать до закрытия 03
