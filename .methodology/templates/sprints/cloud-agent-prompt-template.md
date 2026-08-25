# Cursor Cloud Agent — Промпт для запуска Sprint NN

> **Назначение:** тонкий лаунчер. План, DoD и решения — в документах спринта (single source of truth).
>
> **Как использовать:** скопируй всё ниже черты `---` в задачу Cloud Agent.

---

# Cursor Cloud Agent — Sprint NN ([имя], [версия roadmap])

Ты — автономный cloud-агент. [Одно предложение о цели спринта.] Пользователя нет — работаешь автономно, **качество > скорость**.

## Источник истины — читай и следуй (промпт НЕ дублирует)

1. `docs/sprints/sprint-NN-<name>/README.md` — цель, DoD, задачи, зависимости.
2. `docs/sprints/sprint-NN-<name>/audit.md` — если есть: главный чеклист дефектов.
3. `docs/sprints/sprint-NN-<name>/tasks/*/plan.md` — детальные планы задач.
4. `docs/concept/` — idea, vision, architecture, api-contracts, frontend-design, frontend-ux-logic.
5. `.cursor/rules/` (00 / 11 / 12 / 13 / 21 / 41) — **обязательны**.
6. [Опционально: `rnd/`, ADR, spec]

**При расхождении промпта и документов спринта — приоритет у документов.**

## Критические принципы

- Порядок задач/стадий **строгий** по README.
- **Skills + MCP — ДО кода** (`41-skills-mcp-router.mdc`).
- **Реальный прогон** каждой задачи: backend → curl/pytest; UI → browser (Playwright MCP или Computer Use): console clean, network без неожиданных 4xx/5xx, скрины в `tasks/NN-*/assets/`.
- **Не идти с известными дефектами.**
- WIP-коммиты в Фазе 2; финальный коммит без `wip:`; **не пушить** без явной команды.

## Автономный workflow

`21-workflow.mdc` требует «ок» пользователя. Пользователя нет → **self-review**:

- После плана: `> Self-review: ✅ (дата)` в начале `plan.md`.
- После самопроверки: то же в `summary.md`.
- Draft→Ready PR делает **человек**; ты отмечаешь «готов к ревью» в PR/summary.

## Завершение спринта

- Регресс happy-path по DoD спринта.
- Demo: прочитать `.agents/skills/demo-screencast/SKILL.md` и `references/narrate-pattern.md`; написать сценарий; записать mp4; скопировать в `docs/sprints/sprint-NN-<name>/demo.mp4`; поставить ссылку в README спринта и в `docs/roadmap.md`. Если нечего показать — фраза в README, не пустой файл.
- Обновить sprint README, roadmap, body Draft PR.

## Секреты

- Только из `.env` / secrets окружения cloud. **Не коммитить**, не логировать, не в summary.

## Старт

1. Прочитать источники истины.
2. `git checkout sprint/NN-<name>` (или создать от предыдущего sprint).
3. Task 01 → `plan.md` → self-review → реализация → прогон → `summary.md` → далее по конвейеру.
