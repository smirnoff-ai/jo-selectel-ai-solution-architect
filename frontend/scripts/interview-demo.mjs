import { runScreencast } from "../../.agents/skills/demo-screencast/scripts/build.mjs";

const RUN_MS = 180_000;
const outDir = process.env.DEMO_OUT || "/opt/cursor/artifacts";

await runScreencast({
  name: "interview-demo",
  outDir,
  voice: "ru-RU-SvetlanaNeural",
  baseUrl: "http://localhost:3000",
  pageWidth: 1440,
  pageHeight: 900,
  scenario: async ({ goto, chapter, narrate, click, fill, moveTo, wait, page, scrollIntoView }) => {
    const waitBody = async (needle, timeout = RUN_MS) => {
      if (!page) return;
      await page.waitForFunction(
        (text) => document.body.innerText.includes(text),
        needle,
        { timeout },
      );
    };

    const waitAny = async (needles, timeout = RUN_MS) => {
      if (!page) return;
      await page.waitForFunction(
        (texts) => texts.some((text) => document.body.innerText.includes(text)),
        needles,
        { timeout },
      );
    };

    const assertBody = async (needle, label) => {
      if (!page) return;
      const ok = await page.evaluate((text) => document.body.innerText.includes(text), needle);
      if (!ok) throw new Error(`${label}: нет «${needle}»`);
    };

    const createFromPreset = async (label) => {
      await click('button:has-text("Создать обращение")');
      await page.waitForURL("**/appeals/new", { timeout: 15000 });
      await wait(500);
      await click(`button:has-text("${label}")`);
      await wait(700);
      await click("form button[type='submit']");
      await page.waitForURL(/\/appeals\/\d+/, { timeout: 20000 });
      await waitBody("R-", 20000);
    };

    const waitRunFinished = async ({ afterReply = false } = {}) => {
      if (afterReply) {
        await waitAny(["идёт разбор", "run: идёт"], 20000);
      }
      await waitBody("прогон закончен", RUN_MS);
      await wait(800);
    };

    const showCard = async (needle) => {
      await scrollIntoView(`text=${needle}`);
      await moveTo(`text=${needle}`);
      await wait(900);
    };

    await goto("/login");
    await chapter("Рефлекс");
    await narrate("Входим одним логином диспетчера. Клиентов СеверФуда на этом экране нет.", async () => {
      await fill("#login", "dispatcher");
      await fill("#password", "secret");
      await click('button[type="submit"]');
      await page.waitForURL("**/desk", { timeout: 15000 });
    });

    await chapter("Стол диспетчера");
    await narrate(
      "Четыре корзины — очередь разбора, не почтовый ящик. Разобранные заявки уходят в журнал.",
      async () => {
        await wait(2200);
      },
    );

    await chapter("S1. Полный запрос");
    await narrate(
      "Пакетный сценарий: СеверФуд, Дмитровское, ХУ-18. Время мира демо — тринадцатое августа, шестнадцать сорок.",
      async () => {
        await createFromPreset("S1. Относительно полный запрос");
      },
    );
    await narrate("Слева карточка, справа ход агента. Смотрим, как вызываются справочники.", async () => {
      await waitAny(["Поиск площадок", "search_sites", "слоты обновляются"], 90000);
      await wait(1500);
    });
    await narrate("Агент ищет площадку в CRM и установку в реестре. Слоты заполняются по ходу.", async () => {
      await waitRunFinished();
      await assertBody("Создать заявку", "S1");
    });
    await narrate("Клиент, объект и ХУ-18 опознаны однозначно. Это A-1003 на Дмитровском.", async () => {
      await showCard("Оборудование");
      await wait(1200);
    });
    await narrate("Договор Gold, SLA шестьдесят минут. Дедлайн — семнадцать сорок по Москве.", async () => {
      await showCard("Договор");
      await wait(1000);
    });
    await narrate("Примерка в ITSM прошла. Запись не сохранилась: persisted false. Пишет код, не модель.", async () => {
      await showCard("Примерка ITSM");
      await wait(1400);
    });

    await chapter("S2. Две семнадцатых");
    await narrate("Неоднозначный текст: снова семнадцатая, температура плюс восемь. Город в письме не назван.", async () => {
      await createFromPreset("S2. Неоднозначный запрос");
    });
    await narrate("Агент не угадывает склад. Две ХУ-17 на разных площадках — исход уточнение.", async () => {
      await waitRunFinished();
      await assertBody("Нужно уточнение", "S2");
    });
    await narrate("На оборудовании бейдж «несколько»: Москва и Екатеринбург. Тикет город не выбирает.", async () => {
      await showCard("Оборудование");
      await wait(1400);
    });
    await narrate("Вопросы клиенту не пустые: какой город, какая семнадцатая. Примерки заявки нет.", async () => {
      await showCard("Вопросы");
      await wait(1600);
    });

    await chapter("Вопрос диспетчера");
    await narrate("Спрашиваем в треде, почему не создаём заявку, если клиент один.", async () => {
      await fill("#reply", "Почему не создаём заявку, если клиент один?");
      await wait(400);
      await click('form:has(#reply) button[type="submit"]');
    });
    await narrate("Агент отвечает по карточке: клиент один, объектов два. Исход не меняем наугад.", async () => {
      await waitRunFinished({ afterReply: true });
      await wait(1800);
    });

    await chapter("S3. Повторный звонок");
    await narrate("Расшифровка: Андрей с Дмитровского, уже писал по семнадцатой. Канал — звонок.", async () => {
      await createFromPreset("S3. Возможное повторное обращение");
    });
    await narrate("Площадка одна, актив A-1001, открыт T-884. Это тот же инцидент.", async () => {
      await waitRunFinished();
      await assertBody("T-884", "S3");
      await assertBody("Обновить заявку", "S3");
    });
    await narrate("Исход — обновить T-884. Примерка патч, не новая заявка с would-id.", async () => {
      await showCard("Примерка ITSM");
      await wait(1400);
    });

    await chapter("S4. Кода нет в реестре");
    await narrate("Клиент называет КМ-9 на Дмитровском. Такого кода в сиде нет.", async () => {
      await createFromPreset("S4. Код назвали, в реестре пусто");
    });
    await narrate("Площадка ясна — этого мало для заявки. Оборудование: не найдено.", async () => {
      await waitRunFinished();
      await assertBody("не найдено", "S4");
      await assertBody("Нужно уточнение", "S4");
    });
    await narrate("T-884 про ХУ-17, не про КМ-9. Чужой инцидент не клеим.", async () => {
      await showCard("Оборудование");
      await wait(1200);
    });
    await narrate("Вопросы: какой код на самом деле. Примерки нет, автоматом в прод не идём.", async () => {
      await showCard("Вопросы");
      await wait(1600);
    });

    await chapter("Журнал");
    await narrate("В журнале видны исходы: create и update разобраны, два уточнения ждут ответа.", async () => {
      await click('a:has-text("Журнал")');
      await page.waitForURL("**/journal", { timeout: 15000 });
      await page.waitForSelector("table tbody tr", { timeout: 15000 });
      await wait(1800);
    });
    await narrate("Текст разобран, неопределённость не спрятана, write только dry-run.", async () => {
      await wait(1600);
    });
  },
});
