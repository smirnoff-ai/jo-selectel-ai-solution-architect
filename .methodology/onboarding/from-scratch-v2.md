# Onboarding: From Scratch (v2 — после опыта DocPoint)

> **Режим:** новый проект, нет ни кода, ни продуктовой документации (или только ТЗ / PoC).
> **Отличие от [from-scratch.md](from-scratch.md):** расширенный конвейер концепта, работа от готового ТЗ, UI-доки, проектные rules, шаблон cloud-агента.
>
> **Референс-сессия:** старт DocPoint — [agent transcript 4b4601eb](https://cursor.com) (2026-05-28).

**Скопируй блок «Промпт для агента» ниже и отправь как первое сообщение.**

---

## Когда использовать v2, а не v1

| Ситуация | Версия |
|----------|--------|
| Чистый greenfield, ответы только из головы | [from-scratch.md](from-scratch.md) |
| Есть **ТЗ / договор / requirements** — ответы извлекаем из файла | **v2 (этот документ)** |
| Есть **R&D / PoC** — переносим в vision/architecture | **v2** |
| Продукт с **веб-UI** — нужны `frontend-design` + `frontend-ux-logic` | **v2** |
| Планируется **cloud-агент** на реализацию | **v2** (+ шаблон cloud-agent-prompt) |
| Есть **LLM-агент** — нужны `agent-harness` + `agent-security` + обычно `generation` | **v2** |
| Есть **RAG / retrieval-tool** — нужен `rag.md` | **v2** |
| Агент предлагает **профиль** (`agent-platform-v1`), а не допрос по каждой развилке | **v2** |

---

## Дополнительные шаблоны (нет в базовой `.methodology/templates/`)

Созданы по опыту DocPoint — лежат рядом с базовыми:

| Шаблон | Назначение |
|--------|------------|
| [frontend-design-template.md](../templates/concept/frontend-design-template.md) | Визуальная спецификация UI |
| [frontend-ux-logic-template.md](../templates/concept/frontend-ux-logic-template.md) | Поведение UI (клики, persistence, recovery) |
| [docs-readme-template.md](../templates/docs/docs-readme-template.md) | Навигатор `docs/README.md` |
| [audit-template.md](../templates/sprints/audit-template.md) | Чеклист дефектов для refactor-спринта |
| [design-discussion-template.md](../templates/sprints/design-discussion-template.md) | Живой док обсуждения до ADR/plan |
| [cloud-agent-prompt-template.md](../templates/sprints/cloud-agent-prompt-template.md) | Тонкий лаунчер автономного спринта |
| [roadmap-eval-template.md](../templates/roadmap/roadmap-eval-template.md) | Отдельный трек (бенчмарк, eval) |
| [agent-harness-template.md](../templates/concept/agent-harness-template.md) | Конфиг, LLM-путь, tools, память |
| [agent-security-template.md](../templates/concept/agent-security-template.md) | Уровень защиты, угрозы |
| [rag-template.md](../templates/concept/rag-template.md) | Индекс и search как tool |
| [generation-template.md](../templates/concept/generation-template.md) | invoke/stream, события, история |
| [profiles/README.md](../profiles/README.md) | Как предлагать профиль |

**Проектные rules** (не шаблон, а чеклист копирования): см. шаг 10 в промпте ниже.

---

## Промпт для агента

```
Мы начинаем новый проект с нуля по методологии AI-Driven Development (расширенный конвейер v2).

Методология: `.methodology/METHODOLOGY.md` + шаблоны `.methodology/templates/`.
Прочитай METHODOLOGY.md прежде чем начинать.

## Общие правила работы

1. **Пошагово.** На каждом шаге: вопросы (если нужны) → черновик/план → документ → жди явного «ок».
2. **Источник истины.** Если я указал файл ТЗ (`docs/requirements-*.md`, договор, appendix) — **сначала извлеки ответы оттуда**, спрашивай только пробелы.
3. **Plan Mode для сложных шагов** (vision, architecture, api-contracts, frontend-design): сформулируй план в чате, дождись «ок», затем пиши файл.
4. **Итерации нормальны.** Если я прошу «переделай план / шаг целиком» — не спорь, обнови план и покажи снова.
5. **Skills + MCP до кода** — на этапе концепта при проектировании агента, БД, API сверяйся с MCP (см. будущие `.cursor/rules/41-skills-mcp-router.mdc`).
6. **Не упрощай стек** ради «быстрее в пилоте», если в проектных conventions уже зафиксирован стек (Next.js, shadcn, …). Embeddable UI — отдельный пакет, не отказ от conventions.
7. **R&D / PoC:** если есть папка `rnd/` или аналог — явно раздели в vision: что переносим в продукт, что не переносим (границы доступа к данным, точка входа CLI→API).

---

## ШАГ 0: Входные материалы (один раз)

Спроси одним сообщением:

- Есть ли **ТЗ / requirements** (путь к файлу)?
- Есть ли **R&D / PoC** (путь)?
- Есть ли **готовые conventions** (`.cursor/rules/`, другой репо)?
- **MVP** = весь пилот по ТЗ или суженный v0.1?
- Нужен ли **отдельный eval/benchmark-трек** (да/нет)?
- Есть ли **LLM-агент**? RAG? Стрим ответа в UI?
- Принимаем ли файлы / изображения во вход?
- Контур пилот или production (уровень защиты)?
- Если агент — предложить профиль `agent-platform-v1` и спросить: целиком / отклонения / без профиля.

Если ТЗ уже приложено — не дублируй вопросы, извлеки сам.

---

## ШАГ 0b: Профиль

Если продукт агентный — покажи таблицу профиля `agent-platform-v1` (кратко)
и дождись: «берём» / список отклонений / «без профиля».
Дальше заполняй шаблоны, подставляя утверждённые ответы, не переспрашивая их.

---

## ШАГ 1: idea.md

Шаблон: `.methodology/templates/concept/idea-template.md`
Создай: `docs/concept/idea.md`

Из ТЗ или вопросов: название, суть, **одна ключевая роль** (если пилот для одной аудитории — не раздувай), проблема, MVP-scope, 5–7 примеров действий, критерий успеха MVP одной фразой, блок «не является».

---

## ШАГ 2: vision.md

Шаблон: `.methodology/templates/concept/vision-template.md`
Создай: `docs/concept/vision.md`

Обязательно:

- Сценарии по **всему** ТЗ (группами), не 3–5 обобщённых фраз.
- **Mermaid** high-level; **раздельные** компоненты данных (не сливать разные facade/API в один узел).
- Если UI embeddable — monorepo `apps/` + `packages/`, пакет **без** зависимостей от framework хоста (`next/*` и т.п.).
- Если есть PoC — § «миграция из R&D»: что берём кодом, что меняем на границах.
- Agent: конфигурации (id, LLM, промпты/skills per config или общие), `AgentFactory`, откуда UI получает список конфигов.
- Trace/stream: типы событий для UI (не foreground/background — явные `type`), Langfuse для observability, не ручная сборка trace для UI.
- Таблица технологий **согласована** с conventions (не Vite «для простоты», если conventions = Next.js).
- Короткая таблица пути к LLM и ссылка на harness — не переносить каталог tools и словарь событий в vision.
- Три контура памяти одной фразой + ссылки на harness и data-model.
- Заглушка ADR в `docs/decisions/`.

Итерации по vision — нормальны (обсуждали билдеры, runtime protocol, context window — фиксируй в vision по мере согласования).

---

## ШАГ 3: architecture.md (если ≥2 компонентов)

Шаблон: `.methodology/templates/concept/architecture-template.md`
Создай: `docs/concept/architecture.md`

Обязательно:

- Sequence-диаграммы ключевых сценариев (lazy-load, новый чат, stream/invoke).
- **API → Repository → DB**, не API напрямую в Postgres.
- Транспорт стрима (SSE / …) — зафиксировать здесь или ADR.
- Docker-compose локально; кратко production.

---

## ШАГ 4: data-model.md (если есть БД)

Шаблон: `.methodology/templates/concept/data-model-template.md`
Создай: `docs/concept/data-model.md`

Перед схемой — прочитать skill `postgresql-table-design` (когда rules уже есть).

---

## ШАГ 5: integrations.md (если есть внешние сервисы)

Шаблон: `.methodology/templates/concept/integrations-template.md`
Создай: `docs/concept/integrations.md`

---

## ШАГ 6: api-contracts.md (если есть публичный API)

Шаблон: `.methodology/templates/concept/api-contracts-template.md`
Создай: `docs/concept/api-contracts.md`

Для агентного UI: словарь `TraceEvent`, SSE-протокол, контракт «final после chunks». Детали протокола живут в `generation.md`; api-contracts — пути и примеры кадров.

---

## ШАГ 6a: frontend-design.md (если есть веб-UI)

Шаблон: `.methodology/templates/concept/frontend-design-template.md`
Создай: `docs/concept/frontend-design.md`

Порядок работы (как в DocPoint):

1. Задай **вопросы по оформлению** (тема, layout, trace, таблицы отчёта, …).
2. Опционально — reference-мокапы в `docs/concept/refs/` с **явным дисклеймером**: reference only, не pixel-perfect; источник истины — текст спецификации.
3. Зафиксируй per-event streaming UI (как Cursor): live expand → auto-collapse, не один монолитный trace-блок.

---

## ШАГ 6b: frontend-ux-logic.md (если есть веб-UI)

Шаблон: `.methodology/templates/concept/frontend-ux-logic-template.md`
Создай: `docs/concept/frontend-ux-logic.md`

Спутник `frontend-design.md`: **как ведёт себя** UI — клики, переключение ДИ при активном стриме, persistence (`localStorage` / `sessionStorage`), recovery после reload, optimistic UI, error/empty/loading. Для агентного UI — Send/Stop и фоновый стрим согласовать с `generation.md`.

---

## ШАГ 6c: agent-harness.md (если есть агент)

Шаблон: `.methodology/templates/concept/agent-harness-template.md`
Создай: `docs/concept/agent-harness.md`
Plan Mode. Подставь ответы профиля, спроси только пробелы и отклонения.

---

## ШАГ 6d: agent-security.md (если есть агент)

Шаблон: `.methodology/templates/concept/agent-security-template.md`
Создай: `docs/concept/agent-security.md`

---

## ШАГ 6e: rag.md (если есть индекс / retrieval-tool)

Шаблон: `.methodology/templates/concept/rag-template.md`
Создай: `docs/concept/rag.md`

---

## ШАГ 6f: generation.md (если есть LLM-ответ / стрим)

Шаблон: `.methodology/templates/concept/generation-template.md`
Создай: `docs/concept/generation.md`
Для агентного UI: словарь событий, SSE, «final после chunks», что пишется в историю.

---

## ШАГ 7: roadmap.md

Шаблон: `.methodology/templates/roadmap/roadmap-template.md`
Создай: `docs/roadmap.md`

- **v0.1 MVP** — единственный детально декомпозированный этап (8–12 спринтов max на первый проход).
- v0.2+ — одной строкой в backlog, без ложной детализации.
- Если eval-трек — отдельный `docs/roadmap-eval.md` по шаблону `roadmap-eval-template.md`.

---

## ШАГ 8: Первый sprint

- `docs/sprints/sprint-01-<name>/README.md` — по `sprint-template.md`
- `docs/sprints/sprint-01-.../tasks/01-<name>/plan.md` — по `plan-template.md` с **детальным** DoD и артефактами (infra-sprint: repo, backend skeleton, frontend skeleton, docker, integrations)
- Опционально: `docs/sprints/sprint-01-.../cloud-agent-prompt.md` — по `cloud-agent-prompt-template.md`, если реализацию будет вести cloud-агент

При закрытии каждого спринта с runtime агент записывает demo-видео skill'ом `demo-screencast` (ставится вместе с методологией в `.agents/skills/`). Сценарий — один файл рядом с UI. Копия mp4 — в папке спринта. После последнего спринта версии — отдельное сквозное демо.

---

## ШАГ 9: docs/README.md

Шаблон: `.methodology/templates/docs/docs-readme-template.md`
Навигатор по всем созданным документам + ссылка на ТЗ + sprint/eval.

---

## ШАГ 10: Проектные rules (`.cursor/rules/`)

Скопировать и адаптировать из generic `.methodology/rules/`:

| Файл | Содержание |
|------|------------|
| `00-methodology.mdc` | Entry point, структура docs, 4 фазы |
| `11-conventions.mdc` | Стек, git (stack branches, WIP), E2E, доки |
| `12-*-structure.mdc` | Правила кода backend (по необходимости) |
| `13-frontend.mdc` | Frontend conventions (по необходимости) |
| `21-workflow.mdc` | 4 фазы, Playwright MCP / Computer Use |
| `41-skills-mcp-router.mdc` | Skills + MCP обязательны до кода |

Не править `.methodology/` in-place — проект живёт в `.cursor/rules/`.

После первого cloud-спринта дополнять rules по audit follow-ups (Draft PR, скрины в репо, scope exception для infra-fix).

---

## ШАГ 10b: Skills стека

По `.methodology/rules/40-skills-router.mdc` выпиши skills, нужные выбранному стеку и профилю.
Для каждого: есть ли `.agents/skills/<name>/SKILL.md`? Нет — скопируй из `~/.agents/skills/` / `~/.cursor/skills/` или из другого проекта и проверь `Read`.
Строка в таблице есть, файла нет — **стоп**, не начинай реализацию «по здравому смыслу».
Покажи список: установлено / откуда взято / чего не хватает. Жди «ок».

---

## ШАГ 11 (опционально): ТЗ в репозитории

Если ТЗ пришло извне — положить в `docs/requirements-*.md` или `docs/contract/` и ссылаться из idea/vision.

---

Начни с **ШАГа 0** — спроси про входные материалы (или прочитай уже указанный ТЗ) и перейди к ШАГу 1.
```

---

## Чек-лист по завершении онбординга v2

### Концепт

- [ ] `docs/concept/idea.md`
- [ ] `docs/concept/vision.md` (mermaid, сценарии, PoC-границы)
- [ ] `docs/concept/architecture.md` (или пропуск с обоснованием)
- [ ] `docs/concept/data-model.md` (или пропуск)
- [ ] `docs/concept/integrations.md` (или пропуск)
- [ ] `docs/concept/api-contracts.md` (или пропуск)
- [ ] `docs/concept/frontend-design.md` (если UI)
- [ ] `docs/concept/frontend-ux-logic.md` (если UI)
- [ ] профиль утверждён или явно отвергнут
- [ ] `docs/concept/agent-harness.md` (или пропуск с обоснованием)
- [ ] `docs/concept/agent-security.md` (или пропуск)
- [ ] `docs/concept/rag.md` (или пропуск)
- [ ] `docs/concept/generation.md` (или пропуск)
- [ ] `docs/concept/refs/` + дисклеймер reference-only (если были мокапы)

### Планирование

- [ ] `docs/roadmap.md` (MVP детально)
- [ ] `docs/roadmap-eval.md` (если eval-трек)
- [ ] `docs/sprints/sprint-01-.../README.md`
- [ ] `docs/sprints/sprint-01-.../tasks/01-.../plan.md`
- [ ] `docs/sprints/sprint-01-.../cloud-agent-prompt.md` (если cloud)

### Инфраструктура методологии

- [ ] `docs/README.md`
- [ ] `.cursor/rules/00, 11, 21, 41` (+ 12/13 по стеку)
- [ ] skills стека лежат в `.agents/skills/` и открываются по путям из `40-skills-router`
- [ ] ТЗ/requirements в `docs/` (если есть)

---

## После онбординга — реализация

**Copilot (IDE):** правило двух согласований — «ок» на plan и «ок» на самопроверку.

**Cloud-агент:** self-review вместо «ок» (строка `> Self-review: ✅` в plan/summary); см. `cloud-agent-prompt-template.md`.

**Refactor / аудит:** перед спринтом — `audit.md` по `audit-template.md`.

**Сложная архитектура до plan:** `design-discussion.md` по `design-discussion-template.md`.

---

## Что перенести в следующий проект (процесс, не стек)

Рекомендуемые ответы на развилки — в `.methodology/profiles/agent-platform-v1.md`.
Этот список больше не источник default'ов.

Процессные уроки оставить: ТЗ как источник на idea/vision; два UI-дока (design + ux-logic); проектные `.cursor/rules/` с первого дня; отдельный eval-трек; customer snapshot — когда появится поставка.
