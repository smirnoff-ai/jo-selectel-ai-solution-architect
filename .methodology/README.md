# AI-Driven Development

Самодостаточный методологический пакет для AI-driven / Spec-driven разработки с агентами.

Скопируйте папку `.methodology/` в любой новый или существующий проект — и команда (или агент) сразу получает единый проектный язык, структуру документов, правила процесса и точки входа.

---

## Что внутри

```
.methodology/
├── METHODOLOGY.md          # цельное описание: 5 слоёв, иерархия, поток работы
├── GLOSSARY.md             # словарь терминов
├── rules/                  # правила для .cursor/rules/
├── skills/                 # поставляемые agent skills (копируются в .agents/skills/)
├── templates/              # шаблоны для всех слоёв
├── profiles/               # именованные предложения ответов на развилки
├── onboarding/             # точки входа: from-scratch, from-scratch-v2, existing-code, continue-project
├── ci/                     # стартер CI/Git
└── examples/               # живые примеры заполненной методологии
```

---

## Установка в проект (4 шага)

### Шаг 1. Скопировать пакет

```bash
cp -r .methodology/ /path/to/your-project/.methodology/
```

### Шаг 2. Активировать правила в Cursor

```bash
mkdir -p /path/to/your-project/.cursor/rules/methodology
cp .methodology/rules/*.mdc /path/to/your-project/.cursor/rules/methodology/
```

Убедитесь, что правила `alwaysApply: true` в метаданных каждого `.mdc` файла, или включите их вручную в настройках Cursor.

### Шаг 3. Поставить skills

Рантайм читает `.agents/skills/`, не `.methodology/skills/`. Сначала копируются **поставляемые** skills пакета, затем недостающие из роутера — с машины.

```bash
mkdir -p /path/to/your-project/.agents/skills
cp -R .methodology/skills/. /path/to/your-project/.agents/skills/
```

Дальше по [`rules/40-skills-router.mdc`](rules/40-skills-router.mdc): выпиши имена под стек и профиль. Чего нет в `.agents/skills/` — возьми из `~/.agents/skills/`, `~/.cursor/skills/` или другого проекта. Проверь `Read` по пути из таблицы. Нет файла — skill не установлен, работу не начинай.

Новый репозиторий из этого канона удобнее поднимать скиллом `init-methodology-project` в репозитории методологии: он копирует пакет, rules и skills и выдаёт промпт для нового чата.

### Шаг 4. Выбрать onboarding-режим

| Ситуация | Промпт |
|----------|--------|
| Проект с нуля — нет ни кода, ни документов | [`onboarding/from-scratch.md`](onboarding/from-scratch.md) |
| С нуля + ТЗ/PoC, веб-UI, cloud-агент | [`onboarding/from-scratch-v2.md`](onboarding/from-scratch-v2.md) |
| Есть рабочий код, но нет документов | [`onboarding/existing-code.md`](onboarding/existing-code.md) |
| Проект уже на методологии, открыть следующую задачу | [`onboarding/continue-project.md`](onboarding/continue-project.md) |

Скопируйте содержимое нужного промпта и отправьте агенту как первое сообщение.

---

## Быстрая навигация

| Что нужно | Куда |
|-----------|------|
| Понять методологию целиком | [METHODOLOGY.md](METHODOLOGY.md) |
| Найти термин | [GLOSSARY.md](GLOSSARY.md) |
| Написать идею проекта | [templates/concept/idea-template.md](templates/concept/idea-template.md) |
| Написать техническое видение | [templates/concept/vision-template.md](templates/concept/vision-template.md) |
| Составить архитектуру | [templates/concept/architecture-template.md](templates/concept/architecture-template.md) |
| Спроектировать базу данных | [templates/concept/data-model-template.md](templates/concept/data-model-template.md) |
| Зафиксировать внешние интеграции | [templates/concept/integrations-template.md](templates/concept/integrations-template.md) |
| Зафиксировать API-контракты | [templates/concept/api-contracts-template.md](templates/concept/api-contracts-template.md) |
| Описать визуал веб-UI | [templates/concept/frontend-design-template.md](templates/concept/frontend-design-template.md) |
| Описать поведение веб-UI | [templates/concept/frontend-ux-logic-template.md](templates/concept/frontend-ux-logic-template.md) |
| Описать агентный харнес | [templates/concept/agent-harness-template.md](templates/concept/agent-harness-template.md) |
| Описать RAG (индекс и search-tool) | [templates/concept/rag-template.md](templates/concept/rag-template.md) |
| Описать invoke/stream и события UI | [templates/concept/generation-template.md](templates/concept/generation-template.md) |
| Описать защиту агента | [templates/concept/agent-security-template.md](templates/concept/agent-security-template.md) |
| Выбрать / предложить профиль | [profiles/README.md](profiles/README.md) |
| Собрать навигатор docs/ | [templates/docs/docs-readme-template.md](templates/docs/docs-readme-template.md) |
| Составить дорожную карту | [templates/roadmap/roadmap-template.md](templates/roadmap/roadmap-template.md) |
| Отдельный eval/benchmark-трек | [templates/roadmap/roadmap-eval-template.md](templates/roadmap/roadmap-eval-template.md) |
| Спланировать спринт | [templates/sprints/sprint-template.md](templates/sprints/sprint-template.md) |
| Чеклист дефектов refactor-спринта | [templates/sprints/audit-template.md](templates/sprints/audit-template.md) |
| Живое обсуждение до ADR/plan | [templates/sprints/design-discussion-template.md](templates/sprints/design-discussion-template.md) |
| Лаунчер автономного спринта | [templates/sprints/cloud-agent-prompt-template.md](templates/sprints/cloud-agent-prompt-template.md) |
| Создать план задачи | [templates/tasks/plan-template.md](templates/tasks/plan-template.md) |
| Зафиксировать итог задачи | [templates/tasks/summary-template.md](templates/tasks/summary-template.md) |
| Записать видео-демо | [templates/tasks/demo-template.md](templates/tasks/demo-template.md) |
| Skill скринкаста спринта | [skills/demo-screencast/SKILL.md](skills/demo-screencast/SKILL.md) |
| Написать спецификацию фичи | [templates/specs/spec-template.md](templates/specs/spec-template.md) |
| Зафиксировать архитектурное решение | [templates/decisions/adr-template.md](templates/decisions/adr-template.md) |
| Настроить CI/Git | [ci/git-conventions.md](ci/git-conventions.md) |

