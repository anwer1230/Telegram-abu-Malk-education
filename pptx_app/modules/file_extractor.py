# -*- coding: utf-8 -*-
"""استخراج المحتوى من ملفات Word و PDF و PowerPoint (.pptx) والنصوص."""

import io
import os
import re
import zipfile
from pathlib import Path
from typing import Dict, Any, List


def extract_from_word(file_bytes: bytes) -> Dict[str, Any]:
    import docx

    doc = docx.Document(io.BytesIO(file_bytes))
    result: Dict[str, Any] = {
        "text_blocks": [],
        "tables": [],
        "images": [],
        "full_text": "",
    }
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style = para.style.name if para.style else ""
        result["text_blocks"].append({"type": "paragraph", "style": style, "text": text})
        result["full_text"] += text + "\n"

    for table in doc.tables:
        rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
        if rows:
            result["tables"].append(rows)

    return result


def extract_from_pdf(file_bytes: bytes) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "text_blocks": [],
        "tables": [],
        "images": [],
        "full_text": "",
    }
    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                if text.strip():
                    result["text_blocks"].append(
                        {"type": "page", "style": f"صفحة {page_num}", "text": text.strip()}
                    )
                    result["full_text"] += text.strip() + "\n"
                for tbl in page.extract_tables() or []:
                    if tbl:
                        cleaned = [[cell or "" for cell in row] for row in tbl]
                        result["tables"].append(cleaned)
    except Exception as e:
        result["full_text"] = f"خطأ في قراءة PDF: {str(e)}"
    return result


def extract_from_pptx(file_bytes: bytes) -> Dict[str, Any]:
    """استخراج تفصيلي لشرائح ملف PowerPoint (.pptx): العناوين، النقاط، الجداول، الملاحظات، الخطوط والألوان."""
    from pptx import Presentation

    prs = Presentation(io.BytesIO(file_bytes))
    slides_info: List[Dict[str, Any]] = []
    all_tables: List[List[List[str]]] = []
    fonts_used = set()
    colors_used = set()
    images_count = 0
    full_text_parts: List[str] = []

    for idx, slide in enumerate(prs.slides, start=1):
        title_text = ""
        bullets: List[str] = []
        slide_tables: List[List[List[str]]] = []
        slide_images = 0

        try:
            if slide.shapes.title and hasattr(slide.shapes.title, "text"):
                title_text = (slide.shapes.title.text or "").strip()
        except Exception:
            pass

        for shape in slide.shapes:
            if shape.shape_type == 13:  # PICTURE
                slide_images += 1
                images_count += 1
            if getattr(shape, "has_table", False):
                rows = []
                for row in shape.table.rows:
                    rows.append([cell.text.strip() for cell in row.cells])
                if rows:
                    slide_tables.append(rows)
                    all_tables.append(rows)
            if getattr(shape, "has_text_frame", False):
                is_title_shape = False
                try:
                    is_title_shape = (slide.shapes.title is not None and shape.shape_id == slide.shapes.title.shape_id)
                except Exception:
                    pass
                for p in shape.text_frame.paragraphs:
                    txt = (p.text or "").strip()
                    if not txt:
                        continue
                    for r in p.runs:
                        if r.font and r.font.name:
                            fonts_used.add(r.font.name)
                        try:
                            if r.font and r.font.color and r.font.color.rgb:
                                colors_used.add(f"#{str(r.font.color.rgb)}")
                        except Exception:
                            pass
                    if not title_text and not is_title_shape:
                        title_text = txt
                    elif txt != title_text:
                        bullets.append(txt)

        notes_text = ""
        try:
            if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
                notes_text = (slide.notes_slide.notes_text_frame.text or "").strip()
        except Exception:
            pass

        if not title_text:
            title_text = f"شريحة {idx}"

        stype = "title" if idx == 1 else ("table" if slide_tables else ("conclusion" if idx == len(prs.slides) and len(prs.slides) > 2 else "bullets"))
        slide_obj: Dict[str, Any] = {
            "slide_number": idx,
            "title": title_text,
            "subtitle": bullets[0] if (stype == "title" and bullets) else "",
            "bullets": bullets if stype != "title" else bullets[1:],
            "slide_type": stype,
            "notes": notes_text,
            "image_count": slide_images,
        }
        if slide_tables:
            slide_obj["table_data"] = slide_tables[0]

        slides_info.append(slide_obj)
        chunk = [f"--- شريحة {idx}: {title_text} ---"] + bullets
        if notes_text:
            chunk.append(f"[ملاحظات]: {notes_text}")
        full_text_parts.append("\n".join(chunk))

    full_text = "\n\n".join(full_text_parts)
    return {
        "text_blocks": [{"type": "slide", "style": f"شريحة {s['slide_number']}", "text": s["title"] + "\n" + "\n".join(s["bullets"])} for s in slides_info],
        "tables": all_tables,
        "images": [],
        "slides": slides_info,
        "slide_count": len(slides_info),
        "images_count": images_count,
        "fonts_used": sorted(list(fonts_used))[:10],
        "colors_used": sorted(list(colors_used))[:10],
        "full_text": full_text,
    }


def extract_content(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """دالة موحدة لاستخراج المحتوى من Word / PDF / PPTX / Text."""
    ext = Path(filename).suffix.lower()
    if ext in (".docx", ".doc"):
        return extract_from_word(file_bytes)
    elif ext == ".pdf":
        return extract_from_pdf(file_bytes)
    elif ext == ".pptx":
        return extract_from_pptx(file_bytes)
    else:
        text = file_bytes.decode("utf-8", errors="ignore")
        return {
            "text_blocks": [{"type": "paragraph", "style": "Normal", "text": text}],
            "tables": [],
            "images": [],
            "full_text": text,
        }
