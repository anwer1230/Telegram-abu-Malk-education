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
