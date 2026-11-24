/* أداة قص الصور التفاعلية لشواهد الخدمات التعليمية (تعمل باللمس والفأرة بدون مغادرة الصفحة) */
(function (global) {
  'use strict';

  const CROP_MODAL_ID = 'eduImageCropperModal';
  let initialized = false;
  let state = {
    queue: [],
    index: 0,
    onDone: null,
    img: null,
    rotation: 0,
    aspect: 0, // 0 = free
    drawW: 0,
    drawH: 0,
    crop: { x: 0, y: 0, w: 100, h: 100 },
    dragMode: null, // 'move' | 'nw' | 'ne' | 'sw' | 'se'
    dragStart: { x: 0, y: 0 },
    cropStart: { x: 0, y: 0, w: 0, h: 0 },
    isSingleMode: false,
  };

  function injectStylesAndDom() {
    if (initialized) return;
    initialized = true;

    const style = document.createElement('style');
    style.id = 'eduImageCropperStyles';
    style.textContent = `
      #${CROP_MODAL_ID} {
        display: none; position: fixed; inset: 0; z-index: 260000;
        background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(4px);
        align-items: center; justify-content: center; padding: 14px;
        direction: rtl; font-family: 'Cairo', sans-serif;
      }
      #${CROP_MODAL_ID}.show { display: flex; }
      #${CROP_MODAL_ID} .crop-card {
        background: #ffffff; border-radius: 16px; width: 100%; max-width: 760px;
        max-height: 94vh; display: flex; flex-direction: column; overflow: hidden;
        box-shadow: 0 24px 64px rgba(0,0,0,0.45);
      }
      #${CROP_MODAL_ID} .crop-head {
        background: linear-gradient(135deg, #1e293b, #334155); color: #fff;
        padding: 12px 18px; display: flex; align-items: center; justify-content: space-between; gap: 10px;
      }
      #${CROP_MODAL_ID} .crop-head h4 { margin: 0; font-size: 16px; font-weight: 800; }
      #${CROP_MODAL_ID} .crop-close {
        background: #ef4444; color: #fff; border: none; width: 32px; height: 32px;
        border-radius: 50%; font-size: 16px; font-weight: 900; cursor: pointer;
      }
      #${CROP_MODAL_ID} .crop-tools {
        padding: 10px 14px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
        display: flex; flex-wrap: wrap; gap: 6px; align-items: center; justify-content: space-between;
      }
      #${CROP_MODAL_ID} .crop-btn-row { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
      #${CROP_MODAL_ID} .crop-tool-btn {
        background: #fff; color: #334155; border: 1.5px solid #cbd5e1;
        padding: 5px 10px; border-radius: 7px; font-family: inherit;
        font-size: 12px; font-weight: 700; cursor: pointer;
      }
      #${CROP_MODAL_ID} .crop-tool-btn:hover { border-color: #3b82f6; color: #1d4ed8; }
      #${CROP_MODAL_ID} .crop-tool-btn.active { background: #2563eb; color: #fff; border-color: #2563eb; }
      #${CROP_MODAL_ID} .crop-stage {
        flex: 1; min-height: 260px; max-height: 54vh; background: #0f172a;
        display: flex; align-items: center; justify-content: center;
        padding: 12px; overflow: hidden; position: relative;
      }
      #${CROP_MODAL_ID} canvas {
        max-width: 100%; max-height: 100%; display: block;
        touch-action: none; user-select: none; cursor: crosshair;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
      }
      #${CROP_MODAL_ID} .crop-foot {
        padding: 12px 16px; background: #fff; border-top: 1px solid #e2e8f0;
        display: flex; flex-wrap: wrap; gap: 8px; align-items: center; justify-content: space-between;
      }
      #${CROP_MODAL_ID} .crop-dim {
        font-size: 12px; color: #475569; font-weight: 700;
        background: #f1f5f9; padding: 4px 10px; border-radius: 6px;
      }
      #${CROP_MODAL_ID} .crop-primary {
        background: #16a34a; color: #fff; border: none; padding: 9px 18px;
        border-radius: 8px; font-family: inherit; font-size: 13px; font-weight: 800; cursor: pointer;
      }
      #${CROP_MODAL_ID} .crop-secondary {
        background: #2563eb; color: #fff; border: none; padding: 9px 14px;
        border-radius: 8px; font-family: inherit; font-size: 13px; font-weight: 700; cursor: pointer;
      }
      #${CROP_MODAL_ID} .crop-skip {
        background: #64748b; color: #fff; border: none; padding: 9px 14px;
        border-radius: 8px; font-family: inherit; font-size: 13px; font-weight: 700; cursor: pointer;
      }
      @media print {
        #${CROP_MODAL_ID} { display: none !important; }
      }
    `;
    document.head.appendChild(style);

    const modal = document.createElement('div');
    modal.id = CROP_MODAL_ID;
    modal.innerHTML = `
      <div class="crop-card" onclick="event.stopPropagation()">
        <div class="crop-head">
          <h4 id="eduCropTitle">✂️ اقتصاص الصورة قبل الرفع</h4>
          <button type="button" class="crop-close" id="eduCropCancelTopBtn" title="إلغاء">✕</button>
        </div>
        <div class="crop-tools">
          <div class="crop-btn-row">
            <span style="font-size:12px;color:#475569;font-weight:700;">النسبة:</span>
            <button type="button" class="crop-tool-btn active" data-crop-aspect="0">حر</button>
            <button type="button" class="crop-tool-btn" data-crop-aspect="1">مربع 1:1</button>
            <button type="button" class="crop-tool-btn" data-crop-aspect="1.3333">أفقي 4:3</button>
            <button type="button" class="crop-tool-btn" data-crop-aspect="1.7777">عريض 16:9</button>
            <button type="button" class="crop-tool-btn" data-crop-aspect="0.75">عمودي 3:4</button>
          </div>
          <div class="crop-btn-row">
            <button type="button" class="crop-tool-btn" id="eduCropRotLeftBtn">↺ تدوير يسار</button>
            <button type="button" class="crop-tool-btn" id="eduCropRotRightBtn">↻ تدوير يمين</button>
            <button type="button" class="crop-tool-btn" id="eduCropSelectAllBtn">⛶ تحديد الكل</button>
          </div>
        </div>
        <div class="crop-stage" id="eduCropStage">
          <canvas id="eduCropCanvas"></canvas>
        </div>
        <div class="crop-foot">
          <span class="crop-dim" id="eduCropDimInfo">اسحب الزوايا لتحديد الجزء المطلوب</span>
          <div class="crop-btn-row">
            <button type="button" class="crop-primary" id="eduCropApplyBtn">✂️ قص واعتماد الجزء المحدد</button>
            <button type="button" class="crop-secondary" id="eduCropFullBtn">🖼️ رفع كاملة بدون قص</button>
            <button type="button" class="crop-skip" id="eduCropSkipBtn">تخطي</button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    modal.querySelector('#eduCropCancelTopBtn').onclick = cancelAll;
    modal.querySelector('#eduCropSkipBtn').onclick = skipCurrent;
    modal.querySelector('#eduCropFullBtn').onclick = acceptFullImage;
    modal.querySelector('#eduCropApplyBtn').onclick = acceptCroppedImage;
    modal.querySelector('#eduCropRotLeftBtn').onclick = () => rotateBy(-90);
    modal.querySelector('#eduCropRotRightBtn').onclick = () => rotateBy(90);
    modal.querySelector('#eduCropSelectAllBtn').onclick = resetCropFull;

    modal.querySelectorAll('[data-crop-aspect]').forEach(btn => {
      btn.onclick = () => {
        modal.querySelectorAll('[data-crop-aspect]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.aspect = parseFloat(btn.dataset.cropAspect) || 0;
        applyAspectToCrop();
        renderCanvas();
      };
    });

    const canvas = modal.querySelector('#eduCropCanvas');
    canvas.addEventListener('pointerdown', onPointerDown);
    window.addEventListener('pointermove', onPointerMove);
    window.addEventListener('pointerup', onPointerUp);
  }

  function getRotatedDimensions() {
    if (!state.img) return { w: 1, h: 1 };
    const rot = ((state.rotation % 360) + 360) % 360;
    if (rot === 90 || rot === 270) {
      return { w: state.img.naturalHeight || state.img.height, h: state.img.naturalWidth || state.img.width };
    }
    return { w: state.img.naturalWidth || state.img.width, h: state.img.naturalHeight || state.img.height };
  }

  function setupCanvasForImage() {
    const stage = document.getElementById('eduCropStage');
    const canvas = document.getElementById('eduCropCanvas');
    if (!stage || !canvas || !state.img) return;
    const maxW = Math.max(260, stage.clientWidth - 24);
    const maxH = Math.max(220, Math.min(460, window.innerHeight * 0.50));
    const nat = getRotatedDimensions();
    const scale = Math.min(maxW / nat.w, maxH / nat.h, 1.5);
    state.drawW = Math.max(120, Math.round(nat.w * scale));
    state.drawH = Math.max(120, Math.round(nat.h * scale));
    canvas.width = state.drawW;
    canvas.height = state.drawH;
    // تحديد مبدئي 84% في المنتصف لتسهيل القص فوراً أو تعديل الزوايا
    const padX = Math.round(state.drawW * 0.08);
    const padY = Math.round(state.drawH * 0.08);
    state.crop = {
      x: padX,
      y: padY,
      w: Math.max(40, state.drawW - padX * 2),
      h: Math.max(40, state.drawH - padY * 2),
    };
    if (state.aspect > 0) applyAspectToCrop();
    renderCanvas();
  }

  function resetCropFull() {
    state.crop = { x: 0, y: 0, w: state.drawW, h: state.drawH };
    if (state.aspect > 0) applyAspectToCrop();
    renderCanvas();
  }

  function applyAspectToCrop() {
    if (!state.aspect || !state.drawW || !state.drawH) return;
    const cx = state.crop.x + state.crop.w / 2;
    const cy = state.crop.y + state.crop.h / 2;
    let w = state.crop.w;
    let h = w / state.aspect;
    if (h > state.drawH) {
      h = state.drawH * 0.9;
      w = h * state.aspect;
    }
    if (w > state.drawW) {
      w = state.drawW * 0.9;
      h = w / state.aspect;
    }
    let x = Math.max(0, Math.min(state.drawW - w, cx - w / 2));
    let y = Math.max(0, Math.min(state.drawH - h, cy - h / 2));
    state.crop = { x: Math.round(x), y: Math.round(y), w: Math.round(w), h: Math.round(h) };
  }

  function rotateBy(deg) {
    state.rotation = (((state.rotation + deg) % 360) + 360) % 360;
    setupCanvasForImage();
  }

  function drawRotatedImage(ctx, targetW, targetH) {
    const rot = ((state.rotation % 360) + 360) % 360;
    ctx.save();
    ctx.translate(targetW / 2, targetH / 2);
    ctx.rotate((rot * Math.PI) / 180);
    if (rot === 90 || rot === 270) {
      ctx.drawImage(state.img, -targetH / 2, -targetW / 2, targetH, targetW);
    } else {
      ctx.drawImage(state.img, -targetW / 2, -targetH / 2, targetW, targetH);
    }
    ctx.restore();
  }

  function renderCanvas() {
    const canvas = document.getElementById('eduCropCanvas');
    if (!canvas || !state.img) return;
    const ctx = canvas.getContext('2d');
    const { drawW, drawH, crop } = state;
    ctx.clearRect(0, 0, drawW, drawH);
    drawRotatedImage(ctx, drawW, drawH);

    // تغميق المناطق خارج التحديد
    ctx.fillStyle = 'rgba(15, 23, 42, 0.58)';
    ctx.fillRect(0, 0, drawW, crop.y);
    ctx.fillRect(0, crop.y + crop.h, drawW, drawH - (crop.y + crop.h));
    ctx.fillRect(0, crop.y, crop.x, crop.h);
    ctx.fillRect(crop.x + crop.w, crop.y, drawW - (crop.x + crop.w), crop.h);

    // حدود منطقة القص
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.strokeRect(crop.x + 1, crop.y + 1, Math.max(1, crop.w - 2), Math.max(1, crop.h - 2));

    // خطوط التثليث الإرشادية
    ctx.strokeStyle = 'rgba(255,255,255,0.4)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(crop.x + crop.w / 3, crop.y);
    ctx.lineTo(crop.x + crop.w / 3, crop.y + crop.h);
    ctx.moveTo(crop.x + (2 * crop.w) / 3, crop.y);
    ctx.lineTo(crop.x + (2 * crop.w) / 3, crop.y + crop.h);
    ctx.moveTo(crop.x, crop.y + crop.h / 3);
    ctx.lineTo(crop.x + crop.w, crop.y + crop.h / 3);
    ctx.moveTo(crop.x, crop.y + (2 * crop.h) / 3);
    ctx.lineTo(crop.x + crop.w, crop.y + (2 * crop.h) / 3);
    ctx.stroke();

    // مقابض الزوايا الأربعة
    const handles = [
      [crop.x, crop.y],
      [crop.x + crop.w, crop.y],
      [crop.x, crop.y + crop.h],
      [crop.x + crop.w, crop.y + crop.h],
    ];
    handles.forEach(([hx, hy]) => {
      ctx.fillStyle = '#38bdf8';
      ctx.strokeStyle = '#0f172a';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(hx, hy, 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    });

    const nat = getRotatedDimensions();
    const realW = Math.round((crop.w / drawW) * nat.w);
    const realH = Math.round((crop.h / drawH) * nat.h);
    const infoEl = document.getElementById('eduCropDimInfo');
    if (infoEl) infoEl.textContent = `الجزء المحدد: ${realW} × ${realH} بكسل`;
  }

  function getCanvasCoords(e) {
    const canvas = document.getElementById('eduCropCanvas');
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / Math.max(1, rect.width);
    const scaleY = canvas.height / Math.max(1, rect.height);
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
    };
  }

  function hitTest(pt) {
    const { x, y, w, h } = state.crop;
    const r = 22;
    if (Math.hypot(pt.x - x, pt.y - y) <= r) return 'nw';
    if (Math.hypot(pt.x - (x + w), pt.y - y) <= r) return 'ne';
    if (Math.hypot(pt.x - x, pt.y - (y + h)) <= r) return 'sw';
    if (Math.hypot(pt.x - (x + w), pt.y - (y + h)) <= r) return 'se';
    if (pt.x >= x && pt.x <= x + w && pt.y >= y && pt.y <= y + h) return 'move';
    return 'new';
  }

  function onPointerDown(e) {
    if (!state.img) return;
    e.preventDefault();
    const canvas = document.getElementById('eduCropCanvas');
    if (canvas && canvas.setPointerCapture) {
      try { canvas.setPointerCapture(e.pointerId); } catch (_) {}
    }
    const pt = getCanvasCoords(e);
    state.dragMode = hitTest(pt);
    state.dragStart = pt;
    state.cropStart = { ...state.crop };
    if (state.dragMode === 'new') {
      state.crop = { x: Math.max(0, Math.min(state.drawW, pt.x)), y: Math.max(0, Math.min(state.drawH, pt.y)), w: 12, h: 12 };
      state.dragMode = 'se';
      state.cropStart = { ...state.crop };
    }
  }

  function onPointerMove(e) {
    if (!state.dragMode || !state.img) return;
    const pt = getCanvasCoords(e);
    const dx = pt.x - state.dragStart.x;
    const dy = pt.y - state.dragStart.y;
    const cs = state.cropStart;
    const minSz = 24;
    let { x, y, w, h } = cs;

    if (state.dragMode === 'move') {
      x = Math.max(0, Math.min(state.drawW - cs.w, cs.x + dx));
      y = Math.max(0, Math.min(state.drawH - cs.h, cs.y + dy));
    } else {
      let x1 = cs.x;
      let y1 = cs.y;
      let x2 = cs.x + cs.w;
      let y2 = cs.y + cs.h;

      if (state.dragMode === 'nw') { x1 = Math.min(x2 - minSz, Math.max(0, pt.x)); y1 = Math.min(y2 - minSz, Math.max(0, pt.y)); }
      if (state.dragMode === 'ne') { x2 = Math.max(x1 + minSz, Math.min(state.drawW, pt.x)); y1 = Math.min(y2 - minSz, Math.max(0, pt.y)); }
      if (state.dragMode === 'sw') { x1 = Math.min(x2 - minSz, Math.max(0, pt.x)); y2 = Math.max(y1 + minSz, Math.min(state.drawH, pt.y)); }
      if (state.dragMode === 'se') { x2 = Math.max(x1 + minSz, Math.min(state.drawW, pt.x)); y2 = Math.max(y1 + minSz, Math.min(state.drawH, pt.y)); }

      w = x2 - x1;
      h = y2 - y1;
      if (state.aspect > 0) {
        h = w / state.aspect;
        if (state.dragMode === 'nw' || state.dragMode === 'ne') {
          y1 = y2 - h;
          if (y1 < 0) { y1 = 0; h = y2; w = h * state.aspect; }
        } else {
          if (y1 + h > state.drawH) { h = state.drawH - y1; w = h * state.aspect; }
        }
        if (state.dragMode === 'nw' || state.dragMode === 'sw') {
          x1 = x2 - w;
          if (x1 < 0) { x1 = 0; w = x2; h = w / state.aspect; }
        } else {
          if (x1 + w > state.drawW) { w = state.drawW - x1; h = w / state.aspect; }
        }
      }
      x = x1;
      y = y1;
    }

    state.crop = { x: Math.round(x), y: Math.round(y), w: Math.round(w), h: Math.round(h) };
    renderCanvas();
  }

  function onPointerUp() {
    state.dragMode = null;
  }

  function exportImage({ full = false } = {}) {
    if (!state.img) return '';
    const nat = getRotatedDimensions();
    // رسم الصورة المدورة بالكامل أولاً بدقتها الأصلية (محدودة بحد أقصى آمن)
    const maxSrc = 1800;
    const srcScale = Math.min(1, maxSrc / Math.max(nat.w, nat.h));
    const fullW = Math.round(nat.w * srcScale);
    const fullH = Math.round(nat.h * srcScale);

    const fullCanvas = document.createElement('canvas');
    fullCanvas.width = fullW;
    fullCanvas.height = fullH;
    const fCtx = fullCanvas.getContext('2d');
    fCtx.fillStyle = '#ffffff';
    fCtx.fillRect(0, 0, fullW, fullH);
    drawRotatedImage(fCtx, fullW, fullH);

    if (full) {
      return fullCanvas.toDataURL('image/jpeg', 0.90);
    }

    const sx = Math.max(0, Math.round((state.crop.x / state.drawW) * fullW));
    const sy = Math.max(0, Math.round((state.crop.y / state.drawH) * fullH));
    const sw = Math.max(10, Math.min(fullW - sx, Math.round((state.crop.w / state.drawW) * fullW)));
    const sh = Math.max(10, Math.min(fullH - sy, Math.round((state.crop.h / state.drawH) * fullH)));

    const maxOut = 1400;
    const outScale = Math.min(1, maxOut / Math.max(sw, sh));
    const outW = Math.max(1, Math.round(sw * outScale));
    const outH = Math.max(1, Math.round(sh * outScale));

    const outCanvas = document.createElement('canvas');
    outCanvas.width = outW;
    outCanvas.height = outH;
    const oCtx = outCanvas.getContext('2d');
    oCtx.fillStyle = '#ffffff';
    oCtx.fillRect(0, 0, outW, outH);
    oCtx.drawImage(fullCanvas, sx, sy, sw, sh, 0, 0, outW, outH);
    return outCanvas.toDataURL('image/jpeg', 0.90);
  }

  function loadCurrentItem() {
    if (state.index >= state.queue.length) {
      closeModal();
      return;
    }
    const item = state.queue[state.index];
    const titleEl = document.getElementById('eduCropTitle');
    if (titleEl) {
      titleEl.textContent = state.isSingleMode
        ? '✂️ تعديل واقتصاص الصورة'
        : `✂️ اقتصاص الصورة (${state.index + 1} من ${state.queue.length})`;
    }
    const skipBtn = document.getElementById('eduCropSkipBtn');
    if (skipBtn) skipBtn.textContent = state.queue.length > 1 ? '⏭️ تخطي هذه الصورة' : 'إلغاء';

    const img = new Image();
    img.onload = () => {
      state.img = img;
      state.rotation = 0;
      state.aspect = 0;
      const modal = document.getElementById(CROP_MODAL_ID);
      if (modal) {
        modal.querySelectorAll('[data-crop-aspect]').forEach(b => b.classList.toggle('active', b.dataset.cropAspect === '0'));
        modal.classList.add('show');
      }
      requestAnimationFrame(() => setupCanvasForImage());
    };
    img.onerror = () => skipCurrent();
    img.src = item;
  }

  function advanceNext() {
    state.index += 1;
    if (state.index < state.queue.length) {
      loadCurrentItem();
    } else {
      closeModal();
    }
  }

  function acceptCroppedImage() {
    const url = exportImage({ full: false });
    if (url && typeof state.onDone === 'function') state.onDone(url);
    advanceNext();
  }

  function acceptFullImage() {
    const url = exportImage({ full: true });
    if (url && typeof state.onDone === 'function') state.onDone(url);
    advanceNext();
  }

  function skipCurrent() {
    advanceNext();
  }

  function cancelAll() {
    closeModal();
  }

  function closeModal() {
    const modal = document.getElementById(CROP_MODAL_ID);
    if (modal) modal.classList.remove('show');
    state.queue = [];
    state.img = null;
    state.onDone = null;
  }

  function openQueue(filesOrDataUrls, onEachAccepted) {
    injectStylesAndDom();
    const list = Array.from(filesOrDataUrls || []);
    if (!list.length) return;
    Promise.all(
      list.map(item => {
        if (typeof item === 'string') return Promise.resolve(item);
        return new Promise(resolve => {
          const reader = new FileReader();
          reader.onload = e => resolve(e.target.result || '');
          reader.onerror = () => resolve('');
          reader.readAsDataURL(item);
        });
      })
    ).then(urls => {
      const valid = urls.filter(Boolean);
      if (!valid.length) return;
      state.queue = valid;
      state.index = 0;
      state.onDone = onEachAccepted;
      state.isSingleMode = false;
      loadCurrentItem();
    });
  }

  function cropExisting(dataUrl, onCropped) {
    injectStylesAndDom();
    if (!dataUrl) return;
    state.queue = [dataUrl];
    state.index = 0;
    state.onDone = onCropped;
    state.isSingleMode = true;
    loadCurrentItem();
  }

  global.EduImageCropper = {
    openQueue,
    cropExisting,
  };
})(window);
