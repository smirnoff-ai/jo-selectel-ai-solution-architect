# Sprint 07: live agent + окно обращения

> **Версия roadmap:** v0.1 follow-up  
> **Roadmap:** [../../roadmap.md](../../roadmap.md)  
> **Статус:** Done  
> **Открыт:** 2026-08-25  
> **Закрыт:** 2026-08-25

Папку не переименовывали: сначала здесь была копилка UI. Спеки остаются входом, не пиксель-перфекционизм.

Вход: [notes.md](notes.md) · [appeal-window.md](appeal-window.md) · [docpoint-stream.md](docpoint-stream.md) · [mocks/](mocks/)

**Не в этом спринте:** визуал логина, стола, журнала («пульт») — [sprint 08](../../roadmap.md).

---

## Цель спринта

`create_agent` со стримом и Langfuse как в DocPoint; финал модели, не код; без тихого `complete_catalog`; живое окно обращения (карточка + чат). `make up` поднимает UI.

---

## DoD спринта

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `make up` отдаёт frontend на `:3000` | compose, без ручного `make dev-frontend` |
| 2 | Чат: thought и ответ токен за токеном, тулы сразу | браузер, не dump после паузы |
| 3 | Langfuse: session/thread = `appeal_id`, видны LLM и tools | UI Langfuse `:3001` |
| 4 | Финал — JSON модели; guard только страховка по уже найденным слотам | `make accept` + трасса |
| 5 | `complete_catalog` нет; слоты только из тулов модели | нет файла, нет вызова в runner |
| 6 | Трасса: поиски read-only → `update_card` → при create/update явный `calculate` | `make accept` / лента |
| 7 | S1–S4 зелёные без добора кодом | `make accept` |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Образ frontend / `make up` | Done | [plan](tasks/01-compose-frontend/plan.md) | [summary](tasks/01-compose-frontend/summary.md) |
| 02 | `create_agent` + стрим + Langfuse | Done | [plan](tasks/02-create-agent-stream/plan.md) | [summary](tasks/02-create-agent-stream/summary.md) |
| 03 | Финал модели, выкинуть `complete_catalog` | Done | [plan](tasks/03-finale-no-catalog/plan.md) | [summary](tasks/03-finale-no-catalog/summary.md) |
| 04 | Окно обращения (карточка + живой чат) | Done | [plan](tasks/04-appeal-window/plan.md) | [summary](tasks/04-appeal-window/summary.md) |
| 05 | Карточный цикл: спека, тулы, промпт | Done | [plan](tasks/05-card-loop/plan.md) | [summary](tasks/05-card-loop/summary.md) |
| 06 | Accept и проверка цикла в окне | Done | [plan](tasks/06-accept-card-loop/plan.md) | [summary](tasks/06-accept-card-loop/summary.md) |

---

## Итог

Live-агент в `create_agent`, стрим мысли и тулов, Langfuse session = `appeal_id`. Тихого `complete_catalog` нет: поиски только читают, карточку пишет `update_card`, срок — явный `calculate`. Окно: слева документ, справа чат. `make accept` S1–S4 зелёные.

demo-видео не записывали.

Хвост: отчёт в чат пока собирает код, если модель не дала markdown (Finale — стоп). Голос модели в briefing — не в этом спринте.
