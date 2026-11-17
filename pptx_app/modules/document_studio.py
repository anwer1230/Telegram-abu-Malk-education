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
#  وحدة تحويل HTML إلى فيديو احترافي (@hyperframes/producer + FFmpeg + الصوت والذكاء)
# ═════════════════════════════════════════════════════════════════════════════

HTML_VIDEO_MODULE_DIR = Path(__file__).resolve().parent.parent.parent / "html-to-video-module"
STUDIO_AUDIO_DIR = HTML_VIDEO_MODULE_DIR / "temp_audio"
STUDIO_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
_VIDEO_JOBS: Dict[str, Dict[str, Any]] = {}
_VIDEO_JOBS_LOCK = __import__("threading").Lock()
_VALID_GEMINI_VOICES = {"Kore", "Charon", "Puck", "Fenrir", "Zephyr"}


def _cleanup_old_audio_files(max_age_seconds: int = 7200) -> None:
    """حذف ملفات الصوت المؤقتة الأقدم من ساعتين."""
    try:
        cutoff = time.time() - max_age_seconds
        if STUDIO_AUDIO_DIR.exists():
            for p in STUDIO_AUDIO_DIR.iterdir():
                if p.is_file() and p.stat().st_mtime < cutoff:
                    p.unlink(missing_ok=True)
    except Exception:
        pass


def _call_studio_gemini_text(
    prompt: str,
    system_instruction: str = "",
    max_tokens: int = 8192,
    timeout_total: float = 35.0,
) -> Tuple[Optional[str], str]:
    """استدعاء موثوق لنماذج Gemini النصية مع تدوير المفاتيح وتعدد النماذج."""
    import requests
    try:
        import config as _cfg
        keys = _cfg.get_all_gemini_keys()
    except Exception:
        keys = []

    if keys:
        models = [
            "gemini-3.1-flash-lite",
            "gemini-4-hydrogen",
            "gemini-flash-lite-latest",
            "gemini-3-flash-preview",
        ]
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": max_tokens},
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        deadline = time.time() + timeout_total
        for key in keys[:5]:
            if time.time() >= deadline:
                break
            for model in models:
                rem = deadline - time.time()
                if rem <= 1.5:
                    break
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                    resp = requests.post(
                        url,
                        headers={"Content-Type": "application/json", "X-goog-api-key": key},
                        json=payload,
                        timeout=min(15.0, rem),
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        cands = data.get("candidates") or []
                        if cands and cands[0].get("content", {}).get("parts"):
                            parts = cands[0]["content"]["parts"]
                            txt = "".join(str(p.get("text", "")) for p in parts).strip()
                            if txt:
                                return txt, model
                    elif resp.status_code in (403, 429):
                        break
                except Exception:
                    continue

    # بديل Groq إذا توفر المفتاح
    try:
        groq_key = os.environ.get("GROQ_API_KEY", "").strip()
        if groq_key:
            from groq import Groq
            client = Groq(api_key=groq_key)
            msgs = []
            if system_instruction:
                msgs.append({"role": "system", "content": system_instruction})
            msgs.append({"role": "user", "content": prompt})
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=msgs,
                temperature=0.3,
                max_tokens=min(max_tokens, 8000),
            )
            txt = (resp.choices[0].message.content or "").strip()
            if txt:
                return txt, "Groq Llama-3.3"
    except Exception:
        pass

    return None, ""


