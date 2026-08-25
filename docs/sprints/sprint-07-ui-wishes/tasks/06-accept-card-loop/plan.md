# Task 06: Accept и проверка карточного цикла

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** текущая `feat/backend-7-create-agent-stream`
> **Spec:** [05-card-loop/plan.md](../05-card-loop/plan.md), [scenarios.md](../../../../requirements/severholod/scenarios.md)

---

## Цель

S1–S4 и живое окно соответствуют новому циклу: слот слева загорается только после `update_card`; расчёт — после явного `calculate`.

---

## Состав работ

- [ ] `scripts/accept_s1_s4.py`: после поиска есть `update_card`; на create/update есть `calculate`
- [ ] Пересобрать backend и frontend (код в образе)
- [ ] `make accept`
- [ ] Браузер: создать обращение S1-подобное, убедиться что поиск не заполняет слот, запись и расчёт видны, итог понятен диспетчеру
- [ ] Сверка с ТЗ: однозначный объект для create; два актива — clarify; без заявки на площадку при ненайденном активе
- [ ] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Accept проверяет `update_card` после поиска и `calculate` на create/update | `scripts/accept_s1_s4.py` |
| 2 | S1–S4 по ожиданиям пакета (S2/S4 — clarify) | `make accept` |
| 3 | В окне обращения слот не загорается от одного `get_contract` / поиска | браузер |
| 4 | В чате видны `update_card` и `calculate`, итог для диспетчера | браузер |

---

## Артефакты

- `scripts/accept_s1_s4.py`
- `docs/sprints/sprint-06-accept-s1-s4/report.json` (пишет accept)
- `docs/sprints/sprint-07-ui-wishes/README.md` — статус задачи

---

## Scope

**Трогаем:** accept, проверка live, README спринта.

**НЕ трогаем:** визуал пульта; `summary.md` до «ок».
