# Summary: Task 01 — Accept + README + demo

> **План:** [plan.md](./plan.md)
> **PR:** будет после merge
> **Дата закрытия:** 2026-08-25

---

## Что реализовано

- `scripts/accept_s1_s4.py` + `make accept` — живые S1–S4, отчёт `docs/sprints/sprint-06-accept-s1-s4/report.json`
- `README.md`, `docs/ai-journal.md` — пакет для интервьюера
- `frontend/scripts/sprint-06-demo.mjs` → `docs/sprints/sprint-06-accept-s1-s4/demo.mp4`
- `backend/src/backend/agent/complete_catalog.py` — добор CRM/EAM/ITSM кодом после цикла тулов
- `backend/src/backend/agent/bindings.py` — адрес сужает 2 площадки/актива; тикет не клеим к not_found/ambiguous

---

## Отклонения от плана

Нет по составу. Добор справочников не планировали отдельно: Qwen пропускал `search_sites` / `search_tickets` на S3, без кода кейс красный.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| `complete_catalog` после tool loop | Binding пишет код, не порядок тулов модели | — |
| Адрес из текста сужает N площадок | «Дмитровском» — не угадывание Москвы | — |
| Тикет только при resolved активе | S4/S2 не клеить к T-884 | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| Пустой поиск «Андрей» хоронил СеверФуд | не `not_found`, если клиент уже resolved / query ≠ mention |
| S3 без search_sites: site ambiguous из двух ХУ-17 | адрес в `apply_*` + добор CRM |
| S4 клеился к T-884 | `apply_tickets` молчит при asset not_found/ambiguous |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Жёсткие поля S1–S4 | ✅ `make accept` OK |
| 2 | README ≤ 3 стр. | ✅ |
| 3 | demo.mp4 в спринте | ✅ |
| 4 | Lint / тесты backend | ✅ |

---

## Что дальше

- Заказчик смотрит S1–S4 вживую; отдельное видео версии не пишем
- Циклы приёмки vs `task.md` §9–12 — по отдельной просьбе

---

## Ссылки

- [scenarios.md](../../../../requirements/severholod/scenarios.md)
- [agent-harness.md](../../../../concept/agent-harness.md)
