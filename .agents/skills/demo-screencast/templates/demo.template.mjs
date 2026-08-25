// Скринкаст-шаблон. Скопировать в frontend/scripts/<имя>.mjs и отредактировать.
//
// Запуск: node scripts/<имя>.mjs
// Требует: запущенный стек и установленный edge-tts.

import { runScreencast } from "../../.agents/skills/demo-screencast/scripts/build.mjs";

await runScreencast({
  name: "my-demo",                         // итоговый файл: /opt/cursor/artifacts/my-demo.mp4
  outDir: "/opt/cursor/artifacts",
  voice: "ru-RU-SvetlanaNeural",
  baseUrl: "http://localhost:3001",
  pageWidth: 1440,
  pageHeight: 900,
  scenario: async ({
    goto,
    role,
    chapter,
    narrate,
    click,
    fill,
    moveTo,
    wait,
    page,
  }) => {
    // Пример: подача заявки
    await goto("/officer/new");

    await chapter("1. Подача заявки");

    await narrate(
      "В кабинете уполномоченного работника заполняем форму новой заявки.",
      async () => {
        await fill('input[name="inn"]', "7707083893");
        await fill('input[name="company_name"]', "ООО «Пример»");
      },
    );

    await narrate(
      "Форма валидирует ИНН, ОГРН, телефон и email до отправки.",
      async () => {
        await click('button[type="submit"]');
      },
    );
  },
});
