// html-to-video.js
import { readFile, writeFile, mkdir, rm, stat } from "node:fs/promises";
import { existsSync, readdirSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { homedir } from "node:os";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { createRenderJob, executeRenderJob } from "@hyperframes/producer";

const execFileAsync = promisify(execFile);

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

  // استخراج مدة + تأخير حركات CSS مثل animation: fade 4s 2s
  for (const m of html.matchAll(
    /animation(?:-duration|-delay)?\s*:[^;{}]*?([0-9]+(?:\.[0-9]+)?)\s*(ms|s)\b/gi
  )) {
    const num = Number.parseFloat(m[1]);
    if (Number.isFinite(num) && num > 0) {
      const sec = m[2].toLowerCase() === "ms" ? num / 1000 : num;
      if (sec <= 300) candidates.push(sec);
    }
  }

  // استخراج أطول setTimeout بالمللي ثانية داخل السكربتات (غالباً لتبديل الشرائح)
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

/**
 * يستبدل أو يضيف سمة على وسم الفتح الأول لعنصر يحتوي data-composition-id أو body.
 */
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

  // إذا كان HTML يحتوي مسبقاً على data-composition-id نفرض الأبعاد والمدة المطلوبة على كل جذر تكوين لمنع التقصير
  if (/data-composition-id\s*=/i.test(html)) {
    html = html.replace(/<([a-zA-Z0-9-]+)\b([^>]*\bdata-composition-id\s*=[^>]*)>/gi, (fullTag) => {
      let updated = fullTag;
      updated = upsertAttrOnTag(updated, "data-width", String(evenWidth));
      updated = upsertAttrOnTag(updated, "data-height", String(evenHeight));
      updated = upsertAttrOnTag(updated, "data-duration", String(safeDuration));
      updated = upsertAttrOnTag(updated, "data-composition-duration", String(safeDuration));
      // إزالة data-end إذا كانت أقصر من المدة المطلوبة
      updated = updated.replace(/\sdata-end\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)/gi, "");
      return updated;
    });
    return { html, resolvedDuration: safeDuration, detectedDuration: detectedDur };
  }

  // حقن سمات التكوين مباشرة على body أو تغليف المحتوى عند عدم وجود body
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

async function probeOutputVideo(outputPath) {
  try {
    const { stdout } = await execFileAsync("ffprobe", [
      "-v",
      "error",
      "-show_entries",
      "format=duration",
      "-show_entries",
      "stream=nb_frames,r_frame_rate,duration,width,height",
      "-of",
      "json",
      outputPath,
    ]);
    const parsed = JSON.parse(stdout || "{}");
    const stream = Array.isArray(parsed.streams) ? parsed.streams[0] || {} : {};
    const fmtDur = Number.parseFloat(parsed.format?.duration || stream.duration || "");
    const nbFrames = Number.parseInt(stream.nb_frames || "", 10);
    return {
      actualDurationSeconds: Number.isFinite(fmtDur) ? Math.round(fmtDur * 100) / 100 : null,
      actualFrames: Number.isFinite(nbFrames) ? nbFrames : null,
      actualWidth: stream.width || null,
      actualHeight: stream.height || null,
    };
  } catch {
    return null;
  }
}

/**
 * يحوّل ملف HTML إلى فيديو MP4 (أو WebM / MOV / GIF / PNG Sequence) مع الالتزام الصارم بالمدة المحددة.
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
  onProgress,
}) {
  if (!inputPath || !outputPath) {
    throw new Error("يجب تحديد مسار الإدخال (inputPath) ومسار الإخراج (outputPath).");
  }

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

  const startedAt = Date.now();
  try {
    const job = createRenderJob(jobConfig);

    await executeRenderJob(job, projectDir, absOutputPath, (currentJob, message) => {
      if (onProgress) {
        const rawProgress = typeof currentJob?.progress === "number" ? currentJob.progress : 0;
        const percent = rawProgress <= 1 ? Math.round(rawProgress * 100) : Math.min(100, Math.round(rawProgress));
        onProgress(percent, message || currentJob?.currentStage || "");
      }
    });

    let fileSize = 0;
    try {
      const st = await stat(absOutputPath);
      fileSize = st.size || 0;
    } catch {
      fileSize = 0;
    }

    const probed = validFormat !== "png-sequence" ? await probeOutputVideo(absOutputPath) : null;
    const elapsedMs = Date.now() - startedAt;

    return {
      success: true,
      outputPath: absOutputPath,
      width: probed?.actualWidth || job.perfSummary?.resolution?.width || targetWidth,
      height: probed?.actualHeight || job.perfSummary?.resolution?.height || targetHeight,
      fps: safeFps,
      format: validFormat,
      quality: validQuality,
      duration: elapsedMs,
      requestedDurationSeconds: resolvedDuration,
      detectedHtmlDurationSeconds: detectedDuration,
      compositionDurationSeconds:
        probed?.actualDurationSeconds || job.duration || job.perfSummary?.compositionDurationSeconds || resolvedDuration,
      frameCount: probed?.actualFrames || job.totalFrames || job.framesRendered || job.perfSummary?.totalFrames || null,
      fileSize,
      stages: job.perfSummary?.stages || {},
    };
  } finally {
    await rm(workEntryPath, { force: true }).catch(() => {});
  }
}
