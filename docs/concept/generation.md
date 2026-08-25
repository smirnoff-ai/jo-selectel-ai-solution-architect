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
| `thought` | reasoning провайдера: live — поле `delta`, в историю — поле `text` одним блоком в конце мысли | да | да, одним блоком |
| `tool_call` | имя и аргументы | да | да |
| `tool_result` | summary + JSON | да | да |
| `card_updated` | актуальный card после `update_card` | левая колонка | нет (card в строке appeal) |
| `message_delta` | токен markdown | да live | нет |
| `message_final` | готовый markdown | да | да |
| `run_finished` | исход, status, auto_in_prod | да | событие хронологии |
| `run_error` | упал | да | да |
| `context_usage` | токены провайдера в конце | нет | нет |

---

## 4. Токены

Backend шлёт `thought` с `delta` по мере токенов мысли, затем в историю кладёт один `thought` с полным `text`. После серии `message_delta` обязан прислать `message_final`. UI копит delta и заменяет на final. Reasoning не выдумываем. В конце прогона может прийти `context_usage` (токены провайдера) — в UI не рисуем.

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

## 7. Стоп прогона

Последний ход модели — markdown диспетчеру (`message_final`). Structured output и `ToolStrategy` нет. Решение живёт в `card.decision`: модель пишет его тулом `update_card`. Код исход, reason и grounds не переписывает и шаблонный отчёт не собирает. GET ленты отдаёт только сохранённые сообщения.

После прогона стол берёт `outcome` с карточки (если пусто — колонка `dispatch`). Dry-run ITSM — только если `card.decision.outcome` равен `create` или `update`; иначе черновик и примерка очищаются. Опора для черновика проверяется при сборке `ticket_draft`, не сменой исхода.

---

## 8. UI

Thought и tool — compact, auto-collapse после шага. Markdown диспетчеру — раскрыт. Стрим только на карточке. Ушёл на стол — SSE можно оборвать, прогон на сервере доигрывает; стол обновится по reload или повторному заходу.

---

## 9. Cancel и контекст

Stop нет. Обрыв SSE без `run_finished` — перечитать card; если `running`, подписать снова. `context_usage` — в конце прогона на backend, в UI не рисуем (прототип).
