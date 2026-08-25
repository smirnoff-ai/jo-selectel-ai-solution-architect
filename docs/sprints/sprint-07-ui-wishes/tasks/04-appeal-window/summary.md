# Summary: Task 04 — Окно обращения

> **План:** [plan.md](./plan.md)  
> **Дата закрытия:** 2026-08-25

---

## Что реализовано

- `frontend/src/components/appeal-workspace.tsx` — две колонки, SSE, pending thought / message
- `frontend/src/components/card-document.tsx` — форма слотов и JSON того же `card`
- `frontend/src/components/card-chat.tsx` — лента: вход, думаю, тулы, markdown, метка конца прогона
- `frontend/src/lib/appeal-stream.ts` — `thought.delta` и `message_delta`
- `frontend/src/components/journal-view.tsx` — строка журнала открывает обращение
- `frontend/src/components/app-shell.tsx` — «Создать обращение» на столе и в журнале

---

## Отклонения от плана

Ветка осталась `feat/backend-7-create-agent-stream`, не `feat/frontend-7-appeal-window`.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| Форма перерисовывается снимком `card` после `card_updated` | Нет частичного патча в React | — |
| Заглушки «агент разбирает…» нет | Сразу видны дельты и карточки тулов | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| Финальный markdown модели не приходил (ToolStrategy) | В 06: отчёт в ленту после guard, если `message_final` пуст |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Нет заглушки; видны дельты мысли и ответа | ✅ |
| 2 | Форма покрывает слоты; JSON — тот же card | ✅ |
| 3 | Клик по строке журнала открывает обращение | ✅ |
| 4 | Кнопка создания в шапке | ✅ |
| 5 | Lint фронта | ✅ |

---

## Что дальше

- Задачи 05–06 на той же ветке (закрыты в этом спринте)
- Визуал пульта — sprint 08

---

## Ссылки

- [appeal-window.md](../../appeal-window.md)
- [generation.md](../../../../concept/generation.md)
