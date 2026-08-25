# Вдохновение: стрим чата из AI DocPoint

Собрано 2026-08-25. Код не трогаем. Источник: соседний репозиторий `monolit-docpoint` + актуальные доки LangChain / OpenRouter.

DocPoint — ИИ-ассистент по должностным инструкциям. Там чат `@docpoint/chat-panel` реально рисует мысль и ответ **по мере токенов**, а не «висит → валится трейс». Это тот эффект, которого не хватает в Рефлексе.

---

## 1. Почему у них красиво, а у нас нет

| Слой | DocPoint | Рефлекс сейчас |
|------|----------|----------------|
| Вызов модели | `stream: True`, reasoning в `extra_body` | `streaming=False`, `reasoning.max_tokens: 256` |
| Как читают LLM | свой адаптер → reasoning-блоки LangChain | `ChatOpenAI.ainvoke` → мысль целиком в `additional_kwargs` |
| События в UI | `reasoning_chunk` / `assistant_chunk` сразу | контракт есть (`thought`, `message_delta`), **delta не шлётся** |
| UI | `pendingReasoning` + `pendingAssistant` копятся | лента из готовых сообщений; пока пусто — «агент разбирает…» |
| Тулы | карточка `tool_call` сразу, потом result | то же по контракту, но только после полного `ainvoke` |

Корень «висит, потом dump»: цикл в `loop.py` ждёт **весь** `ainvoke`, потом один `thought` и тулы. UI в `appeal-workspace.tsx` кладёт в ленту только `thought` / `tool_*` / `message_final`. `message_delta` в словаре есть, в маппер не попадает.

---

## 2. Как устроено в DocPoint (не копировать каркас целиком)

Пайплайн:

```
OpenRouterReasoningChat (stream=True)
  → create_deep_agent.astream_events(..., version="v3")
  → V3StreamMapper → TraceEvent
  → SSE event:trace / event:end
  → chat-panel: pending* + history
```

Ключ не Deep Agents. Ключ — **три буфера**:

1. **Чанки мысли** (`reasoning_chunk.payload.delta`) → строка `pendingReasoning` → блок «думаю» с курсором.
2. **Чанки ответа** (`assistant_chunk.payload.delta`) → `pendingAssistant` → markdown live.
3. **Дискретные шаги** (`tool_call`, `tool_result`, …) → сразу в историю карточками.

Финал (`reasoning` / `assistant`) сбрасывает pending и кладёт готовый блок. Чанки **в БД не пишут**. После `end` перечитывают history.

Файлы-ориентиры (абсолютные пути на этой машине):

| Роль | Путь |
|------|------|
| Адаптер OpenRouter | `/Users/gazebo/work/smirnoff_ai/projects/monolit-docpoint/backend/agents/openrouter_reasoning_chat.py` |
| Сырой v3 → продукт | `…/backend/agents/stream_mapper.py` |
| SSE | `…/backend/api/public/v1/messages_router.py` |
| Клиент SSE | `…/frontend/packages/chat-panel/src/api.ts` |
| Состояние стрима | `…/frontend/packages/chat-panel/src/chat-panel.tsx` |
| Live-рендер | `…/frontend/packages/chat-panel/src/conversation.tsx` |
| Блок мысли | `…/frontend/packages/chat-panel/src/reasoning-block.tsx` |

UI-деталь, которую стоит взять: две пульсирующие точки + `uppercase reasoning` + моно курсив + мигающий `|`. Не неон, плотность.

Дыра DocPoint (не повторять): `subagent_message_chunk` эмитится, в UI не копится, после reload пропадает. У нас сабагентов нет — но правило то же: **если чанк не в pending и не в history, пользователь его не видел**.

---

## 3. Что проверить в вебе — актуально

