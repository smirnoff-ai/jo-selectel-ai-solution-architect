import { runScreencast } from "../../.agents/skills/demo-screencast/scripts/build.mjs";

await runScreencast({
  name: "sprint-06-demo",
  outDir: "/tmp/reflex-sprint-06-demo",
  voice: "ru-RU-DmitryNeural",
  baseUrl: "http://localhost:3000",
  pageWidth: 1440,
  pageHeight: 900,
  scenario: async ({ goto, chapter, narrate, click, fill, wait, page }) => {
    await goto("/login");
    await chapter("Рефлекс");
    await narrate("Входим одним логином диспетчера. Клиентов СеверФуда на этом экране нет.", async () => {
      await fill("#login", "dispatcher");
      await fill("#password", "secret");
      await click('button[type="submit"]');
      await page.waitForURL("**/desk", { timeout: 15000 });
    });

    await chapter("Стол");
    await narrate(
      "Четыре корзины — очередь, не почтовый ящик. Разобранные create и update уходят в журнал.",
      async () => {
        await wait(2200);
      },
    );

    await chapter("Журнал");
    await narrate("В журнале четыре кейса пакета: канал, отправитель, статус.", async () => {
      await click('a:has-text("Журнал")');
      await page.waitForURL("**/journal");
      await page.waitForSelector("table tbody tr", { timeout: 15000 });
    });

    await chapter("S1 — create");
    await narrate(
      "ХУ-18 на Дмитровском однозначна. Код пишет create и примерку заявки, не модель.",
      async () => {
        await goto("/appeals/1");
        await page.waitForFunction(
          () => document.body.innerText.includes("Создать заявку") || document.body.innerText.includes("A-1003"),
          null,
          { timeout: 20000 },
        );
        await wait(1500);
      },
    );

    await chapter("S2 — уточнение");
    await narrate(
      "Две семнадцатых на разных складах. Город не угадываем — исход clarify, без заявки.",
      async () => {
        await goto("/appeals/2");
        await page.waitForFunction(
          () => document.body.innerText.includes("Нужно уточнение"),
          null,
          { timeout: 20000 },
        );
        await wait(1500);
      },
    );

    await chapter("S3 — update");
    await narrate(
      "Повтор на Дмитровском клеим к открытому T-884. Примерка — патч, не новая заявка.",
      async () => {
        await goto("/appeals/3");
        await page.waitForFunction(
          () => document.body.innerText.includes("T-884") || document.body.innerText.includes("Обновить заявку"),
          null,
          { timeout: 20000 },
        );
        await wait(1500);
      },
    );

    await chapter("S4 — нет в реестре");
    await narrate(
      "КМ-9 назвали и не нашли. Площадка ясна — этого мало. T-884 чужой инцидент, не клеим.",
      async () => {
        await goto("/appeals/4");
        await page.waitForFunction(
          () => document.body.innerText.includes("не найдено") || document.body.innerText.includes("КМ-9"),
          null,
          { timeout: 20000 },
        );
        await wait(1500);
      },
    );

    await narrate("Демо достаточно: текст разобран, неопределённость не спрятана, write только dry-run.", async () => {
      await wait(1200);
    });
  },
});
