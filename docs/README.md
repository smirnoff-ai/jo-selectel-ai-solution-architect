# Рефлекс — документация

> Навигатор. Это прототип ИИ-диспетчерской для пилота «СеверХолод».

Прототип живой. Вход для интервьюера — корневой [README.md](../README.md). Бриф: [requirements/task.md](requirements/task.md), пакет объекта: [requirements/severholod/](requirements/severholod/).

---

## Быстрый старт

1. [concept/idea.md](concept/idea.md) — что это
2. [concept/vision.md](concept/vision.md) — два контура
3. [concept/architecture.md](concept/architecture.md) — потоки
4. [concept/api-contracts-mock.md](concept/api-contracts-mock.md) — контракт мока
5. [roadmap.md](roadmap.md) — сначала мок, потом Рефлекс

---

## Два контура

| Контур | Зачем | Контракт |
|--------|-------|----------|
| **Мок СеверХолода** | Справочники и dry-run ITSM | [concept/api-contracts-mock.md](concept/api-contracts-mock.md), ТЗ [requirements/severholod/api.md](requirements/severholod/api.md) |
| **Рефлекс** | Обращения, агент, UI | [concept/api-contracts.md](concept/api-contracts.md) |

---

## Концепт

| Документ | Назначение |
|----------|------------|
| [concept/idea.md](concept/idea.md) | Суть, MVP, ограничения прототипа |
| [concept/vision.md](concept/vision.md) | Сценарии, стек, два контура |
| [concept/architecture.md](concept/architecture.md) | Sequence, слои, compose |
| [concept/data-model.md](concept/data-model.md) | Сид мока + таблицы Рефлекса |
| [concept/integrations.md](concept/integrations.md) | Мок, LLM, Langfuse |
| [concept/api-contracts-mock.md](concept/api-contracts-mock.md) | HTTP мока |
| [concept/api-contracts.md](concept/api-contracts.md) | HTTP и SSE Рефлекса |
| [concept/frontend-design.md](concept/frontend-design.md) | Визуал |
| [concept/frontend-ux-logic.md](concept/frontend-ux-logic.md) | Поведение UI |
| [concept/agent-harness.md](concept/agent-harness.md) | Агент |
| [concept/agent-security.md](concept/agent-security.md) | Защита агента |
| [concept/generation.md](concept/generation.md) | Стрим |
| rag.md | нет: semantic RAG вне scope |

---

## ТЗ и материалы заказчика

| Документ | Назначение |
|----------|------------|
| [requirements/task.md](requirements/task.md) | Селектловский бриф |
| [requirements/severholod/README.md](requirements/severholod/README.md) | Сопроводительное |
| [requirements/severholod/scope-analysis.md](requirements/severholod/scope-analysis.md) | Два контура, as-is / to-be |
| [requirements/severholod/api.md](requirements/severholod/api.md) | ТЗ API объекта |
| [requirements/severholod/functional-spec.md](requirements/severholod/functional-spec.md) | Экраны |
| [requirements/severholod/card.md](requirements/severholod/card.md) | JSON карточки |
| [requirements/severholod/harness.md](requirements/severholod/harness.md) | Канон агента у заказчика |
| [requirements/severholod/regulations.md](requirements/severholod/regulations.md) | Лестница и формулы |
| [requirements/severholod/scenarios.md](requirements/severholod/scenarios.md) | S1–S4 |
| [requirements/severholod/prompts/system.md](requirements/severholod/prompts/system.md) | System prompt |

Мокапы в `requirements/severholod/mockups/` не канон.

---

## Дорожная карта

| Документ | Назначение |
|----------|------------|
| [roadmap.md](roadmap.md) | v0.1 и follow-up 07–08 |
| [roadmap-eval.md](roadmap-eval.md) | Контракт мока + S1–S4 |
| [sprints/](sprints/) | история реализации |

---

## ADR

[adrs/](adrs/) — два контура; dry-run ITSM; рантайм агента.

---

## Skills

Установлены в `.agents/skills/` из DocPoint (стек роутера + langfuse + harness). Не ставили: landing, deepagents, чужие продуктовые skills.

---

## Методология

- [`.methodology/`](../.methodology/)
- Проектные rules: [`.cursor/rules/`](../.cursor/rules/)
