# Task 01: Стоп без Finale и без guard

> **Sprint:** [../../README.md](../../README.md)  
> **Тип:** feat  
> **Ветка:** `feat/sprint-08-agent-voice`  
> **Spec:** [generation.md](../../../../concept/generation.md), [agent-harness.md](../../../../concept/agent-harness.md)

---

## Цель

Прогон останавливается на markdown модели. Решение берём с карточки, код его не переписывает.

---

## Состав работ

- [ ] `create_agent` без `response_format`
- [ ] Runner: нет `apply_guard`, нет `_finale_from_card`, нет синтеза отчёта
- [ ] Стол и ITSM dry-run из `card.decision`
- [ ] Удалить Finale / guard / dispatcher_report и их тесты
- [ ] Обновить концепты
- [ ] Самопроверка по DoD
- [ ] (после «ок») `summary.md`

## Skills

Read: `agent-harness-construction`, `python-testing-patterns`.

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Нет `ToolStrategy(Finale)` | чтение factory |
| 2 | Нет синтеза отчёта и guard | pytest + чтение runner |
| 3 | Lint и тесты backend | `make lint-backend` / `make test-backend` |

---

## Артефакты

- `backend/src/backend/agent/factory.py`
- `backend/src/backend/agent/runner.py`
- `backend/src/backend/agent/desk_status.py` — карта стола
- удаление: `finale.py`, `guard.py`, `dispatcher_report.py` и тесты
- `backend/src/backend/agent/stream_mapper.py` — без разбора Finale
- `docs/concept/generation.md`, `docs/concept/agent-harness.md`
- `docs/requirements/severholod/harness.md`
- ADR 0003 если есть упоминание Finale
- `docs/sprints/sprint-08-agent-voice/tasks/01-stop-no-finale/summary.md`

---

## Scope

**Трогаем:** файлы из «Артефакты».

**НЕ трогаем:** промпт и `search_tickets` (02); frontend.

---

## Риски и допущения

- Пока промпт старый, модель может всё ещё звать Finale — 02 снимает это.

---

## Открытые вопросы

- Нет.
