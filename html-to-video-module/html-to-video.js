// html-to-video.js
import { readFile, writeFile, mkdir, rm, stat, rename } from "node:fs/promises";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { createRenderJob, executeRenderJob } from "@hyperframes/producer";

const execFileAsync = promisify(execFile);
const VALID_TTS_VOICES = new Set(["Kore", "Charon", "Puck", "Fenrir", "Zephyr"]);

const PRESET_RESOLUTIONS = new Map([
  ["1920x1080", "landscape"],
  ["1080x1920", "portrait"],
  ["1080x1080", "square"],
  ["3840x2160", "landscape-4k"],
  ["2160x3840", "portrait-4k"],
  ["2160x2160", "square-4k"],
  ["2560x1440", "landscape-1440p"],
  ["1440x2560", "portrait-1440p"],
  ["1440x1440", "square-1440p"],
  ["1280x720", "landscape-720p"],
  ["720x1280", "portrait-720p"],
  ["720x720", "square-720p"],
  ["854x480", "landscape-480p"],
  ["480x854", "portrait-480p"],
  ["480x480", "square-480p"],
]);

/**
 * يبحث عن أي نسخة مثبتة من chrome-headless-shell أو chrome/chromium لتفادي فشل التحقق من الإصدار المثبت.
 */
export function resolveBrowserExecutable() {
  const envCandidates = [
    process.env.PRODUCER_HEADLESS_SHELL_PATH,
    process.env.CHROME_PATH,
    process.env.PUPPETEER_EXECUTABLE_PATH,
  ].filter(Boolean);

  for (const p of envCandidates) {
    if (existsSync(p)) return p;
  }

  const home = homedir() || "/root";
  const cacheDirs = [
    join(home, ".cache", "hyperframes", "chrome", "chrome-headless-shell"),
    join(home, ".cache", "puppeteer", "chrome-headless-shell"),
    join(home, ".cache", "puppeteer", "chrome"),
    "/root/.cache/puppeteer/chrome-headless-shell",
    "/root/.cache/puppeteer/chrome",
  ];

  const platformDirs =
    process.platform === "linux"
      ? [
          ["chrome-headless-shell-linux64", "chrome-headless-shell"],
          ["chrome-linux64", "chrome"],
        ]
      : process.platform === "darwin"
        ? [
            ["chrome-headless-shell-mac-arm64", "chrome-headless-shell"],
            ["chrome-headless-shell-mac-x64", "chrome-headless-shell"],
          ]
        : [["chrome-headless-shell-win64", "chrome-headless-shell.exe"]];

  for (const base of cacheDirs) {
    if (!existsSync(base)) continue;
    try {
      const versions = readdirSync(base).sort().reverse();
      for (const v of versions) {
        for (const sub of platformDirs) {
          const bin = join(base, v, ...sub);
          if (existsSync(bin)) return bin;
        }
      }
    } catch {
      // ignore unreadable dirs
    }
  }

  for (const sysBin of [
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
  ]) {
    if (existsSync(sysBin)) return sysBin;
  }

  return undefined;
}

/**
 * يكشف أقصى مدة عرض مذكورة داخل كود HTML (سمات data-duration / حركات CSS / مؤقتات setTimeout).
 */
