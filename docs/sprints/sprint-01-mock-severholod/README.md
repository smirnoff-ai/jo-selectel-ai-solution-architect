# Sprint 01: mock-severholod

> **Версия roadmap:** v0.1
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** Done
> **Открыт:** 2026-08-25

---

## Цель спринта

Интервьюер может поднять мок систем СеверХолода и проверить честный поиск 0/1/N и dry-run заявок без агента и UI.

---

## DoD спринта

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `/health` отвечает ok | pytest + curl |
| 2 | Два ХУ-17 без площадки — оба актива | pytest |
| 3 | Пустой поиск — 200 и `items: []` | pytest |
| 4 | Dry-run create: accepted, persisted false, would-id | pytest |
| 5 | ФЛК провал — 400 | pytest |
| 6 | Образ собирается, healthcheck есть | Dockerfile |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | HTTP + сид | Done | [plan](tasks/01-http-seed/plan.md) | [summary](tasks/01-http-seed/summary.md) |

---

## Demo

demo-видео не записывали: нет UI.
