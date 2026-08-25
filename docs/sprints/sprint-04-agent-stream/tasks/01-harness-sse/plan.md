# Task 01: Harness + SSE

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/backend-4-agent`
> **Spec:** [agent-harness.md](../../../../concept/agent-harness.md), [generation.md](../../../../concept/generation.md)
>
> Self-review: ✅ (2026-08-25)

---

## Цель

Один агент `reflex-appeal`: пять тулов, финал, предохранитель, примерка ITSM, SSE, Langfuse.

---

## Состав работ

- [x] Переписать `prompts/system.md` skill'ом harness-construction
- [x] Тулы + binding 0/1/N + расчёт + guard + dry-run
- [x] Прогон на POST/reply, словарь SSE (`run_tool_loop` вместо `create_agent`)
- [x] pytest без живой LLM; live-smoke отдельно

## Skills

Read: agent-harness-construction, langfuse, fastapi-templates, python-testing-patterns.

MCP: Docs by LangChain (`create_agent`, stream, `response_format`); Langfuse docs (CallbackHandler).

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Binding / SLA / guard зелёные | pytest |
| 2 | Stream не заглушка | pytest |
| 3 | Lint | ruff |

---

## Scope

**Трогаем:** `backend/`, `docs/requirements/severholod/prompts/system.md`, sprint docs, roadmap.

**НЕ трогаем:** полный UI, S1–S4 как e2e приёмка.
