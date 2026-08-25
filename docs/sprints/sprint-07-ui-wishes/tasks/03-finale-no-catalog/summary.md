# Summary: Task 03 — Финал модели, выкинуть `complete_catalog`

> **План:** [plan.md](./plan.md)  
> **Дата закрытия:** 2026-08-25

---

## Что реализовано

- `docs/requirements/severholod/prompts/system.md` — процесс патч → поиск → патч `system`, без демо-оверфита
- `backend/src/backend/agent/factory.py` — `response_format=ToolStrategy(Finale)`
- `backend/src/backend/agent/stream_mapper.py` — финал из `structured_response`, иначе JSON текста
- `backend/src/backend/agent/runner.py` — без `complete_catalog`; запасной structured-шаг по карточке, если модель не вернула Finale
- `backend/src/backend/agent/guard.py` — только страховка, согласованный JSON не переписывает
- `backend/src/backend/agent/complete_catalog.py` — удалён
- `backend/src/backend/agent/tools/*.py` + `schemas/patch_facts.py` — LLM-facing тексты; `search_assets` без `ensure_sites`
- `scripts/accept_s1_s4.py` — в трассе нужны `search_*` и `patch_facts` после них
- `docs/concept/generation.md` §7, `docs/concept/agent-harness.md` §5/§9

---

## Отклонения от плана

Ветка осталась `feat/backend-7-create-agent-stream` — новую `feat/backend-7-finale-no-catalog` не резали.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| `ToolStrategy(Finale)`, не ProviderStrategy | Qwen/OpenRouter часто даёт 400 на tools + native format | — |
| Пустой финал → `dispatch`, не лестница create/update | Не выдумывать исход кодом | — |
| Разбор JSON-строк в слотах `patch_facts` | Модель часто сериализует вложенный объект строкой и зацикливается | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| Рекурсия 20 на цикле `patch_facts` 422 | coerce слотов + `recursion_limit=40` |
| S4 без Finale при готовой карточке | structured-шаг по `card` после стрима |
| S2: модель уточняет площадки и не идёт в EAM | актив может остаться `mentioned`; исход `clarify` верный |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Нет `complete_catalog.py` и вызова в runner | ✅ |
| 2 | `search_assets` не зовёт `ensure_sites` | ✅ |
| 3 | S1–S4: `search_*` и повторный `patch_facts` | ⚠️ S1/S3/S4 зелёные; S2 `clarify`, но актив `mentioned` (EAM не вызван) |
| 4 | Стол берёт `outcome` из JSON, если согласован с card | ✅ S1 create, S3 update, S4 clarify |
| 5 | Pytest без живой LLM | ✅ 38 passed |
| 6 | Lint | ✅ |

---

## Что дальше

- Задача 04: окно обращения (карточка + живой чат)
- Хвост: S2 без поиска актива — чинить промптом, не каталогом

---

## Ссылки

- [generation.md](../../../../concept/generation.md) §7
- [agent-harness.md](../../../../concept/agent-harness.md) §9
