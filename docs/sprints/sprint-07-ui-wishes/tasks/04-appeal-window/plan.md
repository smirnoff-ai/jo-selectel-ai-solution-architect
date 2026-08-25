# Task 04: Окно обращения

> **Sprint:** [../../README.md](../../README.md)  
> **Тип:** feat  
> **Ветка:** `feat/frontend-7-appeal-window`  
> **Spec:** [appeal-window.md](../../appeal-window.md), [generation.md](../../../../concept/generation.md), [docpoint-stream.md](../../docpoint-stream.md)

---

## Цель

Экран обращения: слева документ `card` (форма / JSON), справа чат на высоту окна со стримом токен за токеном. Без заглушки «агент разбирает…».

---

## Состав работ

- [ ] Каркас: две колонки на оставшуюся высоту, скролл колонок по отдельности
- [ ] Слева: форма слотов по appeal-window.md + переключатель JSON того же объекта
- [ ] Справа: pending-буферы `thought` / `message_delta`, тулы сразу карточками (техн. + бизнес-имя, args/result), markdown ответа
- [ ] Журнал: открытие по клику на всю строку
- [ ] «Создать обращение» в верхнем тулбаре (если ещё не дожато)
- [ ] Прогон в браузере: стрим, слоты по `card_updated`, пустой/ошибка
- [ ] Самопроверка по DoD
- [ ] (после «ок») `summary.md`, строка задачи в sprint README

## Skills

Read: `nextjs-app-router-patterns`, `vercel-react-best-practices`, `frontend-design`, `shadcn`, `web-design-guidelines`.

MCP: не обязателен.

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Нет заглушки «агент разбирает…»; видны дельты мысли и ответа | браузер, живой прогон |
| 2 | Форма покрывает слоты из appeal-window.md; JSON — тот же `card` | браузер |
| 3 | Клик по строке журнала открывает обращение | браузер |
| 4 | Кнопка создания в шапке на столе и в журнале | браузер |
| 5 | Lint фронта | `make lint-frontend` |

> Рестайл логина / стола / журнала — не проверяем (sprint 08).

---

## Артефакты

- `frontend/src/components/appeal-workspace.tsx` — поток событий, pending
- `frontend/src/components/card-document.tsx` — форма / JSON
- `frontend/src/components/card-chat.tsx` — лента, курсор, тулы
- `frontend/src/lib/appeal-stream.ts` — `message_delta` / thought delta
- `frontend/src/components/journal-view.tsx` — клик по строке
- `frontend/src/components/app-shell.tsx` — кнопка создания
- новые компоненты слота/тула — только если иначе раздувается файл
- `docs/sprints/sprint-07-ui-wishes/tasks/04-appeal-window/summary.md` — после «ок»

---

## Scope

**Трогаем:** только файлы из «Артефакты».

**НЕ трогаем:** визуал корзин стола и логина; backend-харнес (уже 02–03); `complete_catalog`.

---

## Риски и допущения

- События дельт должны уже идти с backend (02). Если нет — не рисовать фейковый стрим.
- Макеты — тон, не копировать неон и лишние колонки.

---

## Открытые вопросы

- Нет. Стартовать после закрытия 03.
