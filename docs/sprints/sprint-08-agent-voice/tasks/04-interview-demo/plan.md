# Task 04: Интервью-скринкаст S1–S4

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** docs
> **Ветка:** текущая
> **Spec:** [scenarios.md](../../../../requirements/severholod/scenarios.md), skill `demo-screencast`

---

## Цель

Живой скринкаст для ревьюера тестового: вход, стол, S1–S4 через пресеты, стрим агента, карточка, уточняющие вопросы.

---

## Состав работ

- [x] `plan.md`
- [ ] `frontend/scripts/interview-demo.mjs`
- [ ] `make demo`
- [ ] Запись mp4, копия в спринт
- [ ] Ссылки в README спринта, roadmap, корневой README
- [ ] Самопроверка по DoD
- [ ] (после «ок» пользователя) `summary.md`

## Skills

Read: `demo-screencast` + `references/narrate-pattern.md`.

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Сценарий пишет mp4 skill'ом | `make demo` |
| 2 | Live S1 create, S2 clarify + вопросы + реплика, S3 update T-884, S4 not_found + вопросы | ролик |
| 3 | Курсор, главы, субтитры, русская озвучка | ролик |
| 4 | Копия в спринте и ссылки | файлы |

---

## Артефакты

- `frontend/scripts/interview-demo.mjs` — сценарий записи
- `Makefile` — цель `demo`
- `docs/sprints/sprint-08-agent-voice/demo.mp4` — копия ролика
- `docs/sprints/sprint-08-agent-voice/README.md` — секция Demo
- `docs/roadmap.md` — ссылка v0.1
- `README.md` — блок «Демо для ревьюера»

---

## Scope

**Трогаем:** только файлы из списка «Артефакты» и этот `plan.md`.

**НЕ трогаем:**
- UI, агент, пресеты
- sprint-06 demo
- живой write ITSM
- `summary.md` до второго «ок»

---

## Риски и допущения

- Живой LLM: исход может уехать. Таймаут прогона 180 с; при неверном исходе запись падает, перезаписываем.
- `/opt/cursor/artifacts` может отсутствовать — Makefile создаёт каталог, иначе `DEMO_OUT`.

---

## Открытые вопросы

- [x] Live vs обход готовых карточек — live.
