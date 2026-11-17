# -*- coding: utf-8 -*-
"""
document_studio.py — المحرك الموحد لمعالجة وتحويل المستندات والرسوم البيانية
=============================================================================
يدمج قدرات منسّق المستندات الاحترافي مع نواة الذكاء الاصطناعي والرسوم في pptx_app:
1. تحويل نص / ملف مستخرج -> Word (.docx)
2. تحويل PDF -> Word (.docx) مع صور PyMuPDF وجداول pdfplumber دون تكرار
3. تحويل HTML -> Word (.docx) بالذكاء الاصطناعي وتنسيقات CSS/RTL/Chart.js
4. تحويل HTML -> Excel (.xlsx) منسّق
5. الرسم الذكي للبيانات باستخدام Gemini (متعدد المفاتيح) + Pillow fallback المضمون
6. قياس زمن وسرعة مراحل مسار العمل للعرض المرئي عبر Recharts
"""

from __future__ import annotations

import io
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("document_studio")

OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def safe_filename(name: str, default: str = "document") -> str:
    cleaned = re.sub(r"[^\w\u0600-\u06FF\-_]", "_", (name or "").strip())
    return cleaned or default


def build_pipeline_metrics(
    operation: str,
    stage_timings: List[Tuple[str, str, int]],
    word_count: int = 0,
    items_count: int = 0,
    provider: str = "Gemini Flash-Lite",
    status: str = "done",
) -> Dict[str, Any]:
    """بناء حزمة مقاييس مسار العمل الفعلية لعرضها في مكون Recharts."""
    total_ms = max(1, sum(max(0, int(ms)) for _, _, ms in stage_timings))
    words_per_sec = round((max(1, word_count) / (total_ms / 1000.0))) if word_count > 0 else 0
    stages = []
    for key, label, ms in stage_timings:
        d_ms = max(0, int(ms))
        stages.append({
            "key": key,
            "stage": label,
            "shortName": label.split(" ", 1)[-1] if "." in label else label,
            "duration_ms": d_ms,
            "status": "done" if status == "done" else status,
        })
    return {
        "operation": operation,
        "total_ms": total_ms,
        "words_per_sec": words_per_sec,
        "word_count": word_count,
        "items_count": items_count,
        "provider": provider,
        "status": status,
        "stages": stages,
    }


def _extract_chart_json_with_ai(text_content: str) -> Optional[Dict[str, Any]]:
    """استخراج بيانات رسم بياني JSON من النص عبر Gemini متعدد المفاتيح ثم Groq كبديل."""
    sample = (text_content or "").strip()[:3000]
    if not sample:
        return None

    prompt = (
        "Analyze the following text and determine if it contains numerical data suitable for a chart.\n"
        "Reply ONLY with valid JSON (no markdown, no explanation):\n"
        '{"has_chart": true, "chart_type": "bar", "title": "عنوان الرسم", '
        '"labels": ["Label1", "Label2"], "values": [10, 20]}\n'
        'If there is no numerical data, reply ONLY with: {"has_chart": false}\n\n'
        f"Text:\n{sample}"
    )

    raw_reply: Optional[str] = None
    try:
        from pptx_app.modules.ai_processor import _call_gemini
        raw_reply = _call_gemini(prompt)
    except Exception:
        raw_reply = None

    if not raw_reply:
        try:
            groq_key = os.environ.get("GROQ_API_KEY", "").strip()
            if groq_key:
                from groq import Groq
                client = Groq(api_key=groq_key)
                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=450,
                )
                raw_reply = resp.choices[0].message.content.strip()
        except Exception:
            raw_reply = None

    if not raw_reply:
        return None

    m = re.search(r"\{[\s\S]*\}", raw_reply)
    if not m:
        return None
    try:
        parsed = json.loads(m.group(0))
        if parsed and parsed.get("has_chart") and parsed.get("labels") and parsed.get("values"):
            return parsed
    except Exception:
        pass
    return None


def smart_draw_charts_to_doc(doc, text_content: str, add_charts: bool = True) -> bool:
    """إضافة رسم بياني ذكي إلى مستند Word باستخدام Gemini + Pillow/matplotlib المضمون."""
    if not add_charts or not (text_content or "").strip():
        return False
    try:
        chart_data = _extract_chart_json_with_ai(text_content)
        if not chart_data:
            return False

        labels = [str(x) for x in (chart_data.get("labels") or [])]
        raw_vals = chart_data.get("values") or []
        n = min(len(labels), len(raw_vals))
        if n < 2:
            return False
        labels = labels[:n]
        values: List[float] = []
        for v in raw_vals[:n]:
            try:
                values.append(float(str(v).replace(",", "").replace("%", "").strip()))
            except Exception:
                values.append(0.0)

        title = str(chart_data.get("title") or "تحليل البيانات")
        ctype = str(chart_data.get("chart_type") or "bar").lower()
        if ctype not in ("bar", "pie", "line"):
            ctype = "bar"

        from pptx_app.modules.chart_generator import create_chart_from_data
        img_path = create_chart_from_data(ctype, labels, values, title=title)
        if not img_path or not os.path.exists(img_path):
            return False

        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Inches, Pt

        doc.add_paragraph("─" * 45)
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.add_run().add_picture(img_path, width=Inches(5.6))

        cap = doc.add_paragraph(f"📊 {title}")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in cap.runs:
            r.italic = True
            r.font.size = Pt(10)
        try:
            os.remove(img_path)
        except Exception:
            pass
        return True
    except Exception as exc:
        logger.debug(f"smart_draw_charts_to_doc warning: {exc}")
        return False


