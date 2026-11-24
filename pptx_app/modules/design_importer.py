# -*- coding: utf-8 -*-
"""إدارة واستيراد قوالب كانفا (Canva) وعروضها، وحسابات Google المرتبطة."""

import hashlib
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup

import config as _cfg
from pptx_app.modules.templates import CANVA_TEMPLATES

CANVA_CACHE_FILE = os.path.join(_cfg.DATA_DIR, "canva_imported_templates.json")
GOOGLE_ACCOUNTS_FILE = os.path.join(_cfg.DATA_DIR, "canva_google_accounts.json")
EDU_CANVA_PROCESSED_DIR = os.path.join(_cfg.DATA_DIR, "edu_canva_processed")


def _safe_asset_id(raw_id: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_-]", "_", str(raw_id or "canva_tpl")).strip("_")
    return (clean or "canva_tpl")[:64]


def _hex_to_rgb(hex_color: str, default=(15, 118, 110)) -> tuple:
    s = str(hex_color or "").strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) == 6:
        try:
            return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
        except Exception:
            pass
    return default


def _render_a4_canvas_from_pil(
    im,
    bg_hex: str = "#ffffff",
    primary_hex: str = "#0f766e",
    accent_hex: str = "#d97706",
):
    """ملاءمة أي صورة أو صفحة من كانفا على مقاس A4 قياسي (1240x1754) دون قص أو تشويه."""
    from PIL import Image, ImageDraw
    A4_W, A4_H = 1240, 1754
    src = im.convert("RGB") if im.mode not in ("RGB", "RGBA") else im
    if src.mode == "RGBA":
        flat = Image.new("RGB", src.size, (255, 255, 255))
        flat.paste(src, mask=src.split()[3])
        src = flat

    w, h = max(1, src.width), max(1, src.height)
    ratio = h / float(w)

    # إذا كانت الصورة عمودية بنسبة قريبة من A4 نكبرها/نصغرها مباشرة لملء صفحة A4 بالكامل
    if 1.24 <= ratio <= 1.56:
        return src.resize((A4_W, A4_H), Image.Resampling.LANCZOS)

    # خلاف ذلك نضعها على لوحة A4 أنيقة بإطار ألوان القالب مع الحفاظ على نسبة الأبعاد الأصلية
    bg_rgb = _hex_to_rgb(bg_hex, (248, 250, 252))
    p_rgb = _hex_to_rgb(primary_hex, (15, 118, 110))
    a_rgb = _hex_to_rgb(accent_hex, (217, 119, 6))

    canvas = Image.new("RGB", (A4_W, A4_H), bg_rgb)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([24, 24, A4_W - 24, A4_H - 24], outline=p_rgb, width=6)
    draw.rectangle([38, 38, A4_W - 38, A4_H - 38], outline=a_rgb, width=2)

    max_w = A4_W - 110
    max_h = A4_H - 140
    scale = min(max_w / float(w), max_h / float(h))
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    resized = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
    x = (A4_W - new_w) // 2
    y = (A4_H - new_h) // 2
    canvas.paste(resized, (x, y))
    return canvas


def _render_styled_a4_fallback(tpl: Dict[str, Any]):
    """إنشاء صفحة A4 أنيقة بألوان وتخطيط القالب إذا لم تتوفر صورة خام قابلة للتحميل."""
    from PIL import Image, ImageDraw
    A4_W, A4_H = 1240, 1754
    colors = tpl.get("colors") or {}
    p_rgb = _hex_to_rgb(colors.get("primary"), (15, 118, 110))
    s_rgb = _hex_to_rgb(colors.get("secondary"), (30, 58, 138))
    a_rgb = _hex_to_rgb(colors.get("accent"), (217, 119, 6))
    bg_rgb = _hex_to_rgb(colors.get("bg"), (248, 250, 252))
    layout = (tpl.get("layout") or "gradient_arch").strip()

    canvas = Image.new("RGB", (A4_W, A4_H), bg_rgb)
    draw = ImageDraw.Draw(canvas)

    if layout == "royal_double":
        draw.rectangle([28, 28, A4_W - 28, A4_H - 28], outline=p_rgb, width=10)
        draw.rectangle([48, 48, A4_W - 48, A4_H - 48], outline=a_rgb, width=4)
        draw.rectangle([72, 72, A4_W - 72, 270], fill=p_rgb)
        draw.rectangle([72, 260, A4_W - 72, 274], fill=a_rgb)
    elif layout == "clean_stripe":
        draw.rectangle([A4_W - 44, 0, A4_W, A4_H], fill=p_rgb)
        draw.rectangle([A4_W - 56, 0, A4_W - 44, A4_H], fill=a_rgb)
        draw.rectangle([48, 48, A4_W - 96, 220], fill=p_rgb)
    elif layout == "botanical_frame":
        draw.rounded_rectangle([30, 30, A4_W - 30, A4_H - 30], radius=36, outline=p_rgb, width=7)
        draw.rounded_rectangle([50, 50, A4_W - 50, A4_H - 50], radius=26, outline=a_rgb, width=3)
        draw.rounded_rectangle([90, 90, A4_W - 90, 290], radius=24, fill=p_rgb)
    elif layout == "modern_ribbon":
        draw.rectangle([0, 0, A4_W, 28], fill=a_rgb)
        draw.rectangle([0, A4_H - 28, A4_W, A4_H], fill=p_rgb)
        draw.rounded_rectangle([70, 80, A4_W - 70, 270], radius=18, fill=s_rgb)
    else:
        # gradient_arch / default
        draw.rectangle([0, 0, A4_W, 56], fill=p_rgb)
        draw.rectangle([0, 56, A4_W, 70], fill=a_rgb)
        draw.rounded_rectangle([68, 108, A4_W - 68, 300], radius=20, fill=s_rgb)
        draw.rectangle([68, 290, A4_W - 68, 304], fill=a_rgb)

    # مساحة محتوى منظمة في المنتصف مع تذييل زخرفي
    draw.rounded_rectangle([78, 340, A4_W - 78, A4_H - 130], radius=18, fill=(255, 255, 255), outline=p_rgb, width=2)
    draw.rectangle([78, A4_H - 102, A4_W - 78, A4_H - 96], fill=a_rgb)
    return canvas