export function detectHtmlDurationSeconds(rawHtml) {
  const html = String(rawHtml || "");
  if (!html.trim()) return null;

  const candidates = [];

  for (const m of html.matchAll(
    /\bdata-(?:composition-)?duration\s*=\s*["']\s*([0-9]+(?:\.[0-9]+)?)\s*["']/gi
  )) {
    const val = Number.parseFloat(m[1]);
    if (Number.isFinite(val) && val > 0) candidates.push(val);
  }

  for (const m of html.matchAll(
    /\bdata-end\s*=\s*["']\s*([0-9]+(?:\.[0-9]+)?)\s*["']/gi
  )) {
    const val = Number.parseFloat(m[1]);
    if (Number.isFinite(val) && val > 0) candidates.push(val);
  }

  for (const m of html.matchAll(
    /animation(?:-duration|-delay)?\s*:[^;{}]*?([0-9]+(?:\.[0-9]+)?)\s*(ms|s)\b/gi
  )) {
    const num = Number.parseFloat(m[1]);
    if (Number.isFinite(num) && num > 0) {
      const sec = m[2].toLowerCase() === "ms" ? num / 1000 : num;
      if (sec <= 300) candidates.push(sec);
    }
  }

  for (const m of html.matchAll(/setTimeout\s*\([^,]+,\s*([0-9]{3,6})\s*\)/gi)) {
    const ms = Number.parseFloat(m[1]);
    if (Number.isFinite(ms) && ms >= 500 && ms <= 300000) {
      candidates.push(ms / 1000);
    }
  }

  if (!candidates.length) return null;
  const maxDetected = Math.max(...candidates);
  return Math.round(maxDetected * 10) / 10;
}

function upsertAttrOnTag(tagText, attrName, attrValue) {
  const re = new RegExp(`\\s${attrName}\\s*=\\s*(?:"[^"]*"|'[^']*'|[^\\s>]+)`, "gi");
  const cleaned = tagText.replace(re, "");
  return cleaned.replace(/>$/, ` ${attrName}="${attrValue}">`);
}

/**
 * يهيئ كود HTML ليتوافق مع محرك @hyperframes/producer مع ضمان الالتزام الصارم بالمدة والأبعاد:
 * - "exact": يفرض المدة المحددة بالضبط على جذر التكوين مهما كانت قيمة data-duration السابقة في HTML.
 * - "auto_min": يضمن ألا يقل الفيديو عن المدة المحددة ولا عن المدة المكتشفة داخل HTML.
 * - "from_html": يعتمد المدة المكتشفة داخل HTML (أو durationSeconds كبديل إذا لم توجد).
 */
export function prepareHtmlComposition(
  rawHtml,
  {
    width = 1920,
    height = 1080,
    durationSeconds = 5,
    durationMode = "exact",
    removeMargins = true,
    waitForFonts = true,
  } = {}
) {
  let html = String(rawHtml || "");
  if (!html.trim()) {
    throw new Error("محتوى HTML فارغ.");
  }

  const evenWidth = Math.max(64, (Math.round(Number(width) || 1920) & ~1) || 1920);
  const evenHeight = Math.max(64, (Math.round(Number(height) || 1080) & ~1) || 1080);

  const requestedDur = Math.max(0.5, Number(durationSeconds) || 5);
  const detectedDur = detectHtmlDurationSeconds(html);
  let targetDuration = requestedDur;
  if (durationMode === "auto_min" && detectedDur) {
    targetDuration = Math.max(requestedDur, detectedDur);
  } else if (durationMode === "from_html" && detectedDur) {
    targetDuration = detectedDur;
  }
  const safeDuration = Math.max(0.5, Math.min(300, Math.round(targetDuration * 100) / 100));

  if (!/<html[\s>]/i.test(html)) {
    html = `<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8" /></head><body>${html}</body></html>`;
  }

  const resetCss = removeMargins
    ? `<style id="hf-studio-reset">html,body{margin:0 !important;padding:0 !important;width:100% !important;height:100% !important;overflow:hidden !important;}</style>`
    : "";

  const fontReadyScript = waitForFonts
    ? `<script id="hf-studio-fonts-ready">window.__HF_TARGET_DURATION__=${safeDuration};(function(){try{if(document.fonts&&document.fonts.ready){document.fonts.ready.catch(function(){});}}catch(e){}})();</script>`
    : `<script id="hf-studio-duration-meta">window.__HF_TARGET_DURATION__=${safeDuration};</script>`;

  if (/<\/head>/i.test(html)) {
    html = html.replace(/<\/head>/i, `${resetCss}${fontReadyScript}</head>`);
  } else if (/<body[\s>]/i.test(html)) {
    html = html.replace(/<body([^>]*)>/i, `<head><meta charset="UTF-8" />${resetCss}${fontReadyScript}</head><body$1>`);
  } else {
    html = `${resetCss}${fontReadyScript}${html}`;
  }

  if (/data-composition-id\s*=/i.test(html)) {
    html = html.replace(/<([a-zA-Z0-9-]+)\b([^>]*\bdata-composition-id\s*=[^>]*)>/gi, (fullTag) => {
      let updated = fullTag;
      updated = upsertAttrOnTag(updated, "data-width", String(evenWidth));
      updated = upsertAttrOnTag(updated, "data-height", String(evenHeight));
      updated = upsertAttrOnTag(updated, "data-duration", String(safeDuration));
      updated = upsertAttrOnTag(updated, "data-composition-duration", String(safeDuration));
      updated = updated.replace(/\sdata-end\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)/gi, "");
      return updated;
    });
    return { html, resolvedDuration: safeDuration, detectedDuration: detectedDur };
  }

  if (/<body([^>]*)>/i.test(html)) {
    html = html.replace(/<body([^>]*)>/i, (fullTag) => {
      let updated = fullTag;
      updated = upsertAttrOnTag(updated, "data-composition-id", "studio-root");
      if (!/\bdata-start\s*=/i.test(updated)) {
        updated = upsertAttrOnTag(updated, "data-start", "0");
      }
      updated = upsertAttrOnTag(updated, "data-duration", String(safeDuration));
      updated = upsertAttrOnTag(updated, "data-composition-duration", String(safeDuration));
      updated = upsertAttrOnTag(updated, "data-width", String(evenWidth));
      updated = upsertAttrOnTag(updated, "data-height", String(evenHeight));
      return updated;
    });
  } else {
    html = `<div data-composition-id="studio-root" data-start="0" data-duration="${safeDuration}" data-composition-duration="${safeDuration}" data-width="${evenWidth}" data-height="${evenHeight}" style="width:100vw;height:100vh;margin:0;padding:0;overflow:hidden;">${html}</div>`;
  }

  return { html, resolvedDuration: safeDuration, detectedDuration: detectedDur };
}

async function probeOutputMedia(mediaPath) {
  try {
    const { stdout } = await execFileAsync("ffprobe", [
      "-v",
      "error",
      "-show_entries",
      "format=duration:stream=codec_type,codec_name,nb_frames,r_frame_rate,duration,width,height",
      "-of",
      "json",
      mediaPath,
    ]);
    const parsed = JSON.parse(stdout || "{}");
    const streams = Array.isArray(parsed.streams) ? parsed.streams : [];
    const videoStream = streams.find((s) => s.codec_type === "video") || {};
    const audioStream = streams.find((s) => s.codec_type === "audio") || null;
    const fmtDur = Number.parseFloat(parsed.format?.duration || videoStream.duration || audioStream?.duration || "");
    const nbFrames = Number.parseInt(videoStream.nb_frames || "", 10);
    return {
      actualDurationSeconds: Number.isFinite(fmtDur) ? Math.round(fmtDur * 100) / 100 : null,
      actualFrames: Number.isFinite(nbFrames) ? nbFrames : null,
      actualWidth: videoStream.width || null,
      actualHeight: videoStream.height || null,
      hasAudio: Boolean(audioStream),
      audioCodec: audioStream?.codec_name || null,
    };
  } catch {
    return null;
  }
}

function collectGeminiApiKeys() {
  const keys = [];
  const pushKey = (k) => {
    if (k && typeof k === "object") {
      if (typeof k.key === "string" && k.key.trim()) {
        pushKey(k.key);
        return;
      }
      if (typeof k.encoded_key === "string" && k.encoded_key.trim()) {
        try {
          const decoded = Buffer.from(k.encoded_key.trim(), "base64").toString("utf-8").trim();
          if (decoded) {
            pushKey(decoded);
            return;
          }
        } catch {
          // ignore malformed base64
        }
      }
      return;
    }
    const trimmed = String(k || "").trim();
    if (trimmed && trimmed !== "[object Object]" && !keys.includes(trimmed)) {
      keys.push(trimmed);
    }
  };

  pushKey(process.env.GEMINI_API_KEY);
  pushKey(process.env.GOOGLE_API_KEY);
  if (process.env.GEMINI_API_KEYS) {
    process.env.GEMINI_API_KEYS.replace(/;/g, ",")
      .split(",")
      .forEach(pushKey);
  }

  // قراءة اختيارية من ملفات التهيئة المحلية داخل مساحة العمل إذا لم يُمرر المتغير البيئي
  const moduleDir = dirname(fileURLToPath(import.meta.url));
  const candidateConfigPaths = [
    join(moduleDir, "..", "gemini_keys_config.json"),
    join(process.cwd(), "gemini_keys_config.json"),
  ];
  for (const cfgPath of candidateConfigPaths) {
    if (!existsSync(cfgPath)) continue;
    try {
      const parsed = JSON.parse(readFileSync(cfgPath, "utf-8"));
      if (Array.isArray(parsed)) parsed.forEach(pushKey);
      else if (Array.isArray(parsed?.keys)) parsed.keys.forEach(pushKey);
      else if (typeof parsed?.api_key === "string") pushKey(parsed.api_key);
    } catch {
      // ignore unreadable config
    }
  }
  return keys;
}

function wrapPcmAsWav(pcmBuffer, sampleRate = 24000, channels = 1, bitsPerSample = 16) {
  const byteRate = (sampleRate * channels * bitsPerSample) / 8;
  const blockAlign = (channels * bitsPerSample) / 8;
  const header = Buffer.alloc(44);
  header.write("RIFF", 0, "ascii");
  header.writeUInt32LE(36 + pcmBuffer.length, 4);
  header.write("WAVE", 8, "ascii");
  header.write("fmt ", 12, "ascii");
  header.writeUInt32LE(16, 16);
  header.writeUInt16LE(1, 20);
  header.writeUInt16LE(channels, 22);
  header.writeUInt32LE(sampleRate, 24);
  header.writeUInt32LE(byteRate, 28);
  header.writeUInt16LE(blockAlign, 32);
  header.writeUInt16LE(bitsPerSample, 34);
  header.write("data", 36, "ascii");
  header.writeUInt32LE(pcmBuffer.length, 40);
  return Buffer.concat([header, pcmBuffer]);
}

/**
 * يولّد ملف WAV ناطق من نص `ttsText` عبر Gemini TTS (`gemini-3.8-flash-lite-tts` ثم `gemini-3.8-flash-tts`).
 */
export async function synthesizeTtsAudioToWav({
  ttsText,
  outputWavPath,
  voiceName = "Kore",
  styleInstruction = "",
}) {
  const text = String(ttsText || "").trim();
  if (!text) {
    throw new Error("نص التعليق الصوتي (ttsText) فارغ.");
  }
  const keys = collectGeminiApiKeys();
  if (!keys.length) {
    throw new Error("لا يتوفر مفتاح GEMINI_API_KEY لتوليد الصوت من النص (ttsText).");
  }

  const safeVoice = VALID_TTS_VOICES.has(voiceName) ? voiceName : "Kore";
  const models = ["gemini-3.8-flash-lite-tts", "gemini-3.8-flash-tts"];
  let lastError = "";

  for (const key of keys.slice(0, 5)) {
    for (const model of models) {
      try {
        const part = { text };
        if (styleInstruction) {
          part.speechMetadata = { style: styleInstruction };
        }
        const payload = {
          contents: [{ role: "user", parts: [part] }],
          generationConfig: {
            responseModalities: ["AUDIO"],
            speechConfig: {
              voiceConfig: {
                prebuiltVoiceConfig: { voiceName: safeVoice },
              },
            },
          },
        };
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;
        const resp = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-goog-api-key": key,
          },
          body: JSON.stringify(payload),
        });

        if (!resp.ok) {
          lastError = `HTTP ${resp.status}`;
          if (resp.status === 403 || resp.status === 429) break;
          continue;
        }

        const data = await resp.json();
        const inline = data?.candidates?.[0]?.content?.parts?.[0]?.inlineData;
        const b64 = inline?.data || "";
        const mime = String(inline?.mimeType || "").toLowerCase();
        if (!b64) continue;

        const rawBuf = Buffer.from(b64, "base64");
        let wavBuf = rawBuf;
        if (!(rawBuf.subarray(0, 4).toString("ascii") === "RIFF" && (!mime || mime.includes("wav")))) {
          const rateMatch = mime.match(/rate=(\d+)/i);
          const sampleRate = rateMatch ? Number.parseInt(rateMatch[1], 10) : 24000;
          wavBuf = wrapPcmAsWav(rawBuf, sampleRate, 1, 16);
        }

        await mkdir(dirname(outputWavPath), { recursive: true });
        await writeFile(outputWavPath, wavBuf);
        return outputWavPath;
      } catch (err) {
        lastError = err?.message || String(err);
      }
    }
  }

  throw new Error(`تعذر توليد الصوت النصي عبر Gemini TTS: ${lastError || "فشل الاتصال"}`);
}

