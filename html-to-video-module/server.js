// server.js
import express from "express";
import { writeFile, mkdir, rm } from "node:fs/promises";
import { join } from "node:path";
import { renderHtmlToVideo } from "./html-to-video.js";

const app = express();
app.use(express.json({ limit: "10mb" }));

const TEMP_DIR = "./temp";
const OUTPUT_DIR = "./outputs";

app.post("/api/render", async (req, res) => {
  const {
    html,
    width = 1920,
    height = 1080,
    fps = 30,
    duration = 10,
    durationMode = "exact",
    quality = "standard",
    format = "mp4",
    videoFrameFormat = "png",
    deviceScaleFactor = 1,
    removeMargins = true,
    audioPath,
    ttsText,
    voiceName = "Kore",
    audioFitMode = "fit_pad_trim",
    audioVolume = 1.0,
  } = req.body || {};

  if (!html) {
    return res.status(400).json({ error: "الحقل 'html' مطلوب." });
  }

  const timestamp = Date.now();
  const tempHtmlPath = join(TEMP_DIR, `input-${timestamp}.html`);
  const ext = format === "png-sequence" ? "frames" : format;
  const outputPath = join(OUTPUT_DIR, `video-${timestamp}.${ext}`);

  try {
    await mkdir(TEMP_DIR, { recursive: true });
    await mkdir(OUTPUT_DIR, { recursive: true });
    await writeFile(tempHtmlPath, html, "utf-8");

    const result = await renderHtmlToVideo({
      inputPath: tempHtmlPath,
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
      audioPath,
      ttsText,
      voiceName,
      audioFitMode,
      audioVolume,
    });

    res.download(result.outputPath, `video-${timestamp}.${ext}`);
  } catch (error) {
    console.error("فشل الترميز:", error);
    res.status(500).json({ error: error.message });
  } finally {
    await rm(tempHtmlPath, { force: true }).catch(() => {});
  }
});

const PORT = process.env.HTML_VIDEO_PORT || 3001;
app.listen(PORT, () => {
  console.log(`🚀 خادم HTML إلى فيديو يعمل على http://localhost:${PORT}/api/render`);
});
