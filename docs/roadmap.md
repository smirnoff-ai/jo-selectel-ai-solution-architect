# Roadmap — Рефлекс

> **Vision:** [concept/vision.md](concept/vision.md)
> **Последнее обновление:** 2026-08-26

---

## Цель продукта

Прототип: свободный текст → видимый разбор → контролируемое действие (dry-run заявки или честный останов). Сначала живой мок объекта, потом Рефлекс.

---

## Легенда

- Planned — запланирован
- In Progress — в работе
- Done — завершён
- Paused — на паузе

---

## v0.1 — MVP: два контура  (Done)

**Цель:** интервьюер может поднять compose, прогнать мок curl'ом, затем разобрать S1–S4 в UI.

**Демо версии:** live в UI (`http://localhost:3000`). Скринкаст спринта — [sprints/sprint-06-accept-s1-s4/demo.mp4](sprints/sprint-06-accept-s1-s4/demo.mp4).

**Ключевые результаты:**

- [x] Мок отвечает по [api-contracts-mock.md](concept/api-contracts-mock.md): 0/1/N и dry-run
- [x] Диспетчер создаёт обращение и видит карточку со стримом
- [x] S1 create, S2 clarify, S3 update T-884, S4 clarify без заявки на площадку
- [x] README задания 2–3 страницы и журнал AI; Langfuse — локальный контейнер, прогон не валит карточку

**Спринты:**

| # | Sprint | Цель | Статус |
|---|--------|------|--------|
| 01 | [mock-severholod](sprints/sprint-01-mock-severholod/README.md) | Сервис, сид, контракт, тесты поиска и dry-run. Без агента и UI | Done |
| 02 | [reflex-skeleton](sprints/sprint-02-reflex-skeleton/README.md) | backend+frontend каркас, Postgres, compose, логин, fail-fast секретов | Done |
| 03 | [appeals-api](sprints/sprint-03-appeals-api/README.md) | Создание обращения, стол, журнал, карточка без агента | Done |
| 04 | [agent-stream](sprints/sprint-04-agent-stream/README.md) | Харнес и промпт переписать skill'ом (не копировать черновик), пять тулов, SSE, предохранитель, dry-run | Done |
| 05 | [dispatcher-ui](sprints/sprint-05-dispatcher-ui/README.md) | Стол, журнал, форма, карточка, чат по ux-logic | Done |
| 06 | [accept-s1-s4](sprints/sprint-06-accept-s1-s4/README.md) | Сценарии пакета, README, журнал AI, demo | Done |
| 07 | [live-agent](sprints/sprint-07-ui-wishes/README.md) | `create_agent`, стрим, Langfuse thread, без `complete_catalog`, окно обращения | Done |
| 08 | [agent-voice](sprints/sprint-08-agent-voice/README.md) | Отчёт модели без Finale, без guard, широкий поиск заявок | Done |

---

## v0.2 — после пилота  (Planned)

Одной строкой, без декомпозиции: очередь входящих, живые каналы, живой write в ITSM, SSO, назначение группы, праздничный календарь SLA.

---

## Backlog (не в v0.1)

- Stop / cancel прогона
- Пагинация журнала
- Кнопка «агент не прав»
- Semantic RAG
- Выбор модели в UI