Проверено 2026-08-25 по [LangChain event streaming](https://docs.langchain.com/oss/python/langchain/event-streaming), [streaming / reasoning](https://docs.langchain.com/oss/python/langchain/streaming#streaming-thinking-/-reasoning-tokens), [models § reasoning](https://docs.langchain.com/oss/python/langchain/models#reasoning), [OpenRouter reasoning tokens](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens), карточка [qwen/qwen3.6-35b-a3b](https://openrouter.ai/qwen/qwen3.6-35b-a3b).

### LangChain — да, так и надо стримить

- Канон агента: `stream_events(..., version="v3")` (с langchain 1.3, май 2026). Проекции `message.reasoning` и `message.text` — токен за токеном.
- Без графа достаточно `model.stream` / `astream` и `chunk.content_blocks` с `type == "reasoning"`.
- Стандартный параметр `reasoning_effort` есть у `ChatOpenAI` (`langchain-openai>=1.4.1`). Это **не** замена OpenRouter `extra_body.reasoning`.
- **Важно:** `ChatOpenAI` + `base_url=OpenRouter` целится в спеку OpenAI. Поля роутера (`delta.reasoning`, `reasoning_content`) **могут потеряться**. Доки прямо говорят: для OpenRouter предпочитать `langchain-openrouter` / `ChatOpenRouter`, не голый `ChatOpenAI`.
- Поэтому кастомный адаптер DocPoint всё ещё оправдан *как идея*. Перед копированием файла — сначала попробовать официальный `ChatOpenRouter`: если reasoning-блоки уже нормализуются, свой класс не нужен.

Рефлексу **не обязательно** тащить Deep Agents и `create_agent`. Наш `bind_tools` + цикл шагов ок, если шаг станет `astream`, а не `ainvoke`.

### OpenRouter — reasoning живой, параметры те же

В теле запроса (через OpenAI SDK — в `extra_body`):

```json
"reasoning": {
  "effort": "high"
}
```

или `max_tokens` (бюджет мысли). **Не оба сразу**, если значения конфликтуют — шлюз даёт 400.

| Поле | Смысл |
|------|--------|
| `effort` | `max` / `xhigh` / `high` / `medium` / `low` / `minimal` / `none` |
| `max_tokens` | бюджет мысли (Gemini / Anthropic / часть Qwen → `thinking_budget`) |
| `exclude` | `true` — думает, но в ответ не отдаёт (нам не надо) |
| `enabled` | включить с дефолтом medium |

В стриме мысль приходит в `delta.reasoning` / `reasoning_content` / `reasoning_details`, не только в финальном `usage.reasoningTokens`.

Для tool-loop OpenRouter просит **вернуть** `reasoning_details` в следующее assistant-сообщение, иначе мысль на следующем шаге обрывается. Сейчас `ainvoke` + LangChain messages это могут не прокинуть — отдельная проверка при включении стрима.

`qwen/qwen3.6-35b-a3b`: thinking mode + traces между ходами заявлены на карточке модели. Какой рычаг живой (`effort` vs `max_tokens`) — смотреть `GET /api/v1/models` → `reasoning.supported_efforts` / `supports_max_tokens`. Сейчас у нас как раз урезанный `max_tokens: 256` — это и есть потолок мысли в 256 токенов.

### Транспорт

SSE по-прежнему норма. DocPoint: POST + `fetch` + `ReadableStream` (у `EventSource` только GET). У нас GET `/appeals/{id}/stream` + `EventSource` — **оставить**, менять транспорт не за чем. Обязательно: не буферить SSE в Next rewrite / nginx (`X-Accel-Buffering: no`, ping 15 с — у нас в `generation.md` уже так).

---

## 4. Что перенести в Рефлекс (когда будем делать)

Не тащить Deep Agents, `TraceEvent` с `source=subagent`, friendly-mode.

**Backend**

1. Стримить вызов модели (`streaming=True` / `astream`).
2. Reasoning явно: `effort` (скорее `high` / `medium`), общий `max_tokens` ответа большой. Не экономить мысль `256`.
3. Достать `delta.reasoning*` из OpenRouter: `ChatOpenRouter` **или** тонкий адаптер как в DocPoint (маппинг в `content: [{type: "reasoning", …}]`).
4. Эмитить в уже свой словарь:
   - чанки мысли → серия `thought` с `delta` **или** новое `thought_delta` (тогда поправить `generation.md`: сейчас «thought одним блоком»);
   - чанки ответа → `message_delta`;
   - в конце шага — `thought` целиком (если нужен в истории) и `message_final`.
5. Чанки в `messages` не писать. Тулы — как сейчас, после полного args (частичный JSON аргументов не стримить — так и в `generation.md`).

**Frontend**

1. Убрать заглушку «агент разбирает…».
2. Как DocPoint: `pendingThought` / `pendingAnswer` + курсор; тулы в историю сразу.
3. `messageFromEvent` должен понимать delta, не только final.
4. Блок мысли: тусклый моно, свернуть после шага. Ответ — тот же markdown renderer, копит текст.
5. Левая колонка по-прежнему только `card_updated`.

Имена тулов (техн. + бизнес) — в [appeal-window.md](appeal-window.md), не в DocPoint.

---

## 5. Что не брать

- Смену каркаса на Deep Agents ради стрима.
- POST-stream вместо нашего GET EventSource — без нужды.
- Копировать `OpenRouterReasoningChat` байт в байт: сначала официальный пакет 2026 года.
- Их `execution_mode` invoke/stream/friendly.
- Их дыру с чанками сабагента.

---

## 6. Ссылки

- Контракт Рефлекса: [generation.md](../../concept/generation.md)
- Окно обращения: [appeal-window.md](appeal-window.md)
- DocPoint контракт: `monolit-docpoint/docs/concept/api-contracts.md` §4.4 / §8
- ADR SSE: `monolit-docpoint/docs/decisions/0005-sse-for-stream.md`
- LangChain: [event streaming v3](https://docs.langchain.com/oss/python/langchain/event-streaming), [reasoning tokens](https://docs.langchain.com/oss/python/langchain/streaming#streaming-thinking-/-reasoning-tokens)
- OpenRouter: [reasoning tokens](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)
