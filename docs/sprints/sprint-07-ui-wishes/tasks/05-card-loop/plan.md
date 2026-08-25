# Task 05: Карточный цикл — спека, тулы, промпт

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** текущая `feat/backend-7-create-agent-stream`
> **Spec:** [harness.md](../../../../requirements/severholod/harness.md), [card.md](../../../../requirements/severholod/card.md)

---

## Цель

Агент сам собирает контекст поисками, сам пишет карточку через `update_card`, сам вызывает `calculate` и переносит результат. Поиски и договор карточку не трогают.

---

## Состав работ

- [ ] Канон: `harness.md`, `agent-harness.md`, `card.md`, `regulations.md`, `generation.md`, ADR 0003, схемы
- [ ] System prompt и LLM-тексты тулов без внутренних сокращений
- [ ] Поиски и `get_contract` — только наблюдение; параметры явные
- [ ] `calculate` — формула из регламента, в карточку не ходит
- [ ] `update_card` вместо `patch_facts`: любые поля карточки, ответ — полный `card`
- [ ] `card_updated` только после `update_card`
- [ ] Юнит-тесты схемы, мержа, расчёта, промпта
- [ ] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Поиски и договор не меняют `card` | pytest + чтение тулов |
| 2 | `calculate` считает по аргументам, не читает карточку | pytest |
| 3 | `update_card` пишет слоты / договор / расчёт / решение; неизвестный id отклоняет | pytest |
| 4 | В промпте есть цикл, все реквизиты, шесть тулов; нет `patch_facts` | pytest + файл |
| 5 | Lint и тесты backend | `make lint-backend` / `make test-backend` |

---

## Артефакты

- `docs/requirements/severholod/prompts/system.md`
- `docs/requirements/severholod/harness.md`
- `docs/requirements/severholod/card.md`
- `docs/requirements/severholod/regulations.md`
- `docs/requirements/severholod/schemas/update_card.py`
- `docs/requirements/severholod/README.md`
- `docs/concept/agent-harness.md`
- `docs/concept/generation.md`
- `docs/adrs/0003-agent-runtime.md`
- `backend/src/backend/agent/**` — тулы, схемы, merge, calculation, factory, runner
- `backend/tests/test_*.py`
- `frontend/src/lib/labels.ts`

---

## Scope

**Трогаем:** харнес агента, канон, подписи тулов в UI.

**НЕ трогаем:** визуал пульта (стол / логин / журнал), задача 04 summary, ветка.

---

## Риски и допущения

- Модель может забыть `update_card` или `calculate` — ловим accept и промптом, не тихим кодом.
- `received_at` для расчёта берём со строки обращения, не из аргументов модели.
