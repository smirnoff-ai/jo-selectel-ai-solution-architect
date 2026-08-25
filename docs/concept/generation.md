# Generation и стриминг — Рефлекс

> Профиль: частично `agent-platform-v1`. Пути — [api-contracts.md](api-contracts.md).

---

## 1. Режимы

| Режим | Для кого | Клиент видит | В историю |
|-------|----------|--------------|-----------|
| `stream` | UI карточки | события по мере работы | финалы и тулы, не каждый token |
| `invoke` | e2e / API без UI | один JSON в конце | то же, что после прогона |

Режим на обращении не храним: UI всегда stream, e2e может invoke. Селектора в UI нет. Cancel нет.

---

## 2. Транспорт

| Вопрос | Решение |
|--------|---------|
| Протокол | SSE |
| Заголовки | `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `X-Accel-Buffering: no` |
| Keep-alive | комментарий SSE каждые 15 с, пока прогон жив |
| Reconnect | без Last-Event-ID: GET card + messages, при `running` снова SSE |
| Конец | событие `run_finished`, затем закрыть поток |

---

## 3. События

Сырой LangChain в UI не отдаём. Имя `type` — открытая строка. Неизвестный type — карточка-заглушка.

| `type` | Смысл | В UI | В историю |
|--------|-------|:----:|:---------:|
| `run_started` | прогон пошёл | да | нет |
| `thought` | reasoning провайдера | да | да, одним блоком в конце мысли |
| `tool_call` | имя и аргументы | да | да |
| `tool_result` | summary + JSON | да | да |
| `card_updated` | актуальный card | левая колонка | нет (card в строке appeal) |
| `message_delta` | токен markdown | да live | нет |
| `message_final` | готовый markdown | да | да |
| `run_finished` | исход, status, auto_in_prod | да | событие хронологии |
| `run_error` | упал | да | да |

---

## 4. Токены

Backend обязан прислать `message_final` после серии `message_delta`. UI копит delta и заменяет на final. Reasoning — блок, если провайдер прислал; не выдумываем.

---

## 5. Tools

Пара `tool_call` + `tool_result` с одним id. Ошибка — `status: error` внутри `tool_result`. Частичный JSON аргументов не стримим.

---

## 6. История

| Класс | Stream → UI | Stream → messages | Invoke → messages |
|-------|:-----------:|:-----------------:|:-----------------:|
| delta | да | нет | нет |
| thought / tools / final | да | да | да |
| card_updated | да | нет | нет |

---

## 7. Structured output

Финал — короткий объект: outcome, reason, questions, warnings, reply_draft. Код мержит в `card.decision`, затем предохранитель и опционально dry-run. Исход на стол пишет **предохранитель по карточке**, не доверие к JSON модели. Нет валидного финала — reason «Модель не вернула финал», outcome всё равно из лестницы (create/update/clarify/…). Карточку успехом не врём: статус стола = исход после guard.

---

## 8. UI

Thought и tool — compact, auto-collapse после шага. Markdown диспетчеру — раскрыт. Стрим только на карточке. Ушёл на стол — SSE можно оборвать, прогон на сервере доигрывает; стол обновится по reload или повторному заходу.

---

## 9. Cancel и контекст

Stop нет. Обрыв SSE без `run_finished` — перечитать card; если `running`, подписать снова. `context_usage` — в конце прогона на backend, в UI не рисуем (прототип).
