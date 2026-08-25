# Task 03: Финал модели, выкинуть `complete_catalog`

> **Sprint:** [../../README.md](../../README.md)  
> **Тип:** feat  
> **Ветка:** `feat/backend-7-finale-no-catalog`  
> **Spec:** [generation.md](../../../../concept/generation.md) §7, [agent-harness.md](../../../../concept/agent-harness.md) §9, [prompts/system.md](../../../../requirements/severholod/prompts/system.md)

---

## Цель

Исход на стол — из короткого JSON модели. Тихого добора справочников нет. В трассе: патч упоминаний → поиски → снова патч с `system`.

---

## Состав работ

- [ ] Переписать `system.md` и LLM-facing тексты пяти тулов (описания, `Annotated`/`Field`): без демо-оверфита, без «binding 0/1/N», язык «однозначно выбран / несколько / не найдено»; few-shot — траектории тулов + Finale JSON
- [ ] `create_agent` отдаёт `Finale` (`response_format=ToolStrategy`). Если Qwen даёт 400 на tools+format — отдельный structured-шаг после тулов, не угадывание исхода кодом
- [ ] Guard только страховка: правит противоречие с уже найденными слотами / 5xx каталога. Не подменяет согласованный JSON модели
- [ ] Удалить `complete_catalog`: вызов в runner, модуль, тесты, `ensure_sites` из `search_assets`
- [ ] Промпт: без поисков финала нет; после успешного поиска обязателен `patch_facts` с evidences `kind=system` и `record.id` из `result`
- [ ] `make accept` (или отчёт) проверяет порядок: есть `search_*` и `patch_facts` **после** них, не только в начале
- [ ] Обновить generation.md §7, harness §9 (схема добора уходит), system.md
- [ ] Самопроверка по DoD
- [ ] (после «ок») `summary.md`, строка задачи в sprint README

## Skills

Read: `agent-harness-construction`, `python-testing-patterns`.

MCP: LangChain structured output / `response_format` у `create_agent`.

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Нет `complete_catalog.py` и вызова в runner | grep / дерево |
| 2 | `search_assets` не зовёт `ensure_sites` | код |
| 3 | S1–S4: в трассе есть нужные `search_*` и повторный `patch_facts` | `make accept` |
| 4 | Стол берёт `outcome` из JSON, если он согласован с `card` | accept + один живой прогон |
| 5 | Pytest без живой LLM | `make test-backend` |
| 6 | Lint | `make lint-backend` |

Как смотреть: `make accept` + трасса в Langfuse (есть `search_*` и `patch_facts` после них). Живой чат из 04 не нужен.

> Зелёный accept за счёт возврата тихого поиска — провал задачи.

---

## Артефакты

- `backend/src/backend/agent/runner.py` — без `complete_catalog`, merge `Finale`
- `backend/src/backend/agent/factory.py` — `ToolStrategy(Finale)`
- `backend/src/backend/agent/stream_mapper.py` — `structured_response`
- `backend/src/backend/agent/guard.py` — только страховка
- `backend/src/backend/agent/complete_catalog.py` — удалить
- `backend/tests/test_complete_catalog.py` — удалить
- `backend/src/backend/agent/tools/*.py` + `schemas/patch_facts.py` — LLM-facing тексты
- `backend/src/backend/agent/tools/search_assets_tool.py` — без `ensure_sites`
- `backend/tests/test_bindings.py` / guard-тесты — по факту смены контракта
- `scripts/accept_s1_s4.py` — проверка тулов в трассе
- `docs/requirements/severholod/prompts/system.md` — процесс, тулы, few-shot без демо-фикстур
- `docs/concept/agent-harness.md` — без добора кодом
- `docs/concept/generation.md` §7
- `docs/sprints/sprint-07-ui-wishes/tasks/03-finale-no-catalog/summary.md` — после «ок»

---

## Scope

**Трогаем:** только файлы из «Артефакты».

**НЕ трогаем:** UI окна обращения (04), образ frontend, визуал стола.

Binding 0/1/N внутри вызванного тула остаётся — это не добор.

---

## Риски и допущения

- S1–S4 покраснеют сразу после удаления добора — чинить промпт и агента, не возвращать модуль.
- `tools` + `response_format` на Qwen — запасной ход: structured после тулов.

---

## Открытые вопросы

- Нет. Стартовать после закрытия 02.
