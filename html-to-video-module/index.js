// index.js
import { renderHtmlToVideo } from "./html-to-video.js";

const cliArgs = process.argv.slice(2);
const readArg = (flag, fallback) => {
  const idx = cliArgs.indexOf(flag);
  return idx !== -1 && cliArgs[idx + 1] ? cliArgs[idx + 1] : fallback;
};

const inputPath = readArg("--input", "./example.html");
const outputPath = readArg("--output", "./output.mp4");
const width = Number(readArg("--width", "1080"));
const height = Number(readArg("--height", "1080"));
const fps = Number(readArg("--fps", "30"));
const duration = Number(readArg("--duration", "10"));
const durationMode = readArg("--duration-mode", "exact");
const quality = readArg("--quality", "standard");
const format = readArg("--format", "mp4");
const videoFrameFormat = readArg("--frame-format", "png");
const deviceScaleFactor = Number(readArg("--dpr", "1"));
const removeMargins = readArg("--remove-margins", "true") !== "false";
const audioPath = readArg("--audio", "");
const ttsText = readArg("--tts-text", "");
const voiceName = readArg("--voice", "Kore");
const audioFitMode = readArg("--audio-fit", "fit_pad_trim");
const audioVolume = Number(readArg("--audio-volume", "1.0"));

try {
  const result = await renderHtmlToVideo({
    inputPath,
    outputPath,
    width,
    height,
    fps,
    duration,
    durationMode,
    quality,
    format,
    videoFrameFormat,
    deviceScaleFactor,
    removeMargins,
    ...(audioPath ? { audioPath } : {}),
    ...(ttsText ? { ttsText } : {}),
    voiceName,
    audioFitMode,
    audioVolume,
    onProgress: (percent, stage) => {
      if (process.stdout.isTTY) {
        process.stdout.write(`\r⏳ التقدم: ${percent}% (${stage || ""})`);
      } else {
        console.log(JSON.stringify({ type: "progress", percent, stage }));
      }
    },
  });

  if (cliArgs.includes("--json")) {
    console.log(JSON.stringify({ type: "result", ...result }));
  } else {
    console.log(`\n✅ تم إنشاء الفيديو: ${result.outputPath}`);
    console.log(`🎬 مدة الفيديو الناتج: ${result.compositionDurationSeconds} ثانية`);
    console.log(`🔊 الصوت المدمج: ${result.hasAudio ? `${result.audioCodec} (${result.audioSource})` : "بدون صوت"}`);
    console.log(`⏱️ زمن التصيير: ${result.duration} مللي ثانية`);
    console.log(`🎞️ عدد الإطارات: ${result.frameCount ?? "غير متاح"}`);
  }
} catch (error) {
  if (cliArgs.includes("--json")) {
    console.error(JSON.stringify({ type: "error", error: error.message }));
  } else {
    console.error("\n❌ فشل التحويل:", error.message);
  }
  process.exit(1);
}