function buildAtempoFilters(ratio) {
  const filters = [];
  let r = ratio;
  while (r > 2.0) {
    filters.push("atempo=2.0");
    r /= 2.0;
  }
  while (r < 0.5) {
    filters.push("atempo=0.5");
    r /= 0.5;
  }
  filters.push(`atempo=${r.toFixed(3)}`);
  return filters;
}

/**
 * يزامن ملف الصوت (سواء مرفوع `audioPath` أو مولّد من `ttsText`) مع المدة الدقيقة للفيديو ويدمجه عبر FFmpeg.
 */
async function mergeAudioWithVideo({
  videoPath,
  sourceAudioPath,
  format,
  targetDurationSeconds,
  audioFitMode = "fit_pad_trim",
  audioVolume = 1.0,
}) {
  const dur = Math.max(0.5, Number(targetDurationSeconds) || 5);
  const vol = Math.max(0.05, Math.min(2.0, Number(audioVolume) || 1.0));
  const mode = ["fit_pad_trim", "loop", "fit_tempo"].includes(audioFitMode) ? audioFitMode : "fit_pad_trim";

  const srcProbe = await probeOutputMedia(sourceAudioPath);
  const srcDur = Number(srcProbe?.actualDurationSeconds) || dur;

  const workDir = dirname(videoPath);
  const uid = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  const fittedWavPath = join(workDir, `.hf-audio-${uid}.wav`);
  const tmpMuxedPath = join(workDir, `.hf-mux-${uid}-${basename(videoPath)}`);

  try {
    const filters = [`volume=${vol.toFixed(2)}`];
    const fitArgs = ["-y"];

    if (mode === "loop" && srcDur < dur - 0.15) {
      fitArgs.push("-stream_loop", "-1", "-i", sourceAudioPath);
    } else if (mode === "fit_tempo" && srcDur > 0.4) {
      const ratio = srcDur / dur;
      if (ratio >= 0.75 && ratio <= 1.5 && Math.abs(ratio - 1.0) > 0.04) {
        filters.push(...buildAtempoFilters(ratio));
      }
      fitArgs.push("-i", sourceAudioPath);
    } else {
      fitArgs.push("-i", sourceAudioPath);
    }

    const fadeOutStart = Math.max(0, dur - 0.45);
    filters.push(`apad=whole_dur=${dur.toFixed(3)}`);
    filters.push(`atrim=0:${dur.toFixed(3)}`);
    filters.push("asetpts=PTS-STARTPTS");
    filters.push("afade=t=in:st=0:d=0.12");
    filters.push(`afade=t=out:st=${fadeOutStart.toFixed(3)}:d=0.45`);

    fitArgs.push("-vn", "-af", filters.join(","), "-ac", "2", "-ar", "44100", fittedWavPath);
    await execFileAsync("ffmpeg", fitArgs);

    const audioCodec = format === "webm" ? "libopus" : "aac";
    const muxArgs = [
      "-y",
      "-i",
      videoPath,
      "-i",
      fittedWavPath,
      "-map",
      "0:v:0",
      "-map",
      "1:a:0",
      "-c:v",
      "copy",
      "-c:a",
      audioCodec,
      "-b:a",
      "192k",
      "-t",
      dur.toFixed(3),
    ];
    if (format === "mp4") {
      muxArgs.push("-movflags", "+faststart");
    }
    muxArgs.push(tmpMuxedPath);

    await execFileAsync("ffmpeg", muxArgs);
    await rename(tmpMuxedPath, videoPath);
  } finally {
    await rm(fittedWavPath, { force: true }).catch(() => {});
    await rm(tmpMuxedPath, { force: true }).catch(() => {});
  }
}

