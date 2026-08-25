---
name: demo-screencast
description: Записывает AI-managed скринкасты продукта с голосовой озвучкой, стильными субтитрами, видимым курсором и «главами». Применяется когда пользователь просит записать демо-видео, презентацию фичи, скринкаст спринта, клиентское демо. Запускается на Node + Playwright + edge-tts + ffmpeg. Готовый mp4 кладётся в `/opt/cursor/artifacts/`.
user-invocable: false
allowed-tools: Bash(node *), Bash(ffmpeg *), Bash(ffprobe *), Bash(edge-tts *), Bash(pip3 install --user edge-tts *)
---

# demo-screencast

Производит готовый демо-скринкаст одной командой `node scripts/<имя>.mjs`. Ответственен за: запись видео через Playwright, синтез русской/английской речи через `edge-tts`, стильные DOM-оверлеи (субтитры, заголовки глав), видимый курсор с ripple-эффектом.

## Когда применять

- «Запиши демо нового функционала»
- «Сделай скринкаст для заказчика»
- «Нужно видео-презентацию спринта»
- любые запросы, где нужно видео с озвучкой и понятными пояснениями

## Файлы

```
.agents/skills/demo-screencast/
├── SKILL.md                       # этот файл
├── references/
│   ├── narrate-pattern.md         # паттерн синхронизации голос↔экран (MUST-READ)
│   ├── cursor-overlay.md          # DOM-курсор, клики, attention-ring
│   ├── subtitle-style.md          # внешний вид всплывашек и субтитров
│   └── tts-voices.md              # рекомендуемые edge-tts голоса
├── assets/overlay.css             # стили (инжектятся в page)
├── scripts/
│   ├── build.mjs                  # движок — импортируется из сценария
│   ├── tts.mjs                    # обёртка edge-tts + ffprobe
│   └── overlay.js                 # JS для page.addInitScript (курсор, субтитр, глава)
└── templates/
    └── demo.template.mjs          # бойлерплейт нового скринкаста
```

## Принципы

1. **Один скринкаст — один файл в `frontend/scripts/<имя>.mjs`**. Этот файл тонкий: импортирует `runScreencast` и передаёт функцию-сценарий.

2. **Pre-synth TTS перед записью.** Все реплики синтезируются в mp3 заранее, чтобы `durations[i]` были известны и можно было синхронизировать паузы. См. `references/narrate-pattern.md`.

3. **Синхронизация через `narrate(text, action)`.** Субтитр + озвучка + действие стартуют одновременно. Движок ждёт `max(ttsDur + buffer, actionDur)`. Никогда не делайте `say(...)` → `await sleep(...)` → `page.click(...)` последовательно — это ломает синхронизацию.

4. **Курсор должен быть виден.** DOM-курсор инжектируется автоматически. Используйте `click(selector)` / `fill(selector, text)` / `moveTo(selector)` из api сценария — они двигают курсор плавно, показывают ripple на клике и attention-ring вокруг цели. `page.click()` напрямую не использовать — курсор не покажется.

5. **Субтитры и заголовки — DOM, не ffmpeg.** ASS burn-in ограничен по стилям. Мы рендерим overlay'и прямо в странице, поэтому доступны Inter, gradients, rounded corners, emoji. Ffmpeg только muxит видео + аудио.

6. **Всплывашки-главы и субтитры — разные элементы.** 
   - Chapter: большой заголовок сверху-центру, ~1.5 сек, fade-in/out.
   - Subtitle: низ экрана, держится пока озвучка идёт, полупрозрачный градиент.

## Быстрый старт

### 1. Скопировать бойлерплейт

```bash
cp .agents/skills/demo-screencast/templates/demo.template.mjs frontend/scripts/my-demo.mjs
```

### 2. Заполнить сценарий

```js
import { runScreencast } from "../../.agents/skills/demo-screencast/scripts/build.mjs";

await runScreencast({
  name: "my-demo",
  outDir: "/opt/cursor/artifacts",
  voice: "ru-RU-SvetlanaNeural",
  baseUrl: "http://localhost:3001",
  scenario: async (api) => {
    const { goto, chapter, narrate, click, fill, role } = api;

    await goto("/officer/new");
    await chapter("1. Подача заявки");
    await narrate(
      "Форма проверяется до отправки.",
      async () => {
        await fill('input[name="inn"]', "123");
        await click('button[type="submit"]');
      },
    );
  },
});
```

### 3. Запустить

Требуется запущенный стек и установленный edge-tts (`pip3 install --user edge-tts`).

```bash
cd frontend && node scripts/my-demo.mjs
```

Готовое видео: `/opt/cursor/artifacts/my-demo.mp4` + `.srt` + `.segments.json`.

## Минимальные требования среды

- `node` ≥ 20
- `playwright` с установленным chromium (`npx playwright install chromium`)
- `edge-tts` в `PATH` (pip3 install --user edge-tts → `$HOME/.local/bin/edge-tts`)
- `ffmpeg`, `ffprobe`

## Обязательное чтение перед сценарием

- [references/narrate-pattern.md](references/narrate-pattern.md) — как правильно писать реплики, чтобы голос читался пока на экране происходят действия.
- [references/cursor-overlay.md](references/cursor-overlay.md) — когда использовать `click`/`fill`/`moveTo` вместо `page.*`.
- [references/subtitle-style.md](references/subtitle-style.md) — стили chapters и subtitles (не кастомизировать без причины).
- [references/tts-voices.md](references/tts-voices.md) — какой голос выбрать.