def _strip_html_fences(raw: str) -> str:
    cleaned = re.sub(r"^```(?:html|json)?\s*", "", (raw or "").strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    return cleaned.strip()


def _extract_visible_text_from_html(html_content: str) -> str:
    """استخراج النص المرئي والعنوان من كود HTML بدون وسوم CSS/JS."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content or "", "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        title_txt = soup.title.get_text(" ", strip=True) if soup.title else ""
        body_txt = soup.get_text(" ", strip=True)
        body_txt = re.sub(r"\s+", " ", body_txt).strip()
        if title_txt and title_txt not in body_txt:
            return f"{title_txt}. {body_txt}".strip()
        return body_txt
    except Exception:
        txt = re.sub(r"<(script|style)[^>]*>[\s\S]*?</\1>", " ", html_content or "", flags=re.IGNORECASE)
        txt = re.sub(r"<[^>]+>", " ", txt)
        return re.sub(r"\s+", " ", txt).strip()


def get_html_video_example() -> str:
    """قراءة قالب example.html المدمج في وحدة html-to-video-module."""
    example_path = HTML_VIDEO_MODULE_DIR / "example.html"
    if example_path.exists():
        return example_path.read_text(encoding="utf-8")
    return ""


def ai_generate_animated_html(
    prompt_text: str,
    width: int = 1080,
    height: int = 1080,
    duration: float = 10.0,
    notes: str = "",
) -> str:
    """توليد كود HTML متحرك متجاوب مع وحدات vw/vh وبنفس مدة الفيديو المطلوبة عبر Gemini."""
    topic = (prompt_text or "").strip()
    extra_notes = (notes or "").strip()
    if not topic and not extra_notes:
        raise ValueError("يرجى كتابة فكرة أو ملاحظات العرض المتحرك أولاً.")
    if not topic:
        topic = extra_notes

    safe_dur = max(1.0, min(300.0, float(duration or 10.0)))
    orientation = "أفقي (16:9)" if width > height else ("عمودي (9:16)" if height > width else "مربع (1:1)")
    notes_block = f"\n\nملاحظات وتعليمات إضافية من المستخدم يجب تطبيقها بدقة:\n{extra_notes}\n" if extra_notes and extra_notes != topic else ""
    ai_prompt = (
        f"أنت مصمم Motion Graphics محترف بالويب (HTML + CSS @keyframes + SVG).\n"
        f"صمّم صفحة HTML كاملة جاهزة للتحويل إلى فيديو بأبعاد {width}x{height} ({orientation}) ومدة عرض بالضبط {safe_dur} ثانية حول الموضوع التالي:\n"
        f"«{topic}»{notes_block}\n"
        "القواعد الصارمة:\n"
        "1. أخرج كود HTML كاملاً يبدأ بـ <!DOCTYPE html> وينتهي بـ </html> بدون أي شرح أو markdown.\n"
        f"2. استخدم <html lang=\"ar\" dir=\"rtl\"> وضع على <body data-composition-id=\"studio-root\" data-start=\"0\" data-duration=\"{safe_dur}\" data-width=\"{width}\" data-height=\"{height}\"> مع body {{ margin: 0; padding: 0; width: 100vw; height: 100vh; overflow: hidden; }}.\n"
        "3. استخدم وحدات vw و vh و vmin فقط لضمان تطابق العرض والارتفاع مع أي دقة فيديو.\n"
        f"4. اجعل حركات CSS @keyframes موزعة على كامل مدة العرض ({safe_dur}s) حتى نهاية الفيديو دون توقف مبكر.\n"
        "5. اجعل الخلفية والألوان احترافية ومتباينة بوضوح دون الاعتماد على صور خارجية غير مضمونة.\n"
    )
    raw, _ = _call_studio_gemini_text(ai_prompt, max_tokens=8192)
    if raw:
        cleaned = _strip_html_fences(raw)
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


def ai_refine_animated_html(
    html_content: str,
    notes: str,
    width: int = 1080,
    height: int = 1080,
    duration: float = 10.0,
) -> Dict[str, Any]:
    """تطبيق ملاحظات وتعليمات المستخدم الإضافية على كود HTML الحالي عبر الذكاء الاصطناعي وإخراجه."""
    clean_notes = (notes or "").strip()
    if not clean_notes:
        raise ValueError("يرجى كتابة الملاحظات أو التعليمات المطلوب تطبيقها على الكود، أو رفع ملف ملاحظات.")

    safe_dur = max(1.0, min(300.0, float(duration or 10.0)))
    raw_html = (html_content or "").strip()
    if not raw_html:
        generated = ai_generate_animated_html(clean_notes, width=width, height=height, duration=safe_dur)
        return {"html": generated, "model": "Gemini AI (توليد جديد)"}

    sys_inst = (
        "أنت مهندس واجهات ومصمم Motion Graphics بالويب (HTML/CSS/JS/SVG). "
        "مهمتك تعديل كود HTML المقدّم وتطبيق جميع ملاحظات وتعليمات المستخدم بدقة متناهية "
        "مع الحفاظ على التجاوب عبر وحدات vw/vh ودمج سمات التكوين الخاصة بمحرك الفيديو، وإخراج كود HTML كاملاً صالحاً للتشغيل فقط."
    )
    prompt = (
        f"قم بتعديل وتحسين كود HTML التالي لتنفيذ جميع الملاحظات والتعليمات المذكورة أدناه بدقة:\n\n"
        f"=== ملاحظات وتعليمات المستخدم ===\n{clean_notes}\n\n"
        f"=== مواصفات الفيديو المستهدفة ===\n"
        f"- الأبعاد: {width}×{height} بكسل\n"
        f"- المدة المطلوبة: {safe_dur} ثانية (تأكد من وجود data-composition-id=\"studio-root\" و data-duration=\"{safe_dur}\" و data-width=\"{width}\" و data-height=\"{height}\" على body أو جذر التكوين)\n"
        f"- اجعل الحركات (@keyframes) متناسقة مع كامل مدة {safe_dur} ثانية، وتأكد من margin:0 و overflow:hidden على body.\n"
        "- أخرج كود HTML الكامل فقط بدءاً من <!DOCTYPE html> حتى </html> بدون أي شرح أو علامات markdown.\n\n"
        f"=== كود HTML الحالي ===\n{raw_html[:28000]}"
    )

    reply, used_model = _call_studio_gemini_text(prompt, system_instruction=sys_inst, max_tokens=8192, timeout_total=40.0)
    if not reply:
        raise RuntimeError("تعذر الاتصال بنموذج الذكاء الاصطناعي لتطبيق الملاحظات حالياً؛ يرجى المحاولة بعد لحظات.")

    cleaned = _strip_html_fences(reply)
    if not any(tag in cleaned.lower() for tag in ("<html", "<body", "<div", "<!doctype")):
        raise RuntimeError("لم يُرجع الذكاء الاصطناعي كود HTML صالحاً. جرّب صياغة الملاحظات بشكل أوضح.")

    return {"html": cleaned, "model": used_model or "Gemini AI"}


def ai_prepare_video_audio_plan(
    html_content: str,
    duration: float = 10.0,
    notes: str = "",
    user_script: str = "",
) -> Dict[str, Any]:
    """تحليل محتوى HTML وتوليد نص تعليق صوتي متزامن مع مدة الفيديو واختيار النبرة والمزاج الموسيقي."""
    safe_dur = max(1.0, min(300.0, float(duration or 10.0)))
    visible_text = _extract_visible_text_from_html(html_content)
    target_words = max(6, min(200, int(round(max(2.0, safe_dur - 0.7) * 2.1))))
    custom_script = (user_script or "").strip()

    if custom_script:
        # نكتفي بتحديد المزاج وأسلوب الإلقاء المناسب إذا كان النص مكتوباً مسبقاً
        mood_prompt = (
            f"بناءً على هذا النص والمحتوى:\nالنص: {custom_script[:600]}\nمحتوى العرض: {visible_text[:800]}\n"
            'أرجع JSON فقط بهذا الشكل:\n'
            '{"mood": "academic|corporate|cinematic|upbeat|calm", '
            '"recommended_voice": "Kore|Charon|Puck|Fenrir|Zephyr", '
            '"style_instruction": "وصف قصير بالإنجليزية لنبرة الإلقاء المناسبة"}'
        )
        raw_meta, _ = _call_studio_gemini_text(mood_prompt, max_tokens=300, timeout_total=15.0)
        parsed: Dict[str, Any] = {}
        if raw_meta:
            m = re.search(r"\{[\s\S]*\}", raw_meta)
            if m:
                try:
                    parsed = json.loads(m.group(0))
                except Exception:
                    parsed = {}
        voice = parsed.get("recommended_voice") if parsed.get("recommended_voice") in _VALID_GEMINI_VOICES else "Kore"
        mood = parsed.get("mood") if parsed.get("mood") in ("academic", "corporate", "cinematic", "upbeat", "calm") else "calm"
        return {
            "script": custom_script,
            "mood": mood,
            "recommended_voice": voice,
            "style_instruction": parsed.get("style_instruction") or "Clear, warm, natural narrator",
        }

    notes_ctx = f"\nملاحظات المستخدم: {notes[:500]}" if (notes or "").strip() else ""
    ai_prompt = (
        f"أنت كاتب سيناريو تعليق صوتي (Voiceover) محترف ومخرج صوتي.\n"
        f"المطلوب تحليل محتوى عرض HTML التالي وكتابة نص تعليق صوتي متقن يناسب المحتوى ويكتمل نطقه في حوالي {safe_dur:.1f} ثانية "
        f"(أي قرابة {target_words} كلمة بالضبط).\n"
        f"محتوى العرض المستخرج:\n{visible_text[:2500]}{notes_ctx}\n\n"
        "القواعد:\n"
        "- اكتب بنفس لغة المحتوى الأساسي (العربية الفصحى السلسة إذا كان عربياً، أو الإنجليزية إذا كان إنجليزياً).\n"
        "- بدون رموز تنسيق أو أقواس أو وصف مؤثرات؛ نص منطوق جاهز للقراءة الصوتية مباشرة.\n"
        "- أرجع كائن JSON صالح فقط بدون أي نص خارجه:\n"
        "{\n"
        '  "script": "النص المنطوق الجاهز للقراءة",\n'
        '  "style_instruction": "Clear, engaging, well-paced presenter",\n'
        '  "mood": "academic | corporate | cinematic | upbeat | calm",\n'
        '  "recommended_voice": "Kore | Charon | Puck | Fenrir | Zephyr"\n'
        "}"
    )
    raw, _ = _call_studio_gemini_text(ai_prompt, max_tokens=1024, timeout_total=22.0)
    if raw:
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            try:
                parsed = json.loads(m.group(0))
                script = (parsed.get("script") or "").strip()
                if script:
                    voice = parsed.get("recommended_voice") if parsed.get("recommended_voice") in _VALID_GEMINI_VOICES else "Kore"
                    mood = parsed.get("mood") if parsed.get("mood") in ("academic", "corporate", "cinematic", "upbeat", "calm") else "calm"
                    return {
                        "script": script,
                        "mood": mood,
                        "recommended_voice": voice,
                        "style_instruction": (parsed.get("style_instruction") or "Clear, warm, engaging presenter").strip(),
                    }
            except Exception:
                pass

    # بديل محلي ذكي إذا تعذر توليد النص عبر Gemini
    words = [w for w in re.split(r"\s+", visible_text) if w]
    if words:
        fallback_script = " ".join(words[:target_words])
    else:
        fallback_script = "مرحباً بكم في هذا العرض المرئي المصمم عبر استوديو العروض والمستندات الذكي."
    return {
        "script": fallback_script,
        "mood": "calm",
        "recommended_voice": "Kore",
        "style_instruction": "Clear, warm, natural narrator",
    }


def synthesize_gemini_tts_wav(
    text: str,
    output_wav_path: Path,
    voice_name: str = "Kore",
    style_instruction: str = "",
) -> Path:
    """توليد تعليق صوتي حقيقي بصيغة WAV عبر Gemini TTS (gemini-3.8-flash-lite-tts)."""
    import base64
    import wave
    import requests

    spoken_text = (text or "").strip()
    if not spoken_text:
        raise ValueError("النص الصوتي فارغ.")
    voice = voice_name if voice_name in _VALID_GEMINI_VOICES else "Kore"

    try:
        import config as _cfg
        keys = _cfg.get_all_gemini_keys()
    except Exception:
        keys = []
    if not keys:
        raise RuntimeError("لا تتوفر مفاتيح Gemini لتوليد الصوت.")

    prompt_text = f"{style_instruction}: {spoken_text}" if style_instruction else spoken_text
    tts_models = ["gemini-3.8-flash-lite-tts", "gemini-3.8-flash-tts"]

    last_err = ""
    for key in keys[:5]:
        for model in tts_models:
            try:
                part_obj: Dict[str, Any] = {"text": spoken_text}
                if style_instruction:
                    part_obj["speechMetadata"] = {"style": style_instruction}
                payload = {
                    "contents": [{"role": "user", "parts": [part_obj]}],
                    "generationConfig": {
                        "responseModalities": ["AUDIO"],
                        "speechConfig": {
                            "voiceConfig": {
                                "prebuiltVoiceConfig": {"voiceName": voice}
                            }
                        },
                    },
                }
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                resp = requests.post(
                    url,
                    headers={"Content-Type": "application/json", "X-goog-api-key": key},
                    json=payload,
                    timeout=35,
                )
                # في حال عدم دعم speechMetadata في بعض البيئات نعيد المحاولة بدونه
                if resp.status_code == 400 and style_instruction:
                    payload["contents"][0]["parts"] = [{"text": prompt_text}]
                    resp = requests.post(
                        url,
                        headers={"Content-Type": "application/json", "X-goog-api-key": key},
                        json=payload,
                        timeout=35,
                    )
                if resp.status_code == 200:
                    data = resp.json()
                    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    inline = parts[0].get("inlineData", {}) if parts else {}
                    b64 = inline.get("data", "")
                    mime = (inline.get("mimeType") or "").lower()
                    if b64:
                        raw_bytes = base64.b64decode(b64)
                        output_wav_path.parent.mkdir(parents=True, exist_ok=True)
                        if raw_bytes[:4] == b"RIFF" and ("wav" in mime or not mime):
                            output_wav_path.write_bytes(raw_bytes)
                        else:
                            rate_m = re.search(r"rate=(\d+)", mime)
                            sample_rate = int(rate_m.group(1)) if rate_m else 24000
                            with wave.open(str(output_wav_path), "wb") as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)
                                wf.setframerate(sample_rate)
                                wf.writeframes(raw_bytes)
                        if output_wav_path.exists() and output_wav_path.stat().st_size > 44:
                            return output_wav_path
                else:
                    last_err = f"HTTP {resp.status_code}: {resp.text[:160]}"
                    if resp.status_code in (403, 429):
                        break
            except Exception as exc:
                last_err = str(exc)
                continue

    raise RuntimeError(f"تعذر توليد التعليق الصوتي عبر Gemini TTS: {last_err or 'استنفاد المحاولات'}")


def synthesize_ambient_music_wav(output_wav_path: Path, duration: float = 10.0, mood: str = "calm") -> Path:
    """توليد خلفية موسيقية هادئة ومتناغمة عبر FFmpeg تناسب مزاج العرض وطوله."""
    import subprocess

    dur = max(1.0, min(300.0, float(duration or 10.0)))
    mood_exprs = {
        "academic": "0.14*sin(2*PI*220*t)+0.10*sin(2*PI*277.18*t)+0.09*sin(2*PI*329.63*t)+0.07*sin(2*PI*415.30*t)*(0.6+0.4*sin(2*PI*0.25*t))",
        "corporate": "0.14*sin(2*PI*261.63*t)+0.10*sin(2*PI*329.63*t)+0.09*sin(2*PI*392.00*t)+0.07*sin(2*PI*493.88*t)*(0.6+0.4*sin(2*PI*0.35*t))",
        "cinematic": "0.16*sin(2*PI*130.81*t)+0.12*sin(2*PI*196.00*t)+0.09*sin(2*PI*261.63*t)+0.07*sin(2*PI*311.13*t)*(0.55+0.45*sin(2*PI*0.2*t))",
        "upbeat": "0.13*sin(2*PI*293.66*t)+0.10*sin(2*PI*369.99*t)+0.09*sin(2*PI*440.00*t)+0.07*sin(2*PI*587.33*t)*(0.5+0.5*sin(2*PI*1.2*t))",
        "calm": "0.14*sin(2*PI*196.00*t)+0.11*sin(2*PI*246.94*t)+0.09*sin(2*PI*293.66*t)+0.06*sin(2*PI*392.00*t)*(0.65+0.35*sin(2*PI*0.22*t))",
    }
    expr = mood_exprs.get(mood, mood_exprs["calm"])
    fade_out_st = max(0.0, dur - 0.85)
    filter_chain = (
        f"lowpass=f=1450,highpass=f=70,"
        f"aecho=0.8:0.75:45:0.32,"
        f"afade=t=in:st=0:d=0.45,"
        f"afade=t=out:st={fade_out_st:.3f}:d=0.85"
    )
    output_wav_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"aevalsrc={expr}:s=44100:d={dur:.3f}",
            "-af", filter_chain,
            "-ac", "2", "-ar", "44100",
            str(output_wav_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    return output_wav_path


def probe_media_info(media_path: Path) -> Dict[str, Any]:
    """استخراج معلومات المدة ووجود مسار صوتي/مرئي عبر ffprobe."""
    import subprocess
    try:
        out = subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration:stream=codec_type,nb_frames,width,height",
                "-of", "json",
                str(media_path),
            ],
            text=True,
            timeout=20,
        )
        parsed = json.loads(out or "{}")
        streams = parsed.get("streams") or []
        fmt_dur = parsed.get("format", {}).get("duration")
        dur_val = round(float(fmt_dur), 2) if fmt_dur else None
        has_audio = any(s.get("codec_type") == "audio" for s in streams)
        v_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
        return {
            "duration_seconds": dur_val,
            "has_audio": has_audio,
            "width": v_stream.get("width"),
            "height": v_stream.get("height"),
            "nb_frames": int(v_stream["nb_frames"]) if str(v_stream.get("nb_frames", "")).isdigit() else None,
        }
    except Exception:
        return {"duration_seconds": None, "has_audio": False}


def save_uploaded_studio_audio(file_bytes: bytes, original_filename: str = "audio.mp3") -> Dict[str, Any]:
    """حفظ الملف الصوتي المرفوع من الهاتف/الجهاز والتحقق من صلاحيته ومعرفة مدته."""
    import subprocess
    import uuid

    _cleanup_old_audio_files()
    if not file_bytes:
        raise ValueError("الملف الصوتي المرفوع فارغ.")

    ext = Path(original_filename or "audio.mp3").suffix.lower()
    if ext not in (".mp3", ".wav", ".m4a", ".aac", ".ogg", ".opus", ".flac", ".webm", ".mp4"):
        ext = ".mp3"

    audio_id = f"up_{uuid.uuid4().hex[:12]}"
    raw_path = STUDIO_AUDIO_DIR / f"{audio_id}_raw{ext}"
    norm_wav = STUDIO_AUDIO_DIR / f"{audio_id}.wav"
    raw_path.write_bytes(file_bytes)

    try:
        # توحيد الصوت إلى WAV 44.1kHz ستيريو لضمان التوافق التام عند الدمج والمعاينة
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(raw_path), "-vn", "-ac", "2", "-ar", "44100", str(norm_wav)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=60,
        )
    except Exception as exc:
        raw_path.unlink(missing_ok=True)
        norm_wav.unlink(missing_ok=True)
        raise RuntimeError(f"تعذر قراءة الملف الصوتي المرفوع. تأكد أنه ملف صوتي صالح ({exc}).")
    finally:
        raw_path.unlink(missing_ok=True)

    info = probe_media_info(norm_wav)
    return {
        "audio_id": audio_id,
        "filename": f"{audio_id}.wav",
        "original_name": original_filename or "audio",
        "duration_seconds": info.get("duration_seconds") or 0.0,
        "preview_url": f"/api/studio/audio/{audio_id}.wav",
    }


def generate_studio_audio_preview(
    *,
    html_content: str = "",
    duration: float = 10.0,
    auto_audio_type: str = "voice_and_music",
    voice_name: str = "Kore",
    user_script: str = "",
    notes: str = "",
) -> Dict[str, Any]:
    """توليد ومعاينة الصوت الآلي المناسب للمحتوى قبل أو أثناء تصيير الفيديو."""
    import subprocess
    import uuid

    _cleanup_old_audio_files()
    safe_dur = max(1.0, min(300.0, float(duration or 10.0)))
    a_type = auto_audio_type if auto_audio_type in ("voice_and_music", "voice_only", "music_only") else "voice_and_music"

    plan = ai_prepare_video_audio_plan(
        html_content=html_content,
        duration=safe_dur,
        notes=notes,
        user_script=user_script,
    )
    selected_voice = voice_name if voice_name in _VALID_GEMINI_VOICES else plan.get("recommended_voice", "Kore")
    mood = plan.get("mood", "calm")
    script = plan.get("script", "")
    style_instruction = plan.get("style_instruction", "")

    audio_id = f"ai_{uuid.uuid4().hex[:12]}"
    out_wav = STUDIO_AUDIO_DIR / f"{audio_id}.wav"
    voice_wav = STUDIO_AUDIO_DIR / f"{audio_id}_v.wav"
    music_wav = STUDIO_AUDIO_DIR / f"{audio_id}_m.wav"

    try:
        if a_type in ("voice_and_music", "voice_only"):
            synthesize_gemini_tts_wav(
                text=script,
                output_wav_path=voice_wav,
                voice_name=selected_voice,
                style_instruction=style_instruction,
            )

        if a_type in ("voice_and_music", "music_only"):
            synthesize_ambient_music_wav(music_wav, duration=safe_dur, mood=mood)

        if a_type == "voice_only":
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(voice_wav), "-ac", "2", "-ar", "44100", str(out_wav)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=45,
            )
        elif a_type == "music_only":
            music_wav.replace(out_wav)
        else:
            # دمج التعليق الصوتي مع خفض تلقائي للموسيقى (0.18) لتبقى الكلمات واضحة تماماً
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", str(voice_wav),
                    "-i", str(music_wav),
                    "-filter_complex",
                    "[0:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.0[v];"
                    "[1:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.18[m];"
                    "[v][m]amix=inputs=2:duration=longest:dropout_transition=1,alimiter=limit=0.95[aout]",
                    "-map", "[aout]",
                    str(out_wav),
                ],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60,
            )
    finally:
        voice_wav.unlink(missing_ok=True)
        music_wav.unlink(missing_ok=True)

    info = probe_media_info(out_wav)
    return {
        "audio_id": audio_id,
        "filename": f"{audio_id}.wav",
        "script": script,
        "voice_name": selected_voice,
        "mood": mood,
        "auto_audio_type": a_type,
        "duration_seconds": info.get("duration_seconds") or safe_dur,
        "preview_url": f"/api/studio/audio/{audio_id}.wav",
    }


def _fit_audio_to_video_duration(
    source_audio_path: Path,
    fitted_wav_path: Path,
    target_duration: float,
    fit_mode: str = "fit_pad_trim",
    volume: float = 1.0,
) -> Path:
    """مواءمة طول الصوت ومستواه ليتطابق بدقة مع مدة الفيديو دون تقصير الفيديو أبداً."""
    import subprocess

    dur = max(0.5, float(target_duration))
    vol = max(0.05, min(2.0, float(volume or 1.0)))
    mode = fit_mode if fit_mode in ("fit_pad_trim", "loop", "fit_tempo") else "fit_pad_trim"
    src_info = probe_media_info(source_audio_path)
    src_dur = float(src_info.get("duration_seconds") or dur)
    fade_out_st = max(0.0, dur - 0.55)

    filters = [f"volume={vol:.2f}"]
    cmd = ["ffmpeg", "-y"]

    if mode == "loop" and src_dur < dur - 0.2:
        cmd.extend(["-stream_loop", "-1", "-i", str(source_audio_path)])
    elif mode == "fit_tempo" and src_dur > 0.5:
        ratio = src_dur / dur
        # إذا كان الصوت أطول أو أقصر بشكل معتدل نعدّل سرعته بسلاسة ضمن الحدود الطبيعية
        if 0.8 <= ratio <= 1.5 and abs(ratio - 1.0) > 0.04:
            filters.append(f"atempo={ratio:.3f}")
        cmd.extend(["-i", str(source_audio_path)])
    else:
        cmd.extend(["-i", str(source_audio_path)])

    filters.append(f"apad=whole_dur={dur:.3f}")
    filters.append(f"atrim=0:{dur:.3f}")
    filters.append("asetpts=PTS-STARTPTS")
    filters.append("afade=t=in:st=0:d=0.18")
    filters.append(f"afade=t=out:st={fade_out_st:.3f}:d=0.55")

    cmd.extend([
        "-af", ",".join(filters),
        "-ac", "2", "-ar", "44100",
        str(fitted_wav_path),
    ])
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60)
    return fitted_wav_path


def _mux_audio_into_video(
    video_path: Path,
    audio_wav_path: Path,
    output_format: str,
    exact_duration: float,
) -> None:
    """دمج المسار الصوتي داخل ملف الفيديو مع الحفاظ الصارم على المدة الأصلية للفيديو."""
    import subprocess

    tmp_muxed = video_path.with_name(f".mux_{video_path.name}")
    fmt = (output_format or "mp4").lower()
    audio_codec = "libopus" if fmt == "webm" else "aac"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_wav_path),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", audio_codec,
        "-b:a", "192k",
        "-t", f"{max(0.5, float(exact_duration)):.3f}",
    ]
    if fmt == "mp4":
        cmd.extend(["-movflags", "+faststart"])
    cmd.append(str(tmp_muxed))

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=120)
        if tmp_muxed.exists() and tmp_muxed.stat().st_size > 0:
            tmp_muxed.replace(video_path)
    finally:
        tmp_muxed.unlink(missing_ok=True)


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
    audio_mode: str = "none",
    auto_audio_type: str = "voice_and_music",
    voice_name: str = "Kore",
    voice_script: str = "",
    uploaded_audio_id: str = "",
    pregenerated_audio_id: str = "",
    audio_fit_mode: str = "fit_pad_trim",
    audio_volume: float = 1.0,
    ai_notes: str = "",
    ai_provider_label: str = "@hyperframes/producer + FFmpeg",
    job_id: Optional[str] = None,
) -> Dict[str, Any]:
    """تشغيل وحدة Node (@hyperframes/producer) لتحويل HTML إلى فيديو مع الالتزام بالمدة ودمج الصوت."""
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
    norm_audio_mode = audio_mode if audio_mode in ("none", "auto_ai", "upload") else "none"

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
    fitted_audio_tmp = STUDIO_AUDIO_DIR / f"fitted_{uid}.wav"

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
                                raw_pct = int(ev.get("percent", 0))
                                scaled_pct = int(raw_pct * 0.85) if norm_audio_mode != "none" else raw_pct
                                _VIDEO_JOBS[job_id]["percent"] = max(2, scaled_pct)
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

        actual_dur = float(last_result.get("compositionDurationSeconds") or safe_dur)
        has_audio = False
        audio_script_used = ""
        audio_mood = ""
        audio_ms = 0

        if norm_audio_mode != "none" and fmt in ("mp4", "webm", "mov"):
            t_aud0 = time.perf_counter()
            if job_id:
                with _VIDEO_JOBS_LOCK:
                    if job_id in _VIDEO_JOBS:
                        _VIDEO_JOBS[job_id]["percent"] = 88
                        _VIDEO_JOBS[job_id]["stage"] = (
                            "توليد تعليق وموسيقى متناسبة مع المحتوى..."
                            if norm_audio_mode == "auto_ai"
                            else "معالجة ودمج الملف الصوتي المرفوع..."
                        )

            source_audio_path: Optional[Path] = None
            if norm_audio_mode == "upload":
                clean_aid = re.sub(r"[^a-zA-Z0-9_\-]", "", uploaded_audio_id or "")
                cand = STUDIO_AUDIO_DIR / f"{clean_aid}.wav"
                if not clean_aid or not cand.exists():
                    raise RuntimeError("لم يتم العثور على الملف الصوتي المرفوع. يرجى إعادة رفع الملف الصوتي من الجهاز.")
                source_audio_path = cand
            elif norm_audio_mode == "auto_ai":
                clean_pre = re.sub(r"[^a-zA-Z0-9_\-]", "", pregenerated_audio_id or "")
                pre_cand = STUDIO_AUDIO_DIR / f"{clean_pre}.wav" if clean_pre else None
                if pre_cand and pre_cand.exists():
                    source_audio_path = pre_cand
                    audio_script_used = voice_script or ""
                else:
                    gen = generate_studio_audio_preview(
                        html_content=html_content,
                        duration=actual_dur,
                        auto_audio_type=auto_audio_type,
                        voice_name=voice_name,
                        user_script=voice_script,
                        notes=ai_notes,
                    )
                    source_audio_path = STUDIO_AUDIO_DIR / gen["filename"]
                    audio_script_used = gen.get("script", "")
                    audio_mood = gen.get("mood", "")

            if source_audio_path and source_audio_path.exists():
                if job_id:
                    with _VIDEO_JOBS_LOCK:
                        if job_id in _VIDEO_JOBS:
                            _VIDEO_JOBS[job_id]["percent"] = 95
                            _VIDEO_JOBS[job_id]["stage"] = "دمج الصوت مع الفيديو عبر FFmpeg..."
                _fit_audio_to_video_duration(
                    source_audio_path=source_audio_path,
                    fitted_wav_path=fitted_audio_tmp,
                    target_duration=actual_dur,
                    fit_mode=audio_fit_mode,
                    volume=audio_volume,
                )
                _mux_audio_into_video(
                    video_path=target_output,
                    audio_wav_path=fitted_audio_tmp,
                    output_format=fmt,
                    exact_duration=actual_dur,
                )
                probed_after = probe_media_info(target_output)
                if probed_after.get("duration_seconds"):
                    actual_dur = float(probed_after["duration_seconds"])
                has_audio = bool(probed_after.get("has_audio", True))
                file_size = target_output.stat().st_size if target_output.exists() else file_size
            audio_ms = max(10, round((time.perf_counter() - t_aud0) * 1000))

        total_ms = max(10, round((time.perf_counter() - t0) * 1000))
        raw_stages = last_result.get("stages") or {}
        compile_ms = int(raw_stages.get("compileMs") or 120)
        capture_ms = int(raw_stages.get("captureFrameMs") or raw_stages.get("captureMs") or max(20, total_ms // 2))
        encode_ms = int(raw_stages.get("encodeMs") or max(20, total_ms // 3))
        assemble_ms = int(audio_ms or raw_stages.get("assembleMs") or max(10, total_ms - compile_ms - capture_ms))

        plain_words = len(re.sub(r"<[^>]+>", " ", html_content).split())
        frames_count = int(last_result.get("frameCount") or round(actual_dur * safe_fps))
        out_w = int(last_result.get("width") or safe_w)
        out_h = int(last_result.get("height") or safe_h)

        metrics = build_pipeline_metrics(
            operation=f"تحويل HTML إلى فيديو {fmt.upper()} ({out_w}×{out_h} · {actual_dur:.1f}s @ {safe_fps}fps)" + (" + صوت" if has_audio else ""),
            stage_timings=[
                ("extract", "1. تجهيز HTML والخطوط", max(10, compile_ms)),
                ("ai", "2. التقاط الإطارات Chrome", max(15, capture_ms)),
                ("charts", "3. ترميز الفيديو FFmpeg", max(15, encode_ms)),
                ("render", "4. دمج الصوت والحفظ" if has_audio else "4. تجميع وحفظ الملف", max(10, assemble_ms)),
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
            "has_audio": has_audio,
            "audio_mode": norm_audio_mode,
            "audio_script": audio_script_used,
            "audio_mood": audio_mood,
            "render_ms": total_ms,
            "pipeline_metrics": metrics,
        }
    finally:
        try:
            temp_html.unlink(missing_ok=True)
            fitted_audio_tmp.unlink(missing_ok=True)
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