def _save_processed_pages_and_pdf(
    asset_id: str,
    pil_pages: List[Any],
    existing_pdf_bytes: Optional[bytes] = None,
) -> Dict[str, Any]:
    """حفظ الصفحات المعالجة كصور PNG قياسية A4 وملف PDF متوافق في مجلد الأصول المحلي."""
    import io
    safe_id = _safe_asset_id(asset_id)
    out_dir = os.path.join(EDU_CANVA_PROCESSED_DIR, safe_id)
    os.makedirs(out_dir, exist_ok=True)

    if not pil_pages:
        raise ValueError("لا توجد صفحات صالحة بعد معالجة القالب")

    processed_pages = []
    rgb_pages = []
    for idx, page_im in enumerate(pil_pages[:12], start=1):
        rgb = page_im.convert("RGB")
        rgb_pages.append(rgb)
        fname = f"page_{idx:02d}.png"
        fpath = os.path.join(out_dir, fname)
        rgb.save(fpath, format="PNG", optimize=True)
        processed_pages.append({
            "page_index": idx,
            "image_url": f"/api/edu/canva/asset/{safe_id}/{fname}",
            "width": rgb.width,
            "height": rgb.height,
        })

    pdf_path = os.path.join(out_dir, "template.pdf")
    if existing_pdf_bytes:
        with open(pdf_path, "wb") as pf:
            pf.write(existing_pdf_bytes)
    else:
        pdf_buf = io.BytesIO()
        first = rgb_pages[0]
        rest = rgb_pages[1:]
        first.save(pdf_buf, format="PDF", resolution=150.0, save_all=True, append_images=rest)
        with open(pdf_path, "wb") as pf:
            pf.write(pdf_buf.getvalue())

    return {
        "processed": True,
        "processed_asset_id": safe_id,
        "processed_format": "PNG + PDF (A4)",
        "processed_page_count": len(processed_pages),
        "processed_pdf_url": f"/api/edu/canva/asset/{safe_id}/template.pdf",
        "processed_pages": processed_pages,
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def _render_pdf_bytes_to_pil_pages(
    pdf_bytes: bytes,
    max_pages: int = 12,
    bg_hex: str = "#ffffff",
    primary_hex: str = "#0f766e",
    accent_hex: str = "#d97706",
) -> List[Any]:
    """تحويل صفحات ملف PDF إلى صور PIL عالية الدقة باستخدام Ghostscript ثم مواءمتها على A4."""
    import io
    import shutil
    import subprocess
    import tempfile
    from PIL import Image
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(pdf_bytes))
    num_pages = min(len(reader.pages), max_pages)
    if num_pages <= 0:
        raise ValueError("ملف PDF لا يحتوي على صفحات")

    gs_bin = shutil.which("gs") or "/usr/bin/gs"
    if not os.path.exists(gs_bin):
        raise ValueError("أداة Ghostscript غير متوفرة لتحويل ملف PDF")

    tmp_dir = tempfile.mkdtemp(prefix="canva_pdf_")
    try:
        in_pdf = os.path.join(tmp_dir, "input.pdf")
        with open(in_pdf, "wb") as f:
            f.write(pdf_bytes)
        out_pat = os.path.join(tmp_dir, "pg_%02d.png")
        cmd = [
            gs_bin, "-dSAFER", "-dBATCH", "-dNOPAUSE",
            "-sDEVICE=png16m", "-r150",
            "-dFirstPage=1", f"-dLastPage={num_pages}",
            f"-sOutputFile={out_pat}", in_pdf,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        if proc.returncode != 0:
            raise ValueError(f"فشل تحويل PDF إلى صور: {(proc.stderr or proc.stdout)[:160]}")

        rendered = []
        for idx in range(1, num_pages + 1):
            p_file = os.path.join(tmp_dir, f"pg_{idx:02d}.png")
            if os.path.exists(p_file):
                with Image.open(p_file) as im:
                    rendered.append(_render_a4_canvas_from_pil(im, bg_hex=bg_hex, primary_hex=primary_hex, accent_hex=accent_hex))
        if not rendered:
            raise ValueError("تعذر استخراج صفحات من ملف PDF")
        return rendered
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _try_canva_api_export_pdf_bytes(canva_id: str, canva_token: str) -> Optional[bytes]:
    """محاولة تصدير التصميم الأصلي كملف PDF من Canva Connect API إذا توفر رمز وصول صالح."""
    tok = (canva_token or "").strip()
    cid = (canva_id or "").strip()
    if not tok or not cid:
        return None
    headers = {
        "Authorization": f"Bearer {tok}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        r = requests.post(
            "https://api.canva.com/rest/v1/exports",
            headers=headers,
            json={"design_id": cid, "format": {"type": "pdf"}},
            timeout=12,
        )
        if not r.ok:
            return None
        job = (r.json() or {}).get("job") or r.json() or {}
        job_id = job.get("id")
        if not job_id:
            return None
        import time as _t
        for _ in range(12):
            _t.sleep(1.2)
            pr = requests.get(f"https://api.canva.com/rest/v1/exports/{job_id}", headers=headers, timeout=10)
            if not pr.ok:
                break
            pdata = (pr.json() or {}).get("job") or pr.json() or {}
            status = (pdata.get("status") or "").lower()
            if status == "completed":
                urls = pdata.get("urls") or []
                if urls:
                    dl = requests.get(urls[0], timeout=20)
                    if dl.ok and dl.content.startswith(b"%PDF"):
                        return dl.content
                break
            if status == "failed":
                break
    except Exception:
        pass
    return None


def _load_json(path: str, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def _save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _extract_canva_slug_and_id(url: str) -> tuple[str, str]:
    """استخراج اسم القالب ومعرف التصميم (11 محرفاً) من رابط كانفا بأسلوب دقيق."""
    clean = (url or "").strip()
    path_part = clean.split("?")[0].rstrip("/")
    segs = [s for s in path_part.split("/") if s]
    canva_id = ""
    raw_slug = ""

    m_design = re.search(r"/design/([A-Za-z0-9_-]{8,})", path_part)
    m_tpl = re.search(r"/templates/([^/?#]+)", path_part)
    if m_design:
        canva_id = m_design.group(1)
        last_seg = segs[-1] if segs else ""
        if last_seg in ("view", "edit", "watch") and len(segs) >= 2:
            last_seg = segs[-2]
        raw_slug = "" if last_seg == canva_id else last_seg
    elif m_tpl:
        seg = m_tpl.group(1)
        m_11 = re.match(r"^([DE]A[A-Za-z0-9_-]{9})(?:-(.+))?$", seg)
        if m_11:
            canva_id = m_11.group(1)
            raw_slug = m_11.group(2) or ""
        else:
            m_any = re.match(r"^([DE]A[A-Za-z0-9_]{6,})(?:-(.+))?$", seg)
            if m_any:
                canva_id = m_any.group(1)
                raw_slug = m_any.group(2) or ""
            else:
                raw_slug = seg
    else:
        last_seg = segs[-1] if segs else ""
        raw_slug = last_seg

    slug = re.sub(r"[-_]+", " ", raw_slug).strip()
    if slug and len(slug) >= 3:
        return slug.title()[:70], canva_id
    return "", canva_id


def _is_bot_challenge_title(title: str) -> bool:
    t = (title or "").strip().lower()
    if not t:
        return True
    blocked = (
        "client challenge",
        "just a moment",
        "attention required",
        "access denied",
        "verify you are human",
        "cloudflare",
        "captcha",
        "canva",
    )
    return t in blocked or any(b in t for b in ("client challenge", "just a moment", "attention required", "access denied"))


def _fetch_canva_oembed(url: str) -> Dict[str, str]:
    """محاولة جلب بيانات oEmbed الرسمية لقالب/تصميم كانفا."""
    out: Dict[str, str] = {}
    try:
        r = requests.get(
            "https://www.canva.com/_ajax/oembed",
            params={"url": url},
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0 Safari/537.36"},
        )
        if r.ok and r.text:
            raw = re.sub(r"^[^\{]*", "", r.text.strip())
            if raw.startswith("{"):
                data = json.loads(raw)
                t = (data.get("title") or "").strip()
                if t and not _is_bot_challenge_title(t):
                    out["title"] = t[:75]
                th = (data.get("thumbnail_url") or "").strip()
                if th.startswith("http"):
                    out["thumbnail_url"] = th
    except Exception:
        pass
    return out


class DesignImporter:
    def get_all_designs(self, category: str = "all", keyword: str = "") -> List[Dict[str, Any]]:
        """إرجاع جميع قوالب كانفا المدمجة + القوالب والعروض المستوردة من كانفا."""
        custom = _load_json(CANVA_CACHE_FILE, [])
        if not isinstance(custom, list):
            custom = []
        combined = custom + list(CANVA_TEMPLATES)

        kw = (keyword or "").strip().lower()
        cat = (category or "all").strip()
        results = []
        for d in combined:
            if cat != "all" and d.get("category", "") != cat:
                continue
            if kw:
                hay = f"{d.get('name','')} {d.get('category','')} {d.get('source','')} {d.get('description','')}".lower()
                if kw not in hay:
                    continue
            results.append(d)
        return results

    def get_design_by_id(self, design_id: str) -> Optional[Dict[str, Any]]:
        if not design_id:
            return None
        for d in self.get_all_designs():
            if d.get("id") == design_id:
                return d
        return None

    def import_canva_url(
        self,
        url: str,
        custom_name: str = "",
        category: str = "تصاميمي المجلوبة",
    ) -> Dict[str, Any]:
        """استيراد رابط تصميم أو قالب من كانفا وتحويله لقالب قابل للتطبيق المباشر."""
        clean_url = (url or "").strip()
        if not clean_url.startswith(("http://", "https://")):
            raise ValueError("يرجى إدخال رابط كانفا صحيح يبدأ بـ https://")

        slug_title, canva_id = _extract_canva_slug_and_id(clean_url)
        title = (custom_name or "").strip()
        preview_image = ""
        extracted_theme_color = None

        # 1) محاولة oEmbed الرسمية أولاً
        oe = _fetch_canva_oembed(clean_url)
        if not title and oe.get("title"):
            title = oe["title"]
        if oe.get("thumbnail_url"):
            preview_image = oe["thumbnail_url"]

        # 2) محاولة قراءة الوسوم المفتوحة مع تجاهل صفحة Client Challenge تماماً
        if not title or not preview_image:
            try:
                resp = requests.get(
                    clean_url,
                    timeout=6,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"},
                    allow_redirects=True,
                )
                if resp.ok and resp.text and "client challenge" not in resp.text[:4000].lower():
                    soup = BeautifulSoup(resp.text[:120000], "lxml")
                    if not title:
                        og_t = soup.find("meta", property="og:title")
                        cand_t = ""
                        if og_t and og_t.get("content"):
                            cand_t = og_t["content"].replace("| Canva", "").replace("- Canva", "").strip()
                        elif soup.find("title"):
                            cand_t = soup.find("title").get_text(strip=True)[:80]
                        if cand_t and not _is_bot_challenge_title(cand_t):
                            title = cand_t
                    if not preview_image:
                        og_img = soup.find("meta", property="og:image")
                        if og_img and og_img.get("content"):
                            preview_image = og_img["content"].strip()
                    theme_meta = soup.find("meta", attrs={"name": "theme-color"})
                    if theme_meta and theme_meta.get("content"):
                        extracted_theme_color = theme_meta["content"].strip()
            except Exception:
                pass

        # 3) إذا كان الرابط لقالب كانفا (/templates/EA...) ولم ترجع الصورة، نبحث في CDN كانفا marketplace.canva.com
        if not preview_image and canva_id:
            found_mp = _lookup_marketplace_image_by_id(canva_id)
            if found_mp:
                preview_image = found_mp

        if not title or _is_bot_challenge_title(title):
            title = slug_title or (f"تصميم كانفا ({canva_id[:10]})" if canva_id else "قالب كانفا مستورد")

        canva_embed_url = ""
        if canva_id and "/design/" in clean_url:
            canva_embed_url = f"https://www.canva.com/design/{canva_id}/view?embed"

        # لوحة ألوان تلقائية + حفظ نسخة Base64 من الصورة إن توفرت للعرض الفوري
        import base64 as _b64
        palette = None
        safe_data_url = ""
        if preview_image:
            try:
                ir = requests.get(preview_image, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
                ctype = (ir.headers.get("Content-Type") or "").split(";")[0].strip().lower()
                if ir.ok and ctype.startswith("image/") and len(ir.content) < 4_000_000:
                    palette = _extract_palette_from_image_bytes(ir.content)
                    safe_data_url = f"data:{ctype};base64,{_b64.b64encode(ir.content).decode('ascii')}"
            except Exception:
                pass

        primary = extracted_theme_color if (extracted_theme_color and extracted_theme_color.startswith("#")) else "#008B94"
        item_id = "canva_url_" + hashlib.md5(clean_url.encode("utf-8")).hexdigest()[:8]
        tpl = {
            "id": item_id,
            "name": title[:75],
            "title": title[:75],
            "category": category or "تصاميمي المجلوبة",
            "source": "رابط Canva مستورد",
            "theme_color": "blue",
            "layout": _infer_layout_from_text(f"{slug_title} {clean_url}"),
            "font_name": "Cairo",
            "description": f"قالب كانفا مستورد داخل الأداة ({canva_id or clean_url[:48]})",
            "colors": palette or {
                "primary": primary,
                "secondary": "#0F2942",
                "accent": "#00C4CC",
                "bg": "#F4F8FB",
                "card_bg": "#FFFFFF",
                "text_dark": "#0F172A",
                "text_light": "#FFFFFF",
            },
            "canva_url": clean_url,
            "canva_embed_url": canva_embed_url,
            "preview_image": preview_image,
            "safe_preview_data_url": safe_data_url,
            "badge_text": "رابط كانفا",
            "imported_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        tpl = _normalize_edu_template(tpl)

        existing = _load_json(CANVA_CACHE_FILE, [])
        if not isinstance(existing, list):
            existing = []
        existing = [x for x in existing if x.get("id") != item_id]
        existing.insert(0, tpl)
        _save_json(CANVA_CACHE_FILE, existing[:35])
        return tpl

    def import_canva_uploaded_file(
        self,
        filename: str,
        raw_bytes: bytes,
        custom_name: str = "",
        category: str = "تصاميمي المجلوبة",
    ) -> Dict[str, Any]:
        """استيراد ومعالجة تصميم مصدّر من كانفا (صورة أو PDF أو PPTX) وتحويله لصيغة متوافقة (PNG A4 + PDF)."""
        import base64 as _b64
        import io
        from PIL import Image
        if not raw_bytes:
            raise ValueError("الملف المرفوع فارغ")
        ext = os.path.splitext(filename or "")[1].lower()
        base_title = (custom_name or "").strip() or re.sub(r"[-_]+", " ", os.path.splitext(os.path.basename(filename or "تصميم كانفا"))[0]).strip() or "تصميم كانفا مستورد"
        fid = "canva_file_" + hashlib.md5(raw_bytes[:65536] + base_title.encode("utf-8")).hexdigest()[:8]

        palette = None
        safe_data_url = ""
        pil_pages: List[Any] = []
        existing_pdf_bytes: Optional[bytes] = None

        if ext in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
            try:
                im = Image.open(io.BytesIO(raw_bytes))
                palette = _extract_palette_from_image_bytes(raw_bytes) or {
                    "primary": "#0f766e", "secondary": "#134e4a", "accent": "#d97706",
                    "bg": "#f8fafc", "card_bg": "#ffffff", "text_dark": "#0f172a", "text_light": "#ffffff",
                }
                a4_im = _render_a4_canvas_from_pil(
                    im,
                    bg_hex=palette.get("bg", "#ffffff"),
                    primary_hex=palette.get("primary", "#0f766e"),
                    accent_hex=palette.get("accent", "#d97706"),
                )
                pil_pages = [a4_im]
                thumb = im.convert("RGB")
                thumb.thumbnail((1100, 1550))
                buf = io.BytesIO()
                thumb.save(buf, format="JPEG", quality=86)
                safe_data_url = "data:image/jpeg;base64," + _b64.b64encode(buf.getvalue()).decode("ascii")
            except Exception as exc:
                raise ValueError(f"تعذر قراءة ومعالجة صورة القالب: {exc}")
        elif ext == ".pdf":
            try:
                pil_pages = _render_pdf_bytes_to_pil_pages(raw_bytes, max_pages=12)
                existing_pdf_bytes = raw_bytes
                buf_p1 = io.BytesIO()
                thumb = pil_pages[0].copy()
                thumb.thumbnail((1100, 1550))
                thumb.save(buf_p1, format="JPEG", quality=86)
                p1_bytes = buf_p1.getvalue()
                palette = _extract_palette_from_image_bytes(p1_bytes)
                safe_data_url = "data:image/jpeg;base64," + _b64.b64encode(p1_bytes).decode("ascii")
            except Exception as exc:
                raise ValueError(f"تعذر معالجة ملف PDF المصدّر من كانفا: {exc}")
        elif ext == ".pptx":
            try:
                from pptx import Presentation
                prs = Presentation(io.BytesIO(raw_bytes))
                found_hex = []
                slide_pil_candidates = []
                for slide in list(prs.slides)[:8]:
                    best_blob = None
                    try:
                        fill = slide.background.fill
                        if fill.type and hasattr(fill.fore_color, "rgb") and fill.fore_color.rgb:
                            found_hex.append("#" + str(fill.fore_color.rgb))
                    except Exception:
                        pass
                    for shp in slide.shapes:
                        try:
                            if shp.fill.type and hasattr(shp.fill.fore_color, "rgb") and shp.fill.fore_color.rgb:
                                found_hex.append("#" + str(shp.fill.fore_color.rgb))
                        except Exception:
                            pass
                        try:
                            if hasattr(shp, "image") and shp.image and shp.image.blob:
                                if best_blob is None or len(shp.image.blob) > len(best_blob):
                                    best_blob = shp.image.blob
                        except Exception:
                            pass
                    if best_blob:
                        try:
                            slide_pil_candidates.append(Image.open(io.BytesIO(best_blob)))
                        except Exception:
                            pass

                uniq = [h for i, h in enumerate(found_hex) if h.lower() not in ("#ffffff", "#000000") and h not in found_hex[:i]]
                p_c = uniq[0] if len(uniq) >= 1 else "#1e3a8a"
                s_c = uniq[1] if len(uniq) >= 2 else "#0f2357"
                a_c = uniq[2] if len(uniq) >= 3 else "#d97706"
                palette = {
                    "primary": p_c,
                    "secondary": s_c,
                    "accent": a_c,
                    "bg": "#f8fafc",
                    "card_bg": "#ffffff",
                    "text_dark": "#0f172a",
                    "text_light": "#ffffff",
                }
                if slide_pil_candidates:
                    pil_pages = [
                        _render_a4_canvas_from_pil(im, bg_hex="#f8fafc", primary_hex=p_c, accent_hex=a_c)
                        for im in slide_pil_candidates[:8]
                    ]
                    buf = io.BytesIO()
                    th = pil_pages[0].copy()
                    th.thumbnail((1100, 1550))
                    th.save(buf, format="JPEG", quality=86)
                    safe_data_url = "data:image/jpeg;base64," + _b64.b64encode(buf.getvalue()).decode("ascii")
            except Exception as exc:
                raise ValueError(f"تعذر قراءة ملف PowerPoint المصدّر من كانفا: {exc}")
        else:
            raise ValueError("الصيغ المدعومة هي صور (PNG / JPG / WebP) أو PDF أو عروض PowerPoint (.pptx) المصدّرة من كانفا")

        default_pal = palette or {
            "primary": "#0f766e",
            "secondary": "#134e4a",
            "accent": "#d97706",
            "bg": "#f8fafc",
            "card_bg": "#ffffff",
            "text_dark": "#0f172a",
            "text_light": "#ffffff",
        }

        tpl = {
            "id": fid,
            "name": base_title[:75],
            "category": category or "تصاميمي المجلوبة",
            "source": "ملف Canva مستورد",
            "layout": _infer_layout_from_text(base_title),
            "font_family": "Cairo",
            "heading_font": "Amiri",
            "description": f"قالب مستورد مباشرة من ملف كانفا ({os.path.basename(filename)})",
            "colors": default_pal,
            "safe_preview_data_url": safe_data_url,
            "badge_text": "ملف PDF كانفا" if ext == ".pdf" else "ملف كانفا",
            "imported_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        if not pil_pages:
            pil_pages = [_render_styled_a4_fallback(tpl)]
        proc_meta = _save_processed_pages_and_pdf(fid, pil_pages, existing_pdf_bytes=existing_pdf_bytes)
        tpl.update(proc_meta)
        tpl = _normalize_edu_template(tpl)

        existing = _load_json(CANVA_CACHE_FILE, [])
        if not isinstance(existing, list):
            existing = []
        existing = [x for x in existing if x.get("id") != fid]
        existing.insert(0, tpl)
        _save_json(CANVA_CACHE_FILE, existing[:35])
        return tpl

    def fetch_canva_api_designs(self, access_token: str) -> List[Dict[str, Any]]:
        """جلب تصاميم وقوالب المستخدم الفعلية من Canva Connect API عند توفر رمز OAuth."""
        tok = (access_token or "").strip()
        if not tok:
            raise ValueError("رمز الوصول (Canva Access Token) مطلوب")
        headers = {"Authorization": f"Bearer {tok}", "Accept": "application/json"}
        resp = requests.get("https://api.canva.com/rest/v1/designs", headers=headers, timeout=12)
        if not resp.ok:
            raise ValueError(f"رفضت واجهة Canva API الطلب (HTTP {resp.status_code})")
        payload = resp.json() or {}
        items = list(payload.get("items") or [])

        # محاولة جلب Brand Templates أيضاً إذا توفرت الصلاحية
        try:
            bt_resp = requests.get("https://api.canva.com/rest/v1/brand-templates", headers=headers, timeout=8)
            if bt_resp.ok:
                for bt in (bt_resp.json() or {}).get("items") or []:
                    bt["_is_brand_template"] = True
                    items.append(bt)
        except Exception:
            pass

        fetched: List[Dict[str, Any]] = []
        palettes = [
            ("#0F2942", "#1D4E89", "#F59E0B", "#F8FAFC"),
            ("#008B94", "#0F3D5E", "#00C4CC", "#F0FDFA"),
            ("#4C1D95", "#2E1065", "#F59E0B", "#FAF5FF"),
            ("#E11D48", "#9F1239", "#FB7185", "#FFF1F2"),
        ]
        for idx, it in enumerate(items[:25]):
            did = str(it.get("id", f"canva_api_{idx}"))
            title = (it.get("title") or "تصميم كانفا بدون عنوان").strip()
            urls = it.get("urls") or {}
            view_url = urls.get("view_url") or it.get("view_url") or ""
            edit_url = urls.get("edit_url") or it.get("create_url") or view_url or f"https://www.canva.com/design/{did}/view"
            thumb = ((it.get("thumbnail") or {}).get("url") or "").strip()
            p_col, s_col, a_col, bg_col = palettes[idx % len(palettes)]
            embed_url = f"https://www.canva.com/design/{did}/view?embed" if not it.get("_is_brand_template") else ""
            fetched.append({
                "id": f"canva_api_{did}",
                "name": f"{title} (حسابي في كانفا)",
                "category": "تصاميمي",
                "source": "حساب Canva المتصل",
                "theme_color": "blue",
                "layout": "modern_card",
                "font_name": "Cairo",
                "description": "تصميم مجلوب مباشرة من حسابك في كانفا",
                "colors": {
                    "primary": p_col,
                    "secondary": s_col,
                    "accent": a_col,
                    "bg": bg_col,
                    "card_bg": "#FFFFFF",
                    "text_dark": "#0F172A",
                    "text_light": "#FFFFFF",
                },
                "canva_url": view_url or edit_url,
                "canva_embed_url": embed_url,
                "preview_image": thumb,
                "badge_text": "حسابي في كانفا",
                "imported_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })

        if fetched:
            existing = _load_json(CANVA_CACHE_FILE, [])
            if not isinstance(existing, list):
                existing = []
            fetched_ids = {x["id"] for x in fetched}
            kept = [x for x in existing if x.get("id") not in fetched_ids]
            _save_json(CANVA_CACHE_FILE, (fetched + kept)[:40])
        return fetched

    # ── إدارة حسابات Google المتصلة للدخول السريع إلى كانفا ──
    def get_google_accounts(self) -> Dict[str, Any]:
        data = _load_json(GOOGLE_ACCOUNTS_FILE, {"accounts": [], "active_email": ""})
        if not isinstance(data, dict):
            data = {"accounts": [], "active_email": ""}
        data.setdefault("accounts", [])
        data.setdefault("active_email", "")
        return data

    def save_google_account(
        self,
        email: str,
        name: str = "",
        photo_url: str = "",
        provider: str = "google",
        set_active: bool = True,
    ) -> Dict[str, Any]:
        clean_email = (email or "").strip().lower()
        if not clean_email or "@" not in clean_email:
            raise ValueError("البريد الإلكتروني لحساب Google غير صحيح")

        store = self.get_google_accounts()
        accounts = [a for a in store["accounts"] if a.get("email", "").lower() != clean_email]
        display_name = (name or "").strip() or clean_email.split("@")[0]
        entry = {
            "email": clean_email,
            "name": display_name,
            "photo_url": (photo_url or "").strip(),
            "provider": provider or "google",
            "last_used": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        accounts.insert(0, entry)
        store["accounts"] = accounts[:15]
        if set_active or not store.get("active_email"):
            store["active_email"] = clean_email
        _save_json(GOOGLE_ACCOUNTS_FILE, store)
        return store

    def select_google_account(self, email: str) -> Dict[str, Any]:
        clean_email = (email or "").strip().lower()
        store = self.get_google_accounts()
        found = next((a for a in store["accounts"] if a.get("email", "").lower() == clean_email), None)
        if not found:
            raise ValueError("الحساب غير موجود في القائمة المحفوظة")
        found["last_used"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        store["active_email"] = clean_email
        _save_json(GOOGLE_ACCOUNTS_FILE, store)
        return store

    def remove_google_account(self, email: str) -> Dict[str, Any]:
        clean_email = (email or "").strip().lower()
        store = self.get_google_accounts()
        store["accounts"] = [a for a in store["accounts"] if a.get("email", "").lower() != clean_email]
        if store.get("active_email", "").lower() == clean_email:
            store["active_email"] = store["accounts"][0]["email"] if store["accounts"] else ""
        _save_json(GOOGLE_ACCOUNTS_FILE, store)
        return store


# ── قوالب كانفا التعليمية A4 الموثّقة والحقيقية (ملفات أداء / شواهد / تقارير / شهادات) ──
EDU_CANVA_FETCHED_FILE = os.path.join(_cfg.DATA_DIR, "edu_canva_fetched.json")
EDU_CANVA_BROWSE_CACHE_FILE = os.path.join(_cfg.DATA_DIR, "edu_canva_browse_cache.json")
EDU_CANVA_LIVE_CACHE_FILE = os.path.join(_cfg.DATA_DIR, "edu_canva_live_cache.json")


def _infer_layout_from_text(text: str) -> str:
    low = (text or "").lower()
    if any(k in low for k in ("floral", "flower", "botanical", "watercolor", "garden", "rose", "lavender", "leaf")):
        return "botanical_frame"
    if any(k in low for k in ("gold", "diploma", "certificate", "royal", "award", "luxury", "formal", "classic")):
        return "royal_double"
    if any(k in low for k in ("pink", "pastel", "thank-you", "soft", "cute", "vintage", "cream", "beige")):
        return "pastel_card"
    if any(k in low for k in ("geometric", "bold", "abstract", "modern-bold", "infographic", "tech", "cyan")):
        return "geometric_split"
    if any(k in low for k in ("minimal", "minimalist", "clean", "brief", "resume", "cv", "stripe", "blanco")):
        return "clean_stripe"
    if any(k in low for k in ("ribbon", "planner", "schedule", "orange", "coral", "warm")):
        return "modern_ribbon"
    return "gradient_arch"


EDU_CANVA_TEMPLATES: List[Dict[str, Any]] = [
    {
        "id": "canva_tpl_EAF-1kLSdBs",
        "canva_id": "EAF-1kLSdBs",
        "name": "قالب كانفا — تقرير الأداء والإنجاز السنوي A4",
        "category": "تقارير مدرسية",
        "source": "Canva Marketplace",
        "layout": "royal_double",
        "font_family": "Cairo",
        "heading_font": "Amiri",
        "description": "قالب كانفا A4 رسمي بالزيتي والذهبي المعتمد لتقارير الإنجاز والملفات السنوية.",
        "colors": {
            "primary": "#2f5d50",
            "secondary": "#1d3b32",
            "accent": "#d4a448",
            "bg": "#fafaf7",
            "card_bg": "#ffffff",
            "text_dark": "#13221d",
            "text_light": "#ffffff",
        },
        "preview_image": "https://marketplace.canva.com/EAF-1kLSdBs/1/0/1131w/canva-green-and-yellow-simple-annual-report-a4-document-dgpah4kY-f0.jpg",
        "canva_url": "https://www.canva.com/templates/EAF-1kLSdBs-green-and-yellow-simple-annual-report-a4-document/",
        "badge_text": "Canva A4 تقرير",
    },
    {
        "id": "canva_tpl_EAG-5dQh2hI",
        "canva_id": "EAG-5dQh2hI",
        "name": "قالب كانفا — الفيروزي والأزرق للتقارير الحديثة A4",
        "category": "ملفات أداء وإنجاز",
        "source": "Canva Marketplace",
        "layout": "gradient_arch",
        "font_family": "Cairo",
        "heading_font": "Amiri",
        "description": "تصميم كانفا فيروزي حديث بتنسيق A4 منظّم لملفات الأداء الوظيفي والجداول.",
        "colors": {
            "primary": "#1f5f74",
            "secondary": "#123c4a",
            "accent": "#4ebbdf",
            "bg": "#f4f9fb",
            "card_bg": "#ffffff",
            "text_dark": "#0f242c",
            "text_light": "#ffffff",
        },
        "preview_image": "https://marketplace.canva.com/EAG-5dQh2hI/1/0/283w/canva-blue-and-teal-modern-supermarket-annual-report-a4-GizZY_IqcS0.jpg",
        "canva_url": "https://www.canva.com/templates/EAG-5dQh2hI-blue-and-teal-modern-annual-report-a4/",
        "badge_text": "Canva A4 أداء",
    },
    {
        "id": "canva_tpl_EAF-BzwpAQk",
        "canva_id": "EAF-BzwpAQk",
        "name": "قالب كانفا — الإطار الزهري المائي الأزرق A4",
        "category": "شواهد وتوثيق",
        "source": "Canva Marketplace",
        "layout": "botanical_frame",
        "font_family": "Cairo",
        "heading_font": "Amiri",
        "description": "تصميم كانفا ناعم بألوان مائية وزهور زرقاء مثالي لتوثيق الشواهد والسيرة التربوية.",
        "colors": {
            "primary": "#2f5d80",
            "secondary": "#1b3a52",
            "accent": "#7fb0d9",
            "bg": "#f7fbff",
            "card_bg": "#ffffff",
            "text_dark": "#152635",
            "text_light": "#ffffff",
        },
        "preview_image": "https://marketplace.canva.com/EAF-BzwpAQk/1/0/400w/canva-blue-watercolor-floral-blank-background-document-a4-%28landscape%29-7z1qpPONOYQ.jpg",
        "canva_url": "https://www.canva.com/templates/EAF-BzwpAQk-blue-watercolor-floral-blank-background-document-a4/",
        "badge_text": "Canva شواهد",
    },
    {
        "id": "canva_tpl_EAF-CqXas4E",
        "canva_id": "EAF-CqXas4E",
        "name": "قالب كانفا — الوردي الكلاسيكي الهادئ A4",
        "category": "شواهد وتوثيق",
        "source": "Canva Marketplace",
        "layout": "pastel_card",
        "font_family": "Cairo",
        "heading_font": "Amiri",
        "description": "قالب كانفا أنيق بالوردي الهادئ والإطارات الكلاسيكية لملفات المعلمات والشواهد.",
        "colors": {
            "primary": "#8c4a58",
            "secondary": "#5c2d37",
            "accent": "#e09f97",
            "bg": "#fff8f8",
            "card_bg": "#ffffff",
            "text_dark": "#2d181e",
            "text_light": "#ffffff",
        },
        "preview_image": "https://marketplace.canva.com/EAF-CqXas4E/1/0/566w/canva-pink-vintage-thank-you-letter-a4-9gvBKO2ywtY.jpg",
        "canva_url": "https://www.canva.com/templates/EAF-CqXas4E-pink-vintage-thank-you-letter-a4/",
        "badge_text": "Canva A4 ناعم",
    },
    {
        "id": "canva_tpl_EAG-5Ng6h30",
        "canva_id": "EAG-5Ng6h30",
        "name": "قالب كانفا — البنفسجي المعماري الحديث A4",
        "category": "ملفات أداء وإنجاز",
        "source": "Canva Marketplace",
        "layout": "clean_stripe",
        "font_family": "Cairo",
        "heading_font": "Amiri",
        "description": "تصميم كانفا بنفسجي وعاجي بلمسة تنفيذية راقية لعرض معايير الأداء الوظيفي.",
        "colors": {
            "primary": "#564a8e",
            "secondary": "#382f62",
            "accent": "#c9a86a",
            "bg": "#faf8ff",
            "card_bg": "#ffffff",
            "text_dark": "#1d1833",
            "text_light": "#ffffff",
        },
        "preview_image": "https://marketplace.canva.com/EAG-5Ng6h30/1/0/1131w/canva-documento-a4-brief-para-proyecto-moderno-morado-beige-negro-VnEvWKVIxnQ.jpg",
        "canva_url": "https://www.canva.com/templates/EAG-5Ng6h30-documento-a4-brief-para-proyecto-moderno/",
        "badge_text": "Canva A4 ملف",
    },
    {
        "id": "canva_tpl_EAF-JNz4vIQ",
        "canva_id": "EAF-JNz4vIQ",
        "name": "قالب كانفا — الأخضر والذهبي للشهادات والتكريم",
        "category": "شهادات وتكريم",
        "source": "Canva Marketplace",
        "layout": "royal_double",
        "font_family": "Cairo",
        "heading_font": "Amiri",
        "description": "تصميم كانفا زمردي وذهبي فخم مناسب لشهادات التقدير والتكريم والشواهد الرسمية.",
        "colors": {
            "primary": "#14532d",
            "secondary": "#052e16",
            "accent": "#d97706",
            "bg": "#fafaf5",
            "card_bg": "#ffffff",
            "text_dark": "#13261a",
            "text_light": "#ffffff",
        },
        "preview_image": "https://marketplace.canva.com/EAF-JNz4vIQ/1/0/400w/canva-green-and-gold-modern-sport-competition-certificate-landscape-ja1wKVOZM40.jpg",
        "canva_url": "https://www.canva.com/templates/EAF-JNz4vIQ-green-and-gold-modern-certificate/",
        "badge_text": "Canva شهادة",
    },
    {
        "id": "canva_tpl_EAF-tJtgCxA",
        "canva_id": "EAF-tJtgCxA",
        "name": "قالب كانفا — العنابي والذهبي للشهادات التقديرية",
        "category": "شهادات وتكريم",
        "source": "Canva Marketplace",
        "layout": "modern_ribbon",
        "font_family": "Cairo",
        "heading_font": "Amiri",
        "description": "تصميم كانفا فخم بالعنابي العميق والذهبي لإبراز الشهادات والمنجزات التربوية.",
        "colors": {
            "primary": "#7f1d1d",
            "secondary": "#450a0a",
            "accent": "#eab308",
            "bg": "#fffaf8",
            "card_bg": "#ffffff",
            "text_dark": "#291212",
            "text_light": "#ffffff",
        },
        "preview_image": "https://marketplace.canva.com/EAF-tJtgCxA/1/0/400w/canva-red-and-yellow-minimalist-certificate-of-appreciation-QPPDeBB-7BM.jpg",
        "canva_url": "https://www.canva.com/templates/EAF-tJtgCxA-red-and-yellow-minimalist-certificate-of-appreciation/",
        "badge_text": "Canva تقدير",
    },
    {
        "id": "canva_tpl_EAF-dadDGhw",
        "canva_id": "EAF-dadDGhw",
        "name": "قالب كانفا — الأزرق الملكي والبرتقالي لبورتفوليو الإنجاز",
        "category": "ملفات أداء وإنجاز",
        "source": "Canva Marketplace",
        "layout": "geometric_split",
        "font_family": "Cairo",
        "heading_font": "Cairo",
        "description": "هوية كانفا جريئة بالأزرق الكوبالت والعنبر مثالية لبورتفوليو المعلم وتوثيق المبادرات.",
        "colors": {
            "primary": "#124698",
            "secondary": "#0c2f67",
            "accent": "#f59e0b",
            "bg": "#f5f8ff",
            "card_bg": "#ffffff",
            "text_dark": "#0f1e3a",
            "text_light": "#ffffff",
        },
        "preview_image": "https://marketplace.canva.com/EAF-dadDGhw/1/0/400w/canva-modern-bold-graphic-designer-creative-portfolio-presentation-W_nnHi_vuJI.jpg",
        "canva_url": "https://www.canva.com/templates/EAF-dadDGhw-modern-bold-creative-portfolio-presentation/",
        "badge_text": "Canva بورتفوليو",
    },
    {
        "id": "canva_tpl_EAF-D6D5Q8Q",
        "canva_id": "EAF-D6D5Q8Q",
        "name": "قالب كانفا — البيج والذهب الدافئ للتخطيط الأسبوعي A4",
        "category": "شواهد وتوثيق",
        "source": "Canva Marketplace",
        "layout": "pastel_card",
        "font_family": "Cairo",
        "heading_font": "Amiri",
        "description": "تصميم كانفا هادئ بالبيج والذهبي الرملي يناسب الخطط والجداول والملفات التنظيمية.",
        "colors": {
            "primary": "#6e5c4f",
            "secondary": "#463930",
            "accent": "#c8a97e",
            "bg": "#fdfaf6",
            "card_bg": "#ffffff",
            "text_dark": "#261e18",
            "text_light": "#ffffff",
        },
        "preview_image": "https://marketplace.canva.com/EAF-D6D5Q8Q/1/0/566w/canva-beige-and-gold-minimal-weekly-a4-planner-VPvaDK9Stjw.jpg",
        "canva_url": "https://www.canva.com/templates/EAF-D6D5Q8Q-beige-and-gold-minimal-weekly-a4-planner/",
        "badge_text": "Canva A4 خطط",
    },
    {
        "id": "canva_tpl_EAF-5dONlxQ",
        "canva_id": "EAF-5dONlxQ",
        "name": "قالب كانفا — الرمادي الرسمي التحريري A4",
        "category": "تقارير مدرسية",
        "source": "Canva Marketplace",
        "layout": "clean_stripe",
        "font_family": "Cairo",
        "heading_font": "Amiri",
        "description": "خطوط تحريرية نظيفة ومستند رسمي عالي الوضوح للتقارير المدرسية والخطابات المعتمدة.",
        "colors": {
            "primary": "#2d3748",
            "secondary": "#1a202c",
            "accent": "#0d9488",
            "bg": "#ffffff",
            "card_bg": "#f8fafc",
            "text_dark": "#0f172a",
            "text_light": "#ffffff",
        },
        "preview_image": "https://marketplace.canva.com/EAF-5dONlxQ/1/0/1131w/canva-documento-a4-carta-formal-blanco-y-gris-vCza1-eQ7gQ.jpg",
        "canva_url": "https://www.canva.com/templates/EAF-5dONlxQ-documento-a4-carta-formal-blanco-y-gris/",
        "badge_text": "Canva A4 رسمي",
    },
    {
        "id": "canva_tpl_EAG-d21lfTM",
        "canva_id": "EAG-d21lfTM",
        "name": "قالب كانفا — الأزرق الهندسي لتقارير البرامج والأنشطة",
        "category": "تقارير مدرسية",
        "source": "Canva Marketplace",
        "layout": "geometric_split",
        "font_family": "Cairo",
        "heading_font": "Cairo",
        "description": "تصميم كانفا هندسي بدرجات الأزرق والأردوازي لتقارير البرامج والأنشطة الطلابية.",
        "colors": {
            "primary": "#2b4596",
            "secondary": "#1b2c63",
            "accent": "#38bdf8",
            "bg": "#f3f6ff",
            "card_bg": "#ffffff",
            "text_dark": "#101b3d",
            "text_light": "#ffffff",
        },
        "preview_image": "https://marketplace.canva.com/EAG-d21lfTM/1/0/400w/canva-blue-gray-bold-social-media-report-presentation-_m7kW6xIZmE.jpg",
        "canva_url": "https://www.canva.com/templates/EAG-d21lfTM-blue-gray-bold-report-presentation/",
        "badge_text": "Canva تقارير",
    },
    {
        "id": "canva_tpl_EAF--nReQEY",
        "canva_id": "EAF--nReQEY",
        "name": "قالب كانفا — المدرسي التوضيحي الأزرق A4",
        "category": "تقارير مدرسية",
        "source": "Canva Marketplace",
        "layout": "gradient_arch",
        "font_family": "Cairo",
        "heading_font": "Cairo",
        "description": "قالب كانفا تعليمي مشرق مناسب للجداول المدرسية والأنشطة والتقارير الصفية.",
        "colors": {
            "primary": "#26538d",
            "secondary": "#16355e",
            "accent": "#60a5fa",
            "bg": "#f0f7ff",
            "card_bg": "#ffffff",
            "text_dark": "#10233d",
            "text_light": "#ffffff",
        },
        "preview_image": "https://marketplace.canva.com/EAF--nReQEY/1/0/400w/canva-biru-putih-ilustratif-jadwal-pelajaran-sekolah-a4-lanskap-IxOupTK0efI.jpg",
        "canva_url": "https://www.canva.com/templates/EAF--nReQEY-school-schedule-a4/",
        "badge_text": "Canva مدرسي",
    },
]


def _extract_palette_from_image_bytes(raw_bytes: bytes) -> Optional[Dict[str, str]]:
    """استخراج لوحة ألوان عالية التباين من صورة قالب كانفا المجلوب عند توفر Pillow."""
    try:
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        img.thumbnail((64, 64))
        pixels = list(img.get_flattened_data()) if hasattr(img, "get_flattened_data") else list(img.getdata())
        chromatic = [
            (r, g, b) for (r, g, b) in pixels
            if (max(r, g, b) - min(r, g, b)) > 22 and 20 < (r + g + b) / 3 < 235
        ]
        if not chromatic:
            return None
        chromatic.sort(key=lambda c: (max(c) - min(c)), reverse=True)
        r0, g0, b0 = chromatic[min(len(chromatic) - 1, max(0, len(chromatic) // 8))]

        # ضمان تباين واضح للنص الأبيض فوق الترويسة (luminance <= 105)
        lum = 0.2126 * r0 + 0.7152 * g0 + 0.0722 * b0
        scale = min(0.82, 102.0 / max(lum, 1.0)) if lum > 102 else 0.85
        pr = max(18, min(180, int(r0 * scale)))
        pg = max(18, min(180, int(g0 * scale)))
        pb = max(18, min(180, int(b0 * scale)))
        sr = max(12, int(pr * 0.68))
        sg = max(12, int(pg * 0.68))
        sb = max(12, int(pb * 0.68))
        ar, ag, ab = chromatic[0]
        return {
            "primary": f"#{pr:02x}{pg:02x}{pb:02x}",
            "secondary": f"#{sr:02x}{sg:02x}{sb:02x}",
            "accent": f"#{ar:02x}{ag:02x}{ab:02x}",
            "bg": "#fafbfd",
            "card_bg": "#ffffff",
            "text_dark": "#0f172a",
            "text_light": "#ffffff",
        }
    except Exception:
        return None


def _build_edu_canva_thumb_data_url(tpl: Dict[str, Any]) -> str:
    """إنشاء معاينة SVG احتياطية فقط عند تعذر تحميل الصورة الأصلية من كانفا."""
    import base64
    from html import escape as _esc

    c = tpl.get("colors") or {}
    p = str(c.get("primary") or "#3b6978")
    s = str(c.get("secondary") or "#204051")
    a = str(c.get("accent") or "#c9a86a")
    bg = str(c.get("bg") or "#f8fafc")
    layout = str(tpl.get("layout") or "gradient_arch")
    badge = _esc(str(tpl.get("badge_text") or tpl.get("category") or "Canva A4")[:24])
    title = _esc(str(tpl.get("name") or "قالب كانفا تعليمي").replace("قالب كانفا — ", "")[:34])

    if layout == "royal_double":
        frame_svg = (
            f'<rect x="14" y="14" width="372" height="232" rx="10" fill="none" stroke="{p}" stroke-width="3"/>'
            f'<rect x="21" y="21" width="358" height="218" rx="7" fill="none" stroke="{a}" stroke-width="1.5"/>'
        )
    elif layout == "botanical_frame":
        frame_svg = (
            f'<rect x="14" y="14" width="372" height="232" rx="18" fill="none" stroke="{p}" stroke-width="2.4"/>'
            f'<circle cx="32" cy="32" r="10" fill="{a}" opacity="0.35"/>'
            f'<circle cx="368" cy="228" r="12" fill="{p}" opacity="0.22"/>'
        )
    elif layout == "clean_stripe":
        frame_svg = f'<rect x="374" y="0" width="26" height="260" fill="url(#g1)"/>'
    else:
        frame_svg = f'<path d="M0,0 H400 V72 Q200,98 0,72 Z" fill="url(#g1)"/>'

    header_block = (
        f'<rect x="32" y="28" width="336" height="54" rx="10" fill="url(#g1)"/>'
        if layout in ("royal_double", "botanical_frame", "pastel_card")
        else ""
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 260" width="400" height="260">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{p}"/>
      <stop offset="100%" stop-color="{s}"/>
    </linearGradient>
  </defs>
  <rect width="400" height="260" fill="{bg}"/>
  {frame_svg}
  {header_block}
  <rect x="44" y="38" width="84" height="20" rx="10" fill="{a}"/>
  <text x="86" y="52" text-anchor="middle" font-family="Cairo, Arial, sans-serif" font-size="10" font-weight="bold" fill="#ffffff">{badge}</text>
  <text x="352" y="54" text-anchor="end" font-family="Cairo, Arial, sans-serif" font-size="13" font-weight="bold" fill="#ffffff">{title}</text>
  <circle cx="62" cy="242" r="6" fill="{p}"/>
  <circle cx="78" cy="242" r="6" fill="{s}"/>
  <circle cx="94" cy="242" r="6" fill="{a}"/>
</svg>'''
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _translate_canva_query_keywords(query: str, category: str = "all") -> List[str]:
    """تحويل البحث العربي أو الإنجليزي إلى كلمات مفتاحية متوافقة مع قوالب كانفا الحقيقية."""
    q = (query or "").strip().lower()
    mapping = {
        "تقرير": ["report", "annual-report"],
        "تقارير": ["report", "annual-report"],
        "مدرسي": ["school", "education"],
        "مدرسية": ["school", "education"],
        "مدرسة": ["school", "education"],
        "شاهد": ["portfolio", "document", "certificate"],
        "شواهد": ["portfolio", "document", "certificate"],
        "توثيق": ["document", "portfolio", "report"],
        "أداء": ["portfolio", "report", "a4"],
        "اداء": ["portfolio", "report", "a4"],
        "إنجاز": ["portfolio", "achievement", "report"],
        "انجاز": ["portfolio", "achievement", "report"],
        "ملف": ["portfolio", "document", "a4"],
        "شهادة": ["certificate", "appreciation", "award"],
        "شهادات": ["certificate", "diploma", "award"],
        "تكريم": ["award", "appreciation", "certificate"],
        "شكر": ["thank-you", "appreciation", "certificate"],
        "خطة": ["planner", "plan", "a4"],
        "خطط": ["planner", "plan"],
        "علاجية": ["worksheet", "plan"],
        "ورقة": ["worksheet"],
        "سيرة": ["resume", "cv"],
        "معلم": ["teacher", "education"],
        "معلمة": ["teacher", "education"],
        "طالب": ["student", "school"],
        "طلاب": ["student", "school"],
        "مبادرة": ["project", "presentation", "report"],
        "إذاعة": ["school", "poster", "flyer"],
        "اذاعة": ["school", "poster", "flyer"],
        "زهور": ["floral", "botanical"],
        "وردي": ["pink", "floral"],
        "أزرق": ["blue"],
        "أخضر": ["green"],
        "ذهبي": ["gold"],
        "بنفسجي": ["purple"],
        "بسيط": ["simple", "minimal"],
        "حديث": ["modern"],
        "رسمي": ["formal", "classic"],
    }
    terms: List[str] = []
    for ar_k, en_list in mapping.items():
        if ar_k in q:
            terms.extend(en_list)

    # إضافة الكلمات الإنجليزية إن وُجدت في البحث
    for tok in re.findall(r"[a-zA-Z0-9]{2,}", q):
        terms.append(tok)

    if not terms:
        if category == "شهادات وتكريم":
            terms = ["certificate", "diploma", "award"]
        elif category == "تقارير مدرسية":
            terms = ["report", "school", "a4"]
        elif category == "شواهد وتوثيق":
            terms = ["document", "a4", "floral"]
        else:
            terms = ["a4", "report", "portfolio", "school", "certificate"]

    # إزالة التكرار مع الحفاظ على الترتيب
    dedup: List[str] = []
    for t in terms:
        if t not in dedup:
            dedup.append(t)
    return dedup[:6]


def _lookup_marketplace_image_by_id(canva_id: str) -> str:
    """البحث عن صورة المعاينة الحقيقية لقالب كانفا عبر معرف التصميم (EAF.../EAG.../EAD...)."""
    cid = re.sub(r"[^A-Za-z0-9_-]", "", (canva_id or "").strip())
    if len(cid) < 8:
        return ""
    # 1) الفحص الفوري في القوالب الموثقة والمخزنة محلياً
    local_pool = list(EDU_CANVA_TEMPLATES)
    cached_live = _load_json(EDU_CANVA_LIVE_CACHE_FILE, {})
    if isinstance(cached_live, dict):
        for lst in cached_live.values():
            if isinstance(lst, list):
                local_pool.extend(lst)
    for item in local_pool:
        if not isinstance(item, dict):
            continue
        pimg = item.get("preview_image") or ""
        curl = item.get("canva_url") or ""
        tid = item.get("id") or ""
        if pimg.startswith("http") and (f"/{cid}/" in pimg or cid in curl or tid.endswith(cid)):
            return pimg

    # 2) البحث السريع في فهرس marketplace.canva.com
    try:
        r = requests.get(
            "https://web.archive.org/cdx/search/cdx",
            params={
                "url": f"marketplace.canva.com/{cid}/*",
                "filter": ["statuscode:200", "mimetype:image/.*"],
                "output": "json",
                "limit": 10,
            },
            timeout=4,
        )
        if r.ok:
            rows = r.json()[1:]
            best = ""
            for row in rows:
                u = row[2]
                if "/400w/" in u or "/566w/" in u or "/1131w/" in u or "/800w/" in u:
                    return u
                if not best:
                    best = u
            return best
    except Exception:
        pass
    return ""


def _parse_marketplace_url_to_template(img_url: str, fallback_cat: str = "ملفات أداء وإنجاز") -> Optional[Dict[str, Any]]:
    import urllib.parse
    m = re.search(
        r"https?://marketplace\.canva\.com/([A-Za-z0-9_-]{8,})/1/0/(\d+w)/canva-([^/]+)\.(?:jpg|png|webp)$",
        img_url,
        re.IGNORECASE,
    )
    if not m:
        return None
    cid, _sz, raw_slug = m.group(1), m.group(2), m.group(3)
    decoded_slug = urllib.parse.unquote(raw_slug)
    # استبعاد العناوين غير المقروءة (رموز CJK أو نسبة عالية من غير اللاتيني/العربي)
    ascii_words = re.findall(r"[a-zA-Z0-9]+", decoded_slug)
    if len(ascii_words) < 3:
        return None
    # إزالة الهاش الختامي من الاسم المقروء
    clean_words = ascii_words[:-1] if len(ascii_words) > 3 and len(ascii_words[-1]) >= 8 else ascii_words
    readable = " ".join(clean_words).strip().title()[:64]
    low = readable.lower()

    if any(k in low for k in ("certificate", "diploma", "award", "appreciation")):
        cat = "شهادات وتكريم"
        badge = "Canva شهادة"
    elif any(k in low for k in ("report", "annual", "school", "schedule", "newsletter")):
        cat = "تقارير مدرسية"
        badge = "Canva تقرير"
    elif any(k in low for k in ("floral", "letter", "planner", "thank", "document", "worksheet")):
        cat = "شواهد وتوثيق"
        badge = "Canva شواهد"
    else:
        cat = fallback_cat if fallback_cat != "all" else "ملفات أداء وإنجاز"
        badge = "Canva A4"

    if any(k in low for k in ("pink", "rose", "pastel", "coral")):
        pal = {"primary": "#8c4a58", "secondary": "#5c2d37", "accent": "#e09f97", "bg": "#fff8f9", "card_bg": "#ffffff", "text_dark": "#2d181e", "text_light": "#ffffff"}
    elif any(k in low for k in ("green", "emerald", "sage")):
        pal = {"primary": "#166534", "secondary": "#14532d", "accent": "#10b981", "bg": "#f3fbf6", "card_bg": "#ffffff", "text_dark": "#13261a", "text_light": "#ffffff"}
    elif any(k in low for k in ("purple", "violet", "lavender", "morado")):
        pal = {"primary": "#5b3b8c", "secondary": "#3b2362", "accent": "#c084fc", "bg": "#faf5ff", "card_bg": "#ffffff", "text_dark": "#1f1235", "text_light": "#ffffff"}
    elif any(k in low for k in ("gold", "yellow", "beige", "cream", "brown")):
        pal = {"primary": "#6b4f2d", "secondary": "#433018", "accent": "#d97706", "bg": "#fdfaf4", "card_bg": "#ffffff", "text_dark": "#24190c", "text_light": "#ffffff"}
    elif any(k in low for k in ("red", "maroon", "burgundy")):
        pal = {"primary": "#881337", "secondary": "#4c0519", "accent": "#fb7185", "bg": "#fff5f7", "card_bg": "#ffffff", "text_dark": "#2b0d17", "text_light": "#ffffff"}
    else:
        pal = {"primary": "#1e4b6e", "secondary": "#102e47", "accent": "#00b4d8", "bg": "#f4f9fc", "card_bg": "#ffffff", "text_dark": "#0f172a", "text_light": "#ffffff"}

    slug_for_url = re.sub(r"[^a-zA-Z0-9-]+", "-", "-".join(clean_words)).strip("-").lower()
    return {
        "id": f"canva_mp_{cid}",
        "canva_id": cid,
        "name": f"كانفا — {readable}",
        "category": cat,
        "source": "Canva Marketplace Live",
        "layout": _infer_layout_from_text(low),
        "font_family": "Cairo",
        "heading_font": "Amiri",
        "description": f"قالب كانفا حقيقي ({readable}) جاهز للجلب وتطبيق المحتوى والطباعة A4.",
        "colors": pal,
        "preview_image": img_url,
        "canva_url": f"https://www.canva.com/templates/{cid}-{slug_for_url}/",
        "badge_text": badge,
    }


def _canva_live_search_scrape(query: str = "", category: str = "all", limit: int = 12) -> List[Dict[str, Any]]:
    """جلب قوالب كانفا الحقيقية من Canva Marketplace + الكاش الذكي مع استخراج الألوان الفعلية."""
    from concurrent.futures import ThreadPoolExecutor

    kw_list = _translate_canva_query_keywords(query, category)
    kw_regex = "|".join(re.escape(k) for k in kw_list)
    q_seed = sum(ord(ch) for ch in (query or "edu")) % 6

    # بادئات متنوعة حتى لا تتكرر نفس النتائج في كل بحث
    all_prefixes = ["EAF-", "EAG-", "EAFa", "EAFb", "EAFc", "EAFd", "EAFm", "EAGa"]
    chosen_prefixes = [all_prefixes[(q_seed + i) % len(all_prefixes)] for i in range(3)]
    fallback_cat = category if (category and category != "all" and category != "تصاميمي المجلوبة") else "ملفات أداء وإنجاز"

    def _query_cdx(prefix: str) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        try:
            flt_kw = f"original:.*/1/0/(?:400w|566w|800w|1131w)/canva-[a-z0-9-]*(?:{kw_regex})[a-z0-9-]*-[A-Za-z0-9_-]+\\.(?:jpg|png|webp)$"
            r = requests.get(
                "https://web.archive.org/cdx/search/cdx",
                params={
                    "url": f"marketplace.canva.com/{prefix}*",
                    "filter": ["statuscode:200", "mimetype:image/.*", flt_kw],
                    "output": "json",
                    "limit": 18,
                    "collapse": "urlkey",
                },
                timeout=5,
            )
            if r.ok:
                rows = r.json()[1:]
                for row in rows:
                    tpl = _parse_marketplace_url_to_template(row[2], fallback_cat=fallback_cat)
                    if tpl:
                        out.append(tpl)
        except Exception:
            pass
        return out

    discovered: List[Dict[str, Any]] = []
    seen_cids = set()

    with ThreadPoolExecutor(max_workers=3) as pool:
        for batch in pool.map(_query_cdx, chosen_prefixes):
            for item in batch:
                cid = item.get("canva_id") or item["id"]
                if cid in seen_cids:
                    continue
                seen_cids.add(cid)
                discovered.append(item)

    # استخراج الألوان الحقيقية لأول 6 قوالب جديدة عبر تحميل صور marketplace.canva.com مباشرة
    def _enrich_palette(tpl: Dict[str, Any]) -> Dict[str, Any]:
        u = tpl.get("preview_image") or ""
        if not u:
            return tpl
        try:
            ir = requests.get(u, timeout=4, headers={"User-Agent": "Mozilla/5.0"})
            if ir.ok and ir.headers.get("Content-Type", "").startswith("image/"):
                pal = _extract_palette_from_image_bytes(ir.content)
                if pal:
                    tpl["colors"] = pal
        except Exception:
            pass
        return tpl

    if discovered:
        with ThreadPoolExecutor(max_workers=4) as pool:
            enriched = list(pool.map(_enrich_palette, discovered[:6]))
            discovered[:6] = enriched

        # تحديث الكاش المحلي للقوالب الحقيقية المكتشفة لسرعة البحث لاحقاً
        live_cache = _load_json(EDU_CANVA_LIVE_CACHE_FILE, [])
        if not isinstance(live_cache, list):
            live_cache = []
        new_ids = {x["id"] for x in discovered}
        merged_cache = discovered + [x for x in live_cache if isinstance(x, dict) and x.get("id") not in new_ids]
        _save_json(EDU_CANVA_LIVE_CACHE_FILE, merged_cache[:60])
    else:
        # في حال تباطؤ أو انقطاع CDX المؤقت، نستخدم القوالب الحقيقية المحفوظة في الكاش
        live_cache = _load_json(EDU_CANVA_LIVE_CACHE_FILE, [])
        if isinstance(live_cache, list):
            for item in live_cache:
                if not isinstance(item, dict):
                    continue
                hay = f"{item.get('name','')} {item.get('canva_url','')} {item.get('category','')}".lower()
                if any(k in hay for k in kw_list) or not query.strip():
                    discovered.append(item)

    return discovered[:limit]


def _normalize_edu_template(raw: Dict[str, Any]) -> Dict[str, Any]:
    colors = raw.get("colors") if isinstance(raw.get("colors"), dict) else {}
    raw_name = (raw.get("name") or "").strip()
    if _is_bot_challenge_title(raw_name):
        slug_t, cid = _extract_canva_slug_and_id(raw.get("canva_url") or "")
        raw_name = slug_t or (f"تصميم كانفا ({cid[:10]})" if cid else "قالب كانفا تعليمي")

    canva_url = (raw.get("canva_url") or "").strip()
    canva_id = (raw.get("canva_id") or "").strip()
    if not canva_id and canva_url:
        _, canva_id = _extract_canva_slug_and_id(canva_url)

    preview_image = (raw.get("preview_image") or "").strip()
    raw_safe = (raw.get("safe_preview_data_url") or "").strip()
    # عدم تغطية الصورة الحقيقية بصورة SVG المولدة أبداً!
    is_real_raster_data = raw_safe.startswith("data:image/jpeg") or raw_safe.startswith("data:image/png") or raw_safe.startswith("data:image/webp") or raw_safe.startswith("data:image/gif")
    safe_preview_data_url = raw_safe if is_real_raster_data else ""

    norm = {
        "id": str(raw.get("id") or ("edu_tpl_" + hashlib.md5(json.dumps(raw, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:8])),
        "canva_id": canva_id,
        "name": raw_name or "قالب كانفا تعليمي",
        "category": (raw.get("category") or "تعليمي").strip(),
        "source": (raw.get("source") or "Canva Studio").strip(),
        "layout": (raw.get("layout") or "gradient_arch").strip(),
        "font_family": (raw.get("font_family") or "Cairo").strip(),
        "heading_font": (raw.get("heading_font") or "Amiri").strip(),
        "description": (raw.get("description") or "").strip(),
        "colors": {
            "primary": colors.get("primary") or "#3b6978",
            "secondary": colors.get("secondary") or "#204051",
            "accent": colors.get("accent") or "#c9a86a",
            "bg": colors.get("bg") or "#f8fafc",
            "card_bg": colors.get("card_bg") or "#ffffff",
            "text_dark": colors.get("text_dark") or "#0f172a",
            "text_light": colors.get("text_light") or "#ffffff",
        },
        "preview_image": preview_image,
        "safe_preview_data_url": safe_preview_data_url,
        "canva_url": canva_url,
        "canva_embed_url": (raw.get("canva_embed_url") or "").strip(),
        "badge_text": (raw.get("badge_text") or raw.get("category") or "Canva A4").strip(),
        "fetched_at": raw.get("fetched_at") or "",
        "processed": bool(raw.get("processed", False)),
        "processed_asset_id": raw.get("processed_asset_id") or "",
        "processed_format": raw.get("processed_format") or "",
        "processed_page_count": int(raw.get("processed_page_count") or len(raw.get("processed_pages") or []) or 0),
        "processed_pdf_url": raw.get("processed_pdf_url") or "",
        "processed_pages": raw.get("processed_pages") if isinstance(raw.get("processed_pages"), list) else [],
        "processed_at": raw.get("processed_at") or "",
    }
    if not norm["canva_embed_url"] and "/design/" in norm["canva_url"]:
        _, cid = _extract_canva_slug_and_id(norm["canva_url"])
        if cid:
            norm["canva_embed_url"] = f"https://www.canva.com/design/{cid}/view?embed"
    norm["fallback_preview_data_url"] = _build_edu_canva_thumb_data_url(norm)
    return norm


def _edu_patch_importer():
    def browse_edu_canva(
        self,
        query: str = "",
        category: str = "all",
        source: str = "all",
        canva_token: str = "",
    ) -> Dict[str, Any]:
        live_items: List[Dict[str, Any]] = []
        api_error = ""
        if canva_token and canva_token.strip():
            try:
                api_items = self.fetch_canva_api_designs(canva_token.strip())
                live_items.extend(_normalize_edu_template(x) for x in api_items)
            except Exception as exc:
                api_error = str(exc)

        if source in ("all", "live"):
            live_items.extend(_canva_live_search_scrape(query=query, category=category, limit=12))

        imported = _load_json(CANVA_CACHE_FILE, [])
        if not isinstance(imported, list):
            imported = []

        live_cached = _load_json(EDU_CANVA_LIVE_CACHE_FILE, [])
        if not isinstance(live_cached, list):
            live_cached = []

        fetched_saved = _load_json(EDU_CANVA_FETCHED_FILE, [])
        if not isinstance(fetched_saved, list):
            fetched_saved = []

        catalog: List[Dict[str, Any]] = []
        seen_ids = set()
        for src_list in (live_items, imported, EDU_CANVA_TEMPLATES, live_cached, CANVA_TEMPLATES):
            for item in src_list:
                if not isinstance(item, dict):
                    continue
                norm = _normalize_edu_template(item)
                if norm["id"] in seen_ids:
                    continue
                seen_ids.add(norm["id"])
                catalog.append(norm)

        # حفظ فهرس المعرض الحالي للرجوع السريع عند تحديد القوالب
        browse_cache = [
            {k: v for k, v in it.items() if k not in ("safe_preview_data_url", "fallback_preview_data_url")}
            for it in catalog[:90]
        ]
        _save_json(EDU_CANVA_BROWSE_CACHE_FILE, browse_cache)

        kw = (query or "").strip().lower()
        kw_en = _translate_canva_query_keywords(query, category) if kw else []
        cat = (category or "all").strip()
        filtered = []
        for item in catalog:
            if cat != "all":
                if cat == "تصاميمي المجلوبة":
                    if item["source"] not in ("حساب Canva المتصل", "رابط Canva مستورد", "ملف Canva مستورد", "Canva Marketplace Live", "Canva Live Search"):
                        continue
                elif item["category"] != cat:
                    continue
            if kw:
                hay = f"{item['name']} {item['category']} {item['description']} {item['source']} {item.get('canva_url','')}".lower()
                if kw not in hay and not any(ek in hay for ek in kw_en):
                    continue
            filtered.append(item)

        return {
            "templates": filtered,
            "fetched": [_normalize_edu_template(x) for x in fetched_saved],
            "live_count": len(live_items),
            "api_error": api_error,
        }

    def fetch_selected_edu_canva(self, selected_items: List[Dict[str, Any]], canva_token: str = "") -> List[Dict[str, Any]]:
        import base64 as _b64
        if not isinstance(selected_items, list) or not selected_items:
            raise ValueError("يرجى تحديد قالب واحد على الأقل لجلبه")

        catalog_map = {}
        for src_list in (
            _load_json(EDU_CANVA_BROWSE_CACHE_FILE, []),
            _load_json(EDU_CANVA_LIVE_CACHE_FILE, []),
            _load_json(CANVA_CACHE_FILE, []),
            EDU_CANVA_TEMPLATES,
            CANVA_TEMPLATES,
        ):
            if isinstance(src_list, list):
                for it in src_list:
                    if isinstance(it, dict):
                        n = _normalize_edu_template(it)
                        catalog_map[n["id"]] = n

        fetched_results: List[Dict[str, Any]] = []
        for raw_item in selected_items:
            if isinstance(raw_item, str):
                base = catalog_map.get(raw_item, {"id": raw_item, "name": raw_item})
            elif isinstance(raw_item, dict):
                tid = raw_item.get("id", "")
                base = dict(catalog_map.get(tid, {}))
                for k, v in raw_item.items():
                    if v not in (None, ""):
                        base[k] = v
            else:
                continue

            norm = _normalize_edu_template(base)
            c_url = norm.get("canva_url", "")
            if c_url.startswith(("http://", "https://")) and not norm.get("preview_image"):
                oe = _fetch_canva_oembed(c_url)
                if oe.get("title"):
                    norm["name"] = oe["title"]
                if oe.get("thumbnail_url"):
                    norm["preview_image"] = oe["thumbnail_url"]
                if not norm.get("preview_image") and norm.get("canva_id"):
                    norm["preview_image"] = _lookup_marketplace_image_by_id(norm["canva_id"])

            # تحميل صورة القالب الفعلية من كانفا، استخراج ألوانها الحقيقية، وتخزينها محلياً لتفادي CORS أثناء PDF والطباعة
            img_url = norm.get("preview_image", "")
            if img_url.startswith(("http://", "https://")) and not norm.get("safe_preview_data_url"):
                try:
                    img_resp = requests.get(
                        img_url,
                        timeout=7,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 Safari/537.36",
                            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
                        },
                    )
                    if img_resp.ok and img_resp.headers.get("Content-Type", "").startswith("image/") and len(img_resp.content) < 4_500_000:
                        extracted_pal = _extract_palette_from_image_bytes(img_resp.content)
                        if extracted_pal:
                            norm["colors"] = extracted_pal
                        norm["safe_preview_data_url"] = (
                            f"data:{img_resp.headers.get('Content-Type', 'image/jpeg').split(';')[0]};base64,"
                            + _b64.b64encode(img_resp.content).decode("ascii")
                        )
                except Exception:
                    pass

            norm["fetched_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            fetched_results.append(norm)

        existing = _load_json(EDU_CANVA_FETCHED_FILE, [])
        if not isinstance(existing, list):
            existing = []
        new_ids = {x["id"] for x in fetched_results}
        merged = fetched_results + [x for x in existing if isinstance(x, dict) and x.get("id") not in new_ids]
        _save_json(EDU_CANVA_FETCHED_FILE, merged[:40])
        return fetched_results

    def get_fetched_edu_canva(self) -> List[Dict[str, Any]]:
        raw = _load_json(EDU_CANVA_FETCHED_FILE, [])
        if not isinstance(raw, list):
            return []
        return [_normalize_edu_template(x) for x in raw if isinstance(x, dict)]

    def remove_fetched_edu_canva(self, template_id: str) -> List[Dict[str, Any]]:
        raw = _load_json(EDU_CANVA_FETCHED_FILE, [])
        if not isinstance(raw, list):
            raw = []
        filtered = [x for x in raw if isinstance(x, dict) and x.get("id") != template_id]
        _save_json(EDU_CANVA_FETCHED_FILE, filtered)
        return [_normalize_edu_template(x) for x in filtered]

    def process_edu_canva_template_for_merge(
        self,
        template_item: Dict[str, Any],
        canva_token: str = "",
    ) -> Dict[str, Any]:
        """
        معالجة القالب المختار من كانفا وتحويله فعلياً إلى صيغ متوافقة (صور PNG بمقاس A4 + ملف PDF A4)
        جاهزة للتضمين المباشر داخل صفحات ملف الأداء الوظيفي وملف الشواهد.
        """
        import base64 as _b64
        import io
        from PIL import Image

        if not isinstance(template_item, dict):
            raise ValueError("بيانات القالب غير صالحة")

        tid = str(template_item.get("id") or "").strip()
        catalog_map = {}
        for src_list in (
            _load_json(EDU_CANVA_FETCHED_FILE, []),
            _load_json(CANVA_CACHE_FILE, []),
            _load_json(EDU_CANVA_BROWSE_CACHE_FILE, []),
            _load_json(EDU_CANVA_LIVE_CACHE_FILE, []),
            EDU_CANVA_TEMPLATES,
            CANVA_TEMPLATES,
        ):
            if isinstance(src_list, list):
                for it in src_list:
                    if isinstance(it, dict):
                        n = _normalize_edu_template(it)
                        catalog_map[n["id"]] = n

        base = dict(catalog_map.get(tid, {}))
        for k, v in template_item.items():
            if v not in (None, "", []):
                base[k] = v
        norm = _normalize_edu_template(base)
        asset_id = _safe_asset_id(norm.get("processed_asset_id") or norm["id"])

        # 1. التحقق إن كانت الملفات المعالجة (PNG + PDF) موجودة بالفعل على القرص
        existing_pages = norm.get("processed_pages") or []
        if norm.get("processed") and existing_pages:
            pdf_disk = os.path.join(EDU_CANVA_PROCESSED_DIR, asset_id, "template.pdf")
            p1_disk = os.path.join(EDU_CANVA_PROCESSED_DIR, asset_id, "page_01.png")
            if os.path.exists(pdf_disk) and os.path.exists(p1_disk):
                return norm

        c_colors = norm.get("colors") or {}
        bg_hex = c_colors.get("bg", "#ffffff")
        p_hex = c_colors.get("primary", "#0f766e")
        a_hex = c_colors.get("accent", "#d97706")

        pil_pages: List[Any] = []
        pdf_bytes: Optional[bytes] = None

        # 2. محاولة التصدير المباشر PDF من Canva Connect API إذا توفر توكن ومعرف تصميم
        if canva_token and norm.get("canva_id"):
            exported_pdf = _try_canva_api_export_pdf_bytes(norm["canva_id"], canva_token)
            if exported_pdf:
                try:
                    pil_pages = _render_pdf_bytes_to_pil_pages(
                        exported_pdf, max_pages=12, bg_hex=bg_hex, primary_hex=p_hex, accent_hex=a_hex
                    )
                    pdf_bytes = exported_pdf
                except Exception:
                    pil_pages = []
                    pdf_bytes = None

        # 3. إن لم تتوفر، استخدام الصورة النقطية المحفوظة في القالب
        if not pil_pages and norm.get("safe_preview_data_url"):
            try:
                raw_du = norm["safe_preview_data_url"]
                b64_part = raw_du.split(",", 1)[1] if "," in raw_du else raw_du
                raw_img = _b64.b64decode(b64_part)
                with Image.open(io.BytesIO(raw_img)) as im:
                    pil_pages = [_render_a4_canvas_from_pil(im, bg_hex=bg_hex, primary_hex=p_hex, accent_hex=a_hex)]
            except Exception:
                pil_pages = []

        # 4. جلب الصورة الفعلية من رابط preview_image أو Canva oEmbed / CDN ثم معالجتها
        if not pil_pages:
            img_url = norm.get("preview_image") or ""
            c_url = norm.get("canva_url") or ""
            if not img_url and c_url.startswith(("http://", "https://")):
                oe = _fetch_canva_oembed(c_url)
                if oe.get("thumbnail_url"):
                    img_url = oe["thumbnail_url"]
                    norm["preview_image"] = img_url
                if not img_url and norm.get("canva_id"):
                    img_url = _lookup_marketplace_image_by_id(norm["canva_id"])
                    norm["preview_image"] = img_url

            if img_url.startswith(("http://", "https://")):
                try:
                    ir = requests.get(
                        img_url,
                        timeout=8,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 Safari/537.36",
                            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
                        },
                    )
                    if ir.ok and ir.headers.get("Content-Type", "").startswith("image/") and len(ir.content) < 5_000_000:
                        pal = _extract_palette_from_image_bytes(ir.content)
                        if pal:
                            norm["colors"] = pal
                            bg_hex = pal.get("bg", bg_hex)
                            p_hex = pal.get("primary", p_hex)
                            a_hex = pal.get("accent", a_hex)
                        with Image.open(io.BytesIO(ir.content)) as im:
                            pil_pages = [_render_a4_canvas_from_pil(im, bg_hex=bg_hex, primary_hex=p_hex, accent_hex=a_hex)]
                        norm["safe_preview_data_url"] = (
                            f"data:{ir.headers.get('Content-Type', 'image/jpeg').split(';')[0]};base64,"
                            + _b64.b64encode(ir.content).decode("ascii")
                        )
                except Exception:
                    pil_pages = []

        # 5. البديل المصمم عالي الدقة A4 وفق ألوان وتخطيط القالب لضمان عدم تعطل الدمج أبداً
        if not pil_pages:
            pil_pages = [_render_styled_a4_fallback(norm)]

        proc_meta = _save_processed_pages_and_pdf(asset_id, pil_pages, existing_pdf_bytes=pdf_bytes)
        norm.update(proc_meta)
        norm = _normalize_edu_template(norm)

        # تحديث النسخة المحفوظة في fetched_edu_canva إن وجدت
        try:
            fetched = _load_json(EDU_CANVA_FETCHED_FILE, [])
            if isinstance(fetched, list) and any(isinstance(x, dict) and x.get("id") == norm["id"] for x in fetched):
                updated_fetched = [norm if (isinstance(x, dict) and x.get("id") == norm["id"]) else x for x in fetched]
                _save_json(EDU_CANVA_FETCHED_FILE, updated_fetched[:40])
        except Exception:
            pass

        return norm

    DesignImporter.browse_edu_canva = browse_edu_canva
    DesignImporter.fetch_selected_edu_canva = fetch_selected_edu_canva
    DesignImporter.get_fetched_edu_canva = get_fetched_edu_canva
    DesignImporter.remove_fetched_edu_canva = remove_fetched_edu_canva
    DesignImporter.process_edu_canva_template_for_merge = process_edu_canva_template_for_merge


_edu_patch_importer()

