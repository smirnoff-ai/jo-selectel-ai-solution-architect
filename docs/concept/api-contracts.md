# API Contracts — Рефлекс

> **Базовый URL:** `http://localhost:8000`
> **Версия:** `/api/v1/...`
> Мок не дублируем — [api-contracts-mock.md](api-contracts-mock.md).
> Словарь SSE — [generation.md](generation.md).

---

## Общие конвенции

- JSON UTF-8. Ошибки — JSON, не HTML.
- `200` успех чтения, `201` создание обращения, `400` бизнес, `401` нет сессии, `404` нет обращения, `422` схема, `503` мок/LLM недоступны на intake только если не создали строку.
- Пагинации журнала в прототипе нет: `items` целиком.
- Пустой список — `200` и `items: []`.

Ошибка:

```json
{ "detail": "Человекочитаемое описание" }
```

### Аутентификация

Cookie сессии после `POST /api/v1/auth/login`. Один пользователь из конфига. Без JWT и SSO. Методы кроме `/health` и `/login` требуют cookie. e2e логинится тем же методом (или заголовок `X-Reflex-User` не заводим — одна сессия проще).

---

## Сводная таблица

| Метод | Путь | Успех | Сценарий |
|-------|------|:-----:|----------|
| `GET` | `/health` | 200 | Процесс жив |
| `POST` | `/api/v1/auth/login` | 200 | Вход |
| `POST` | `/api/v1/auth/logout` | 204 | Выход |
| `GET` | `/api/v1/auth/me` | 200 | Кто вошёл |
| `GET` | `/api/v1/appeals/desk` | 200 | Виджеты стола |
| `GET` | `/api/v1/appeals` | 200 | Журнал |
| `POST` | `/api/v1/appeals` | 201 | Создать и запустить разбор |
| `GET` | `/api/v1/appeals/{id}` | 200 | Карточка |
| `GET` | `/api/v1/appeals/{id}/messages` | 200 | Лента |
| `POST` | `/api/v1/appeals/{id}/replies` | 202 | Реплика, новый прогон |
| `GET` | `/api/v1/appeals/{id}/stream` | 200 | SSE прогона |

Каталога конфигов агента нет. Cancel нет.

---

## POST /api/v1/auth/login

```json
{ "login": "dispatcher", "password": "secret" }
```

Успех: `200` + Set-Cookie, тело `{ "login": "dispatcher" }`. Неверная пара — `401` на этой же форме, URL не меняем (это UI; API просто 401).

---

## GET /api/v1/appeals/desk

Четыре корзины. `done` нет.

```json
{
  "widgets": [
    {
      "status": "new",
      "count": 1,
      "recent": [
        {
          "id": 1,
          "received_at": "2026-08-13T16:40:00+03:00",
          "channel": "email",
          "sender": "Андрей, СеверФуд",
          "text_preview": "Снова 17-я…",
          "run_status": "running"
        }
      ]
    }
  ]
}
```

---

## GET /api/v1/appeals

| Параметр | Обяз. | Значения |
|----------|:-----:|----------|
| `status` | нет | all / new / clarify / dispatch / approve / done |
| `channel` | нет | all / email / telegram / call / lk |
| `received_from` | нет | дата |
| `received_to` | нет | дата |

Сортировка: `received_at` убыв. Элемент: id, received_at, channel, sender, text_preview, status, created_by.

---

## POST /api/v1/appeals

| Поле | Обяз. | Смысл |
|------|:-----:|--------|
| `channel` | да | email / telegram / call / lk |
| `sender` | нет | строка как в брифе |
| `received_at` | да | timestamptz |
| `text` | да | не пустой |
| `attachment_text` | нет | текст, не файл |

`201`: `{ "id": 1, "status": "new", "run_status": "running" }`. Прогон стартует здесь. Клиент сразу открывает карточку и SSE.

Двойной клик: идемпотентность на клиенте; сервер каждый POST считает новым обращением (склейки нет). UI не шлёт дважды.

---

## GET /api/v1/appeals/{id}

Мета + актуальный `card` (схема — [card.md](../requirements/severholod/card.md)). Нет id — 404.

```json
{
  "id": 1,
  "status": "clarify",
  "run_status": "idle",
  "created_by": "dispatcher",
  "auto_in_prod": false,
  "card": {}
}
```

---

## POST /api/v1/appeals/{id}/replies

```json
{ "text": "Это Дмитровское, ХУ-17" }
```

`202`: `{ "id": 1, "run_status": "running" }`. Входные поля обращения не меняются. Затем тот же SSE.

---

## GET /api/v1/appeals/{id}/stream

`Content-Type: text/event-stream`. Кадр: `event: <type>\ndata: <json>\n\n`. Типы — [generation.md](generation.md). Штатный конец — `run_finished` и закрытие. Неизвестный type клиент показывает карточкой-заглушкой.

Reconnect: перечитать `GET` карточки и messages; догонять живой прогон повторной подпиской. `Last-Event-ID` в прототипе не обещаем.

---

## GET /health

```json
{ "status": "ok" }
```

Не проверяет мок и LLM — иначе дев-цикл встанет. Готовность зависимостей — на старте процесса (fail fast) и в логах.