/**
 * يحوّل ملف HTML إلى فيديو MP4 (أو WebM / MOV / GIF / PNG Sequence) مع الالتزام بالمدة ومزامنة الصوت عبر FFmpeg.
 *
 * @param {Object} options
 * @param {string} options.inputPath - مسار ملف HTML المراد تحويله
 * @param {string} options.outputPath - مسار ملف الفيديو الناتج
 * @param {number} [options.width=1920] - عرض الفيديو بالبكسل
 * @param {number} [options.height=1080] - ارتفاع الفيديو بالبكسل
 * @param {number} [options.fps=30] - معدل الإطارات في الثانية
 * @param {number} [options.duration=5] - مدة الفيديو بالثواني
 * @param {string} [options.durationMode="exact"] - وضع الالتزام بالوقت ("exact", "auto_min", "from_html")
 * @param {number} [options.deviceScaleFactor=1] - معامل التكبير (1x أو 2x لـ 4K)
 * @param {string} [options.quality="standard"] - جودة الترميز ("draft", "standard", "high")
 * @param {string} [options.format="mp4"] - صيغة الإخراج ("mp4", "webm", "mov", "gif", "png-sequence")
 * @param {string} [options.videoFrameFormat="auto"] - صيغة التقاط الإطارات ("auto", "jpg", "png")
 * @param {boolean} [options.removeMargins=true] - إزالة الهوامش الافتراضية تلقائياً
 * @param {string} [options.audioPath] - مسار ملف صوتي مرفوع لدمجه ومزامنته مع الفيديو عبر FFmpeg
 * @param {string} [options.ttsText] - نص يتم تحويله إلى تعليق صوتي عبر Gemini TTS ودمجه مع الفيديو
 * @param {string} [options.voiceName="Kore"] - نبرة الصوت النصي ("Kore", "Charon", "Puck", "Fenrir", "Zephyr")
 * @param {string} [options.audioFitMode="fit_pad_trim"] - طريقة مواءمة طول الصوت ("fit_pad_trim", "loop", "fit_tempo")
 * @param {number} [options.audioVolume=1.0] - مستوى الصوت (0.05 - 2.0)
 * @param {Function} [options.onProgress] - دالة تتبع التقدم
 */
