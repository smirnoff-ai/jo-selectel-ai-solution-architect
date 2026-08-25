// Движок демо-скринкаста.
// Импортируется из frontend/scripts/<name>.mjs.
//
// Отвечает за:
//   1. Pre-synth всех реплик, собранных из сценария (через 2 прохода).
//   2. Запуск Playwright (headless chromium, запись webm).
//   3. Инжект overlay.css + overlay.js в страницу.
//   4. Предоставление api сценария: chapter / narrate / click / fill / moveTo / ...
//   5. Пост-обработка: собрать аудио-дорожку из mp3-сегментов и мукс в mp4.

import fs from "node:fs";
import path from "node:path";
import url from "node:url";
import { spawn } from "node:child_process";
import { createRequire } from "node:module";

import { synthAll, probeDurationMs } from "./tts.mjs";

// Playwright резолвим относительно CWD вызывающего скрипта — skill сам не
// зависит от node_modules. Если в проекте playwright не установлен,
// рядом можно вызывать `pnpm add -D playwright`.
const requireFromCwd = createRequire(path.join(process.cwd(), "package.json"));
let chromium;
try {
  ({ chromium } = requireFromCwd("playwright"));
} catch (e) {
  throw new Error(
    "skill demo-screencast требует playwright в CWD проекта.\n" +
      "Установите: pnpm add -D playwright && npx playwright install chromium\n" +
      "Оригинальная ошибка: " + e.message,
  );
}

const __filename = url.fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ASSETS = path.resolve(__dirname, "..", "assets");

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function runCmd(cmd, args) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { stdio: ["ignore", "pipe", "pipe"] });
    let stderr = "";
    p.stderr.on("data", (d) => (stderr += d.toString()));
    p.on("close", (code) =>
      code === 0
        ? resolve()
        : reject(new Error(`${cmd} ${args.slice(0, 3).join(" ")} exit ${code}\n${stderr}`)),
    );
  });
}

/**
 * Первый проход по сценарию: сбор всех реплик narrate() и chapter()
 * без реального взаимодействия со страницей — ради pre-synth.
 */
async function collectScript(scenarioFn) {
  const script = [];
  let idxCounter = 0;
  const noop = async () => {};
  // В collect-pass action() НЕ вызывается, чтобы избежать сайд-эффектов
  // (например, изменения default mock-сценария в backend, создания заявок).
  // Сценарий в dry-run нужен только для сбора текстов реплик для TTS.
  const collectApi = {
    isDryRun: true,
    page: null,
    async goto() {},
    async role() {},
    async wait() {},
    async moveTo() {},
    async click() {},
    async fill() {},
    async scrollIntoView() {},
    async waitForRows() {
      return 1;
    },
    async chapter(text) {
      script.push({ kind: "chapter", idx: ++idxCounter, text });
    },
    async narrate(text, _action) {
      script.push({ kind: "narrate", idx: ++idxCounter, text });
      // action НЕ выполняется — это dry-run.
    },
    hideCursor: noop,
    showCursor: noop,
  };
  await scenarioFn(collectApi);
  return script;
}

/**
 * Основной проход: реальный Playwright + запись видео + выполнение сценария.
 */
