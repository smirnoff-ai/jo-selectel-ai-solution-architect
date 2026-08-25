# Архитектура системы

> Видение — [vision.md](vision.md). Домен — [data-model.md](data-model.md).

---

## Контекст системы

Диспетчер работает в браузере. Бизнес-логика разбора — в backend Рефлекса. Справочники — в отдельном моке. LLM и Langfuse — снаружи контура объекта.

```mermaid
flowchart TB
    subgraph users["Пользователи"]
        Disp["Диспетчер"]
        E2E["e2e"]
    end

    subgraph reflexClient["Клиент Рефлекса"]
        UI["frontend"]
    end

    subgraph reflexCore["Ядро Рефлекса"]
        API["backend FastAPI"]
        Agent["агент"]
    end

    subgraph data["Данные и сервисы"]
        PG[("Postgres")]
        Mock["mock-severholod"]
        LLM["LLM"]
        LF["Langfuse"]
    end

    Disp --> UI
    UI -->|"REST + SSE"| API
    E2E -->|"REST"| API
    API --> Agent
    API --> PG
    Agent --> PG
    Agent -->|"HTTP"| Mock
    Agent --> LLM
    Agent --> LF
```

---

## Контейнеры и ответственность

| Компонент | Назначение | Технологии | Документация |
|-----------|-----------|-------------|--------------|
| **mock-severholod** | Справочники и dry-run ITSM | FastAPI, JSON-сид | [api-contracts-mock.md](api-contracts-mock.md), [ADR-0001](../adrs/0001-two-contours.md) |
| **backend** | Сессия, обращения, агент, SSE | FastAPI, LangChain, SQLAlchemy | [api-contracts.md](api-contracts.md) |
| **frontend** | Стол, журнал, карточка | Next.js, shadcn | [frontend-ux-logic.md](frontend-ux-logic.md) |
| **postgres** | Обращения Рефлекса + чекпоинтер | PostgreSQL 15+ | [data-model.md](data-model.md) |
| **langfuse** | Трассы | официальный образ | [integrations.md](integrations.md) |

Слои backend: **API → facade/service → repository → DB**. В Postgres из роутера не ходим. Мок: **router → in-memory/JSON store**, репозиторий над файлом сида, без ORM.

Транспорт стрима — **SSE**. Зафиксировано здесь, отдельный ADR не нужен.

---

## Поток: мок сам по себе

```mermaid
sequenceDiagram
    participant T as httpx или curl
    participant M as mock-severholod
    participant S as JSON сид

    T->>M: GET /eam/v1/assets?q=ХУ-17
    M->>S: фильтр
    S-->>M: A-1001 и A-1002
    M-->>T: 200 items оба
    T->>M: POST /itsm/v1/tickets
    M->>M: ФЛК
    M-->>T: accepted true persisted false
```

---

## Поток: новое обращение

```mermaid
sequenceDiagram
    participant U as Диспетчер
    participant UI as frontend
    participant B as backend
    participant DB as Postgres
    participant A as агент
    participant M as мок
    participant L as LLM

    U->>UI: Создать
    UI->>B: POST /api/v1/appeals
    B->>DB: строка appeals + шаблон card
    B-->>UI: 201 + appeal_id
    UI->>B: GET SSE /api/v1/appeals/{id}/stream
    B->>A: stream thread_id=appeal_id
    A->>L: ход
    A->>M: search_sites / assets / contract / tickets
    M-->>A: items
    A->>DB: card через тулы и мерж
    A-->>B: события
    B-->>UI: SSE кадры
    B->>B: если create/update и опора ясна — dry-run ITSM
    B->>DB: status стола, хронология
    B-->>UI: run_finished
```

Ленивого «чата без обращения» нет: обращение рождается на «Создать». Реплика диспетчера — новый `stream` на том же id.

---

## Backend — внутренняя структура

```mermaid
flowchart LR
    R["routers"] --> F["facades"]
    F --> Rep["repositories"]
    F --> Agent["agent factory"]
    Agent --> Tools["tools HTTP мок"]
    Rep --> DB[("Postgres")]
```

Роутер принимает HTTP. Facade ведёт обращение и прогон. Repository — единственный, кто пишет `appeals` и сообщения. Tools — тонкие обёртки над HTTP мока.

---

## Мок — внутренняя структура

```mermaid
flowchart LR
    R2["routers crm eam contracts itsm"] --> Store["seed JSON"]
    R2 --> Flk["проверки заявки"]
```

Один процесс, четыре префикса URL. Отдельных микросервисов нет.

---

## Деплой — локально

`make up` / корневой `docker-compose`: `mock-severholod`, `backend`, `frontend`, `postgres`, `langfuse`. Рефлекс не стартует без `OPENAI_*` и `LANGFUSE_*`. Мок секретов не требует.

## Деплой — production

Нет. Пилот на машине кандидата / интервьюера.

---

## Связанные документы

- [vision.md](vision.md)
- [data-model.md](data-model.md)
- [api-contracts-mock.md](api-contracts-mock.md)
- [api-contracts.md](api-contracts.md)
- [integrations.md](integrations.md)
- [../adrs/](../adrs/)