export async function renderHtmlToVideo({
  inputPath,
  outputPath,
  width = 1920,
  height = 1080,
  fps = 30,
  duration = 5,
  durationMode = "exact",
  deviceScaleFactor = 1,
  quality = "standard",
  format = "mp4",
  videoFrameFormat = "auto",
  removeMargins = true,
  audioPath,
  ttsText,
  voiceName = "Kore",
  audioFitMode = "fit_pad_trim",
  audioVolume = 1.0,
  onProgress,
}) {
  if (!inputPath || !outputPath) {
    throw new Error("يجب تحديد مسار الإدخال (inputPath) ومسار الإخراج (outputPath).");
  }

  const resolvedAudioInput = audioPath ? resolve(String(audioPath)) : null;
  if (resolvedAudioInput && !existsSync(resolvedAudioInput)) {
    throw new Error(`الملف الصوتي المحدد غير موجود: ${resolvedAudioInput}`);
  }
  const cleanTtsText = ttsText ? String(ttsText).trim() : "";

  const absInputPath = resolve(inputPath);
  const absOutputPath = resolve(outputPath);
  const projectDir = dirname(absInputPath);
  const entryName = basename(absInputPath);

  const dpr = Math.max(1, Math.min(3, Math.round(Number(deviceScaleFactor) || 1)));
  const targetWidth = Math.max(64, (Math.round(Number(width) || 1920) & ~1) || 1920);
  const targetHeight = Math.max(64, (Math.round(Number(height) || 1080) & ~1) || 1080);
  const layoutWidth = dpr > 1 ? Math.max(64, (Math.round(targetWidth / dpr) & ~1) || targetWidth) : targetWidth;
  const layoutHeight = dpr > 1 ? Math.max(64, (Math.round(targetHeight / dpr) & ~1) || targetHeight) : targetHeight;

  const rawHtml = await readFile(absInputPath, "utf-8");
  const { html: preparedHtml, resolvedDuration, detectedDuration } = prepareHtmlComposition(rawHtml, {
    width: layoutWidth,
    height: layoutHeight,
    durationSeconds: duration,
    durationMode,
    removeMargins,
    waitForFonts: true,
  });

  const workEntryName = `.hf-prepared-${Date.now()}-${Math.random().toString(36).slice(2, 8)}-${entryName}`;
  const workEntryPath = join(projectDir, workEntryName);

  await mkdir(dirname(absOutputPath), { recursive: true });
  await writeFile(workEntryPath, preparedHtml, "utf-8");

  const validQuality = ["draft", "standard", "high"].includes(quality) ? quality : "standard";
  const validFormat = ["mp4", "webm", "mov", "gif", "png-sequence"].includes(format) ? format : "mp4";
  const validFrameFmt = ["auto", "jpg", "png"].includes(videoFrameFormat) ? videoFrameFormat : "auto";
  const safeFps = Math.max(1, Math.min(60, Math.round(Number(fps) || 30)));
  const hasAudioInput = Boolean(resolvedAudioInput || cleanTtsText) && ["mp4", "webm", "mov"].includes(validFormat);

  const targetPresetKey = `${targetWidth}x${targetHeight}`;
  const outputResolution = dpr > 1 ? PRESET_RESOLUTIONS.get(targetPresetKey) : undefined;

  const chromePath = resolveBrowserExecutable();
  if (chromePath && !process.env.PRODUCER_HEADLESS_SHELL_PATH) {
    process.env.PRODUCER_HEADLESS_SHELL_PATH = chromePath;
  }

  const jobConfig = {
    fps: safeFps,
    quality: validQuality,
    format: validFormat,
    videoFrameFormat: validFrameFmt,
    entryFile: workEntryName,
    strictness: "best-effort",
    workers: 1,
    ...(chromePath ? { producerConfig: { chromePath } } : {}),
    ...(outputResolution ? { outputResolution } : {}),
  };

  const tempTtsWavPath = join(projectDir, `.hf-tts-${Date.now()}-${Math.random().toString(36).slice(2, 8)}.wav`);
  const startedAt = Date.now();
  try {
    const job = createRenderJob(jobConfig);

    await executeRenderJob(job, projectDir, absOutputPath, (currentJob, message) => {
      if (onProgress) {
        const rawProgress = typeof currentJob?.progress === "number" ? currentJob.progress : 0;
        const rawPct = rawProgress <= 1 ? Math.round(rawProgress * 100) : Math.min(100, Math.round(rawProgress));
        const percent = hasAudioInput ? Math.min(88, Math.round(rawPct * 0.88)) : rawPct;
        onProgress(percent, message || currentJob?.currentStage || "");
      }
    });

    const baseProbe = validFormat !== "png-sequence" ? await probeOutputMedia(absOutputPath) : null;
    const videoTargetDuration =
      baseProbe?.actualDurationSeconds || job.duration || job.perfSummary?.compositionDurationSeconds || resolvedDuration;

    let audioSourceType = null;
    if (hasAudioInput) {
      let sourceAudioPath = resolvedAudioInput;
      if (!sourceAudioPath && cleanTtsText) {
        if (onProgress) onProgress(90, "توليد التعليق الصوتي من النص (Gemini TTS)...");
        sourceAudioPath = await synthesizeTtsAudioToWav({
          ttsText: cleanTtsText,
          outputWavPath: tempTtsWavPath,
          voiceName,
        });
        audioSourceType = "tts";
      } else {
        audioSourceType = "file";
      }

      if (sourceAudioPath) {
        if (onProgress) onProgress(95, "مزامنة ودمج الصوت مع الفيديو عبر FFmpeg...");
        await mergeAudioWithVideo({
          videoPath: absOutputPath,
          sourceAudioPath,
          format: validFormat,
          targetDurationSeconds: videoTargetDuration,
          audioFitMode,
          audioVolume,
        });
      }
      if (onProgress) onProgress(100, "اكتمل تصيير الفيديو ودمج الصوت");
    }

    let fileSize = 0;
    try {
      const st = await stat(absOutputPath);
      fileSize = st.size || 0;
    } catch {
      fileSize = 0;
    }

    const finalProbe = validFormat !== "png-sequence" ? await probeOutputMedia(absOutputPath) : null;
    const elapsedMs = Date.now() - startedAt;

    return {
      success: true,
      outputPath: absOutputPath,
      width: finalProbe?.actualWidth || job.perfSummary?.resolution?.width || targetWidth,
      height: finalProbe?.actualHeight || job.perfSummary?.resolution?.height || targetHeight,
      fps: safeFps,
      format: validFormat,
      quality: validQuality,
      duration: elapsedMs,
      requestedDurationSeconds: resolvedDuration,
      detectedHtmlDurationSeconds: detectedDuration,
      compositionDurationSeconds: finalProbe?.actualDurationSeconds || videoTargetDuration,
      frameCount: finalProbe?.actualFrames || job.totalFrames || job.framesRendered || job.perfSummary?.totalFrames || null,
      hasAudio: Boolean(finalProbe?.hasAudio),
      audioCodec: finalProbe?.audioCodec || null,
      audioSource: audioSourceType,
      fileSize,
      stages: job.perfSummary?.stages || {},
    };
  } finally {
    await rm(workEntryPath, { force: true }).catch(() => {});
    await rm(tempTtsWavPath, { force: true }).catch(() => {});
  }
}
