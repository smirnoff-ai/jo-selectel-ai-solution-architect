# Summary: Task 05 — Карточный цикл

> **План:** [plan.md](./plan.md)  
> **Дата закрытия:** 2026-08-25

---

## Что реализовано

- `docs/requirements/severholod/prompts/system.md` — цикл: поиск → запись → расчёт → Finale
- `backend/src/backend/agent/tools/update_card_tool.py` + `schemas/update_card.py` — вместо `patch_facts`; ответ — полный card
- `backend/src/backend/agent/tools/calculate_tool.py` — формула, карточку не читает и не пишет
- поиски и `get_contract` — только чтение; `card_updated` только после `update_card`
- `backend/src/backend/agent/run_context.py` — `seen_ids`, `last_calculation`, `received_at`
- канон: harness, card, regulations, `agent-harness.md`, `generation.md`, ADR 0003
- тесты: `test_update_card.py`, `test_calculation.py`, `test_system_prompt.py`

---

## Отклонения от плана

Нет по составу. Ветка не менялась.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| Поиск не мутирует card | Слот слева загорается только после явной записи | — |
| `calculate` отдельным тулом | SLA считает код, не модель | — |
| Неизвестный id в `resolved` отвергается | Только id из `result.items` этого прогона | — |
| `received_at` со строки обращения | Модель не передаёт время письма | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| S2: модель останавливалась на двух площадках и не искала установку | Промпт: искать оборудование даже при нескольких площадках |
| mention + `binding.empty` | merge ставит `mentioned` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Поиски и договор не меняют card | ✅ |
| 2 | `calculate` по аргументам, не читает карточку | ✅ |
| 3 | `update_card` пишет любые поля; чужой id — отказ | ✅ |
| 4 | В промпте цикл и шесть тулов; нет `patch_facts` | ✅ |
| 5 | Lint и тесты backend | ✅ |

---

## Что дальше

- Задача 06: accept и проверка в окне

---

## Ссылки

- [harness.md](../../../../requirements/severholod/harness.md)
- [card.md](../../../../requirements/severholod/card.md)
