# API Contracts — мок СеверХолода

> **Базовый URL локально:** `http://localhost:8080` (в compose — `http://mock-severholod:8080`)
> **Версия:** префиксы `/crm/v1`, `/eam/v1`, `/contracts/v1`, `/itsm/v1`
> **Канон заказчика:** [docs/requirements/severholod/api.md](../requirements/severholod/api.md) — смысл не перерешаем.
> **Это наш контракт на реализацию** первого контура.

Intake Рефлекса сюда не входит.

---

## Общие конвенции

- HTTP, JSON, UTF-8. Без аутентификации (прототип, мок во внутренней сети compose).
- Пагинации нет: сид маленький, отдаём весь `items`.
- Пустой поиск — `200` и `"items": []`, не `404`.
- Несколько совпадений — все элементы. Мок не выбирает «наиболее вероятное».
- Ресурс по точному id, которого нет — `404`.
- Нет ни одного обязательного фильтра на поиске — `422`.
- Провал ФЛК write — `400` со списком `checks`.
- Неверная схема JSON — `422`.

Ошибка:

```json
{
  "detail": "Человекочитаемое описание",
  "code": "not_found",
  "checks": []
}
```

`checks` заполняем только на ФЛК заявки. Коды: `not_found`, `validation`, `flk_failed`.

---

## Сводная таблица

| Метод | Путь | Успех | Сценарий |
|-------|------|:-----:|----------|
| `GET` | `/health` | 200 | Жив ли процесс |
| `GET` | `/crm/v1/sites` | 200 | Поиск площадок |
| `GET` | `/crm/v1/sites/{site_id}` | 200 | Одна площадка |
| `GET` | `/eam/v1/assets` | 200 | Поиск активов |
| `GET` | `/eam/v1/assets/{asset_id}` | 200 | Один актив |
| `GET` | `/contracts/v1/contracts` | 200 | Договоры площадки |
| `GET` | `/contracts/v1/contracts/{contract_id}` | 200 | Один договор |
| `GET` | `/itsm/v1/tickets` | 200 | Поиск заявок |
| `GET` | `/itsm/v1/tickets/{ticket_id}` | 200 | Одна заявка |
| `POST` | `/itsm/v1/tickets` | 200 | Create dry-run (не 201: записи нет) |
| `PATCH` | `/itsm/v1/tickets/{ticket_id}` | 200 | Update dry-run |

`POST` create при включённых мутациях тоже 200 с `persisted: true` — прототип не плодит два кода.

---

## GET /health

```json
{ "status": "ok" }
```

---

## GET /crm/v1/sites

Нужен хотя бы один параметр. Несколько конкретных — И. `q` дополнительно сужает.

| Параметр | Обяз. | Смысл |
|----------|:-----:|--------|
| `q` | нет | Подстрока по имени клиента, адресу, id |
| `customer_id` | нет | Точное |
| `site_id` | нет | Точное |
| `customer_name` | нет | Подстрока |
| `address` | нет | Подстрока |
| `timezone` | нет | Точное |

`q=Андрей` → пустой список. Контактов нет.

Ответ: `{ "items": [ { site_id, customer_id, customer_name, address, timezone } ] }`.

`GET /crm/v1/sites/{site_id}` — тот же объект без `items`. Нет — 404.

---

## GET /eam/v1/assets

Хотя бы один параметр.

| Параметр | Обяз. | Смысл |
|----------|:-----:|--------|
| `q` | нет | Код, id, тип |
| `asset_id` | нет | Точное |
| `site_id` | нет | Точное |
| `local_code` | нет | Код («ХУ-17») |
| `asset_type` | нет | Подстрока |
| `criticality` | нет | `high` / `medium` |

`local_code=ХУ-17` без площадки → **оба** актива. С `site_id=S-MSK-01` → только A-1001.

Поля элемента: `asset_id`, `site_id`, `local_code`, `asset_type`, `criticality`.

---

## GET /contracts/v1/contracts

`site_id` обязателен. На площадку в сиде один договор или пусто. Поля: `contract_id`, `site_id`, `plan`, `response_sla`, `service_window`, `coverage`.

Коды SLA: `60_minutes`, `4_business_hours`, `next_business_day`.
Окна: `24x7`, `weekdays_09_18_local`.
Покрытие: `diagnostics`, `repair`, `spare_parts_up_to_50000_rub`.

Дедлайн мок не считает.

---

## GET /itsm/v1/tickets

Хотя бы один из `customer_id`, `site_id`, `asset_id`, `contract_id`.

`status=open` — три открытых кода: `new`, `in_progress`, `waiting_for_customer`. Закрытые: `closed`, `cancelled`.

Поля тикета: `ticket_id`, `customer_id`, `site_id`, `asset_id`, `contract_id`, `status`, `priority`, `summary`, `created_at`, `updated_at`.

---

## POST /itsm/v1/tickets и PATCH /itsm/v1/tickets/{id}

Флага `dry_run` в теле нет. Режим — `ALLOW_TICKET_MUTATIONS` (default false).

Create обязательные: `customer_id`, `site_id`, `contract_id`, `summary`, `priority`. `asset_id` опционален, если есть — принадлежит площадке.

PATCH можно: `summary`, `priority`, `status` (только открытый). Идентичность не меняем.

Ответ:

```json
{
  "persisted": false,
  "accepted": true,
  "would_ticket_id": "T-885",
  "would_status": "new",
  "payload": {},
  "checks": [{ "id": "customer_exists", "passed": true }]
}
```

Провал ФЛК — 400, `accepted: false`, все `checks` с `passed`.

Проверки create: customer/site/asset/contract существуют и согласованы, summary не пустой, priority из `low|medium|high|critical`.
Update дополнительно: `ticket_exists`, `ticket_is_open`, `identity_not_changed`.

Назначения группы нет.

---

## Чего нет

Inbox, исходящие, склад, биллинг, вид работ на заявке, расчёт SLA, выбор лучшей площадки.

Полные примеры JSON — в [api.md](../requirements/severholod/api.md).
