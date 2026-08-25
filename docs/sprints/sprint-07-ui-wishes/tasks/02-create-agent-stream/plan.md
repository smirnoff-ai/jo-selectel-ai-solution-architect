# Task 02: `create_agent` + стрим + Langfuse

> **Sprint:** [../../README.md](../../README.md)  
> **Тип:** feat  
> **Ветка:** `feat/backend-7-create-agent-stream`  
> **Spec:** [agent-harness.md](../../../../concept/agent-harness.md), [generation.md](../../../../concept/generation.md), [docpoint-stream.md](../../docpoint-stream.md)

---

## Цель

Прогон идёт через LangChain `create_agent`: в SSE — thought и `message_delta` токенами, в Langfuse — нормальный trace с `thread_id` / session = `appeal_id`.

---

## Состав работ

- [ ] Живой smoke: `create_agent` + `stream_events(..., version="v3")` на текущем OpenRouter **не** висит ~90 с (риск ADR-0003). Нет стрима — стоп, не откатываться на `run_tool_loop` без согласования
- [ ] Заменить цикл в [runner.py](../../../../../backend/src/backend/agent/runner.py) / убрать [loop.py](../../../../../backend/src/backend/agent/loop.py) если больше не нужен
- [ ] Стрим модели: reasoning `effort` (не `max_tokens: 256`). Адаптер: сначала `ChatOpenRouter` / актуальный пакет; иначе тонкий маппинг `delta.reasoning` как в DocPoint. Deep Agents не брать
- [ ] Маппинг событий в словарь generation.md: `thought` (delta), `message_delta` → `message_final`, тулы как сейчас, в конце `context_usage`
- [ ] Langfuse: CallbackHandler на агенте (`langfuse.langchain.CallbackHandler`). Self-host v4 (ClickHouse / Redis / MinIO / worker). `thread_id` / `langfuse_session_id` = `str(appeal_id)`. Не сериализовать SSE в Langfuse
- [ ] Обновить agent-harness.md, ADR-0003, generation.md (таблица событий + токены)
- [ ] Самопроверка по DoD (живой SSE + Langfuse + `make accept`)
- [ ] (после «ок») `summary.md`, строка задачи в sprint README

## Skills

Read: `agent-harness-construction`, `langfuse`, `python-testing-patterns`.

MCP: Docs by LangChain (`create_agent`, `stream_events` v3, reasoning); Langfuse LangChain CallbackHandler.

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Нет ручного `run_tool_loop` на пути прогона | код |
| 2 | SSE отдаёт дельты мысли и ответа, не один dump | живой прогон, Network на `/stream` |
| 3 | Langfuse: session = обращение, видны generation и tools | UI `:3001` после прогона |
| 4 | Lint | `make lint-backend` |
| 5 | Accept не обязан быть «честнее», чем сейчас (`complete_catalog` ещё жив) | `make accept` не хуже старта задачи |

Как смотреть (окна 04 ещё нет): Network на `/stream` — пачки `thought` / `message_delta`; Langfuse `:3001` — session = `appeal_id`, generations и tools. Текущий чат может dump'ить финал — не чинить в этой задаче.

> Те же команды — для самостоятельной проверки.

---

## Артефакты

- `backend/src/backend/agent/runner.py` — вызов `create_agent`, стрим, LF
- `backend/src/backend/agent/factory.py` — модель, streaming, reasoning
- `backend/src/backend/agent/loop.py` — удалить или оставить пустым не надо: удалить, если мёртв
- `backend/src/backend/agent/langfuse_trace.py` — CallbackHandler вместо пустого `lf.trace`
- `backend/src/backend/agent/` — маппер v3 → наши события (новый файл, если нужно)
- `backend/pyproject.toml` / lock — пакет модели / langfuse, если без этого нет reasoning или handler
- `docs/concept/agent-harness.md` — рантайм `create_agent`, без чекпоинтера
- `docs/adrs/0003-agent-runtime.md` — возврат к `create_agent`
- `docs/concept/generation.md` — дельты + `context_usage`
- `docs/sprints/sprint-07-ui-wishes/tasks/02-create-agent-stream/summary.md` — после «ок»

---

## Scope

**Трогаем:** только файлы из «Артефакты».

**НЕ трогаем:** удаление `complete_catalog` (задача 03), окно обращения UI (04), рестайл стола, образ frontend кроме зависимости от уже починенного 01.

Чекпоинтер LangGraph не вводим: `card` в Postgres. `thread_id` только для trace/config.

---

## Риски и допущения

- Hang OpenRouter — стоп и согласование, не тихий откат на ручной цикл.
- `ChatOpenAI` + base_url может съесть reasoning — тогда адаптер / `ChatOpenRouter`.
- Self-host Langfuse v4 (ClickHouse / Redis / MinIO / worker); SDK `langfuse.langchain.CallbackHandler`.

---

## Открытые вопросы

- Нет. Стартовать после закрытия 01.
