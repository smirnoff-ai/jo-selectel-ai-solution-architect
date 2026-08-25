// Обёртка edge-tts: синтезирует mp3 и возвращает длительность в мс.
// Кеширует результаты в targetDir по имени файла.

import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

function edgeTtsBin() {
  const home = process.env.HOME || "";
  const local = path.join(home, ".local", "bin", "edge-tts");
  if (fs.existsSync(local)) return local;
  return "edge-tts";
}

function runCmd(bin, args) {
  return new Promise((resolve, reject) => {
    const p = spawn(bin, args, { stdio: ["ignore", "pipe", "pipe"] });
    let stdout = "";
    let stderr = "";
    p.stdout.on("data", (d) => (stdout += d.toString()));
    p.stderr.on("data", (d) => (stderr += d.toString()));
    p.on("close", (code) =>
      code === 0
        ? resolve({ stdout, stderr })
        : reject(new Error(`${bin} exited with ${code}\n${stderr}`)),
    );
  });
}

export async function synth(text, outFile, voice = "ru-RU-SvetlanaNeural") {
  if (fs.existsSync(outFile)) return outFile;
  const bin = edgeTtsBin();
  // Retry с экспоненциальным backoff: edge-tts иногда отдаёт 503 от Bing.
  let lastErr = null;
  for (let attempt = 1; attempt <= 5; attempt++) {
    try {
      // Удаляем потенциально неполный файл от предыдущей попытки.
      try {
        if (fs.existsSync(outFile)) fs.unlinkSync(outFile);
      } catch {}
      await runCmd(bin, [
        "--voice",
        voice,
        "--rate",
        "+0%",
        "--pitch",
        "+0Hz",
        "--text",
        text,
        "--write-media",
        outFile,
      ]);
      // Проверка что файл не пустой и читается ffprobe.
      const st = fs.statSync(outFile);
      if (st.size < 256) throw new Error("tts output too small");
      return outFile;
    } catch (e) {
      lastErr = e;
      const wait = Math.min(1500 * 2 ** (attempt - 1), 8000);
      await new Promise((r) => setTimeout(r, wait));
    }
  }
  throw lastErr;
}

export async function probeDurationMs(file) {
  // Retry: иногда сразу после записи mp3 ffprobe не успевает прочитать заголовок.
  let lastErr;
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const { stdout } = await runCmd("ffprobe", [
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=nokey=1:noprint_wrappers=1",
        file,
      ]);
      const v = Math.round(parseFloat(stdout) * 1000);
      if (Number.isFinite(v) && v > 0) return v;
      lastErr = new Error(`ffprobe returned ${stdout}`);
    } catch (e) {
      lastErr = e;
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw lastErr;
}

export async function synthAll(texts, { voice, dir }) {
  fs.mkdirSync(dir, { recursive: true });
  const results = [];
  for (let i = 0; i < texts.length; i++) {
    const outFile = path.join(
      dir,
      `seg_${String(i + 1).padStart(3, "0")}.mp3`,
    );
    await synth(texts[i], outFile, voice);
    const dur = await probeDurationMs(outFile);
    results.push({ idx: i + 1, file: outFile, dur, text: texts[i] });
  }
  return results;
}
