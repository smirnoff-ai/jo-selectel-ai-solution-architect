# Task 02: Промпт, тулы, широкий поиск заявок

> **Sprint:** [../../README.md](../../README.md)  
> **Тип:** feat  
> **Ветка:** `feat/sprint-08-agent-voice`  
> **Spec:** [harness.md](../../../../requirements/severholod/harness.md)

---

## Цель

Агент пишет отчёт в чат, отвечает на произвольный вопрос и ищет заявки по любому устойчивому фильтру.

---

## Состав работ

- [ ] Переписать `system.md`: стоп markdown, диалог, контекст целиком, `grounds` фразами
- [ ] Тексты тулов тем же языком
- [ ] `search_tickets`: любой один фильтр, полные поля заявки
- [ ] Тесты промпта и тула
- [ ] Самопроверка по DoD
- [ ] (после «ок») `summary.md`

## Skills

Read: `agent-harness-construction`, `python-testing-patterns`.

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | В промпте нет Finale; есть отчёт и диалог | pytest + файл |
| 2 | `search_tickets` без обязательного `asset_id` | pytest |
| 3 | `grounds` — фразы, не пути слотов | промпт + описание `update_card` |
| 4 | Lint и тесты backend | `make lint-backend` / `make test-backend` |

---

## Артефакты

- `docs/requirements/severholod/prompts/system.md`
- `backend/src/backend/agent/tools/search_tickets_tool.py`
- описания остальных тулов при необходимости
- `docs/requirements/severholod/schemas/update_card.py` — описание grounds
- `backend/tests/test_system_prompt.py`
- `backend/tests/test_search_tickets.py` (новый)
- `docs/sprints/sprint-08-agent-voice/tasks/02-prompt-tickets/summary.md`

---

## Scope

**Трогаем:** файлы из «Артефакты».

**НЕ трогаем:** frontend; runner (01 уже закрыт).

---

## Риски и допущения

- Промпт — правило работы с контекстом, не список фраз-триггеров.

---

## Открытые вопросы

- Нет.