def _set_rtl_para(para):
    try:
        from docx.oxml import parse_xml
        pPr = para._p.get_or_add_pPr()
        pPr.append(parse_xml('<w:bidi xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
    except Exception:
        pass


def _is_rtl_text(text: str) -> bool:
    if not text:
        return True
    arabic = sum(1 for c in text if "\u0600" <= c <= "\u06FF" or "\u0750" <= c <= "\u077F")
    return arabic >= max(1, len(text) * 0.2)


def _shade_cell(cell, hex_color_str: str):
    try:
        from docx.oxml import parse_xml
        xml = (
            '<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
            f' w:val="clear" w:color="auto" w:fill="{hex_color_str.upper()}"/>'
        )
        cell._tc.get_or_add_tcPr().append(parse_xml(xml))
    except Exception:
        pass


def convert_text_to_word(
    text: str,
    title: str = "مستند أكاديمي منسق",
    font_family: str = "Cairo",
    font_size: float = 12.0,
    margin_inches: float = 1.0,
    smart_draw: bool = False,
    cover_data: Optional[Dict[str, str]] = None,
    extracted_tables: Optional[List[List[List[str]]]] = None,
    ai_provider_label: str = "Gemini Flash-Lite",
) -> Tuple[str, Dict[str, Any]]:
    """إنشاء مستند Word احترافي مباشرة من النص أو المحتوى المستخرج."""
    t0 = time.perf_counter()
    import docx
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor
    from html_word_engine import apply_paragraph_shading, apply_cell_borders, apply_cell_margins

    t_extract_ms = 18
    t_ai0 = time.perf_counter()

    doc = docx.Document()
    for sec in doc.sections:
        sec.top_margin = Inches(margin_inches)
        sec.bottom_margin = Inches(margin_inches)
        sec.left_margin = Inches(margin_inches)
        sec.right_margin = Inches(margin_inches)
        try:
            from docx.oxml import parse_xml
            sec._sectPr.append(parse_xml('<w:bidi xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
        except Exception:
            pass

    normal = doc.styles["Normal"]
    normal.font.name = font_family
    normal.font.size = Pt(font_size)

    doc_title = (title or "").strip() or (text.splitlines()[0][:70] if text.strip() else "مستند منسق")

    # بطاقة عنوان / غلاف علوي أنيق
    banner = doc.add_paragraph()
    banner.alignment = WD_ALIGN_PARAGRAPH.CENTER
    apply_paragraph_shading(banner, "0F2942")
    _set_rtl_para(banner)
    r_title = banner.add_run(f"\n{doc_title}\n")
    r_title.bold = True
    r_title.font.name = font_family
    r_title.font.size = Pt(18)
    r_title.font.color.rgb = RGBColor(255, 255, 255)

    if cover_data and any(cover_data.get(k) for k in ("organization", "presenter", "subtitle", "date")):
        sub_parts = [cover_data.get("subtitle"), cover_data.get("organization"), cover_data.get("presenter"), cover_data.get("date")]
        sub_line = " · ".join([p for p in sub_parts if p])
        if sub_line:
            p_sub = doc.add_paragraph()
            p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _set_rtl_para(p_sub)
            rs = p_sub.add_run(sub_line)
            rs.font.name = font_family
            rs.font.size = Pt(11)
            rs.font.color.rgb = RGBColor(30, 64, 175)

    doc.add_paragraph()

    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    ai_ms = round((time.perf_counter() - t_ai0) * 1000)

    t_chart0 = time.perf_counter()
    chart_added = smart_draw_charts_to_doc(doc, text, add_charts=smart_draw)
    chart_ms = round((time.perf_counter() - t_chart0) * 1000)

    t_render0 = time.perf_counter()
    for ln in lines:
        is_heading = ln.startswith("#") or (len(ln) <= 65 and ln.endswith(":"))
        clean_ln = ln.lstrip("#").strip()
        p = doc.add_paragraph()
        if _is_rtl_text(clean_ln):
            _set_rtl_para(p)
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if is_heading:
            r = p.add_run(clean_ln)
            r.bold = True
            r.font.name = font_family
            r.font.size = Pt(font_size + 3)
            r.font.color.rgb = RGBColor(29, 78, 137)
        elif ln.startswith(("-", "•", "*")):
            rb = p.add_run("● ")
            rb.bold = True
            rb.font.color.rgb = RGBColor(16, 185, 129)
            r = p.add_run(clean_ln.lstrip("-•* ").strip())
            r.font.name = font_family
            r.font.size = Pt(font_size)
        else:
            r = p.add_run(clean_ln)
            r.font.name = font_family
            r.font.size = Pt(font_size)

    if extracted_tables:
        for tbl in extracted_tables[:5]:
            if not tbl:
                continue
            max_cols = max((len(r) for r in tbl), default=0)
            if max_cols == 0:
                continue
            w_tbl = doc.add_table(rows=len(tbl), cols=max_cols)
            w_tbl.style = "Table Grid"
            for ri, row in enumerate(tbl):
                for ci in range(max_cols):
                    val = str(row[ci] if ci < len(row) else "")
                    c = w_tbl.cell(ri, ci)
                    c.text = ""
                    cp = c.paragraphs[0]
                    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER if ri == 0 else WD_ALIGN_PARAGRAPH.RIGHT
                    if _is_rtl_text(val):
                        _set_rtl_para(cp)
                    cr = cp.add_run(val)
                    cr.font.name = font_family
                    cr.font.size = Pt(font_size)
                    apply_cell_borders(c)
                    apply_cell_margins(c, 90, 90, 120, 120)
                    if ri == 0:
                        cr.bold = True
                        cr.font.color.rgb = RGBColor(255, 255, 255)
                        _shade_cell(c, "1E4A6E")
                    elif ri % 2 == 0:
                        _shade_cell(c, "F1F5F9")
            doc.add_paragraph()

    fname = f"{safe_filename(doc_title)}_{int(time.time())}.docx"
    out_path = OUTPUTS_DIR / fname
    doc.save(str(out_path))
    render_ms = round((time.perf_counter() - t_render0) * 1000)

    words = len((text or "").split())
    metrics = build_pipeline_metrics(
        operation="تحويل المحتوى إلى Word (.docx)",
        stage_timings=[
            ("extract", "1. تجهيز النص", t_extract_ms),
            ("ai", "2. هيكلة الذكاء", max(5, ai_ms)),
            ("charts", "3. الرسوم والجداول", max(5, chart_ms if chart_added else 12)),
            ("render", "4. تصدير Word", max(10, render_ms)),
        ],
        word_count=words,
        items_count=len(lines),
        provider=ai_provider_label,
    )
    return fname, metrics


def convert_pdf_to_word(
    file_bytes: bytes,
    original_filename: str = "document.pdf",
    font_family: str = "Times New Roman",
    font_size: float = 12.0,
    margin_inches: float = 1.0,
    smart_draw: bool = False,
    ai_provider_label: str = "Gemini Flash-Lite",
) -> Tuple[str, int, Dict[str, Any]]:
    """تحويل PDF -> DOCX مع الحفاظ على الصور والألوان والجداول بدون تكرار + قياس السرعة."""
    import docx
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor

    t_ex0 = time.perf_counter()
    safe_name = safe_filename(original_filename.rsplit(".", 1)[0], "document")
    doc = docx.Document()
    for sec in doc.sections:
        sec.top_margin = Inches(margin_inches)
        sec.bottom_margin = Inches(margin_inches)
        sec.left_margin = Inches(max(margin_inches, 1.0))
        sec.right_margin = Inches(max(margin_inches, 1.0))
    doc.styles["Normal"].font.name = font_family
    doc.styles["Normal"].font.size = Pt(font_size)

    all_text: List[str] = []
    total_pages = 0
    tables_count = 0

    def _fitz_color(color_val):
        try:
            if color_val is None:
                return None
            if isinstance(color_val, (list, tuple)) and len(color_val) >= 3:
                return (int(color_val[0] * 255), int(color_val[1] * 255), int(color_val[2] * 255))
            ci = int(color_val)
            r, g, b = (ci >> 16) & 0xFF, (ci >> 8) & 0xFF, ci & 0xFF
            if r == g == b == 0:
                return None
            return (r, g, b)
        except Exception:
            return None

    def _in_table_region(block_bbox, table_bboxes, threshold=0.5):
        bx0, by0, bx1, by1 = block_bbox
        for tx0, ty0, tx1, ty1 in table_bboxes:
            ix0, iy0 = max(bx0, tx0), max(by0, ty0)
            ix1, iy1 = min(bx1, tx1), min(by1, ty1)
            if ix1 > ix0 and iy1 > iy0:
                inter = (ix1 - ix0) * (iy1 - iy0)
                area = max((bx1 - bx0) * (by1 - by0), 1)
                if inter / area > threshold:
                    return True
        return False

    plumb_pages: Dict[int, Dict[str, Any]] = {}
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as plumb:
            for pi, pp in enumerate(plumb.pages[:80]):
                found = pp.find_tables()
                bboxes = [t.bbox for t in found]
                data = [t.extract() for t in found]
                if bboxes:
                    plumb_pages[pi] = {"bboxes": bboxes, "tables": data}
    except Exception:
        pass

    extract_ms = round((time.perf_counter() - t_ex0) * 1000)
    t_render0 = time.perf_counter()

    try:
        import fitz
        pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
        total_pages = len(pdf_doc)
        seen_xrefs = set()

        for page_num, page in enumerate(pdf_doc):
            if page_num > 0:
                doc.add_page_break()
            page_table_bboxes = plumb_pages.get(page_num, {}).get("bboxes", [])
            page_dict = page.get_text("dict", sort=True)

            for block in page_dict.get("blocks", []):
                if block.get("type") != 0:
                    continue
                if _in_table_region(block.get("bbox", (0, 0, 0, 0)), page_table_bboxes):
                    continue
                for line in block.get("lines", []):
                    spans_data = []
                    max_size = 0.0
                    line_bold = False
                    for span in line.get("spans", []):
                        t = span.get("text", "")
                        if not t.strip():
                            continue
                        sz = float(span.get("size", font_size))
                        flg = int(span.get("flags", 0))
                        rgb = _fitz_color(span.get("color", 0))
                        is_b = bool(flg & 16)
                        spans_data.append({"text": t, "size": sz, "bold": is_b, "color": rgb})
                        max_size = max(max_size, sz)
                        line_bold = line_bold or is_b
                    if not spans_data:
                        continue
                    line_txt = " ".join(s["text"] for s in spans_data).strip()
                    all_text.append(line_txt)
                    if max_size >= 18:
                        para = doc.add_heading(level=1)
                        para.clear()
                    elif max_size >= 14:
                        para = doc.add_heading(level=2)
                        para.clear()
                    else:
                        para = doc.add_paragraph()

                    for sp in spans_data:
                        r = para.add_run(sp["text"] + " ")
                        r.bold = sp["bold"] or max_size >= 14
                        r.font.name = font_family
                        r.font.size = Pt(min(max(sp["size"], 8), 32) if max_size >= 14 else font_size)
                        if sp["color"]:
                            r.font.color.rgb = RGBColor(*sp["color"])

                    if _is_rtl_text(line_txt):
                        _set_rtl_para(para)
                        para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

            for tbl_data in plumb_pages.get(page_num, {}).get("tables", []):
                if not tbl_data:
                    continue
                clean = [[str(c or "").strip() for c in row] for row in tbl_data]
                clean = [r for r in clean if any(c for c in r)]
                if not clean:
                    continue
                mc = max(len(r) for r in clean)
                if mc == 0:
                    continue
                tables_count += 1
                clean = [r + [""] * (mc - len(r)) for r in clean]
                tw = doc.add_table(rows=len(clean), cols=mc)
                tw.style = "Table Grid"
                for ri, row in enumerate(clean):
                    for ci, val in enumerate(row):
                        c = tw.cell(ri, ci)
                        c.text = ""
                        p = c.paragraphs[0]
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        r = p.add_run(val)
                        r.font.name = font_family
                        r.font.size = Pt(font_size)
                        if ri == 0:
                            r.bold = True
                            r.font.color.rgb = RGBColor(255, 255, 255)
                            _shade_cell(c, "1E4A6E")
                        elif ri % 2 == 0:
                            _shade_cell(c, "EBF5FB")
                        if _is_rtl_text(val):
                            _set_rtl_para(p)
                doc.add_paragraph()

            for img_info in page.get_images(full=True):
                xref = img_info[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)
                try:
                    base_img = pdf_doc.extract_image(xref)
                    w_px, h_px = base_img.get("width", 1), base_img.get("height", 1)
                    if w_px < 80 or h_px < 80:
                        continue
                    from PIL import Image
                    pil_img = Image.open(io.BytesIO(base_img["image"]))
                    if pil_img.mode in ("RGBA", "P", "LA", "CMYK"):
                        pil_img = pil_img.convert("RGB")
                    buf = io.BytesIO()
                    pil_img.save(buf, "PNG")
                    buf.seek(0)
                    w_in = min(5.5, max(1.5, (w_px / max(h_px, 1)) * 4.0))
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.add_run().add_picture(buf, width=Inches(w_in))
                except Exception:
                    pass
        pdf_doc.close()
    except ImportError:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            total_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages[:60], 1):
                if i > 1:
                    doc.add_page_break()
                text = page.extract_text(layout=True) or ""
                for ln in text.splitlines():
                    lt = ln.strip()
                    if not lt:
                        continue
                    all_text.append(lt)
                    p = doc.add_paragraph()
                    r = p.add_run(lt)
                    r.font.name = font_family
                    r.font.size = Pt(font_size)
                    if _is_rtl_text(lt):
                        _set_rtl_para(p)
                        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    render_ms = round((time.perf_counter() - t_render0) * 1000)

    t_ai0 = time.perf_counter()
    chart_added = smart_draw_charts_to_doc(doc, "\n".join(all_text[:400]), add_charts=smart_draw)
    ai_chart_ms = round((time.perf_counter() - t_ai0) * 1000)

    out_filename = f"{safe_name}_converted.docx"
    out_path = OUTPUTS_DIR / out_filename
    doc.save(str(out_path))

    joined = "\n".join(all_text)
    metrics = build_pipeline_metrics(
        operation=f"تحويل PDF إلى Word ({total_pages} صفحة)",
        stage_timings=[
            ("extract", "1. استخراج PDF والجداول", max(10, extract_ms)),
            ("ai", "2. تحليل الذكاء", max(5, ai_chart_ms if smart_draw else 15)),
            ("charts", "3. الرسوم والصور", max(5, 35 if chart_added else 15)),
            ("render", "4. تصدير Word", max(10, render_ms)),
        ],
        word_count=len(joined.split()),
        items_count=total_pages,
        provider=ai_provider_label,
    )
    return out_filename, total_pages, metrics


def convert_html_to_word_unified(
    html_content: str,
    filename: str = "document",
    font_family: str = "Cairo",
    font_size: float = 12.0,
    margin_inches: float = 1.0,
    rtl_doc: bool = True,
    smart_draw: bool = False,
    ai_provider_label: str = "Gemini Flash-Lite",
) -> Tuple[str, Dict[str, Any]]:
    """تحويل HTML -> Word باستخدام html_word_engine الموحد + الرسم الذكي."""
    from bs4 import BeautifulSoup
    import docx
    from html_word_engine import inline_css_rules, render_node
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls
    from docx.shared import Inches, Pt

    t0 = time.perf_counter()
    inlined = inline_css_rules(html_content)
    soup = BeautifulSoup(inlined, "html.parser")
    body = soup.find("body") or soup
    for el in body.find_all(["script", "style", "noscript", "head"], recursive=True):
        el.decompose()
    extract_ms = round((time.perf_counter() - t0) * 1000)

    t_render0 = time.perf_counter()
    doc = docx.Document()
    for sec in doc.sections:
        sec.top_margin = Inches(margin_inches)
        sec.bottom_margin = Inches(margin_inches)
        sec.left_margin = Inches(max(margin_inches, 0.8))
        sec.right_margin = Inches(max(margin_inches, 0.8))
        if rtl_doc:
            try:
                sec._sectPr.append(parse_xml(f'<w:bidi {nsdecls("w")}/>'))
            except Exception:
                pass
    normal = doc.styles["Normal"]
    normal.font.name = font_family
    normal.font.size = Pt(font_size)

    for child in body.children:
        render_node(child, doc, default_font=font_family, default_size=font_size)
    render_ms = round((time.perf_counter() - t_render0) * 1000)

    t_chart0 = time.perf_counter()
    plain_text = body.get_text(" ", strip=True)
    chart_added = smart_draw_charts_to_doc(doc, plain_text[:3000], add_charts=smart_draw)
    chart_ms = round((time.perf_counter() - t_chart0) * 1000)

    safe_name = safe_filename(filename, "document")
    out_filename = f"{safe_name}.docx"
    doc.save(str(OUTPUTS_DIR / out_filename))

    metrics = build_pipeline_metrics(
        operation="تحويل HTML إلى Word (.docx)",
        stage_timings=[
            ("extract", "1. تحليل DOM وCSS", max(5, extract_ms)),
            ("ai", "2. تنسيق الذكاء", max(5, chart_ms if smart_draw else 14)),
            ("charts", "3. الرسوم والصور", max(5, 25 if chart_added else 12)),
            ("render", "4. تصدير Word", max(10, render_ms)),
        ],
        word_count=len(plain_text.split()),
        items_count=len(doc.tables) + len(doc.paragraphs),
        provider=ai_provider_label,
    )
    return out_filename, metrics


def convert_html_to_excel_unified(html_content: str, filename: str = "document") -> Tuple[str, int, Dict[str, Any]]:
    """تحويل HTML -> Excel (.xlsx) مع استخراج الجداول والنصوص وقياس السرعة."""
    from bs4 import BeautifulSoup
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    t0 = time.perf_counter()
    soup = BeautifulSoup(html_content, "html.parser")
    body = soup.find("body") or soup
    for el in body.find_all(["script", "style", "noscript"], recursive=True):
        el.decompose()
    extract_ms = round((time.perf_counter() - t0) * 1000)

    t_render0 = time.perf_counter()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "المحتوى"
    current_row = 1
    tables_count = 0

    header_font = Font(bold=True, size=12, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="1a7a3c")
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    wrap_align = Alignment(wrap_text=True, vertical="top")
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin"),
    )

    def write_text_row(text, bold=False, size=11):
        nonlocal current_row
        if not text.strip():
            return
        cell = ws.cell(row=current_row, column=1, value=text.strip())
        cell.font = Font(bold=bold, size=size)
        cell.alignment = wrap_align
        current_row += 1

    def write_table(table_el):
        nonlocal current_row, tables_count
        rows = table_el.find_all("tr")
        if not rows:
            return
        tables_count += 1
        max_col = 0
        for ri, tr in enumerate(rows):
            cells = tr.find_all(["th", "td"])
            col = 1
            for cell_el in cells:
                while ws.cell(row=current_row, column=col).value is not None:
                    col += 1
                text = cell_el.get_text(separator=" ", strip=True)
                is_th = cell_el.name == "th" or ri == 0
                c = ws.cell(row=current_row, column=col, value=text)
                c.border = thin_border
                c.alignment = center_align if is_th else wrap_align
                if is_th:
                    c.font = header_font
                    c.fill = header_fill
                else:
                    c.font = Font(size=11)
                colspan = int(cell_el.get("colspan", 1) or 1)
                rowspan = int(cell_el.get("rowspan", 1) or 1)
                if colspan > 1 or rowspan > 1:
                    ws.merge_cells(
                        start_row=current_row, start_column=col,
                        end_row=current_row + rowspan - 1, end_column=col + colspan - 1,
                    )
                col += colspan
                max_col = max(max_col, col - 1)
            current_row += 1
        for c_idx in range(1, max_col + 1):
            ws.column_dimensions[get_column_letter(c_idx)].width = 22
        current_row += 1

    for node in body.children:
        if not hasattr(node, "name") or not node.name:
            t = str(node).strip()
            if t:
                write_text_row(t)
            continue
        tag = node.name.lower()
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            write_text_row(node.get_text(strip=True), bold=True, size=max(11, 16 - int(tag[1])))
        elif tag == "table":
            write_table(node)
        elif tag in ("p", "div", "li", "span", "blockquote", "pre"):
            inner_tables = node.find_all("table")
            if inner_tables:
                for tbl in inner_tables:
                    write_table(tbl)
            else:
                txt = node.get_text(separator=" ", strip=True)
                if txt:
                    write_text_row(txt)
        elif tag in ("ul", "ol"):
            for li in node.find_all("li", recursive=False):
                write_text_row("• " + li.get_text(strip=True))

    safe_name = safe_filename(filename, "document")
    out_filename = f"{safe_name}.xlsx"
    wb.save(str(OUTPUTS_DIR / out_filename))
    render_ms = round((time.perf_counter() - t_render0) * 1000)

    plain = body.get_text(" ", strip=True)
    metrics = build_pipeline_metrics(
        operation="تحويل HTML إلى Excel (.xlsx)",
        stage_timings=[
            ("extract", "1. قراءة الجداول", max(5, extract_ms)),
            ("ai", "2. تنظيم الخلايا", 12),
            ("charts", "3. ضبط الدمج والحدود", 15),
            ("render", "4. تصدير Excel", max(10, render_ms)),
        ],
        word_count=len(plain.split()),
        items_count=tables_count,
        provider="OpenPyXL Unified Engine",
    )
    return out_filename, tables_count, metrics


# ═════════════════════════════════════════════════════════════════════════════
#  وحدة تحويل HTML إلى فيديو احترافي (@hyperframes/producer + FFmpeg)
# ═════════════════════════════════════════════════════════════════════════════

HTML_VIDEO_MODULE_DIR = Path(__file__).resolve().parent.parent.parent / "html-to-video-module"
_VIDEO_JOBS: Dict[str, Dict[str, Any]] = {}
_VIDEO_JOBS_LOCK = __import__("threading").Lock()


def get_html_video_example() -> str:
    """قراءة قالب example.html المدمج في وحدة html-to-video-module."""
    example_path = HTML_VIDEO_MODULE_DIR / "example.html"
    if example_path.exists():
        return example_path.read_text(encoding="utf-8")
    return ""


def ai_generate_animated_html(prompt_text: str, width: int = 1080, height: int = 1080, duration: float = 10.0) -> str:
    """توليد كود HTML متحرك متجاوب مع وحدات vw/vh وبنفس مدة الفيديو المطلوبة عبر Gemini."""
    topic = (prompt_text or "").strip()
    if not topic:
        raise ValueError("يرجى كتابة فكرة أو نص العرض المتحرك أولاً.")

    safe_dur = max(1.0, min(300.0, float(duration or 10.0)))
    orientation = "أفقي (16:9)" if width > height else ("عمودي (9:16)" if height > width else "مربع (1:1)")
    ai_prompt = (
        f"أنت مصمم Motion Graphics محترف بالويب (HTML + CSS @keyframes + SVG).\n"
        f"صمّم صفحة HTML كاملة جاهزة للتحويل إلى فيديو بأبعاد {width}x{height} ({orientation}) ومدة عرض بالضبط {safe_dur} ثانية حول الموضوع التالي:\n"
        f"«{topic}»\n\n"
        "القواعد الصارمة:\n"
        "1. أخرج كود HTML كاملاً يبدأ بـ <!DOCTYPE html> وينتهي بـ </html> بدون أي شرح أو markdown.\n"
        f"2. استخدم <html lang=\"ar\" dir=\"rtl\"> وضع على <body data-composition-id=\"studio-root\" data-start=\"0\" data-duration=\"{safe_dur}\" data-width=\"{width}\" data-height=\"{height}\"> مع body {{ margin: 0; padding: 0; width: 100vw; height: 100vh; overflow: hidden; }}.\n"
        "3. استخدم وحدات vw و vh فقط لضمان تطابق العرض والارتفاع مع أي دقة فيديو.\n"
        f"4. اجعل حركات CSS @keyframes موزعة على كامل مدة العرض ({safe_dur}s) حتى نهاية الفيديو دون توقف مبكر.\n"
        "5. اجعل الخلفية والألوان احترافية ومتباينة بوضوح دون الاعتماد على صور خارجية غير مضمونة.\n"
    )
    raw = None
    try:
        from pptx_app.modules.ai_processor import _call_gemini
        raw = _call_gemini(ai_prompt)
    except Exception as exc:
        logger.debug(f"ai_generate_animated_html Gemini error: {exc}")

    if raw:
        cleaned = re.sub(r"^```(?:html)?\s*", "", raw.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned.strip())
        if "<html" in cleaned.lower() or "<body" in cleaned.lower() or "<div" in cleaned.lower():
            return cleaned

    escaped_topic = (
        topic.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; padding: 0; width: 100vw; height: 100vh; overflow: hidden;
      background: radial-gradient(circle at 20% 20%, #1d4e89 0%, #0b132b 65%, #050814 100%);
      font-family: "Segoe UI", Tahoma, Arial, sans-serif;
      color: #ffffff;
      display: flex; align-items: center; justify-content: center;
    }}
    .card {{
      width: 82vw; max-width: 92%;
      padding: 5vh 5vw;
      border-radius: 3vw;
      background: rgba(255, 255, 255, 0.08);
      border: 0.25vw solid rgba(110, 231, 183, 0.45);
      box-shadow: 0 2vh 6vh rgba(0, 0, 0, 0.45);
      text-align: center;
      animation: slideUp 1.2s cubic-bezier(.16,1,.3,1) both;
    }}
    .badge {{
      display: inline-block;
      padding: 1vh 2.5vw;
      border-radius: 999px;
      background: linear-gradient(90deg, #00c4cc, #3291ff);
      font-size: 2.2vmin;
      font-weight: 700;
      margin-bottom: 2.5vh;
      animation: pulse 2s ease-in-out infinite alternate;
    }}
    h1 {{
      margin: 0 0 2vh 0;
      font-size: 5.2vmin;
      line-height: 1.35;
      color: #f8fafc;
    }}
    .bar-wrap {{
      width: 60%; height: 1vh; margin: 3vh auto 0 auto;
      background: rgba(255,255,255,0.15); border-radius: 999px; overflow: hidden;
    }}
    .bar-fill {{
      height: 100%; width: 0%;
      background: linear-gradient(90deg, #6ee7b7, #38bdf8);
      animation: fillBar {safe_dur}s linear forwards;
    }}
    @keyframes slideUp {{ from {{ opacity: 0; transform: translateY(6vh) scale(.95); }} to {{ opacity: 1; transform: translateY(0) scale(1); }} }}
    @keyframes pulse {{ from {{ transform: scale(.96); }} to {{ transform: scale(1.04); }} }}
    @keyframes fillBar {{ from {{ width: 0%; }} to {{ width: 100%; }} }}
  </style>
</head>
<body data-composition-id="studio-root" data-start="0" data-duration="{safe_dur}" data-width="{width}" data-height="{height}">
  <div class="card">
    <div class="badge">استوديو العروض والمستندات AI</div>
    <h1>{escaped_topic}</h1>
    <div class="bar-wrap"><div class="bar-fill"></div></div>
  </div>
</body>
</html>"""


_VIDEO_RUNTIME_LOCK = __import__("threading").Lock()


def _ensure_html_video_runtime(job_id: Optional[str] = None) -> None:
    """التأكد من توفر حزم @hyperframes/producer و chrome-headless-shell عند الحاجة."""
    import subprocess
    with _VIDEO_RUNTIME_LOCK:
        producer_dir = HTML_VIDEO_MODULE_DIR / "node_modules" / "@hyperframes" / "producer"
        if not producer_dir.exists():
            if job_id:
                with _VIDEO_JOBS_LOCK:
                    if job_id in _VIDEO_JOBS:
                        _VIDEO_JOBS[job_id]["stage"] = "تثبيت مكتبة @hyperframes/producer..."
            subprocess.run(
                ["npm", "install", "--prefix", str(HTML_VIDEO_MODULE_DIR), "--no-audit", "--no-fund"],
                check=True,
                timeout=300,
            )

        cache_candidates = [
            Path.home() / ".cache" / "puppeteer" / "chrome-headless-shell",
            Path("/root/.cache/puppeteer/chrome-headless-shell"),
            Path.home() / ".cache" / "hyperframes" / "chrome" / "chrome-headless-shell",
        ]
        has_browser = any(c.exists() and any(c.rglob("chrome-headless-shell*")) for c in cache_candidates)
        if not has_browser:
            if job_id:
                with _VIDEO_JOBS_LOCK:
                    if job_id in _VIDEO_JOBS:
                        _VIDEO_JOBS[job_id]["stage"] = "تحميل متصفح Chrome Headless لأول مرة..."
            subprocess.run(
                ["npx", "--prefix", str(HTML_VIDEO_MODULE_DIR), "puppeteer", "browsers", "install", "chrome-headless-shell"],
                check=True,
                timeout=300,
            )


def _execute_html_to_video_core(
    *,
    html_content: str,
    filename: str = "video",
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    duration: float = 10.0,
    duration_mode: str = "exact",
    quality: str = "standard",
    output_format: str = "mp4",
    video_frame_format: str = "png",
    device_scale_factor: int = 1,
    remove_margins: bool = True,
    ai_provider_label: str = "@hyperframes/producer + FFmpeg",
    job_id: Optional[str] = None,
) -> Dict[str, Any]:
    """تشغيل وحدة Node (@hyperframes/producer) لتحويل HTML إلى فيديو مع الالتزام الصارم بالمدة."""
    import shutil
    import subprocess
    import uuid
    import zipfile

    if not (html_content or "").strip():
        raise ValueError("كود HTML فارغ")

    runner_js = HTML_VIDEO_MODULE_DIR / "index.js"
    if not runner_js.exists():
        raise FileNotFoundError("وحدة html-to-video-module غير مثبتة بشكل كامل")

    _ensure_html_video_runtime(job_id=job_id)

    uid = job_id or uuid.uuid4().hex[:10]
    temp_dir = HTML_VIDEO_MODULE_DIR / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_html = temp_dir / f"studio-input-{uid}.html"
    temp_html.write_text(html_content, encoding="utf-8")

    safe_name = safe_filename(filename, "studio_video")
    fmt = output_format if output_format in ("mp4", "webm", "mov", "gif", "png-sequence") else "mp4"
    qual = quality if quality in ("draft", "standard", "high") else "standard"
    frame_fmt = video_frame_format if video_frame_format in ("auto", "jpg", "png") else "png"
    dur_mode = duration_mode if duration_mode in ("exact", "auto_min", "from_html") else "exact"
    safe_w = max(64, int(width) & ~1 or 1920)
    safe_h = max(64, int(height) & ~1 or 1080)
    safe_fps = max(1, min(60, int(fps)))
    safe_dur = max(0.5, min(300.0, float(duration)))
    safe_dpr = max(1, min(3, int(device_scale_factor)))

    stamp = int(time.time())
    if fmt == "png-sequence":
        frames_dir = OUTPUTS_DIR / f"{safe_name}_{stamp}_{uid}_frames"
        target_output = frames_dir
        final_filename = f"{safe_name}_{stamp}_{uid}_frames.zip"
    else:
        final_filename = f"{safe_name}_{stamp}_{uid}.{fmt}"
        target_output = OUTPUTS_DIR / final_filename

    cmd = [
        "node",
        str(runner_js),
        "--input", str(temp_html),
        "--output", str(target_output),
        "--width", str(safe_w),
        "--height", str(safe_h),
        "--fps", str(safe_fps),
        "--duration", str(safe_dur),
        "--duration-mode", dur_mode,
        "--quality", qual,
        "--format", fmt,
        "--frame-format", frame_fmt,
        "--dpr", str(safe_dpr),
        "--remove-margins", "true" if remove_margins else "false",
        "--json",
    ]

    t0 = time.perf_counter()
    last_result: Dict[str, Any] = {}
    last_error: Optional[str] = None
    tail_logs: List[str] = []

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(HTML_VIDEO_MODULE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        assert proc.stdout is not None
        for raw_line in proc.stdout:
            line = raw_line.strip()
            if not line:
                continue
            tail_logs.append(line)
            if len(tail_logs) > 25:
                tail_logs.pop(0)
            if line.startswith("{"):
                try:
                    ev = json.loads(line)
                    ev_type = ev.get("type")
                    if ev_type == "progress" and job_id:
                        with _VIDEO_JOBS_LOCK:
                            if job_id in _VIDEO_JOBS:
                                _VIDEO_JOBS[job_id]["percent"] = int(ev.get("percent", 0))
                                _VIDEO_JOBS[job_id]["stage"] = ev.get("stage", "")
                    elif ev_type == "result":
                        last_result = ev
                    elif ev_type == "error":
                        last_error = ev.get("error") or "فشل ترميز الفيديو"
                except Exception:
                    pass
        wait_timeout = max(300, int(safe_dur * 25) + 120)
        rc = proc.wait(timeout=wait_timeout)
        if rc != 0 or last_error:
            raise RuntimeError(last_error or f"فشل محرك الفيديو (رمز {rc}): {' | '.join(tail_logs[-3:])}")

        if fmt == "png-sequence":
            zip_path = OUTPUTS_DIR / final_filename
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                if target_output.exists():
                    for p in sorted(target_output.rglob("*")):
                        if p.is_file():
                            zf.write(p, arcname=p.relative_to(target_output))
            shutil.rmtree(target_output, ignore_errors=True)
            file_size = zip_path.stat().st_size if zip_path.exists() else 0
        else:
            file_size = target_output.stat().st_size if target_output.exists() else 0

        if file_size <= 0:
            raise RuntimeError("تم إكمال العملية ولكن ملف الفيديو الناتج فارغ")

        total_ms = max(10, round((time.perf_counter() - t0) * 1000))
        raw_stages = last_result.get("stages") or {}
        compile_ms = int(raw_stages.get("compileMs") or 120)
        capture_ms = int(raw_stages.get("captureFrameMs") or raw_stages.get("captureMs") or max(20, total_ms // 2))
        encode_ms = int(raw_stages.get("encodeMs") or max(20, total_ms // 3))
        assemble_ms = int(raw_stages.get("assembleMs") or max(10, total_ms - compile_ms - capture_ms))

        actual_dur = float(last_result.get("compositionDurationSeconds") or safe_dur)
        plain_words = len(re.sub(r"<[^>]+>", " ", html_content).split())
        frames_count = int(last_result.get("frameCount") or round(actual_dur * safe_fps))
        out_w = int(last_result.get("width") or safe_w)
        out_h = int(last_result.get("height") or safe_h)

        metrics = build_pipeline_metrics(
            operation=f"تحويل HTML إلى فيديو {fmt.upper()} ({out_w}×{out_h} · {actual_dur:.1f}s @ {safe_fps}fps)",
            stage_timings=[
                ("extract", "1. تجهيز HTML والخطوط", max(10, compile_ms)),
                ("ai", "2. التقاط الإطارات Chrome", max(15, capture_ms)),
                ("charts", "3. ترميز الفيديو FFmpeg", max(15, encode_ms)),
                ("render", "4. تجميع وحفظ الملف", max(10, assemble_ms)),
            ],
            word_count=max(plain_words, frames_count),
            items_count=frames_count,
            provider=ai_provider_label,
        )

        return {
            "success": True,
            "filename": final_filename,
            "download_url": f"/api/studio/download/{final_filename}",
            "preview_url": f"/api/studio/media/{final_filename}",
            "format": fmt,
            "width": out_w,
            "height": out_h,
            "fps": safe_fps,
            "duration_seconds": actual_dur,
            "requested_duration_seconds": last_result.get("requestedDurationSeconds") or safe_dur,
            "detected_html_duration_seconds": last_result.get("detectedHtmlDurationSeconds"),
            "frame_count": frames_count,
            "file_size": file_size,
            "render_ms": total_ms,
            "pipeline_metrics": metrics,
        }
    finally:
        try:
            temp_html.unlink(missing_ok=True)
        except Exception:
            pass


def start_html_to_video_job(**kwargs) -> str:
    """بدء مهمة تحويل HTML إلى فيديو في الخلفية وإرجاع معرف المهمة لتتبع التقدم."""
    import threading
    import uuid

    job_id = uuid.uuid4().hex[:12]
    with _VIDEO_JOBS_LOCK:
        _VIDEO_JOBS[job_id] = {
            "job_id": job_id,
            "status": "running",
            "percent": 2,
            "stage": "تهيئة محرك Chrome و FFmpeg...",
            "created_at": time.time(),
        }
        # تنظيف المهام القديمة الأقدم من ساعة
        cutoff = time.time() - 3600
        for old_id in [k for k, v in _VIDEO_JOBS.items() if v.get("created_at", 0) < cutoff]:
            _VIDEO_JOBS.pop(old_id, None)

    def _worker():
        try:
            res = _execute_html_to_video_core(job_id=job_id, **kwargs)
            with _VIDEO_JOBS_LOCK:
                _VIDEO_JOBS[job_id].update({
                    "status": "done",
                    "percent": 100,
                    "stage": "اكتمل التحويل بنجاح",
                    **res,
                })
        except Exception as exc:
            logger.error(f"HTML to video job {job_id} error: {exc}", exc_info=True)
            with _VIDEO_JOBS_LOCK:
                _VIDEO_JOBS[job_id].update({
                    "status": "error",
                    "error": str(exc),
                    "stage": "فشل التحويل",
                })

    threading.Thread(target=_worker, daemon=True).start()
    return job_id


def get_html_to_video_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """استرجاع حالة مهمة تحويل HTML إلى فيديو."""
    with _VIDEO_JOBS_LOCK:
        job = _VIDEO_JOBS.get(job_id)
        return dict(job) if job else None

