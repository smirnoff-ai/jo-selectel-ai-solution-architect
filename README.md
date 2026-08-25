# Рефлекс — прототип ИИ-диспетчера (Селектл)

Рабочий демо: свободный текст → карточка разбора → dry-run заявки в ITSM. Объект пилота — вымышленный «СеверХолод».

Логин: `dispatcher` / `secret`. UI: [http://localhost:3000](http://localhost:3000) (не `127.0.0.1` — Next режет origin).

## Запуск

Нужны Docker (Postgres, Langfuse), `uv`, `pnpm`, ключ OpenRouter в Keychain как `OPENROUTER_API_KEY`.

```bash
make env          # .env из Keychain, в git не кладём
docker compose up -d postgres
# мок :8080 и backend :8000 — локально удобнее не из compose-сети
cd mock-severholod && uv run uvicorn mock_severholod.app:app --host 0.0.0.0 --port 8080
make dev-backend  # пишет .env с хостами 127.0.0.1
make dev-frontend
```

Проверка мока: `GET http://127.0.0.1:8080/eam/v1/assets?q=ХУ-17` — два актива.  
Приёмка агента: `make accept` (живой OpenRouter, ~4 минуты). Ожидания — [docs/requirements/severholod/scenarios.md](docs/requirements/severholod/scenarios.md).

## Схема решения

Два контура. **Мок** притворяется CRM / EAM / договором / ITSM: честный 0/1/N, write только dry-run. **Рефлекс** хранит обращения в Postgres, крутит одного агента, рисует стол и карточку.

```
диспетчер → Next.js → FastAPI → агент → HTTP мок
                         ↓
                    Postgres (card + лента)
                         ↓
                    OpenRouter + Langfuse (local)
```

Привязка 0/1/N, SLA и лестница исходов — **код**, не модель. Модель вызывает пять тулов и пишет упоминания. После прогона предохранитель может сменить create на clarify. ITSM — примерка, `persisted: false`.

## Где LLM, где правила

| LLM | Правила |
|-----|---------|
| Извлечь упоминания, выбрать тулы, черновик реплики | Binding 0/1/N, SLA Gold = получено+60 мин, исход по опоре, dry-run |

Модель не выбирает «самую вероятную Москву». Две ХУ-17 → `ambiguous` → `clarify`. Нет актива в реестре → `not_found` → заявка на площадку не заводится.

Промпт: [docs/requirements/severholod/prompts/system.md](docs/requirements/severholod/prompts/system.md). Рантайм — цикл `bind_tools` (LangChain `create_agent` на этом шлюзе зависал).

## Проверки

| id | Смысл | Исход | Примерка |
|----|--------|--------|:--------:|
| S1 | ХУ-18 на Дмитровском | create | да |
| S2 | две «17-х» | clarify | нет |
| S3 | повтор, T-884 | update | да, T-884 |
| S4 | КМ-9 нет в реестре | clarify | нет |

Отчёт последнего прогона: [docs/sprints/sprint-06-accept-s1-s4/report.json](docs/sprints/sprint-06-accept-s1-s4/report.json). Демо: [docs/sprints/sprint-06-accept-s1-s4/demo.mp4](docs/sprints/sprint-06-accept-s1-s4/demo.mp4).

## Assumptions

- Один диспетчер, cookie, без SSO.
- Каналы — поле входа, не живой inbox.
- Время мира демо — 13 авг 2026, 16:40 МСК.
- Модель по умолчанию `qwen/qwen3.6-35b-a3b` через OpenRouter.
- Langfuse в compose; ключи пилота нужно завести в UI контейнера.

## Открытые вопросы заказчику

1. Кто подтверждает HITL (согласование / отказ) вне диалога?
2. Пишем ли в живой ITSM после пилота, и какой идемпотентный ключ?
3. Праздничный календарь SLA — чей источник?
4. Склейка ниток писем — продукт или интеграция канала?

## Путь до production

Очередь входящих, SSO, живой write с журналом отмены, назначение группы, метрики «не угадали объект» / «уложились в SLA», датасет S1–S4 в Langfuse как регрессия.

## Timebox (как распределили)

Концепт и мок ~1 ч; каркас и обращения ~1 ч; агент и SSE ~1 ч; UI и приёмка ~1 ч. Код писал агент в Cursor; решения и приёмка — по [docs/roadmap.md](docs/roadmap.md).

Журнал AI: [docs/ai-journal.md](docs/ai-journal.md). Навигатор: [docs/README.md](docs/README.md).
