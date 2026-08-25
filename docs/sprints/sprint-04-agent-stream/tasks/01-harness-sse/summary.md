# Summary: Task 01 — Harness + SSE

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-08-25

---

## Что реализовано

- `docs/requirements/severholod/prompts/system.md` — переписан skill'ом harness-construction (action space, стоп, untrusted input)
- `backend/src/backend/agent/` — пять тулов, binding 0/1/N, SLA, предохранитель, dry-run ITSM, SSE hub, цикл tools
- `backend/src/backend/routers/appeals.py` — POST/reply стартуют прогон, GET stream не заглушка
- `backend/tests/test_bindings.py`, `test_calculation.py`, `test_guard.py`, `test_system_prompt.py`
- Концепт: рантайм без `create_agent` и без чекпоинтера — [agent-harness.md](../../../../concept/agent-harness.md), [ADR-0003](../../../../adrs/0003-agent-runtime.md)

---

## Отклонения от плана

`create_agent` на OpenRouter зависал (~90 с). Пилот — `run_tool_loop`: `bind_tools`, до 8 шагов. Langfuse — ручной `trace`, не CallbackHandler (LangChain 1 ломает SDK 2.x). Тесты без живой LLM (`use_agent=False`).

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Исход пишет guard по карточке | модель часто не отдаёт JSON-финал |
| `_coerce_args` JSON-строк | Qwen кладёт слоты `patch_facts` строками |
| `reasoning.max_tokens=256`, `max_tokens=4096` | иначе reasoning съедает бюджет |
| Тесты на FakeAgentRunner | pytest не ходит в OpenRouter |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| `create_agent` hang | явный tool loop |
| OpenRouter 400: effort + max_tokens | только `reasoning.max_tokens` |
| CallbackHandler `langchain.callbacks` | ручной Langfuse 2.x |
| Langfuse `:3001` отвечает 401 на `pk-lf-local` | контейнер живой; первый пользователь и ключи проекта — спринт 06 |
| Тест fail-fast читал `.env` после импорта SDK | `monkeypatch.delenv` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Binding / SLA / guard зелёные | ✅ 25 pytest |
| 2 | Stream не заглушка | ✅ pytest + live S2: tools → `update` T-884, dry-run accepted |
| 3 | Lint | ✅ ruff |

Live (короткий S2): клиент C-101, площадка S-MSK-01, актив A-1001, история T-884, договор Gold, дедлайн received+60м, `auto_in_prod=true`. Полный S2 с двумя ХУ-17 — спринт 06.

---

## Что дальше

- Sprint 05: стол, журнал, форма, карточка и чат
