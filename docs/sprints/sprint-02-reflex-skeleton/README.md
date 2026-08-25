# Sprint 02: reflex-skeleton

> **Версия roadmap:** v0.1
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** Done
> **Открыт:** 2026-08-25

---

## Цель спринта

Интервьюер поднимает compose и входит в UI одним логином. Агента и обращений ещё нет.

---

## DoD спринта

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Compose: mock, postgres, backend, frontend, langfuse | `make up` |
| 2 | Backend не стартует без обязательных Settings | pytest + ручной прогон |
| 3 | Логин 200 + cookie; неверная пара 401 | pytest |
| 4 | `/login` в браузере, после входа стол-заглушка | browser |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Compose + логин | Done | [plan](tasks/01-compose-login/plan.md) | [summary](tasks/01-compose-login/summary.md) |

---

## Demo

demo-видео не записывали: закрытие версии — после спринта 06.
