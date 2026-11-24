/* استوديو قوالب كانفا الداخلي للخدمات التعليمية: جلب وتحديد ومعاينة وتطبيق وطباعة داخل واجهة الوظيفة */
(function (global) {
  'use strict';

  const MODAL_ID = 'eduCanvaStudioInline';
  const PRINT_ROOT_ID = 'eduCanvaPrintRoot';
  let initialized = false;
  let currentMode = 'portfolio'; // 'portfolio' | 'witnesses' | 'reports'
  let catalogTemplates = [];
  let fetchedTemplates = [];
  let selectedIds = new Set();
  let appliedPreviews = []; // [{ template, pagesHtml }]
  let activeAppliedId = '';
  let activeCategory = 'all';
  let activeTab = 'browse'; // 'browse' | 'fetched' | 'preview'
  let previewZoom = 'fit';
  let isExportingCanvaPdf = false;
  let isLivePreviewUnsaved = false;

  const TARGET_LABELS = {
    portfolio: 'ملف الأداء الوظيفي',
    witnesses: 'ملف شواهد الأداء',
    reports: 'ملف التقارير والبرامج التربوية والأنشطة المدرسية',
  };

  function detectPageMode() {
    const p = (window.location && window.location.pathname) || '';
    if (p.includes('performance_portfolio')) return 'portfolio';
    if (p.includes('performance_witnesses')) return 'witnesses';
    if (p.includes('school_reports')) return 'reports';
    return null;
  }

  function escHtml(str) {
    return String(str == null ? '' : str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function safeHex(val, fallback) {
    const s = String(val || '').trim();
    return /^#[0-9a-fA-F]{3,8}$/.test(s) ? s : fallback;
  }

  function getFallbackImageSrc(tpl) {
    return (tpl && tpl.fallback_preview_data_url) || '';
  }

  function isRealRasterUrl(u) {
    return typeof u === 'string' && /^data:image\/(jpeg|jpg|png|webp|gif)/i.test(u);
  }

  function getSafeImageSrc(tpl) {
    if (!tpl) return '';
    if (isRealRasterUrl(tpl.safe_preview_data_url)) return tpl.safe_preview_data_url;
    if (tpl.preview_image && /^https?:\/\//i.test(tpl.preview_image)) {
      return '/api/edu/canva/proxy_img?url=' + encodeURIComponent(tpl.preview_image);
    }
    return tpl.fallback_preview_data_url || tpl.safe_preview_data_url || '';
  }

  function ensureStylesInjected() {
    if (document.getElementById('eduCanvaStudioStyles')) return;
    const style = document.createElement('style');
    style.id = 'eduCanvaStudioStyles';
    style.textContent = `
      #ecsInlineDock {
        width: 100%; max-width: 1200px; margin: 0 auto; padding: 0 12px;
        direction: rtl; font-family: 'Cairo', sans-serif; box-sizing: border-box;
      }
      #ecsInlineDock.has-content.dock-below-fixed {
        margin-top: 72px; margin-bottom: -48px;
      }
      #ecsInlineDock.has-content.dock-reports {
        margin-top: 4px; margin-bottom: 14px;
      }
      #${MODAL_ID} {
        display: none; width: 100%; margin: 10px auto 14px auto;
        direction: rtl; font-family: 'Cairo', sans-serif; z-index: 50; position: relative;
      }
      #${MODAL_ID}.show { display: block; }
      @media print {
        #ecsInlineDock, #${MODAL_ID}, #ecsMergedStatusBanner { display: none !important; }
      }
      body.pdf-exporting #ecsInlineDock,
      body.print-preview-mode #ecsInlineDock,
      body.pdf-exporting #${MODAL_ID},
      body.print-preview-mode #${MODAL_ID},
      body.pdf-exporting #ecsMergedStatusBanner,
      body.print-preview-mode #ecsMergedStatusBanner {
        display: none !important;
      }
      #${MODAL_ID} .ecs-shell {
        background: #f8fafc; border-radius: 16px; width: 100%;
        display: flex; flex-direction: column; overflow: hidden;
        border: 2px solid #0f766e; box-shadow: 0 10px 28px rgba(15, 23, 42, 0.14);
      }
      #${MODAL_ID} .ecs-header {
        background: linear-gradient(135deg, #0f766e, #1e3a8a); color: #fff;
        padding: 11px 16px; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px;
      }
      #${MODAL_ID} .ecs-title { font-size: 15.5px; font-weight: 900; display: flex; align-items: center; gap: 8px; }
      #${MODAL_ID} .ecs-tabs { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
      #${MODAL_ID} .ecs-tab-btn {
        background: rgba(255,255,255,0.16); color: #fff; border: 1px solid rgba(255,255,255,0.28);
        padding: 6px 13px; border-radius: 8px; font-family: inherit; font-size: 13px; font-weight: 700; cursor: pointer;
      }
      #${MODAL_ID} .ecs-tab-btn.active { background: #ffffff; color: #0f172a; }
      #${MODAL_ID} .ecs-close-btn {
        background: rgba(239,68,68,0.92); color: #fff; border: none; padding: 6px 12px;
        border-radius: 8px; font-size: 12.5px; font-weight: 800; cursor: pointer; font-family: inherit;
      }
      #${MODAL_ID} .ecs-status {
        background: #e0f2fe; color: #0c4a6e; padding: 7px 16px; font-size: 13px; font-weight: 700;
        border-bottom: 1px solid #bae6fd; display: none;
      }
      #${MODAL_ID} .ecs-status.show { display: block; }
      #${MODAL_ID} .ecs-body { max-height: 74vh; overflow-y: auto; padding: 14px; }
      #${MODAL_ID} .ecs-panel { display: none; }
      #${MODAL_ID} .ecs-panel.active { display: block; }
      #${MODAL_ID} .ecs-bar {
        background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
        padding: 12px; margin-bottom: 14px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
      }
      #${MODAL_ID} .ecs-input {
        flex: 1; min-width: 190px; padding: 8px 12px; border: 1.5px solid #cbd5e1;
        border-radius: 8px; font-family: inherit; font-size: 13px; font-weight: 700;
      }
      #${MODAL_ID} .ecs-btn {
        background: #1e3a8a; color: #fff; border: none; padding: 8px 14px;
        border-radius: 8px; font-family: inherit; font-size: 13px; font-weight: 700; cursor: pointer;
        display: inline-flex; align-items: center; gap: 5px;
      }
      #${MODAL_ID} .ecs-btn:hover { opacity: 0.92; }
      #${MODAL_ID} .ecs-btn.teal { background: #0f766e; }
      #${MODAL_ID} .ecs-btn.amber { background: #d97706; }
      #${MODAL_ID} .ecs-btn.green { background: #16a34a; }
      #${MODAL_ID} .ecs-btn.gray { background: #475569; }
      #${MODAL_ID} .ecs-btn.outline { background: #fff; color: #334155; border: 1.5px solid #cbd5e1; }
      #${MODAL_ID} .ecs-btn.outline.active { background: #1e3a8a; color: #fff; border-color: #1e3a8a; }
      #${MODAL_ID} .ecs-cats { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
      #${MODAL_ID} .ecs-grid {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 14px;
      }
      #${MODAL_ID} .ecs-card {
        background: #fff; border: 2px solid #e2e8f0; border-radius: 12px; overflow: hidden;
        display: flex; flex-direction: column; transition: 0.15s; box-shadow: 0 3px 10px rgba(0,0,0,0.05);
      }
      #${MODAL_ID} .ecs-card.selected { border-color: #0f766e; box-shadow: 0 0 0 3px rgba(15,118,110,0.18); }
      #${MODAL_ID} .ecs-card-art {
        height: 175px; position: relative; padding: 0; display: flex; flex-direction: column;
        justify-content: space-between; cursor: pointer; overflow: hidden; border-bottom: 1px solid #e2e8f0;
      }
      #${MODAL_ID} .ecs-card-body { padding: 11px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; gap: 8px; }
      #${MODAL_ID} .ecs-check-row {
        display: flex; align-items: center; justify-content: space-between; gap: 6px;
        padding-top: 8px; border-top: 1px dashed #e2e8f0;
      }
      #${MODAL_ID} .ecs-check-label {
        display: inline-flex; align-items: center; gap: 6px; cursor: pointer;
        font-size: 13px; font-weight: 800; color: #0f172a;
      }
      #${MODAL_ID} .ecs-check-label input { width: 18px; height: 18px; accent-color: #0f766e; cursor: pointer; }
      #${MODAL_ID} .ecs-preview-stage {
        background: #475569; border-radius: 12px; padding: 18px 10px; min-height: 420px;
        overflow: auto; display: flex; flex-direction: column; align-items: center; gap: 18px;
      }
      #${MODAL_ID} .ecs-applied-bar {
        display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 12px;
        background: #fff; padding: 10px 12px; border-radius: 12px; border: 1px solid #cbd5e1;
      }

      /* صفحات المعاينة والطباعة لقوالب كانفا (A4 دقيق 794px) */
      .canva-a4-sheet {
        width: 794px; min-width: 794px; max-width: 794px; min-height: 1123px;
        background: var(--c-bg, #ffffff); color: var(--c-text, #0f172a);
        position: relative; box-sizing: border-box; overflow: hidden;
        padding: 36px 40px; display: flex; flex-direction: column; gap: 14px;
        box-shadow: 0 12px 32px rgba(0,0,0,0.35);
        page-break-after: always; break-after: page;
        font-family: 'Cairo', sans-serif; direction: rtl; text-align: right;
      }
      .canva-a4-sheet.layout-royal_double::before {
        content: ''; position: absolute; inset: 14px;
        border: 3px solid var(--c-primary, #1e3a8a);
        outline: 1.5px solid var(--c-accent, #d97706); outline-offset: -7px;
        pointer-events: none; z-index: 1;
      }
      .canva-a4-sheet.layout-botanical_frame::before {
        content: ''; position: absolute; inset: 16px;
        border: 2px solid var(--c-primary, #6d5ca0); border-radius: 22px;
        box-shadow: inset 0 0 0 5px rgba(201,168,106,0.14);
        pointer-events: none; z-index: 1;
      }
      .canva-a4-sheet.layout-clean_stripe::after {
        content: ''; position: absolute; top: 0; right: 0; bottom: 0; width: 14px;
        background: linear-gradient(180deg, var(--c-primary), var(--c-accent));
      }
      .canva-a4-sheet.layout-gradient_arch::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 22px;
        background: linear-gradient(135deg, var(--c-primary), var(--c-secondary));
        border-bottom: 4px solid var(--c-accent); pointer-events: none; z-index: 1;
      }
      .canva-a4-sheet.layout-pastel_card {
        background-image: radial-gradient(circle at top left, rgba(224,159,151,0.14), transparent 42%);
      }
      .canva-a4-sheet.layout-pastel_card::before {
        content: ''; position: absolute; inset: 15px; border: 2px dashed var(--c-accent);
        border-radius: 18px; pointer-events: none; z-index: 1;
      }
      .canva-a4-sheet.layout-geometric_split::before {
        content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 14px;
        background: repeating-linear-gradient(-45deg, var(--c-primary) 0 18px, var(--c-accent) 18px 30px, var(--c-secondary) 30px 46px);
        pointer-events: none; z-index: 1;
      }
      .canva-a4-sheet.layout-modern_ribbon::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 10px;
        background: var(--c-accent);
      }
      .canva-a4-sheet.layout-modern_ribbon::after {
        content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 10px;
        background: linear-gradient(90deg, var(--c-primary), var(--c-secondary));
      }
      .canva-a4-sheet > * { position: relative; z-index: 2; }
      .canva-cover-hero {
        flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center; padding: 30px 26px; border-radius: 16px;
        background: var(--c-card, #ffffff); border: 2px solid var(--c-accent, #c9a86a);
      }
      .canva-cover-banner {
        width: 100%; padding: 26px 22px; border-radius: 14px; color: #fff; margin-bottom: 22px;
        background: linear-gradient(135deg, var(--c-primary), var(--c-secondary));
        border-bottom: 5px solid var(--c-accent);
      }
      .canva-page-banner {
        background: linear-gradient(135deg, var(--c-primary), var(--c-secondary));
        color: #fff; padding: 13px 20px; border-radius: 12px;
        display: flex; align-items: center; justify-content: space-between; gap: 10px;
        border-right: 7px solid var(--c-accent);
      }
      .canva-page-banner h2 {
        margin: 0; font-size: 20px; font-weight: 800; color: #fff;
        font-family: 'Amiri', 'Cairo', serif;
      }
      .canva-card-box {
        background: var(--c-card, #fff); border: 1.5px solid rgba(15,23,42,0.12);
        border-right: 5px solid var(--c-primary); border-radius: 10px; padding: 14px 18px;
      }
      .canva-table {
        width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden;
      }
      .canva-table th {
        background: var(--c-primary); color: #fff; padding: 10px 12px;
        font-size: 14px; font-weight: 700; text-align: center; border: 1px solid rgba(255,255,255,0.2);
      }
      .canva-table td {
        padding: 9px 11px; border: 1px solid #cbd5e1; font-size: 13.5px; font-weight: 700;
        color: var(--c-text, #0f172a); vertical-align: top;
      }
      .canva-table tr:nth-child(even) td { background: rgba(15,23,42,0.025); }
      .canva-list { list-style: none; margin: 6px 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
      .canva-list li {
        background: #fff; padding: 8px 12px; border-radius: 7px;
        border-right: 4px solid var(--c-accent); font-size: 13.5px; font-weight: 700;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      }
      .canva-subhead {
        background: rgba(15,23,42,0.05); color: var(--c-primary);
        border-right: 5px solid var(--c-primary); padding: 7px 14px;
        border-radius: 6px; font-size: 15px; font-weight: 800; margin-top: 6px;
      }
      .canva-sig-row {
        display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: auto; padding-top: 14px;
      }
      .canva-sig-box {
        background: #fff; border: 1.5px solid var(--c-accent); border-radius: 10px;
        padding: 12px; text-align: center; font-size: 13px; font-weight: 700;
      }
      .canva-sheet-foot {
        margin-top: auto; padding-top: 8px; border-top: 1px dashed rgba(15,23,42,0.18);
        display: flex; justify-content: space-between; font-size: 11px; color: #64748b; font-weight: 700;
      }

      /* حاوية الطباعة المستقلة لقالب كانفا */
      #${PRINT_ROOT_ID} { display: none; }
      body.printing-canva-preview > *:not(#${PRINT_ROOT_ID}) { display: none !important; }
      body.printing-canva-preview #${PRINT_ROOT_ID} { display: block !important; width: 210mm; margin: 0 auto; background: #fff; }
      @media print {
        body.printing-canva-preview > *:not(#${PRINT_ROOT_ID}) { display: none !important; }
        body.printing-canva-preview #${PRINT_ROOT_ID} { display: block !important; width: 210mm !important; }
        body.printing-canva-preview .canva-a4-sheet {
          width: 210mm !important; min-width: 210mm !important; max-width: 210mm !important;
          min-height: 297mm !important; height: auto !important;
          box-shadow: none !important; margin: 0 !important; transform: none !important;
          page-break-after: always; break-after: page; overflow: visible !important;
        }
      }
      @media (max-width: 720px) {
        #${MODAL_ID} .ecs-header { padding: 10px 12px; }
        #${MODAL_ID} .ecs-title { font-size: 14px; }
        #ecsViewerBody { grid-template-columns: 1fr !important; }
      }
    `;
    document.head.appendChild(style);
  }

  function injectStylesAndModal() {
    if (initialized) return;
    initialized = true;
    ensureStylesInjected();

    const modal = document.createElement('div');
    modal.id = MODAL_ID;
    modal.className = 'no-print edit-only';
    const modeLabel = TARGET_LABELS[detectPageMode() || currentMode] || 'الملف الحالي';
    modal.innerHTML = `
      <div class="ecs-shell" onclick="event.stopPropagation()">
        <div class="ecs-header">
          <div class="ecs-title">🎨 قوالب كانفا داخل واجهة: ${escHtml(modeLabel)}</div>
          <div class="ecs-tabs">
            <button type="button" class="ecs-tab-btn active" data-ecs-tab="browse">1. جلب واستعراض قوالب كانفا</button>
            <button type="button" class="ecs-tab-btn" data-ecs-tab="fetched">2. القوالب المجلوبة (<span id="ecsFetchedBadge">0</span>)</button>
            <button type="button" class="ecs-tab-btn" data-ecs-tab="preview">3. معاينة التطبيق والدمج A4 (<span id="ecsPreviewBadge">0</span>)</button>
          </div>
          <button type="button" class="ecs-close-btn" id="ecsCloseBtn" title="طي وإخفاء لوحة كانفا">▲ إخفاء</button>
        </div>
        <div class="ecs-status" id="ecsStatusBar"></div>
        <div class="ecs-body">
          <!-- عارض كانفا الداخلي لفتح القالب واستعراضه داخل واجهة الوظيفة -->
          <div id="ecsInternalViewer" style="display:none;background:#ffffff;border:2px solid #0f766e;border-radius:14px;padding:14px;margin-bottom:14px;box-shadow:0 12px 30px rgba(15,118,110,0.16);">
            <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;padding-bottom:10px;border-bottom:1px solid #e2e8f0;margin-bottom:12px;">
              <div>
                <div id="ecsViewerTitle" style="font-size:15px;font-weight:900;color:#0f172a;">عرض القالب داخل بوابة كانفا</div>
                <div id="ecsViewerSub" style="font-size:12px;color:#475569;font-weight:700;"></div>
              </div>
              <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;">
                <button type="button" class="ecs-btn outline" id="ecsViewerSelectBtn">☑️ تحديد للجلب</button>
                <button type="button" class="ecs-btn green" id="ecsViewerFetchApplyBtn">⚡ جلب وتطبيق محتواي الآن</button>
                <button type="button" class="ecs-btn gray" id="ecsViewerCloseBtn">إغلاق العارض</button>
              </div>
            </div>
            <div id="ecsViewerBody" style="display:grid;grid-template-columns:minmax(260px,1fr) minmax(260px,1fr);gap:14px;align-items:start;"></div>
          </div>

          <!-- التبويب 1: متصفح كانفا الداخلي + التحديد -->
          <div class="ecs-panel active" id="ecsPanelBrowse">
            <div class="ecs-bar">
              <input type="text" class="ecs-input" id="ecsSearchInput" placeholder="ابحث عن قالب كانفا (مثال: تقارير مدرسية، شهادات، ملف أداء، شواهد، وردي، أزرق)...">
              <button type="button" class="ecs-btn teal" id="ecsFetchLiveBtn">🔄 جلب قوالب من كانفا</button>
              <button type="button" class="ecs-btn outline" id="ecsToggleLinkImportBtn">🔗 استيراد رابط / ملف / Token كانفا</button>
            </div>

            <div id="ecsLinkImportBox" class="ecs-bar" style="display:none;flex-direction:column;align-items:stretch;background:#f0fdfa;border-color:#99f6e4;">
              <div style="font-size:13px;font-weight:800;color:#0f766e;">استيراد قوالب مباشرة من روابط كانفا أو ملف مصدّر من كانفا أو حسابك (داخل واجهة الوظيفة بالكامل):</div>
              <textarea id="ecsUrlsInput" rows="2" class="ecs-input" dir="ltr" placeholder="الصق رابط قالب/تصميم كانفا هنا (مثل https://www.canva.com/templates/... أو /design/.../view)..."></textarea>
              <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
                <input type="text" id="ecsUrlNameInput" class="ecs-input" style="max-width:210px;" placeholder="اسم القالب (اختياري)">
                <button type="button" class="ecs-btn teal" id="ecsImportUrlsBtn">➕ جلب الرابط وإدراجه</button>
                <input type="password" id="ecsCanvaTokenInput" class="ecs-input" dir="ltr" style="max-width:220px;" placeholder="Canva Access Token (اختياري)">
                <button type="button" class="ecs-btn" id="ecsConnectTokenBtn">🔑 جلب تصاميم حسابي</button>
              </div>
              <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding-top:6px;border-top:1px dashed #99f6e4;">
                <span style="font-size:12px;font-weight:800;color:#0f766e;">📤 أو ارفع تصميماً مصدّراً من كانفا (صورة PNG/JPG أو ملف PDF أو PPTX):</span>
                <input type="file" id="ecsFileImportInput" accept="image/*,.pptx,.pdf" style="font-size:12px;max-width:240px;">
                <button type="button" class="ecs-btn amber" id="ecsImportFileBtn">📥 معالجة واستيراد الملف كقالب</button>
              </div>
            </div>

            <div class="ecs-cats" id="ecsCatsWrap">
              <button type="button" class="ecs-btn outline active" data-ecs-cat="all">الكل</button>
              <button type="button" class="ecs-btn outline" data-ecs-cat="ملفات أداء وإنجاز">ملفات أداء وإنجاز</button>
              <button type="button" class="ecs-btn outline" data-ecs-cat="شواهد وتوثيق">شواهد وتوثيق</button>
              <button type="button" class="ecs-btn outline" data-ecs-cat="تقارير مدرسية">تقارير مدرسية</button>
              <button type="button" class="ecs-btn outline" data-ecs-cat="شهادات وتكريم">شهادات وتكريم</button>
              <button type="button" class="ecs-btn outline" data-ecs-cat="تصاميمي المجلوبة">تصاميمي المجلوبة</button>
            </div>

            <div class="ecs-bar" style="background:#eef2ff;border-color:#c7d2fe;justify-content:space-between;">
              <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
                <button type="button" class="ecs-btn outline" id="ecsSelectAllBtn">☑️ تحديد الكل</button>
                <button type="button" class="ecs-btn outline" id="ecsClearSelBtn">إلغاء التحديد</button>
                <span id="ecsSelectedCountLbl" style="font-size:13px;font-weight:900;color:#1e3a8a;">المحدد: 0 قالب</span>
              </div>
              <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
                <button type="button" class="ecs-btn teal" id="ecsFetchOnlySelectedBtn">📥 جلب المحدد لقائمة القوالب</button>
                <button type="button" class="ecs-btn green" id="ecsFetchSelectedBtn">✨ جلب المحدد وتطبيق المحتوى ومعاينته</button>
              </div>
            </div>

            <div class="ecs-grid" id="ecsBrowseGrid"></div>
          </div>

          <!-- التبويب 2: القوالب المجلوبة -->
          <div class="ecs-panel" id="ecsPanelFetched">
            <div class="ecs-bar" style="justify-content:space-between;">
              <div id="ecsDocScopeArea" style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
                <span style="font-size:13px;font-weight:800;color:#334155;">📋 المحتوى المستخرج من ملفك الحالي جاهز للتطبيق تلقائياً.</span>
              </div>
              <button type="button" class="ecs-btn green" id="ecsApplyAllFetchedBtn">✨ تطبيق المحتوى على القوالب المجلوبة وعرض المعاينة</button>
            </div>
            <div class="ecs-grid" id="ecsFetchedGrid"></div>
          </div>

          <!-- التبويب 3: المعاينة الحية والطباعة والدمج -->
          <div class="ecs-panel" id="ecsPanelPreview">
            <div class="ecs-applied-bar" id="ecsAppliedSwitcher" style="justify-content:space-between;"></div>
            <div class="ecs-bar" style="background:#ecfeff;border:1.5px solid #67e8f9;justify-content:space-between;">
              <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
                <span style="font-size:12.5px;font-weight:900;color:#0f766e;">⚙️ إعدادات المعالجة والدمج في الملف:</span>
                <select id="ecsMergeModeSelect" class="ecs-input" style="max-width:300px;min-width:210px;padding:6px 10px;">
                  <option value="dedicated_and_theme">✨ تضمين صفحات القالب المعالجة (PNG/PDF) + الألوان</option>
                  <option value="embedded_pages_only">📄 تضمين صفحات القالب المعالجة كصفحات مخصصة فقط</option>
                  <option value="background_frame">🖼️ تضمين القالب كإطار وخلفية مصممة للصفحات</option>
                  <option value="cover_replace">📑 تضمين القالب المعالج في صفحة الغلاف</option>
                </select>
                <select id="ecsEmbedPosSelect" class="ecs-input" style="max-width:220px;min-width:170px;padding:6px 10px;">
                  <option value="after_cover">📌 بعد صفحة الغلاف مباشرة</option>
                  <option value="as_cover">📌 كصفحة غلاف أولى للملف</option>
                  <option value="before_end">📌 في قسم الشواهد / نهاية الملف</option>
                </select>
              </div>
              <span style="font-size:11.5px;font-weight:700;color:#0e7490;">يتم تحويل القالب تلقائياً إلى صور A4 وملف PDF متوافق قبل التضمين</span>
            </div>
            <div class="ecs-bar" style="justify-content:space-between;background:#f1f5f9;">
              <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
                <button type="button" class="ecs-btn green" id="ecsPrintActiveBtn">🖨️ طباعة هذا القالب</button>
                <button type="button" class="ecs-btn amber" id="ecsPdfActiveBtn">📄 تصدير هذا القالب PDF</button>
                <button type="button" class="ecs-btn outline" id="ecsLivePreviewDocBtn">👁️ معاينة حية على صفحات الملف</button>
                <button type="button" class="ecs-btn teal" id="ecsApplyThemeToDocBtn">✅ معالجة (PNG/PDF) ودمج مباشر في الملف</button>
              </div>
              <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;">
                <button type="button" class="ecs-btn outline active" id="ecsZoomFitBtn">🔍 ملائمة للشاشة</button>
                <button type="button" class="ecs-btn outline" id="ecsZoomFullBtn">🔍 100% A4</button>
                <span id="ecsPreviewPageCount" style="font-size:12px;font-weight:800;color:#334155;"></span>
              </div>
            </div>
            <div class="ecs-preview-stage" id="ecsPreviewStage"></div>
          </div>
        </div>
      </div>
    `;
    const dock = getOrCreateInlineDock(detectPageMode() || currentMode);
    dock.appendChild(modal);

    let printRoot = document.getElementById(PRINT_ROOT_ID);
    if (!printRoot) {
      printRoot = document.createElement('div');
      printRoot.id = PRINT_ROOT_ID;
      document.body.appendChild(printRoot);
    }

    // ربط الأحداث
    modal.querySelector('#ecsCloseBtn').onclick = closeStudio;
    modal.querySelectorAll('[data-ecs-tab]').forEach(btn => {
      btn.onclick = () => switchTab(btn.dataset.ecsTab);
    });
    modal.querySelector('#ecsFetchLiveBtn').onclick = () => loadCatalog(true);
    modal.querySelector('#ecsSearchInput').addEventListener('keydown', e => {
      if (e.key === 'Enter') loadCatalog(true);
    });
    modal.querySelector('#ecsToggleLinkImportBtn').onclick = () => {
      const box = document.getElementById('ecsLinkImportBox');
      box.style.display = box.style.display === 'none' ? 'flex' : 'none';
    };
    modal.querySelector('#ecsImportUrlsBtn').onclick = importCanvaUrls;
    modal.querySelector('#ecsImportFileBtn').onclick = importCanvaFile;
    modal.querySelector('#ecsConnectTokenBtn').onclick = () => loadCatalog(true);

    modal.querySelectorAll('[data-ecs-cat]').forEach(btn => {
      btn.onclick = () => {
        activeCategory = btn.dataset.ecsCat;
        modal.querySelectorAll('[data-ecs-cat]').forEach(b => b.classList.toggle('active', b === btn));
        renderBrowseGrid();
      };
    });

    modal.querySelector('#ecsSelectAllBtn').onclick = () => {
      getFilteredCatalog().forEach(t => selectedIds.add(t.id));
      renderBrowseGrid();
    };
    modal.querySelector('#ecsClearSelBtn').onclick = () => {
      selectedIds.clear();
      renderBrowseGrid();
    };
    modal.querySelector('#ecsFetchSelectedBtn').onclick = () => fetchSelectedTemplates(true);
    modal.querySelector('#ecsFetchOnlySelectedBtn').onclick = () => fetchSelectedTemplates(false);
    modal.querySelector('#ecsViewerCloseBtn').onclick = closeInternalViewer;
    modal.querySelector('#ecsApplyAllFetchedBtn').onclick = () => applyContentToTemplates(fetchedTemplates);
    modal.querySelector('#ecsPrintActiveBtn').onclick = printActivePreview;
    modal.querySelector('#ecsPdfActiveBtn').onclick = exportActivePreviewPdf;
    modal.querySelector('#ecsLivePreviewDocBtn').onclick = () => {
      const item = appliedPreviews.find(x => x.template.id === activeAppliedId);
      if (item && item.template) livePreviewOnDoc(item.template.id);
    };
    modal.querySelector('#ecsApplyThemeToDocBtn').onclick = applyActiveThemeToDocument;
    modal.querySelector('#ecsZoomFitBtn').onclick = () => setZoom('fit');
    modal.querySelector('#ecsZoomFullBtn').onclick = () => setZoom('full');

    window.addEventListener('resize', () => {
      if (activeTab === 'preview' && document.getElementById(MODAL_ID)?.classList.contains('show')) {
        applyPreviewStageZoom();
      }
    });
  }

  function showStatus(msg, isErr) {
    const bar = document.getElementById('ecsStatusBar');
    if (!bar) return;
    bar.textContent = msg;
    bar.style.background = isErr ? '#fee2e2' : '#e0f2fe';
    bar.style.color = isErr ? '#991b1b' : '#0c4a6e';
    bar.classList.add('show');
  }

  function switchTab(tab) {
    activeTab = tab;
    document.querySelectorAll(`#${MODAL_ID} [data-ecs-tab]`).forEach(b => {
      b.classList.toggle('active', b.dataset.ecsTab === tab);
    });
    document.getElementById('ecsPanelBrowse')?.classList.toggle('active', tab === 'browse');
    document.getElementById('ecsPanelFetched')?.classList.toggle('active', tab === 'fetched');
    document.getElementById('ecsPanelPreview')?.classList.toggle('active', tab === 'preview');
    if (tab !== 'browse') closeInternalViewer();
    if (tab === 'preview') applyPreviewStageZoom();
  }

  function updateCounts() {
    const selLbl = document.getElementById('ecsSelectedCountLbl');
    if (selLbl) selLbl.textContent = `المحدد: ${selectedIds.size} قالب`;
    const fb = document.getElementById('ecsFetchedBadge');
    if (fb) fb.textContent = String(fetchedTemplates.length);
    const pb = document.getElementById('ecsPreviewBadge');
    if (pb) pb.textContent = String(appliedPreviews.length);
  }

  async function loadCatalog(liveSearch) {
    const q = (document.getElementById('ecsSearchInput')?.value || '').trim();
    const token = (document.getElementById('ecsCanvaTokenInput')?.value || '').trim();
    showStatus('⏳ جاري فتح بوابة كانفا الداخلية وجلب القوالب الحقيقية...');
    try {
      const res = await fetch('/api/edu/canva/browse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ q, category: activeCategory || 'all', source: liveSearch ? 'live' : 'all', canva_token: token }),
      });
      const data = await res.json();
      if (!res.ok || data.success === false) throw new Error(data.error || 'تعذر جلب القوالب');
      catalogTemplates = data.templates || [];
      if (Array.isArray(data.fetched)) {
        fetchedTemplates = data.fetched;
      }
      renderBrowseGrid();
      renderFetchedGrid();
      updateCounts();
      if (data.api_error) {
        showStatus(`⚠️ تم عرض ${catalogTemplates.length} قالب — تنبيه Canva API: ${data.api_error}`, true);
      } else {
        const extra = data.live_count ? ` (بينها ${data.live_count} قالب مجلوب مباشرة من كانفا)` : '';
        showStatus(`✅ تم جلب ${catalogTemplates.length} قالب كانفا حقيقي داخل واجهة الوظيفة${extra}. اضغط "👁️ فتح" للمعاينة أو حدد ما تريد لجلبه وتطبيق محتواك.`);
      }
    } catch (e) {
      showStatus('❌ ' + (e.message || e), true);
    }
  }

  async function importCanvaUrls() {
    const urls = (document.getElementById('ecsUrlsInput')?.value || '').trim();
    const name = (document.getElementById('ecsUrlNameInput')?.value || '').trim();
    if (!urls) {
      showStatus('⚠️ الصق رابط قالب أو تصميم كانفا أولاً', true);
      return;
    }
    showStatus('⏳ جاري قراءة الرابط وجلب بيانات وصورة القالب من كانفا...');
    try {
      const res = await fetch('/api/edu/canva/import_urls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls, name, category: 'تصاميمي المجلوبة' }),
      });
      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error || 'تعذر استيراد الرابط');
      document.getElementById('ecsUrlsInput').value = '';
      document.getElementById('ecsUrlNameInput').value = '';
      (data.templates || []).forEach(t => selectedIds.add(t.id));
      await loadCatalog(false);
      if (data.templates && data.templates[0]) {
        openInternalViewer(data.templates[0].id);
      }
      showStatus(`✅ تم جلب ${data.count} قالب وتحديده في القائمة — يمكنك معاينته داخلياً أو جلب المحدد وتطبيق المحتوى.`);
    } catch (e) {
      showStatus('❌ ' + e.message, true);
    }
  }

  async function importCanvaFile() {
    const fileInput = document.getElementById('ecsFileImportInput');
    const name = (document.getElementById('ecsUrlNameInput')?.value || '').trim();
    if (!fileInput || !fileInput.files || !fileInput.files.length) {
      showStatus('⚠️ اختر صورة أو ملف PDF أو PPTX مصدّراً من كانفا أولاً', true);
      return;
    }
    const fd = new FormData();
    fd.append('file', fileInput.files[0]);
    if (name) fd.append('name', name);
    fd.append('category', 'تصاميمي المجلوبة');
    showStatus('⏳ جاري استيراد ملف كانفا ومعالجته إلى صور A4 وملف PDF متوافق...');
    try {
      const res = await fetch('/api/edu/canva/import_file', { method: 'POST', body: fd });
      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error || 'تعذر استيراد الملف');
      fileInput.value = '';
      if (data.template && data.template.id) selectedIds.add(data.template.id);
      await loadCatalog(false);
      if (data.template) openInternalViewer(data.template.id);
      const pgCnt = data.template?.processed_page_count || 1;
      showStatus(`✅ تم استيراد ومعالجة قالب "${data.template?.name || 'كانفا'}" بنجاح (${pgCnt} صفحة PNG + PDF جاهزة للدمج)!`);
    } catch (e) {
      showStatus('❌ ' + e.message, true);
    }
  }

  function getFilteredCatalog() {
    return catalogTemplates.filter(t => {
      if (activeCategory !== 'all') {
        if (activeCategory === 'تصاميمي المجلوبة') {
          if (!['حساب Canva المتصل', 'رابط Canva مستورد', 'ملف Canva مستورد', 'Canva Marketplace Live', 'Canva Live Search', 'Canva Studio Fetch'].includes(t.source)) {
            return false;
          }
        } else if (t.category !== activeCategory) {
          return false;
        }
      }
      return true;
    });
  }

  function renderBrowseGrid() {
    const wrap = document.getElementById('ecsBrowseGrid');
    if (!wrap) return;
    const list = getFilteredCatalog();
    if (!list.length) {
      wrap.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:30px;color:#64748b;font-weight:700;">لا توجد قوالب مطابقة — جرّب بحثاً آخر أو اختر "الكل" ثم اضغط "جلب قوالب من كانفا".</div>';
      updateCounts();
      return;
    }

    wrap.innerHTML = list.map(t => {
      const c = t.colors || {};
      const p = safeHex(c.primary, '#3b6978');
      const s = safeHex(c.secondary, '#204051');
      const a = safeHex(c.accent, '#c9a86a');
      const bg = safeHex(c.bg, '#f8fafc');
      const isSel = selectedIds.has(t.id);
      const artImg = getSafeImageSrc(t);
      const fbImg = getFallbackImageSrc(t);

      return `<div class="ecs-card ${isSel ? 'selected' : ''}" data-card-id="${escHtml(t.id)}">
        <div class="ecs-card-art" style="background:${bg};" onclick="EduCanvaStudio.openInternalViewer('${escHtml(t.id)}')">
          ${artImg
            ? `<img src="${escHtml(artImg)}" data-fb="${escHtml(fbImg)}" onerror="if(this.dataset.fb&&this.src!==this.dataset.fb){this.src=this.dataset.fb;}" alt="${escHtml(t.name)}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:top center;display:block;">`
            : `<div style="padding:10px;width:100%;">
                 <div style="height:34px;background:linear-gradient(135deg,${p},${s});border-radius:7px;display:flex;align-items:center;justify-content:space-between;padding:0 10px;">
                   <span style="width:48%;height:6px;background:#fff;border-radius:4px;opacity:0.92;"></span>
                   <span style="width:14px;height:14px;background:${a};border-radius:50%;"></span>
                 </div>
               </div>`
          }
          <span style="position:absolute;top:6px;right:6px;z-index:2;background:rgba(15,23,42,0.78);color:#fff;padding:2px 8px;border-radius:6px;font-size:10.5px;font-weight:800;">${escHtml(t.badge_text || t.category)}</span>
          <span style="position:absolute;bottom:6px;left:6px;z-index:2;background:rgba(255,255,255,0.94);color:#0f172a;padding:3px 8px;border-radius:6px;font-size:10.5px;font-weight:800;box-shadow:0 2px 6px rgba(0,0,0,0.18);">👁️ فتح ومعاينة داخلية</span>
        </div>
        <div class="ecs-card-body">
          <div>
            <div style="font-size:13.5px;font-weight:800;color:#0f172a;margin-bottom:4px;">${escHtml(t.name)}</div>
            <div style="font-size:11.5px;color:#475569;line-height:1.5;">${escHtml(t.description || t.source)}</div>
          </div>
          <div style="display:flex;align-items:center;gap:5px;">
            <span style="width:14px;height:14px;border-radius:50%;background:${p};border:1px solid #cbd5e1;"></span>
            <span style="width:14px;height:14px;border-radius:50%;background:${s};border:1px solid #cbd5e1;"></span>
            <span style="width:14px;height:14px;border-radius:50%;background:${a};border:1px solid #cbd5e1;"></span>
            <span style="font-size:10.5px;color:#64748b;font-weight:700;margin-right:auto;">${escHtml(t.source || '')}</span>
          </div>
          <div class="ecs-check-row">
            <label class="ecs-check-label">
              <input type="checkbox" ${isSel ? 'checked' : ''} onchange="EduCanvaStudio.toggleSelect('${escHtml(t.id)}', this.checked)">
              <span>تحديد للجلب</span>
            </label>
            <div style="display:flex;gap:4px;flex-wrap:wrap;">
              <button type="button" class="ecs-btn outline" style="padding:5px 8px;font-size:11px;" onclick="EduCanvaStudio.openInternalViewer('${escHtml(t.id)}')">👁️ معاينة</button>
              <button type="button" class="ecs-btn amber" style="padding:5px 8px;font-size:11px;" onclick="EduCanvaStudio.livePreviewOnDoc('${escHtml(t.id)}')">🖥️ معاينة بالملف</button>
              <button type="button" class="ecs-btn teal" style="padding:5px 9px;font-size:11px;" onclick="EduCanvaStudio.mergeDirectToCurrentDoc('${escHtml(t.id)}')">✅ تطبيق</button>
            </div>
          </div>
        </div>
      </div>`;
    }).join('');
    updateCounts();
  }

  function closeInternalViewer() {
    const v = document.getElementById('ecsInternalViewer');
    if (v) v.style.display = 'none';
  }

  function openInternalViewer(id) {
    const t = catalogTemplates.find(x => x.id === id) || fetchedTemplates.find(x => x.id === id);
    if (!t) return;
    const viewer = document.getElementById('ecsInternalViewer');
    const titleEl = document.getElementById('ecsViewerTitle');
    const subEl = document.getElementById('ecsViewerSub');
    const bodyEl = document.getElementById('ecsViewerBody');
    const selBtn = document.getElementById('ecsViewerSelectBtn');
    const fetchBtn = document.getElementById('ecsViewerFetchApplyBtn');
    if (!viewer || !bodyEl) return;

    titleEl.textContent = `🎨 ${t.name}`;
    subEl.textContent = `${t.category || ''} — ${t.source || 'Canva Studio'} (مفتوح داخلياً ضمن واجهة الوظيفة)`;

    const c = t.colors || {};
    const p = safeHex(c.primary, '#3b6978');
    const s = safeHex(c.secondary, '#204051');
    const a = safeHex(c.accent, '#c9a86a');
    const bg = safeHex(c.bg, '#f8fafc');
    const artImg = getSafeImageSrc(t);
    const fbImg = getFallbackImageSrc(t);
    const docSnap = extractDocumentData();

    const previewPane = t.canva_embed_url
      ? `<iframe src="${escHtml(t.canva_embed_url)}" style="width:100%;height:370px;border:1.5px solid #cbd5e1;border-radius:10px;background:#fff;" allowfullscreen loading="lazy"></iframe>`
      : `<div style="background:#f1f5f9;border:1.5px solid #cbd5e1;border-radius:12px;padding:10px;display:flex;flex-direction:column;align-items:center;gap:8px;">
           <div style="font-size:12px;font-weight:800;color:#0f172a;width:100%;display:flex;justify-content:space-between;">
             <span>🖼️ معاينة التصميم الأصلي من كانفا:</span>
             <span style="color:#0f766e;">${escHtml(t.canva_id || 'A4')}</span>
           </div>
           ${artImg
             ? `<img src="${escHtml(artImg)}" data-fb="${escHtml(fbImg)}" onerror="if(this.dataset.fb&&this.src!==this.dataset.fb){this.src=this.dataset.fb;}" alt="${escHtml(t.name)}" style="width:100%;max-height:340px;object-fit:contain;border-radius:8px;background:#fff;box-shadow:0 4px 12px rgba(0,0,0,0.12);">`
             : ''}
         </div>`;

    const miniMockupPane = `<div style="display:flex;flex-direction:column;gap:10px;">
      <div style="background:${bg};border:2px solid ${p};border-radius:12px;padding:14px;box-shadow:0 4px 12px rgba(0,0,0,0.06);">
        <div style="font-size:11.5px;font-weight:800;color:${p};margin-bottom:8px;">✨ معاينة مصغّرة لتطبيق محتواك على هذا القالب:</div>
        <div style="background:linear-gradient(135deg,${p},${s});color:#fff;padding:12px 14px;border-radius:9px;border-right:5px solid ${a};margin-bottom:10px;">
          <div style="font-size:15px;font-weight:900;">${escHtml(docSnap.docTitle)}</div>
          <div style="font-size:11px;opacity:0.9;margin-top:2px;">${escHtml((docSnap.subtitle || '').slice(0, 75))}</div>
        </div>
        <div style="background:#fff;border:1px solid #e2e8f0;border-right:4px solid ${a};border-radius:8px;padding:10px;font-size:12px;color:#0f172a;">
          <div style="font-weight:800;color:${p};margin-bottom:4px;">المحتوى الجاهز للتطبيق:</div>
          <div>• الأقسام/الصفحات المستخرجة: <strong>${(docSnap.sections || docSnap.reports || []).length}</strong></div>
          <div>• تخطيط الطباعة: <strong>${escHtml(t.layout || 'gradient_arch')} (A4 قياسي)</strong></div>
        </div>
      </div>
      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px;display:flex;flex-direction:column;gap:8px;">
        <div style="font-size:12.5px;color:#334155;line-height:1.6;">${escHtml(t.description || '')}</div>
        <div style="display:flex;align-items:center;gap:8px;font-size:12px;font-weight:700;">
          <span>الألوان المستخرجة:</span>
          <span style="width:20px;height:20px;border-radius:50%;background:${p};border:1px solid #cbd5e1;" title="الرئيسي"></span>
          <span style="width:20px;height:20px;border-radius:50%;background:${s};border:1px solid #cbd5e1;" title="الثانوي"></span>
          <span style="width:20px;height:20px;border-radius:50%;background:${a};border:1px solid #cbd5e1;" title="المميز"></span>
        </div>
        <div style="padding-top:6px;border-top:1px dashed #cbd5e1;display:flex;flex-direction:column;gap:6px;">
            <div style="font-size:11.5px;color:#0f766e;font-weight:800;">🔒 يتم تحويل القالب إلى صورة A4 وملف PDF متوافق وتضمينه في الصفحات المخصصة للملف مباشرة.</div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;">
              <button type="button" class="ecs-btn amber" style="flex:1;font-size:12px;padding:7px 10px;justify-content:center;" onclick="EduCanvaStudio.livePreviewOnDoc('${escHtml(t.id)}')">👁️ معاينة فورية على صفحات الملف بالأسفل</button>
              <button type="button" class="ecs-btn teal" style="flex:1;font-size:12px;padding:7px 10px;justify-content:center;" onclick="EduCanvaStudio.mergeDirectToCurrentDoc('${escHtml(t.id)}')">✅ تثبيت ودمج نهائي بالملف</button>
            </div>
          </div>
      </div>
    </div>`;

    bodyEl.innerHTML = previewPane + miniMockupPane;

    const refreshViewerSelBtn = () => {
      const checked = selectedIds.has(t.id);
      selBtn.textContent = checked ? '✓ محدد للجلب' : '☑️ تحديد للجلب';
      selBtn.className = checked ? 'ecs-btn teal' : 'ecs-btn outline';
    };
    refreshViewerSelBtn();
    selBtn.onclick = () => {
      toggleSelect(t.id);
      refreshViewerSelBtn();
    };
    fetchBtn.textContent = '⚡ معاينة A4 بمحتوى الملف';
    fetchBtn.onclick = () => fetchSingleAndApply(t.id);

    viewer.style.display = 'block';
    viewer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function toggleSelect(id, forceVal) {
    if (typeof forceVal === 'boolean') {
      if (forceVal) selectedIds.add(id);
      else selectedIds.delete(id);
    } else {
      if (selectedIds.has(id)) selectedIds.delete(id);
      else selectedIds.add(id);
    }
    renderBrowseGrid();
  }

  function stripHeavyFields(item) {
    return {
      id: item.id,
      canva_id: item.canva_id,
      name: item.name,
      category: item.category,
      source: item.source,
      layout: item.layout,
      font_family: item.font_family,
      heading_font: item.heading_font,
      description: item.description,
      colors: item.colors,
      preview_image: item.preview_image,
      safe_preview_data_url: isRealRasterUrl(item.safe_preview_data_url) ? item.safe_preview_data_url : '',
      canva_url: item.canva_url,
      canva_embed_url: item.canva_embed_url,
      badge_text: item.badge_text,
    };
  }

  async function fetchSelectedTemplates(autoApply = true) {
    if (!selectedIds.size) {
      showStatus('⚠️ حدد قالباً واحداً على الأقل من مربعات التحديد أولاً (أو اضغط "تحديد الكل").', true);
      document.querySelector(`#${MODAL_ID} .ecs-body`)?.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }
    const items = catalogTemplates.filter(t => selectedIds.has(t.id)).map(stripHeavyFields);
    if (!items.length) return;
    await doFetchFromServer(items, autoApply);
  }

  async function fetchSingleAndApply(id) {
    const item = catalogTemplates.find(t => t.id === id) || fetchedTemplates.find(t => t.id === id);
    if (!item) return;
    selectedIds.add(id);
    await doFetchFromServer([stripHeavyFields(item)], true);
  }

  async function doFetchFromServer(items, autoApplyAndPreview) {
    const token = (document.getElementById('ecsCanvaTokenInput')?.value || '').trim();
    showStatus(`⏳ جاري جلب ${items.length} قالب فعلياً من كانفا وتجهيز صورها وألوانها داخل واجهة الوظيفة...`);
    try {
      const res = await fetch('/api/edu/canva/fetch_selected', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ templates: items, canva_token: token }),
      });
      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error || 'فشل جلب القوالب المحددة');
      fetchedTemplates = data.fetched || [];
      renderFetchedGrid();
      updateCounts();

      if (autoApplyAndPreview && data.fetched_now && data.fetched_now.length) {
        applyContentToTemplates(data.fetched_now);
      } else {
        switchTab('fetched');
        showStatus(`✅ تم جلب ${data.count} قالب بنجاح داخل واجهة الوظيفة! اضغط الآن "تطبيق المحتوى وعرض المعاينة".`);
      }
    } catch (e) {
      showStatus('❌ ' + e.message, true);
    }
  }

  function renderFetchedGrid() {
    const wrap = document.getElementById('ecsFetchedGrid');
    if (!wrap) return;
    if (!fetchedTemplates.length) {
      wrap.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:34px;color:#64748b;font-weight:700;">لم يتم جلب قوالب بعد — انتقل للتبويب (1) وحدد القوالب التي تريدها ثم اضغط "جلب القوالب المحددة".</div>';
      return;
    }
    wrap.innerHTML = fetchedTemplates.map(t => {
      const c = t.colors || {};
      const p = safeHex(c.primary, '#3b6978');
      const a = safeHex(c.accent, '#c9a86a');
      const bg = safeHex(c.bg, '#f8fafc');
      const artImg = getSafeImageSrc(t);
      const fbImg = getFallbackImageSrc(t);
      return `<div class="ecs-card">
        <div class="ecs-card-art" style="background:${bg};height:145px;cursor:pointer;" onclick="EduCanvaStudio.applySingle('${escHtml(t.id)}')">
          ${artImg ? `<img src="${escHtml(artImg)}" data-fb="${escHtml(fbImg)}" onerror="if(this.dataset.fb&&this.src!==this.dataset.fb){this.src=this.dataset.fb;}" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:top center;">` : ''}
          <div style="position:relative;z-index:2;display:flex;justify-content:space-between;align-items:center;padding:8px;">
            <span style="background:${p};color:#fff;font-size:11px;padding:3px 9px;border-radius:6px;font-weight:800;">${escHtml(t.badge_text || t.category)}</span>
            <span style="width:16px;height:16px;border-radius:50%;background:${a};border:2px solid #fff;"></span>
          </div>
          <div style="position:relative;z-index:2;background:rgba(255,255,255,0.94);padding:5px 8px;margin:6px;border-radius:6px;font-size:12px;font-weight:800;color:#0f172a;">${escHtml(t.name)}</div>
        </div>
        <div class="ecs-card-body">
          <div style="font-size:12px;color:#475569;">${escHtml(t.description || t.source)}</div>
          <div style="display:flex;gap:6px;align-items:center;">
            <button type="button" class="ecs-btn green" style="flex:1;justify-content:center;font-size:12px;" onclick="EduCanvaStudio.applySingle('${escHtml(t.id)}')">✨ تطبيق المحتوى ومعاينة</button>
            <button type="button" class="ecs-btn gray" style="padding:7px 10px;font-size:12px;" onclick="EduCanvaStudio.removeFetched('${escHtml(t.id)}')" title="إزالة">🗑️</button>
          </div>
        </div>
      </div>`;
    }).join('');
  }

  function applySingle(id) {
    const tpl = fetchedTemplates.find(t => t.id === id) || catalogTemplates.find(t => t.id === id);
    if (!tpl) return;
    applyContentToTemplates([tpl]);
  }

  async function removeFetched(id) {
    try {
      const res = await fetch('/api/edu/canva/fetched/' + encodeURIComponent(id), { method: 'DELETE' });
      const d = await res.json();
      if (d.success) fetchedTemplates = d.fetched || [];
    } catch (_) {
      fetchedTemplates = fetchedTemplates.filter(t => t.id !== id);
    }
    renderFetchedGrid();
    updateCounts();
  }

  /* ───── استخراج المحتوى الفعلي من واجهة الوظيفة الحالية ───── */
  function extractDocumentData() {
    const mode = detectPageMode() || currentMode;
    if (mode === 'portfolio') return extractPortfolioData();
    if (mode === 'witnesses') return extractWitnessesData();
    return extractReportsData();
  }

  function cleanText(el) {
    return el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '';
  }

  function uniqueLines(arr) {
    const out = [];
    const seen = new Set();
    arr.forEach(t => {
      const s = String(t || '').trim();
      if (s && !seen.has(s)) {
        seen.add(s);
        out.push(s);
      }
    });
    return out;
  }

  function extractPortfolioData() {
    const pages = Array.from(document.querySelectorAll('#pagesWrap > .page'));
    const coverPage = pages[0];
    const bannerTxt = cleanText(coverPage?.querySelector('.banner'));
    const coverHeaderLines = coverPage
      ? Array.from(coverPage.querySelectorAll('.cover-header-text h2, .cover-header-text h3, .cover-header-text p')).map(cleanText).filter(Boolean)
      : [];
    const coverFooterLines = coverPage
      ? Array.from(coverPage.querySelectorAll('.cover-footer .data-text, .cover-footer h2')).map(cleanText).filter(Boolean)
      : [];
    const coverLines = uniqueLines([...coverHeaderLines, bannerTxt, ...coverFooterLines]);

    const sections = [];
    pages.slice(1).forEach((pg, idx) => {
      const tbl = pg.querySelector('table');
      if (tbl) {
        const title = cleanText(pg.querySelector('.table-title, h2, .text-page-header h2')) || `جدول ${idx + 1}`;
        const headers = Array.from(tbl.querySelectorAll('thead th'))
          .filter(th => !th.classList.contains('edit-only'))
          .map(th => cleanText(th));

        const bodyRows = Array.from(tbl.querySelectorAll('tbody tr')).filter(tr => !tr.classList.contains('witness-subrow'));
        const hasAnyWitness = bodyRows.some(tr => tr.querySelector('td[data-witness]'));

        if (hasAnyWitness) {
          const wRows = bodyRows.map(tr => {
            const cells = Array.from(tr.querySelectorAll('td')).filter(td => !td.classList.contains('action-cell'));
            const texts = cells.map(td => {
              const cc = td.querySelector('.cell-content');
              return cc ? cleanText(cc) : cleanText(td);
            }).filter(Boolean);
            const wTd = tr.querySelector('td[data-witness]');
            let wData = { images: [], links: [], imageSize: 160, imageSizeMode: 'px', imageFit: 'contain', placement: 'below' };
            if (wTd && wTd.dataset.witness) {
              try { wData = { ...wData, ...JSON.parse(wTd.dataset.witness) }; } catch (_) {}
            }
            return { itemText: texts.join(' — '), witness: wData };
          });
          sections.push({ kind: 'witness-table', title, weight: '', rows: wRows });
        } else {
          const rows = bodyRows.map(tr =>
            Array.from(tr.querySelectorAll('td'))
              .filter(td => !td.classList.contains('action-cell'))
              .map(td => {
                const cc = td.querySelector('.cell-content');
                return cc ? cleanText(cc) : cleanText(td);
              })
          );
          sections.push({ kind: 'table', title, headers, rows });
        }
      } else if (pg.querySelector('.bio-grid, .info-grid, .card-grid, .data-grid')) {
        const title = cleanText(pg.querySelector('h2, h3, .text-page-header')) || 'السيرة الذاتية والبيانات';
        const cards = uniqueLines(
          Array.from(pg.querySelectorAll('.bio-item, .info-item, .card-item, .data-cell, tr')).map(cleanText)
        );
        sections.push({ kind: 'cards', title, items: cards.length ? cards : [cleanText(pg)] });
      } else {
        const title = cleanText(pg.querySelector('h1, h2, .section-title, .prayer-title, .conclusion-title')) || `صفحة ${idx + 2}`;
        const rawParas = Array.from(pg.querySelectorAll('.prayer-content, .text-page-box p, .quote-page .speech-bubble p, .toc li, .conclusion-text, .editable-block'))
          .map(cleanText);
        const paragraphs = uniqueLines(rawParas.length ? rawParas : Array.from(pg.querySelectorAll('p, li, .editable-area')).map(cleanText));
        sections.push({ kind: 'text', title, paragraphs: paragraphs.length ? paragraphs : [cleanText(pg)] });
      }
    });

    return {
      docTitle: bannerTxt || 'ملف الأداء الوظيفي',
      subtitle: coverHeaderLines.slice(0, 3).join(' • '),
      coverLines,
      sections,
    };
  }

  function extractWitnessesData() {
    const pages = Array.from(document.querySelectorAll('#pagesWrap > .page'));
    const coverPage = pages[0];
    const coverTitle = cleanText(coverPage?.querySelector('.cover-main-title')) || 'سجل توثيق شواهد الأداء الوظيفي';
    const coverMeta = coverPage
      ? uniqueLines(Array.from(coverPage.querySelectorAll('.ministry-info div, .cover-year-badge, .cover-teacher-name')).map(cleanText))
      : [];

    const sections = [];
    pages.slice(1).forEach((pg, idx) => {
      const wTable = pg.querySelector('.witness-table');
      if (wTable) {
        const title = cleanText(pg.querySelector('.witness-title')) || `شواهد ${idx + 1}`;
        const weight = cleanText(pg.querySelector('.witness-weight'));
        const rows = [];
        Array.from(wTable.querySelectorAll('tbody tr')).forEach(tr => {
          if (tr.classList.contains('witness-subrow')) return;
          const itemText = cleanText(tr.querySelector('td.col-witness .cell-content') || tr.querySelector('td.col-witness'));
          const evTd = tr.querySelector('td.col-evidence');
          let wData = { images: [], links: [], imageSize: 160, imageSizeMode: 'px', imageFit: 'contain', placement: 'opposite', columns: 'auto' };
          if (evTd && evTd.dataset.witness) {
            try { wData = { ...wData, ...JSON.parse(evTd.dataset.witness) }; } catch (_) {}
          }
          rows.push({ itemText, witness: wData });
        });
        sections.push({ kind: 'witness-table', title, weight, rows });
      } else if (pg.querySelector('table')) {
        const tbl = pg.querySelector('table');
        const title = cleanText(pg.querySelector('h2, .cv-header h2, .eval-title')) || `بيانات ${idx + 1}`;
        const headers = Array.from(tbl.querySelectorAll('thead th')).filter(th => !th.classList.contains('edit-only')).map(cleanText);
        const rows = Array.from(tbl.querySelectorAll('tbody tr')).map(tr =>
          Array.from(tr.querySelectorAll('td')).filter(td => !td.classList.contains('action-cell')).map(cleanText)
        );
        sections.push({ kind: 'table', title, headers, rows });
      } else if (pg.querySelector('.cv-card')) {
        const title = cleanText(pg.querySelector('.content-header h2, .cv-header h2')) || 'السيرة الذاتية';
        const items = uniqueLines(
          Array.from(pg.querySelectorAll('.cv-header h2, .cv-header p, .cv-info-item, .cv-list li, .cv-skill-tag')).map(cleanText)
        );
        sections.push({ kind: 'cards', title, items: items.length ? items : [cleanText(pg)] });
      } else {
        const title = cleanText(pg.querySelector('.content-header h2, .goals-title, .bismillah-text, .conclusion-title, h2')) || `صفحة ${idx + 2}`;
        const paragraphs = uniqueLines(
          Array.from(pg.querySelectorAll('.intro-text, .goal-text, .vision-card h3, .vision-card p, .charter-article h4, .charter-article p, .conclusion-text')).map(cleanText)
        );
        sections.push({ kind: 'text', title, paragraphs: paragraphs.length ? paragraphs : [cleanText(pg)] });
      }
    });

    return {
      docTitle: coverTitle,
      subtitle: coverMeta.slice(0, 4).join(' • '),
      coverLines: [coverTitle, ...coverMeta],
      sections,
    };
  }

  function extractReportsData() {
    const scopeSel = document.getElementById('ecsReportFilterSelect');
    const selectedReportIdx = scopeSel ? scopeSel.value : 'all';

    const cover = document.querySelector('#mainContainer .cover');
    const coverLines = cover
      ? Array.from(cover.querySelectorAll('.kingdom, .ministry, .school, .file-title, .year, .info-box p')).map(cleanText).filter(Boolean)
      : ['ملف التقارير التربوية والبرامج والأنشطة المدرسية'];

    const allReports = Array.from(document.querySelectorAll('#mainContainer .report, #mainContainer .single-page-report'));
    const chosenReports = selectedReportIdx === 'all'
      ? allReports
      : [allReports[parseInt(selectedReportIdx, 10)]].filter(Boolean);

    const reports = chosenReports.map((rep, idx) => {
      const title = cleanText(rep.querySelector('.report-title')) || `تقرير ${idx + 1}`;
      const infoRows = Array.from(rep.querySelectorAll('.info-table tr')).map(tr => ({
        k: cleanText(tr.querySelector('th')),
        v: cleanText(tr.querySelector('td')),
      })).filter(r => r.k || r.v);

      const blocks = [];
      Array.from(rep.children).forEach(ch => {
        if (ch.classList.contains('page-ctrl-bar') || ch.classList.contains('witness-actions') || ch.classList.contains('report-title') || ch.classList.contains('info-table') || ch.classList.contains('signatures')) return;
        if (ch.classList.contains('sub-heading')) {
          blocks.push({ type: 'heading', text: cleanText(ch) });
        } else if (ch.classList.contains('evidence-grid')) {
          let images = [], links = [];
          try { images = JSON.parse(ch.dataset.images || '[]'); } catch (_) {}
          try { links = JSON.parse(ch.dataset.links || '[]'); } catch (_) {}
          blocks.push({
            type: 'evidence',
            images,
            links,
            cols: Number(ch.dataset.cols || 2),
            imgHeight: ch.dataset.imgHeight || '240',
            fit: ch.dataset.imgFit || 'contain',
          });
        } else if (ch.tagName === 'UL') {
          const items = Array.from(ch.querySelectorAll('li')).map(cleanText).filter(Boolean);
          if (items.length) blocks.push({ type: 'list', items });
        } else if (ch.tagName === 'TABLE') {
          const headers = Array.from(ch.querySelectorAll('th')).map(cleanText);
          const rows = Array.from(ch.querySelectorAll('tbody tr')).map(tr => Array.from(tr.querySelectorAll('td')).map(cleanText));
          if (rows.length) blocks.push({ type: 'table', headers, rows });
        } else {
          const t = cleanText(ch);
          if (t) blocks.push({ type: 'paragraph', text: t });
        }
      });

      const signatures = Array.from(rep.querySelectorAll('.signature-box')).map(sb => ({
        label: cleanText(sb.querySelector('.label')),
        name: cleanText(sb.querySelector('.name')),
      }));

      return { title, infoRows, blocks, signatures };
    });

    return {
      docTitle: coverLines[3] || 'ملف التقارير التربوية والبرامج',
      subtitle: coverLines.slice(0, 3).join(' • '),
      coverLines,
      reports,
    };
  }

  /* ───── بناء صفحات كانفا A4 المطبقة بالمحتوى ───── */
  function buildSheetStyleVars(tpl) {
    const c = tpl.colors || {};
    return `--c-primary:${safeHex(c.primary, '#3b6978')};--c-secondary:${safeHex(c.secondary, '#204051')};--c-accent:${safeHex(c.accent, '#c9a86a')};--c-bg:${safeHex(c.bg, '#ffffff')};--c-card:${safeHex(c.card_bg, '#ffffff')};--c-text:${safeHex(c.text_dark, '#0f172a')};`;
  }

  function renderCoverSheet(tpl, docData) {
    const styleVars = buildSheetStyleVars(tpl);
    const layoutClass = 'layout-' + (tpl.layout || 'gradient_arch');
    const lines = docData.coverLines || [];
    const safeRaster = isRealRasterUrl(tpl.safe_preview_data_url) ? tpl.safe_preview_data_url : '';

    return `<div class="canva-a4-sheet ${layoutClass}" style="${styleVars}">
      <div class="canva-cover-hero">
        <div class="canva-cover-banner" style="display:flex;align-items:center;justify-content:space-between;gap:16px;text-align:right;">
          <div style="flex:1;">
            <div style="font-size:13px;opacity:0.92;margin-bottom:6px;">${escHtml(lines[0] || 'المملكة العربية السعودية — وزارة التعليم')}</div>
            <h1 style="margin:0;font-size:32px;font-weight:900;font-family:'Amiri','Cairo',serif;line-height:1.4;color:#fff;">${escHtml(docData.docTitle)}</h1>
            <div style="font-size:14.5px;margin-top:8px;opacity:0.92;">${escHtml(docData.subtitle || '')}</div>
          </div>
          ${safeRaster ? `<div style="width:94px;height:126px;flex-shrink:0;border-radius:10px;overflow:hidden;border:2px solid rgba(255,255,255,0.75);background:#fff;box-shadow:0 4px 12px rgba(0,0,0,0.25);"><img src="${escHtml(safeRaster)}" alt="" style="width:100%;height:100%;object-fit:cover;display:block;"></div>` : ''}
        </div>
        <div style="width:100%;display:flex;flex-direction:column;gap:9px;text-align:center;">
          ${lines.slice(1, 9).map(l => `<div style="background:rgba(15,23,42,0.035);padding:9px 14px;border-radius:8px;font-size:15px;font-weight:700;border-right:4px solid var(--c-accent);">${escHtml(l)}</div>`).join('')}
        </div>
      </div>
      <div class="canva-sheet-foot">
        <span>قالب كانفا: ${escHtml(tpl.name)}</span>
        <span>صفحة الغلاف</span>
      </div>
    </div>`;
  }

  function renderWitnessImagesBlock(wData) {
    if (!wData || !wData.images || !wData.images.length) return '';
    const isFull = wData.imageSizeMode === 'full';
    const wStyle = isFull ? 'width:100%;' : `width:${Math.min(520, Number(wData.imageSize) || 160)}px;max-width:100%;`;
    const fitStyle = wData.imageFit === 'cover' ? 'aspect-ratio:1;object-fit:cover;' : 'height:auto;object-fit:contain;';
    return `<div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:flex-start;margin-top:8px;">
      ${wData.images.map(src => `<div style="${wStyle}border:1.5px solid var(--c-primary);border-radius:6px;overflow:hidden;background:#fff;">
        <img src="${src}" alt="شاهد" style="width:100%;${fitStyle}display:block;">
      </div>`).join('')}
    </div>`;
  }

  function renderWitnessLinksQr(wData) {
    if (!wData || !wData.links || !wData.links.length) return '';
    return `<div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:6px;">
      ${wData.links.map(lk => `<div style="text-align:center;background:#fff;padding:4px;border:1px solid #cbd5e1;border-radius:6px;">
        <div class="canva-qr-slot" data-canva-qr="${escHtml(lk.url)}" style="width:56px;height:56px;margin:0 auto;"></div>
        <div style="font-size:9px;color:#475569;max-width:90px;word-break:break-word;margin-top:2px;">${escHtml(lk.title || lk.url)}</div>
      </div>`).join('')}
    </div>`;
  }

  function buildAppliedPagesHtml(tpl, docData) {
    const styleVars = buildSheetStyleVars(tpl);
    const layoutClass = 'layout-' + (tpl.layout || 'gradient_arch');
    let html = renderCoverSheet(tpl, docData);
    const effectiveMode = detectPageMode() || currentMode;

    if (effectiveMode === 'portfolio' || effectiveMode === 'witnesses') {
      const secs = docData.sections || [];
      secs.forEach((sec, idx) => {
        let body = '';
        if (sec.kind === 'table') {
          body = `<table class="canva-table">
            ${sec.headers && sec.headers.length ? `<thead><tr>${sec.headers.map(h => `<th>${escHtml(h)}</th>`).join('')}</tr></thead>` : ''}
            <tbody>
              ${(sec.rows || []).map(r => `<tr>${r.map(c => `<td>${escHtml(c)}</td>`).join('')}</tr>`).join('')}
            </tbody>
          </table>`;
        } else if (sec.kind === 'witness-table') {
          body = `${sec.weight ? `<div style="color:var(--c-primary);font-weight:900;font-size:15px;text-align:center;">${escHtml(sec.weight)}</div>` : ''}
          <table class="canva-table">
            <thead><tr><th style="width:62%;">الفقرة / الشاهد</th><th style="width:38%;">المرفقات والباركود</th></tr></thead>
            <tbody>
              ${(sec.rows || []).map(row => {
                const w = row.witness || {};
                const place = w.placement || 'below';
                const imgsHtml = renderWitnessImagesBlock(w);
                const qrHtml = renderWitnessLinksQr(w);
                let out = `<tr>
                  <td style="text-align:right;">
                    <div>${escHtml(row.itemText)}</div>
                    ${place === 'below' ? imgsHtml : ''}
                  </td>
                  <td style="text-align:center;">
                    ${place === 'opposite' ? imgsHtml : ''}
                    ${qrHtml}
                    ${!imgsHtml && !qrHtml ? '<span style="color:#94a3b8;font-size:11px;">—</span>' : ''}
                  </td>
                </tr>`;
                if (place === 'full-row' && imgsHtml) {
                  out += `<tr><td colspan="2" style="background:rgba(15,23,42,0.02);padding:10px;">${imgsHtml}</td></tr>`;
                }
                return out;
              }).join('')}
            </tbody>
          </table>`;
        } else if (sec.kind === 'cards') {
          body = `<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;">
            ${(sec.items || []).map(it => `<div class="canva-card-box">${escHtml(it)}</div>`).join('')}
          </div>`;
        } else {
          body = `<div class="canva-card-box" style="display:flex;flex-direction:column;gap:8px;line-height:1.9;font-size:15px;">
            ${(sec.paragraphs || []).map(p => `<p style="margin:0;">${escHtml(p)}</p>`).join('')}
          </div>`;
        }

        html += `<div class="canva-a4-sheet ${layoutClass}" style="${styleVars}">
          <div class="canva-page-banner">
            <h2>${escHtml(sec.title)}</h2>
            <span style="background:rgba(255,255,255,0.2);padding:3px 10px;border-radius:999px;font-size:12px;">${idx + 2}</span>
          </div>
          ${body}
          <div class="canva-sheet-foot">
            <span>${escHtml(docData.docTitle)}</span>
            <span>قالب: ${escHtml(tpl.name)}</span>
          </div>
        </div>`;
      });
    } else {
      const reps = docData.reports || [];
      reps.forEach((rep, rIdx) => {
        const infoHtml = rep.infoRows.length
          ? `<table class="canva-table" style="margin-bottom:6px;"><tbody>${rep.infoRows.map(r => `<tr><th style="width:28%;">${escHtml(r.k)}</th><td style="text-align:right;">${escHtml(r.v)}</td></tr>`).join('')}</tbody></table>`
          : '';
        const blocksHtml = rep.blocks.map(b => {
          if (b.type === 'heading') return `<div class="canva-subhead">${escHtml(b.text)}</div>`;
          if (b.type === 'list') return `<ul class="canva-list">${b.items.map(it => `<li>${escHtml(it)}</li>`).join('')}</ul>`;
          if (b.type === 'paragraph') return `<div class="canva-card-box" style="line-height:1.8;font-size:14px;">${escHtml(b.text)}</div>`;
          if (b.type === 'table') return `<table class="canva-table">${b.headers.length ? `<thead><tr>${b.headers.map(h => `<th>${escHtml(h)}</th>`).join('')}</tr></thead>` : ''}<tbody>${b.rows.map(r => `<tr>${r.map(c => `<td>${escHtml(c)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
          if (b.type === 'evidence') {
            const cols = [1, 2, 3].includes(b.cols) ? b.cols : 2;
            const hStyle = b.imgHeight === 'auto' ? 'height:auto;max-height:540px;' : `height:${Math.min(540, parseInt(b.imgHeight, 10) || 220)}px;`;
            const imgs = (b.images || []).map(src => `<div style="border:2px solid var(--c-primary);border-radius:8px;overflow:hidden;background:#fff;padding:4px;"><img src="${src}" alt="شاهد" style="width:100%;${hStyle}object-fit:${b.fit === 'cover' ? 'cover' : 'contain'};display:block;border-radius:5px;"></div>`).join('');
            const lks = (b.links || []).map(lk => `<div style="border:1.5px dashed var(--c-accent);border-radius:8px;padding:10px;background:#fff;text-align:center;"><div class="canva-qr-slot" data-canva-qr="${escHtml(lk.url)}" style="width:96px;height:96px;margin:0 auto;"></div><div style="font-size:11px;font-weight:700;margin-top:6px;">${escHtml(lk.title || lk.url)}</div></div>`).join('');
            if (!imgs && !lks) return '';
            return `<div style="display:grid;grid-template-columns:repeat(${cols},minmax(0,1fr));gap:12px;">${imgs}${lks}</div>`;
          }
          return '';
        }).join('');

        const sigHtml = rep.signatures.length
          ? `<div class="canva-sig-row">${rep.signatures.map(s => `<div class="canva-sig-box"><div style="color:var(--c-primary);">${escHtml(s.label)}</div><div style="margin:6px 0;">${escHtml(s.name)}</div><div style="color:#64748b;font-size:11px;border-top:1px dotted #94a3b8;padding-top:6px;margin-top:16px;">التوقيع</div></div>`).join('')}</div>`
          : '';

        html += `<div class="canva-a4-sheet ${layoutClass}" style="${styleVars}">
          <div class="canva-page-banner">
            <h2>${escHtml(rep.title)}</h2>
            <span style="background:rgba(255,255,255,0.2);padding:3px 10px;border-radius:999px;font-size:12px;">${rIdx + 1}</span>
          </div>
          ${infoHtml}
          ${blocksHtml}
          ${sigHtml}
          <div class="canva-sheet-foot">
            <span>${escHtml(docData.docTitle)}</span>
            <span>قالب: ${escHtml(tpl.name)}</span>
          </div>
        </div>`;
      });
    }

    return html;
  }

  function hydrateQrInside(rootEl) {
    if (!rootEl || typeof QRCode === 'undefined') return;
    rootEl.querySelectorAll('[data-canva-qr]').forEach(slot => {
      const url = slot.getAttribute('data-canva-qr');
      if (!url) return;
      slot.innerHTML = '';
      const sz = slot.offsetWidth && slot.offsetWidth > 40 ? Math.min(96, slot.offsetWidth) : 56;
      new QRCode(slot, {
        text: url,
        width: sz,
        height: sz,
        colorDark: '#000000',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.L,
      });
    });
  }

  function applyContentToTemplates(templatesList) {
    const list = (templatesList || []).filter(Boolean);
    if (!list.length) {
      showStatus('⚠️ لا توجد قوالب مجلوبة لتطبيق المحتوى عليها — حدد قوالب من التبويب (1) وجلبها أولاً.', true);
      switchTab('browse');
      return;
    }
    const docData = extractDocumentData();
    appliedPreviews = list.map(tpl => ({
      template: tpl,
      pagesHtml: buildAppliedPagesHtml(tpl, docData),
    }));
    activeAppliedId = appliedPreviews[0].template.id;
    renderAppliedSwitcher();
    renderActivePreview();
    updateCounts();
    switchTab('preview');
    showStatus(`✨ تم تطبيق محتوى ملفك بالكامل داخل ${appliedPreviews.length} قالب كانفا! اختر أي قالب للمعاينة والطباعة.`);
  }

  function renderAppliedSwitcher() {
    const bar = document.getElementById('ecsAppliedSwitcher');
    if (!bar) return;
    bar.innerHTML = `<div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;">
      <span style="font-size:13px;font-weight:800;color:#0f172a;">القوالب المُطبّقة:</span>
      ${appliedPreviews.map(item => {
        const isAct = item.template.id === activeAppliedId;
        const p = safeHex(item.template.colors?.primary, '#3b6978');
        return `<button type="button" class="ecs-btn ${isAct ? '' : 'outline'}" style="${isAct ? `background:${p};border-color:${p};color:#fff;` : ''}" onclick="EduCanvaStudio.selectApplied('${escHtml(item.template.id)}')">
          <span style="width:10px;height:10px;border-radius:50%;background:${p};border:1px solid #fff;display:inline-block;"></span>
          ${escHtml(item.template.name)}
        </button>`;
      }).join('')}
    </div>`;
  }

  function selectApplied(id) {
    activeAppliedId = id;
    renderAppliedSwitcher();
    renderActivePreview();
  }

  function renderActivePreview() {
    const stage = document.getElementById('ecsPreviewStage');
    if (!stage) return;
    const item = appliedPreviews.find(x => x.template.id === activeAppliedId);
    if (!item) {
      stage.innerHTML = '<div style="color:#fff;padding:40px;font-weight:700;">اختر قالباً للمعاينة.</div>';
      return;
    }
    stage.innerHTML = item.pagesHtml;
    hydrateQrInside(stage);
    const sheets = stage.querySelectorAll('.canva-a4-sheet');
    const lbl = document.getElementById('ecsPreviewPageCount');
    if (lbl) lbl.textContent = `${sheets.length} صفحة A4`;
    applyPreviewStageZoom();
  }

  function setZoom(mode) {
    previewZoom = mode;
    document.getElementById('ecsZoomFitBtn')?.classList.toggle('active', mode === 'fit');
    document.getElementById('ecsZoomFullBtn')?.classList.toggle('active', mode === 'full');
    applyPreviewStageZoom();
  }

  function applyPreviewStageZoom() {
    const stage = document.getElementById('ecsPreviewStage');
    if (!stage) return;
    const sheets = stage.querySelectorAll('.canva-a4-sheet');
    const avail = Math.max(260, stage.clientWidth - 28);
    sheets.forEach(sh => {
      sh.style.transform = '';
      sh.style.marginBottom = '';
      sh.style.transformOrigin = 'top center';
      if (previewZoom === 'fit') {
        const scale = Math.min(1, avail / 794);
        if (scale < 0.99) {
          const h = sh.offsetHeight || 1123;
          sh.style.transform = `scale(${scale.toFixed(4)})`;
          sh.style.marginBottom = `${Math.round(-(h * (1 - scale)) + 14)}px`;
        }
      }
    });
  }

  function printActivePreview() {
    const item = appliedPreviews.find(x => x.template.id === activeAppliedId);
    const printRoot = document.getElementById(PRINT_ROOT_ID);
    if (!item || !printRoot) return;
    printRoot.innerHTML = item.pagesHtml;
    hydrateQrInside(printRoot);
    document.body.classList.add('printing-canva-preview');
    const cleanup = () => {
      document.body.classList.remove('printing-canva-preview');
      printRoot.innerHTML = '';
      window.removeEventListener('afterprint', cleanup);
    };
    window.addEventListener('afterprint', cleanup);
    setTimeout(() => {
      try {
        window.focus();
        window.print();
      } catch (_) {}
      setTimeout(cleanup, 1800);
    }, 250);
  }

  async function exportActivePreviewPdf() {
    if (isExportingCanvaPdf) return;
    const item = appliedPreviews.find(x => x.template.id === activeAppliedId);
    if (!item) return;
    if (!window.jspdf || !window.jspdf.jsPDF || typeof window.html2canvas !== 'function') {
      showStatus('⚠️ مكتبة PDF غير متوفرة — سيتم استخدام الطباعة المباشرة.', true);
      printActivePreview();
      return;
    }

    isExportingCanvaPdf = true;
    showStatus('⏳ جاري تجهيز وتصدير ملف PDF للقالب المختار (794px A4)...');
    const tempWrap = document.createElement('div');
    tempWrap.style.cssText = 'position:fixed;left:-99999px;top:0;width:794px;background:#fff;z-index:-1;';
    tempWrap.innerHTML = item.pagesHtml;
    document.body.appendChild(tempWrap);
    hydrateQrInside(tempWrap);

    try {
      if (document.fonts && document.fonts.ready) await document.fonts.ready;
      await new Promise(r => setTimeout(r, 250));
      const sheets = Array.from(tempWrap.querySelectorAll('.canva-a4-sheet'));
      const { jsPDF } = window.jspdf;
      const pdf = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4', compress: true });
      let firstPdf = true;

      for (let i = 0; i < sheets.length; i++) {
        const sh = sheets[i];
        showStatus(`⏳ جاري تحويل صفحة ${i + 1} من ${sheets.length} إلى PDF...`);
        const capH = Math.max(1123, sh.scrollHeight);
        const canvas = await window.html2canvas(sh, {
          scale: 2,
          useCORS: true,
          allowTaint: false,
          backgroundColor: '#ffffff',
          width: 794,
          height: capH,
          windowWidth: 794,
          windowHeight: capH,
          scrollX: 0,
          scrollY: 0,
          logging: false,
        });

        const pageWmm = 210, pageHmm = 297;
        const ratio = canvas.height / Math.max(1, canvas.width);
        if (ratio <= (pageHmm / pageWmm) + 0.025) {
          if (!firstPdf) pdf.addPage('a4', 'p');
          let rW = pageWmm, rH = ratio * pageWmm;
          if (rH > pageHmm) { rH = pageHmm; rW = pageHmm / ratio; }
          pdf.addImage(canvas.toDataURL('image/jpeg', 0.93), 'JPEG', Math.max(0, (pageWmm - rW) / 2), 0, rW, rH, undefined, 'FAST');
          firstPdf = false;
        } else {
          const sliceMaxH = Math.floor(pageHmm * (canvas.width / pageWmm));
          let y = 0;
          while (y < canvas.height) {
            const sH = Math.min(sliceMaxH, canvas.height - y);
            const sc = document.createElement('canvas');
            sc.width = canvas.width;
            sc.height = sliceMaxH;
            const ctx = sc.getContext('2d');
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, sc.width, sc.height);
            ctx.drawImage(canvas, 0, y, canvas.width, sH, 0, 0, canvas.width, sH);
            if (!firstPdf) pdf.addPage('a4', 'p');
            pdf.addImage(sc.toDataURL('image/jpeg', 0.93), 'JPEG', 0, 0, pageWmm, pageHmm, undefined, 'FAST');
            y += sH;
            firstPdf = false;
          }
        }
      }

      const safeTitle = (item.template.name || 'canva_template').replace(/[^\u0600-\u06FFa-zA-Z0-9_-]+/g, '_');
      pdf.save(`${safeTitle}.pdf`);
      showStatus(`✅ تم تصدير القالب كملف PDF احترافي (${sheets.length} صفحة)!`);
    } catch (e) {
      showStatus('❌ تعذر التصدير إلى PDF: ' + (e.message || e), true);
    } finally {
      tempWrap.remove();
      isExportingCanvaPdf = false;
    }
  }

  function getSelectedMergeOptions() {
    const mSel = document.getElementById('ecsMergeModeSelect');
    const pSel = document.getElementById('ecsEmbedPosSelect');
    return {
      merge_mode: (mSel && mSel.value) || 'dedicated_and_theme',
      embed_position: (pSel && pSel.value) || 'after_cover',
    };
  }

  function stripForStorage(tpl) {
    if (!tpl) return null;
    return {
      id: tpl.id,
      canva_id: tpl.canva_id || '',
      name: tpl.name || 'قالب كانفا',
      category: tpl.category || '',
      source: tpl.source || 'Canva Studio',
      layout: tpl.layout || 'gradient_arch',
      colors: tpl.colors || {},
      preview_image: tpl.preview_image || '',
      badge_text: tpl.badge_text || 'Canva',
      processed: Boolean(tpl.processed),
      processed_asset_id: tpl.processed_asset_id || '',
      processed_format: tpl.processed_format || 'PNG + PDF (A4)',
      processed_page_count: Number(tpl.processed_page_count || (tpl.processed_pages || []).length || 0),
      processed_pdf_url: tpl.processed_pdf_url || '',
      processed_pages: Array.isArray(tpl.processed_pages) ? tpl.processed_pages : [],
      merge_mode: tpl.merge_mode || 'dedicated_and_theme',
      embed_position: tpl.embed_position || 'after_cover',
    };
  }

  async function processTemplateForMerge(tpl) {
    if (!tpl) return tpl;
    if (tpl.processed && Array.isArray(tpl.processed_pages) && tpl.processed_pages.length && tpl.processed_pdf_url) {
      return tpl;
    }
    const token = (document.getElementById('ecsCanvaTokenInput')?.value || '').trim();
    try {
      const res = await fetch('/api/edu/canva/process_for_merge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template: stripHeavyFields(tpl), canva_token: token }),
      });
      const data = await res.json();
      if (res.ok && data.success && data.template) {
        return {
          ...tpl,
          ...data.template,
        };
      }
    } catch (_) {}
    return tpl;
  }

  function removeInjectedCanvaPages() {
    document.querySelectorAll('[data-canva-embedded-page="1"]').forEach(el => el.remove());
    document.querySelectorAll('.canva-bg-layer').forEach(el => el.remove());
    document.querySelectorAll('.canva-frame-page-applied').forEach(el => el.classList.remove('canva-frame-page-applied'));
  }

  function buildEmbeddedPageElement(mode, tpl, pageMeta, pageIdx, totalCount) {
    const imgUrl = pageMeta && pageMeta.image_url ? pageMeta.image_url : '';
    const c = tpl.colors || {};
    const p = safeHex(c.primary, '#0f766e');
    const a = safeHex(c.accent, '#d97706');

    if (mode === 'reports') {
      const sec = document.createElement('div');
      sec.className = 'single-page-report canva-embedded-page';
      sec.setAttribute('data-canva-embedded-page', '1');
      sec.setAttribute('data-canva-page-idx', String(pageIdx));
      sec.style.cssText = 'position:relative;width:794px;min-height:1123px;padding:0;overflow:hidden;background:#ffffff;margin:0 auto 20px auto;box-sizing:border-box;';
      sec.innerHTML = `
        <div class="edit-only no-print canva-embedded-controls" style="position:absolute;top:10px;right:10px;left:10px;z-index:20;display:flex;align-items:center;justify-content:space-between;gap:8px;background:rgba(15,23,42,0.84);color:#fff;padding:6px 12px;border-radius:10px;font-family:'Cairo',sans-serif;font-size:12px;">
          <span style="font-weight:800;">🎨 صفحة قالب كانفا المدمجة (${pageIdx}/${totalCount}) — ${escHtml(tpl.name)}</span>
          <div style="display:flex;gap:6px;align-items:center;">
            ${tpl.processed_pdf_url ? `<a href="${escHtml(tpl.processed_pdf_url)}?download=1" download style="background:${a};color:#fff;text-decoration:none;padding:3px 9px;border-radius:6px;font-weight:700;">📥 PDF</a>` : ''}
            <button type="button" onclick="this.closest('[data-canva-embedded-page]').remove()" style="background:#ef4444;color:#fff;border:none;padding:3px 9px;border-radius:6px;font-weight:700;cursor:pointer;font-family:inherit;">🗑️ حذف الصفحة</button>
          </div>
        </div>
        <img src="${escHtml(imgUrl)}" alt="${escHtml(tpl.name)}" style="width:100%;height:1123px;object-fit:contain;display:block;background:#ffffff;">
      `;
      return sec;
    }

    const pg = document.createElement('div');
    pg.className = 'page canva-embedded-page';
    pg.setAttribute('data-canva-embedded-page', '1');
    pg.setAttribute('data-canva-page-idx', String(pageIdx));
    pg.style.cssText = 'position:relative;padding:0 !important;overflow:hidden;background:#ffffff;display:flex;align-items:center;justify-content:center;';
    pg.innerHTML = `
      <div class="edit-only no-print canva-embedded-controls" style="position:absolute;top:10px;right:10px;left:10px;z-index:20;display:flex;align-items:center;justify-content:space-between;gap:8px;background:rgba(15,23,42,0.84);color:#fff;padding:6px 12px;border-radius:10px;font-family:'Cairo',sans-serif;font-size:12px;">
        <span style="font-weight:800;">🎨 صفحة قالب كانفا المدمجة (${pageIdx}/${totalCount}) — ${escHtml(tpl.name)}</span>
        <div style="display:flex;gap:6px;align-items:center;">
          ${tpl.processed_pdf_url ? `<a href="${escHtml(tpl.processed_pdf_url)}?download=1" download style="background:${p};color:#fff;text-decoration:none;padding:3px 9px;border-radius:6px;font-weight:700;">📥 PDF</a>` : ''}
          <button type="button" onclick="this.closest('[data-canva-embedded-page]').remove()" style="background:#ef4444;color:#fff;border:none;padding:3px 9px;border-radius:6px;font-weight:700;cursor:pointer;font-family:inherit;">🗑️ حذف الصفحة</button>
        </div>
      </div>
      <img src="${escHtml(imgUrl)}" alt="${escHtml(tpl.name)}" style="width:100%;height:100%;object-fit:contain;display:block;background:#ffffff;">
    `;
    return pg;
  }

  function injectEmbeddedCanvaPages(tpl, mode) {
    removeInjectedCanvaPages();
    if (!tpl) return 0;

    const mergeMode = tpl.merge_mode || 'dedicated_and_theme';
    const embedPos = tpl.embed_position || 'after_cover';

    let pagesList = Array.isArray(tpl.processed_pages) ? tpl.processed_pages.filter(p => p && p.image_url) : [];
    if (!pagesList.length) {
      const fallbackUrl = getSafeImageSrc(tpl);
      if (fallbackUrl) pagesList = [{ page_index: 1, image_url: fallbackUrl }];
    }
    if (!pagesList.length) return 0;

    const container = mode === 'reports' ? document.getElementById('mainContainer') : document.getElementById('pagesWrap');
    if (!container) return 0;

    // 1. إذا كان الوضع يشمل تضمين الإطار/الخلفية على الغلاف وصفحات الشواهد
    if (mergeMode === 'background_frame') {
      const p1Url = pagesList[0].image_url;
      const targetPages = mode === 'reports'
        ? Array.from(container.querySelectorAll(':scope > .cover, :scope > .report'))
        : Array.from(container.querySelectorAll(':scope > .page'));
      targetPages.forEach((tp, idx) => {
        if (idx === 0 || tp.querySelector('.witness-table, table.eval-table, .evidence-grid')) {
          tp.classList.add('canva-frame-page-applied');
          const bgDiv = document.createElement('div');
          bgDiv.className = 'canva-bg-layer';
          bgDiv.style.cssText = `position:absolute;inset:0;z-index:0;pointer-events:none;background-image:url("${p1Url}");background-size:cover;background-position:center;opacity:${idx === 0 ? '0.20' : '0.12'};`;
          if (getComputedStyle(tp).position === 'static') tp.style.position = 'relative';
          tp.insertBefore(bgDiv, tp.firstChild);
        }
      });
    }

    // 2. إدراج الصفحات المخصصة المعالجة داخل الملف (A4 PNG)
    const frag = document.createDocumentFragment();
    pagesList.forEach((pm, idx) => {
      frag.appendChild(buildEmbeddedPageElement(mode, tpl, pm, pm.page_index || (idx + 1), pagesList.length));
    });

    const effectivePos = mergeMode === 'cover_replace' ? 'as_cover' : embedPos;
    if (mode === 'reports') {
      const coverEl = container.querySelector(':scope > .cover');
      if (effectivePos === 'as_cover') {
        container.insertBefore(frag, container.firstElementChild);
      } else if (effectivePos === 'after_cover' && coverEl) {
        coverEl.after(frag);
      } else {
        container.appendChild(frag);
      }
      if (typeof global.initPageControls === 'function') {
        try { global.initPageControls(); } catch (_) {}
      }
    } else {
      const existingPages = Array.from(container.querySelectorAll(':scope > .page'));
      if (effectivePos === 'as_cover' || !existingPages.length) {
        container.insertBefore(frag, container.firstElementChild);
      } else if (effectivePos === 'after_cover') {
        existingPages[0].after(frag);
      } else {
        container.appendChild(frag);
      }
    }

    return pagesList.length;
  }

  function getOrCreateInlineDock(mode) {
    ensureStylesInjected();
    const resolvedMode = mode || detectPageMode() || currentMode;
    let dock = document.getElementById('ecsInlineDock');
    if (!dock) {
      dock = document.createElement('div');
      dock.id = 'ecsInlineDock';
      dock.className = 'no-print edit-only ' + (resolvedMode === 'reports' ? 'dock-reports' : 'dock-below-fixed');
      const anchorTarget = document.getElementById('pagesWrap') || document.getElementById('mainContainer');
      if (anchorTarget && anchorTarget.parentNode) {
        anchorTarget.parentNode.insertBefore(dock, anchorTarget);
      } else {
        document.body.insertBefore(dock, document.body.firstChild);
      }
    }
    return dock;
  }

  function syncDockVisibility() {
    const dock = document.getElementById('ecsInlineDock');
    if (!dock) return;
    const modalVisible = Boolean(document.getElementById(MODAL_ID)?.classList.contains('show'));
    const hasBanner = Boolean(document.getElementById('ecsMergedStatusBanner'));
    dock.classList.toggle('has-content', modalVisible || hasBanner);
  }

  let currentMergedTpl = null;

  function renderMergedStatusBanner(tpl) {
    const mode = detectPageMode();
    if (!mode) return;
    let banner = document.getElementById('ecsMergedStatusBanner');
    if (!tpl) {
      if (banner) banner.remove();
      syncDockVisibility();
      return;
    }
    if (!banner) {
      const dock = getOrCreateInlineDock(mode);
      banner = document.createElement('div');
      banner.id = 'ecsMergedStatusBanner';
      banner.className = 'no-print edit-only';
      banner.style.cssText = 'position:relative;z-index:60;direction:rtl;font-family:"Cairo",sans-serif;padding:9px 14px;border-radius:12px;margin-bottom:8px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;box-shadow:0 4px 14px rgba(0,0,0,0.16);border:1.5px solid rgba(255,255,255,0.32);';
      dock.insertBefore(banner, dock.firstChild);
    }
    syncDockVisibility();
    const c = tpl.colors || {};
    const p = safeHex(c.primary, '#0f766e');
    const s = safeHex(c.secondary, '#1e3a8a');
    const a = safeHex(c.accent, '#f59e0b');
    const pgCount = Number(tpl.processed_page_count || (tpl.processed_pages || []).length || 1);
    const fmtLabel = tpl.processed_format || 'PNG + PDF (A4)';
    const curMode = tpl.merge_mode || 'dedicated_and_theme';
    const curPos = tpl.embed_position || 'after_cover';

    banner.style.background = `linear-gradient(135deg, ${p}, ${s})`;
    banner.style.color = '#ffffff';
    banner.innerHTML = `
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <span style="background:rgba(255,255,255,0.22);padding:3px 9px;border-radius:6px;font-size:12px;font-weight:900;">${isLivePreviewUnsaved ? '👁️ معاينة حية لقالب كانفا' : '🎨 قالب كانفا المدمج'}</span>
        <strong style="font-size:13.5px;">${escHtml(tpl.name)}</strong>
        <span style="background:${isLivePreviewUnsaved ? '#f59e0b' : '#10b981'};color:#fff;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:800;">${isLivePreviewUnsaved ? '⏳ معاينة غير مثبتة' : `✅ ${escHtml(fmtLabel)} • ${pgCount} صفحة`}</span>
        <select id="ecsBannerMergeMode" style="background:rgba(255,255,255,0.95);color:#0f172a;border:none;border-radius:6px;padding:3px 7px;font-family:inherit;font-size:11.5px;font-weight:800;cursor:pointer;">
          <option value="dedicated_and_theme" ${curMode === 'dedicated_and_theme' ? 'selected' : ''}>صفحات القالب + الألوان</option>
          <option value="embedded_pages_only" ${curMode === 'embedded_pages_only' ? 'selected' : ''}>صفحات القالب فقط</option>
          <option value="background_frame" ${curMode === 'background_frame' ? 'selected' : ''}>خلفية وإطار + صفحات</option>
          <option value="cover_replace" ${curMode === 'cover_replace' ? 'selected' : ''}>في صفحة الغلاف الأولى</option>
        </select>
        <select id="ecsBannerEmbedPos" style="background:rgba(255,255,255,0.95);color:#0f172a;border:none;border-radius:6px;padding:3px 7px;font-family:inherit;font-size:11.5px;font-weight:800;cursor:pointer;">
          <option value="after_cover" ${curPos === 'after_cover' ? 'selected' : ''}>بعد الغلاف</option>
          <option value="as_cover" ${curPos === 'as_cover' ? 'selected' : ''}>غلاف أول</option>
          <option value="before_end" ${curPos === 'before_end' ? 'selected' : ''}>قسم الشواهد/النهاية</option>
        </select>
      </div>
      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
        ${isLivePreviewUnsaved ? `<button type="button" id="ecsBannerConfirmSave" style="background:#22c55e;color:#fff;border:none;padding:5px 12px;border-radius:7px;font-family:inherit;font-size:12px;font-weight:900;cursor:pointer;">✅ تثبيت وحفظ الدمج بالملف</button>` : ''}
        ${tpl.processed_pdf_url ? `<a href="${escHtml(tpl.processed_pdf_url)}?download=1" download style="background:${a};color:#fff;text-decoration:none;padding:5px 10px;border-radius:7px;font-family:inherit;font-size:12px;font-weight:800;">📥 القالب PDF</a>` : ''}
        <button type="button" id="ecsBannerExportFullPdf" style="background:#ffffff;color:#0f172a;border:none;padding:5px 11px;border-radius:7px;font-family:inherit;font-size:12px;font-weight:800;cursor:pointer;">📄 تصدير الملف المدمج PDF</button>
        <button type="button" onclick="EduCanvaStudio.previewMergedDocument()" style="background:rgba(255,255,255,0.22);color:#fff;border:1px solid rgba(255,255,255,0.45);padding:5px 10px;border-radius:7px;font-family:inherit;font-size:12px;font-weight:700;cursor:pointer;">🖨️ معاينة قالب A4</button>
        <button type="button" onclick="EduCanvaStudio.open('${mode}')" style="background:rgba(255,255,255,0.18);color:#fff;border:1px solid rgba(255,255,255,0.4);padding:5px 10px;border-radius:7px;font-family:inherit;font-size:12px;font-weight:700;cursor:pointer;">🔄 اختيار قالب آخر</button>
        <button type="button" onclick="EduCanvaStudio.clearMergedTemplate()" style="background:#ef4444;color:#fff;border:none;padding:5px 10px;border-radius:7px;font-family:inherit;font-size:12px;font-weight:700;cursor:pointer;">✖ إلغاء الدمج</button>
      </div>
    `;

    banner.querySelector('#ecsBannerMergeMode')?.addEventListener('change', (e) => {
      const updated = { ...tpl, merge_mode: e.target.value };
      applyMergedTemplate(updated, !isLivePreviewUnsaved);
    });
    banner.querySelector('#ecsBannerEmbedPos')?.addEventListener('change', (e) => {
      const updated = { ...tpl, embed_position: e.target.value };
      applyMergedTemplate(updated, !isLivePreviewUnsaved);
    });
    banner.querySelector('#ecsBannerConfirmSave')?.addEventListener('click', () => {
      persistCurrentMergedTemplate();
    });
    banner.querySelector('#ecsBannerExportFullPdf')?.addEventListener('click', () => {
      if (typeof global.exportPDF === 'function') global.exportPDF();
      else previewMergedDocument();
    });
  }

  async function applyMergedTemplate(tpl, persist = true, options = {}) {
    if (!tpl) return;
    const mode = detectPageMode();
    if (!mode) return;

    isLivePreviewUnsaved = Boolean(options.previewOnly);

    // التأكد من وجود النسخة المعالجة (PNG + PDF) إذا لم تكن موجودة في البيانات
    let readyTpl = tpl;
    if (!readyTpl.processed || !Array.isArray(readyTpl.processed_pages) || !readyTpl.processed_pages.length) {
      readyTpl = await processTemplateForMerge(readyTpl);
    }
    currentMergedTpl = readyTpl;

    const mergeMode = readyTpl.merge_mode || 'dedicated_and_theme';
    const c = readyTpl.colors || {};
    const p = safeHex(c.primary, '#3b6978');
    const s = safeHex(c.secondary, '#204051');
    const a = safeHex(c.accent, '#c9a86a');
    const bg = safeHex(c.bg, '#fafbfd');

    const root = document.documentElement;
    const cssVars = [
      '--primary', '--primary-teal', '--purple', '--border', '--border-color',
      '--dark', '--dark-teal', '--primary-dark', '--secondary',
      '--accent', '--accent-light', '--light', '--light-teal', '--lavender',
    ];
    if (mergeMode === 'embedded_pages_only') {
      cssVars.forEach(v => root.style.removeProperty(v));
    } else {
      root.style.setProperty('--primary', p);
      root.style.setProperty('--primary-teal', p);
      root.style.setProperty('--purple', p);
      root.style.setProperty('--border', p);
      root.style.setProperty('--border-color', p);
      root.style.setProperty('--dark', s);
      root.style.setProperty('--dark-teal', s);
      root.style.setProperty('--primary-dark', s);
      root.style.setProperty('--secondary', s);
      root.style.setProperty('--accent', a);
      root.style.setProperty('--accent-light', a);
      root.style.setProperty('--light', a);
      root.style.setProperty('--light-teal', a);
      root.style.setProperty('--lavender', a);
    }

    let cssEl = document.getElementById('ecsMergedThemeCss');
    if (!cssEl) {
      cssEl = document.createElement('style');
      cssEl.id = 'ecsMergedThemeCss';
      document.head.appendChild(cssEl);
    }
    const layout = readyTpl.layout || 'gradient_arch';
    let layoutAccentCss = `.page:not(.canva-embedded-page), .report-container { border-top: 6px solid ${p} !important; }`;
    if (layout === 'royal_double') {
      layoutAccentCss = `.page:not(.canva-embedded-page), .report-container { box-shadow: inset 0 0 0 3px ${p}, inset 0 0 0 7px ${a} !important; }`;
    } else if (layout === 'botanical_frame') {
      layoutAccentCss = `.page:not(.canva-embedded-page), .report-container { border: 2px solid ${p} !important; border-radius: 14px !important; box-shadow: inset 0 0 0 5px ${a}24 !important; }`;
    } else if (layout === 'clean_stripe') {
      layoutAccentCss = `.page:not(.canva-embedded-page), .report-container { border-right: 12px solid ${p} !important; }`;
    } else if (layout === 'modern_ribbon') {
      layoutAccentCss = `.page:not(.canva-embedded-page), .report-container { border-top: 8px solid ${a} !important; border-bottom: 8px solid ${p} !important; }`;
    }

    const embeddedSheetCss = `
      .page.canva-embedded-page, .single-page-report.canva-embedded-page {
        padding: 0 !important;
        background: #ffffff !important;
        border: none !important;
      }
      .canva-frame-page-applied > *:not(.canva-bg-layer) {
        position: relative;
        z-index: 2;
      }
      @media print {
        #ecsMergedStatusBanner, #${MODAL_ID}, .canva-embedded-controls { display: none !important; }
        .page.canva-embedded-page, .single-page-report.canva-embedded-page {
          width: 210mm !important; height: 297mm !important; padding: 0 !important;
          margin: 0 !important; box-shadow: none !important; page-break-after: always; break-after: page;
        }
      }
      body.pdf-exporting .page.canva-embedded-page,
      body.pdf-exporting .single-page-report.canva-embedded-page {
        width: 794px !important; min-width: 794px !important; max-width: 794px !important;
        height: 1123px !important; min-height: 1123px !important;
        padding: 0 !important; margin: 0 !important; box-shadow: none !important;
      }
    `;

    cssEl.textContent = (mergeMode === 'embedded_pages_only')
      ? embeddedSheetCss
      : `
        ${embeddedSheetCss}
        ${layoutAccentCss}
        .page:not(.canva-embedded-page) .banner,
        .page:not(.canva-embedded-page) .cover-banner,
        .report-header, .text-page-header, .section-header {
          background: linear-gradient(135deg, ${p}, ${s}) !important;
          border-color: ${a} !important;
          color: #ffffff !important;
        }
        .table-title, .cv-card h3, .vision-card h3 { color: ${p} !important; border-color: ${a} !important; }
        table thead th, .edu-table th { background: ${p} !important; color: #ffffff !important; }
        .page:not(.canva-embedded-page) { background-color: ${bg} !important; }
      `;

    injectEmbeddedCanvaPages(readyTpl, mode);
    renderMergedStatusBanner(readyTpl);

    if (persist) {
      isLivePreviewUnsaved = false;
      try {
        localStorage.setItem('ecs_merged_template_' + mode, JSON.stringify(stripForStorage(readyTpl)));
      } catch (_) {}
      renderMergedStatusBanner(readyTpl);
    }
  }

  function persistCurrentMergedTemplate() {
    const mode = detectPageMode();
    if (!mode || !currentMergedTpl) return;
    isLivePreviewUnsaved = false;
    try {
      localStorage.setItem('ecs_merged_template_' + mode, JSON.stringify(stripForStorage(currentMergedTpl)));
    } catch (_) {}
    renderMergedStatusBanner(currentMergedTpl);
    closeStudio();
    if (typeof global.setStatus === 'function') {
      global.setStatus(`✅ تم تثبيت ودمج قالب "${currentMergedTpl.name}" في الملف`);
    }
  }

  function clearMergedTemplate() {
    const mode = detectPageMode();
    currentMergedTpl = null;
    isLivePreviewUnsaved = false;
    removeInjectedCanvaPages();
    document.getElementById('ecsMergedThemeCss')?.remove();
    document.getElementById('ecsMergedStatusBanner')?.remove();
    syncDockVisibility();
    const vars = [
      '--primary', '--primary-teal', '--purple', '--border', '--border-color',
      '--dark', '--dark-teal', '--primary-dark', '--secondary',
      '--accent', '--accent-light', '--light', '--light-teal', '--lavender',
    ];
    vars.forEach(v => document.documentElement.style.removeProperty(v));
    if (mode) {
      try {
        localStorage.removeItem('ecs_merged_template_' + mode);
        localStorage.removeItem('ecs_pending_merge_' + mode);
      } catch (_) {}
    }
  }

  function previewMergedDocument() {
    const mode = detectPageMode();
    if (!mode) return;
    let tpl = currentMergedTpl;
    if (!tpl) {
      try {
        tpl = JSON.parse(localStorage.getItem('ecs_merged_template_' + mode) || 'null');
      } catch (_) {}
    }
    openStudio(mode);
    if (tpl) {
      applyContentToTemplates([tpl]);
    }
  }

  async function livePreviewOnDoc(id) {
    const mode = detectPageMode();
    if (!mode) return;
    const tpl = catalogTemplates.find(x => x.id === id) || fetchedTemplates.find(x => x.id === id) || appliedPreviews.find(x => x.template.id === id)?.template;
    if (!tpl) return;
    const opts = getSelectedMergeOptions();
    showStatus(`⏳ جاري تجهيز معاينة القالب "${tpl.name}" على صفحات ${TARGET_LABELS[mode] || 'الملف'}...`);
    const processed = await processTemplateForMerge(tpl);
    const enriched = {
      ...processed,
      merge_mode: opts.merge_mode || 'dedicated_and_theme',
      embed_position: opts.embed_position || 'after_cover',
    };
    await applyMergedTemplate(enriched, false, { previewOnly: true });
    showStatus(`👁️ تمت المعاينة الحية للقالب "${tpl.name}" على صفحات الملف بالأسفل — اضغط "✅ تثبيت وحفظ الدمج" لاعتماده.`);
    const targetDoc = document.getElementById('pagesWrap') || document.getElementById('mainContainer');
    if (targetDoc) {
      targetDoc.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  async function applyActiveThemeToDocument() {
    const item = appliedPreviews.find(x => x.template.id === activeAppliedId);
    if (!item) return;
    const opts = getSelectedMergeOptions();
    showStatus(`⏳ جاري معالجة القالب "${item.template.name}" وتحويله إلى (PNG A4 + PDF) وتضمينه بالملف...`);
    const processed = await processTemplateForMerge(item.template);
    const enriched = {
      ...processed,
      merge_mode: opts.merge_mode,
      embed_position: opts.embed_position,
    };
    await applyMergedTemplate(enriched, true);
    closeStudio();
    const pgCount = enriched.processed_page_count || (enriched.processed_pages || []).length || 1;
    showStatus(`✅ تمت معالجة القالب (${pgCount} صفحة PNG + PDF) وتضمينه مباشرة في ${TARGET_LABELS[currentMode] || 'الملف الحالي'}!`);
  }

  function checkPendingMerge() {
    const mode = detectPageMode();
    if (!mode) return;
    let applied = false;
    try {
      const pendRaw = localStorage.getItem('ecs_pending_merge_' + mode);
      if (pendRaw) {
        const pend = JSON.parse(pendRaw);
        localStorage.removeItem('ecs_pending_merge_' + mode);
        if (pend && pend.template) {
          applyMergedTemplate(pend.template, true);
          applied = true;
        }
      }
      if (!applied) {
        const savedRaw = localStorage.getItem('ecs_merged_template_' + mode);
        if (savedRaw) {
          const saved = JSON.parse(savedRaw);
          if (saved && saved.name) applyMergedTemplate(saved, false);
        }
      }
    } catch (_) {}
  }

  function populateReportsScopeSelector() {
    const area = document.getElementById('ecsDocScopeArea');
    if (!area) return;
    const mode = detectPageMode() || currentMode;
    if (mode !== 'reports') {
      area.innerHTML = '<span style="font-size:13px;font-weight:800;color:#334155;">📋 المحتوى المستخرج من ملفك الحالي جاهز للتطبيق والدمج تلقائياً.</span>';
      return;
    }
    const reps = Array.from(document.querySelectorAll('#mainContainer .report, #mainContainer .single-page-report'));
    const opts = reps.map((r, i) => {
      const t = cleanText(r.querySelector('.report-title')) || `تقرير ${i + 1}`;
      return `<option value="${i}">${escHtml(t.substring(0, 65))}</option>`;
    }).join('');
    area.innerHTML = `<label style="font-size:13px;font-weight:800;color:#334155;">نطاق التطبيق:</label>
      <select id="ecsReportFilterSelect" class="ecs-input" style="max-width:340px;">
        <option value="all">جميع التقارير والصفحات (${reps.length})</option>
        ${opts}
      </select>`;
  }

  function openStudio(mode) {
    const detected = mode || detectPageMode();
    if (!detected) return;
    currentMode = detected;
    injectStylesAndModal();
    populateReportsScopeSelector();
    const dock = document.getElementById(MODAL_ID);
    if (dock) {
      dock.classList.add('show');
      syncDockVisibility();
      dock.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    switchTab('browse');
    if (!catalogTemplates.length) {
      loadCatalog(false);
    } else {
      renderBrowseGrid();
      renderFetchedGrid();
      updateCounts();
    }
  }

  function closeStudio() {
    document.getElementById(MODAL_ID)?.classList.remove('show');
    syncDockVisibility();
  }

  function toggleStudio(mode) {
    const dock = document.getElementById(MODAL_ID);
    if (dock && dock.classList.contains('show')) {
      closeStudio();
    } else {
      openStudio(mode);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkPendingMerge);
  } else {
    checkPendingMerge();
  }
  window.addEventListener('eduCanvaReapply', checkPendingMerge);

  async function mergeDirectToCurrentDoc(id) {
    const mode = detectPageMode();
    if (!mode) return;
    const tpl = catalogTemplates.find(x => x.id === id) || fetchedTemplates.find(x => x.id === id) || appliedPreviews.find(x => x.template.id === id)?.template;
    if (!tpl) return;
    const opts = getSelectedMergeOptions();
    showStatus(`⏳ جاري معالجة قالب "${tpl.name}" وتحويله إلى (PNG A4 + PDF) وتضمينه بالملف...`);
    const processed = await processTemplateForMerge(tpl);
    const enriched = {
      ...processed,
      merge_mode: opts.merge_mode || 'dedicated_and_theme',
      embed_position: opts.embed_position || 'after_cover',
    };
    await applyMergedTemplate(enriched, true);
    closeStudio();
    const pgCount = enriched.processed_page_count || (enriched.processed_pages || []).length || 1;
    showStatus(`✅ تمت معالجة القالب (${pgCount} صفحة PNG + PDF) وتضمينه في ${TARGET_LABELS[mode] || 'الملف'}!`);
  }

  global.EduCanvaStudio = {
    open: openStudio,
    toggle: toggleStudio,
    close: closeStudio,
    toggleSelect,
    openInternalViewer,
    closeInternalViewer,
    fetchSingleAndApply,
    applySingle,
    removeFetched,
    selectApplied,
    livePreviewOnDoc,
    mergeDirectToCurrentDoc,
    persistCurrentMergedTemplate,
    processTemplateForMerge,
    applyMergedTemplate,
    clearMergedTemplate,
    checkPendingMerge,
    previewMergedDocument,
  };
})(window);