export async function runScreencast({
  name,
  outDir,
  voice = "ru-RU-SvetlanaNeural",
  baseUrl = "http://localhost:3001",
  pageWidth = 1440,
  pageHeight = 900,
  scenario,
}) {
  if (!name || !scenario) throw new Error("runScreencast: name и scenario обязательны");
  fs.mkdirSync(outDir, { recursive: true });

  const tmpDir = path.join(outDir, `_${name}-tmp`);
  const rawDir = path.join(outDir, `_${name}-raw`);
  fs.rmSync(rawDir, { recursive: true, force: true });
  fs.mkdirSync(rawDir, { recursive: true });
  fs.mkdirSync(tmpDir, { recursive: true });

  // --- 1) Собираем скрипт (dry-run) и синтезируем все реплики ---
  console.log("Collecting script...");
  const script = await collectScript(scenario);
  const voiceScript = script.filter((s) => s.kind === "narrate").map((s) => s.text);
  console.log(`narrate segments: ${voiceScript.length}`);
  const segMeta = await synthAll(voiceScript, { voice, dir: tmpDir });

  // Маппинг: индекс narrate в скрипте → mp3 файл и duration
  const narrateIdx = new Map();
  let j = 0;
  for (const item of script) {
    if (item.kind === "narrate") {
      narrateIdx.set(item.idx, segMeta[j]);
      j += 1;
    }
  }

  // --- 2) Playwright pass ---
  const browser = await chromium.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });
  const context = await browser.newContext({
    viewport: { width: pageWidth, height: pageHeight },
    recordVideo: { dir: rawDir, size: { width: pageWidth, height: pageHeight } },
    locale: "ru-RU",
  });

  // Инжект CSS + JS через addInitScript: запустится в каждом документе до первого скрипта страницы.
  const overlayCss = fs.readFileSync(path.join(ASSETS, "overlay.css"), "utf-8");
  const overlayJs = fs.readFileSync(path.join(ASSETS, "overlay.js"), "utf-8");
  await context.addInitScript({
    content: `
      (function() {
        if (window.__demoCssInjected) return;
        const css = ${JSON.stringify(overlayCss)};
        function inject() {
          if (window.__demoCssInjected) return;
          const target = document.head || document.documentElement;
          if (!target) return false;
          const s = document.createElement("style");
          s.textContent = css;
          target.appendChild(s);
          window.__demoCssInjected = true;
          return true;
        }
        if (!inject()) {
          document.addEventListener("DOMContentLoaded", inject, { once: true });
        }
      })();
      ${overlayJs}
    `,
  });

  const page = await context.newPage();
  page.setDefaultTimeout(45_000);

  const recordStartedAt = Date.now();
  const audioSegments = []; // { start_ms, dur_ms, file, text }

  // Помощники

  async function ensureOverlayReady() {
    try {
      await page.waitForFunction(
        () => window.__demoOverlay && window.__demoCursor,
        { timeout: 8000 },
      );
    } catch {
      // Если addInitScript не сработал (например, страница грузилась слишком
      // медленно или первый goto ещё не произошёл) — инжектируем вручную.
      const overlayCss = fs.readFileSync(path.join(ASSETS, "overlay.css"), "utf-8");
      const overlayJs = fs.readFileSync(path.join(ASSETS, "overlay.js"), "utf-8");
      await page.evaluate(
        ([css, js]) => {
          if (!window.__demoCssInjected) {
            const s = document.createElement("style");
            s.textContent = css;
            document.head.appendChild(s);
            window.__demoCssInjected = true;
          }
          if (!window.__demoInstalled) {
            const el = document.createElement("script");
            el.textContent = js;
            document.head.appendChild(el);
          }
        },
        [overlayCss, overlayJs],
      );
      await page.waitForFunction(
        () => window.__demoOverlay && window.__demoCursor,
        { timeout: 3000 },
      );
    }
  }

  async function getCenterOf(selector) {
    const handle = await page.locator(selector).first();
    await handle.scrollIntoViewIfNeeded();
    const box = await handle.boundingBox();
    if (!box) throw new Error(`Нет boundingBox для ${selector}`);
    return {
      x: box.x + box.width / 2,
      y: box.y + box.height / 2,
      rect: box,
    };
  }

  async function moveTo(selector) {
    await ensureOverlayReady();
    const { x, y } = await getCenterOf(selector);
    await page.evaluate(
      ([cx, cy]) => window.__demoCursor.moveTo(cx, cy),
      [x, y],
    );
    await page.mouse.move(x, y);
  }

  async function click(selector) {
    await ensureOverlayReady();
    const { x, y, rect } = await getCenterOf(selector);
    // курсор к цели
    await page.evaluate(
      ([cx, cy]) => window.__demoCursor.moveTo(cx, cy),
      [x, y],
    );
    // ring + ripple
    await page.evaluate(
      ([r]) => window.__demoOverlay.attentionRing(r, 500),
      [rect],
    );
    await sleep(260);
    await page.evaluate(
      ([cx, cy]) => window.__demoCursor.pressAt(cx, cy),
      [x, y],
    );
    await page.mouse.move(x, y);
    await page.mouse.click(x, y);
  }

  async function fill(selector, text) {
    await ensureOverlayReady();
    const { x, y, rect } = await getCenterOf(selector);
    await page.evaluate(
      ([cx, cy]) => window.__demoCursor.moveTo(cx, cy),
      [x, y],
    );
    await page.evaluate(
      ([r]) => window.__demoOverlay.attentionRing(r, 400),
      [rect],
    );
    await page.locator(selector).first().fill(text);
  }

  async function scrollIntoView(selector) {
    await page.locator(selector).first().scrollIntoViewIfNeeded();
  }

  async function waitForRows(selector, { retryUrl, maxTries = 10, delayMs = 1500 } = {}) {
    for (let i = 0; i < maxTries; i++) {
      if (retryUrl) {
        await page.goto(baseUrl + retryUrl, { waitUntil: "domcontentloaded" }).catch(() => {});
        await ensureOverlayReady();
      }
      await sleep(delayMs);
      const count = await page.locator(selector).count();
      if (count > 0) return count;
    }
    return 0;
  }

  async function goto(pathname) {
    const dest = pathname.startsWith("http") ? pathname : `${baseUrl}${pathname}`;
    await page.goto(dest, { waitUntil: "domcontentloaded" }).catch(() => {});
    await ensureOverlayReady();
  }

  async function role(r, employeeId) {
    await page.evaluate(
      ([rr, ee]) => {
        window.localStorage.setItem("bankbpm.role", rr);
        if (ee) window.localStorage.setItem("bankbpm.employee_id", ee);
        window.dispatchEvent(new Event("bankbpm:role-change"));
      },
      [r, employeeId ?? ""],
    );
  }

  async function hideCursor() {
    await ensureOverlayReady();
    await page.evaluate(() => window.__demoCursor.hide());
  }

  async function showCursor() {
    await ensureOverlayReady();
    await page.evaluate(() => window.__demoCursor.show());
  }

  let currentIdx = 0;

  async function chapter(text) {
    currentIdx += 1;
    await ensureOverlayReady();
    await page.evaluate(
      ([t]) => {
        if (window.__demoOverlay && window.__demoOverlay.hideSubtitle) {
          window.__demoOverlay.hideSubtitle();
        }
        if (window.__demoOverlay && window.__demoOverlay.showChapter) {
          window.__demoOverlay.showChapter(t, 1600);
        }
      },
      [text],
    );
    await sleep(1400);
  }

  async function narrate(text, action, opts = {}) {
    currentIdx += 1;
    const tailMs = opts.tailMs ?? 400;
    const meta = [...narrateIdx.values()][audioSegments.length];
    const ttsMs = meta ? meta.dur : 3000;
    await ensureOverlayReady();
    const start_ms = Date.now() - recordStartedAt;
    // Одновременно: субтитр + (опц.) действие.
    await page.evaluate(
      ([t]) => {
        if (window.__demoOverlay && window.__demoOverlay.showSubtitle) {
          window.__demoOverlay.showSubtitle(t);
        }
      },
      [text],
    );
    const actionPromise = action ? action() : Promise.resolve();
    // Держим не меньше TTS + tail, но и не меньше длительности action.
    const minHold = sleep(ttsMs + tailMs);
    await Promise.all([
      actionPromise.catch((e) => console.error("action err:", e)),
      minHold,
    ]);
    const dur_ms = Date.now() - recordStartedAt - start_ms;
    audioSegments.push({
      start_ms,
      dur_ms,
      tts_ms: ttsMs,
      file: meta?.file,
      text,
    });
  }

  // На первой загрузке страницы монтируем оверлей (иначе первый goto в сценарии
  // загрузит страницу без него).
  await page.goto(baseUrl + "/");
  await page.waitForLoadState("domcontentloaded").catch(() => {});

  const api = {
    page,
    context,
    goto,
    role,
    wait: sleep,
    moveTo,
    click,
    fill,
    scrollIntoView,
    waitForRows,
    chapter,
    narrate,
    hideCursor,
    showCursor,
  };

  try {
    await scenario(api);
  } finally {
    // Даем последнему субтитру доиграть
    await sleep(400);
    await page.evaluate(() => {
      window.__demoOverlay &&
        window.__demoOverlay.hideSubtitle &&
        window.__demoOverlay.hideSubtitle();
    }).catch(() => {});
    await sleep(400);
    await context.close();
    await browser.close();
  }

  // Найти записанное видео
  const files = fs
    .readdirSync(rawDir)
    .filter((f) => f.endsWith(".webm"))
    .map((f) => path.join(rawDir, f));
  files.sort(
    (a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs,
  );
  if (files.length === 0) throw new Error("Видео не записалось");
  const rawVideo = files[0];
  const videoDurationMs = await probeDurationMs(rawVideo);

  // --- 3) Сборка аудиодорожки ---
  const audioFile = path.join(tmpDir, "voice.m4a");
  const ffInputs = [];
  const ffFilter = [];
  audioSegments.forEach((seg, i) => {
    if (!seg.file) return;
    ffInputs.push("-i", seg.file);
    ffFilter.push(`[${ffInputs.length / 2 - 1}:a]adelay=${seg.start_ms}|${seg.start_ms}[a${i}]`);
  });
  if (ffInputs.length === 0) throw new Error("Нет реплик для озвучки");
  const mixParts = audioSegments.map((_, i) => `[a${i}]`).join("");
  ffFilter.push(
    `${mixParts}amix=inputs=${audioSegments.length}:duration=longest:dropout_transition=0,volume=2.0,apad=pad_dur=${Math.round(videoDurationMs / 1000) + 2}[out]`,
  );
  await runCmd("ffmpeg", [
    "-y",
    ...ffInputs,
    "-filter_complex",
    ffFilter.join(";"),
    "-map",
    "[out]",
    "-t",
    (videoDurationMs / 1000).toFixed(3),
    "-c:a",
    "aac",
    "-b:a",
    "160k",
    audioFile,
  ]);

  // --- 4) Мукс видео + аудио ---
  const finalMp4 = path.join(outDir, `${name}.mp4`);
  await runCmd("ffmpeg", [
    "-y",
    "-i",
    rawVideo,
    "-i",
    audioFile,
    "-map",
    "0:v:0",
    "-map",
    "1:a:0",
    "-c:v",
    "libx264",
    "-preset",
    "medium",
    "-crf",
    "22",
    "-c:a",
    "aac",
    "-b:a",
    "160k",
    "-shortest",
    "-movflags",
    "+faststart",
    finalMp4,
  ]);

  // --- 5) Сохранить SRT и segments.json ---
  const srt = audioSegments
    .map((s, i) => {
      const start = msToSrt(s.start_ms);
      const end = msToSrt(s.start_ms + Math.min(s.dur_ms - 100, s.tts_ms + 400));
      return `${i + 1}\n${start} --> ${end}\n${s.text}\n`;
    })
    .join("\n");
  fs.writeFileSync(path.join(outDir, `${name}.srt`), srt, "utf-8");
  fs.writeFileSync(
    path.join(outDir, `${name}.segments.json`),
    JSON.stringify(
      {
        generated_at: new Date().toISOString(),
        voice,
        baseUrl,
        video_duration_ms: videoDurationMs,
        segments: audioSegments,
      },
      null,
      2,
    ),
    "utf-8",
  );

  console.log("DONE:", finalMp4);
  return { mp4: finalMp4, duration_ms: videoDurationMs };
}

function msToSrt(ms) {
  const t = Math.max(0, Math.floor(ms));
  const h = Math.floor(t / 3600_000);
  const m = Math.floor((t % 3600_000) / 60_000);
  const s = Math.floor((t % 60_000) / 1000);
  const ms2 = t % 1000;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")},${String(ms2).padStart(3, "0")}`;
}
