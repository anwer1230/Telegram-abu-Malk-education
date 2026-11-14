# -*- coding: utf-8 -*-
"""مولّد العروض التقديمية — يدعم قوالب كانفا، النصوص العربية RTL، الجداول، الرسوم البيانية، والصور."""

import base64
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import requests
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt, Emu
from lxml import etree

from pptx_app.modules.templates import ProfessionalTemplates

OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def _rgb(t: Tuple[int, int, int]) -> RGBColor:
    return RGBColor(int(t[0]), int(t[1]), int(t[2]))


def _set_rtl(paragraph) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    pPr.set("rtl", "1")


def _set_run_font(run, font_name: str) -> None:
    run.font.name = font_name
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:cs", "a:ea"):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", font_name)


def _add_text_box(
    slide,
    left: float,
    top: float,
    width: float,
    height: float,
    text: str,
    size: int,
    bold: bool = False,
    color: Tuple[int, int, int] = (0, 0, 0),
    align=PP_ALIGN.RIGHT,
    wrap: bool = True,
    font_name: str = "Traditional Arabic",
):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    _set_rtl(p)
    run = p.add_run()
    run.text = str(text or "")
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = _rgb(color)
    _set_run_font(run, font_name)
    return box


class PresentationGenerator:
    def __init__(self):
        self.templates = ProfessionalTemplates()
        self.font_name = "Traditional Arabic"
        self.body_font_size = 22

    def _parse_color(self, color_str: str):
        if not color_str:
            return None
        s = str(color_str).strip().lower()
        if s.startswith("#"):
            c = s.lstrip("#")
            if len(c) == 3:
                c = c[0] * 2 + c[1] * 2 + c[2] * 2
            if len(c) >= 6:
                try:
                    return RGBColor(int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
                except Exception:
                    return None
        if s.startswith("rgb"):
            nums = re.findall(r"[\d.]+", s)
            if len(nums) >= 3:
                r, g, b = int(float(nums[0])), int(float(nums[1])), int(float(nums[2]))
                return RGBColor(min(r, 255), min(g, 255), min(b, 255))
        return None

    def _fetch_image(self, src: str) -> Optional[bytes]:
        if not src:
            return None
        if src.startswith("data:image"):
            try:
                _, data = src.split(",", 1)
                return base64.b64decode(data)
            except Exception:
                return None
        if src.startswith("http"):
            try:
                resp = requests.get(src, timeout=5)
                if resp.ok:
                    return resp.content
            except Exception:
                pass
        return None

    def _save_temp_image(self, src: str) -> Optional[str]:
        data = self._fetch_image(src)
        if not data:
            return None
        ext = "png" if "png" in src.lower() else "jpg"
        fd, path = tempfile.mkstemp(suffix=f".{ext}")
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        return path

    def create_presentation(
        self,
        slides_data: List[Dict[str, Any]],
        theme_color: str = "blue",
        cover_data: Optional[Dict[str, str]] = None,
        extracted_images: Optional[List[str]] = None,
        font_name: str = "Traditional Arabic",
        body_font_size: int = 22,
        ai_images: bool = False,
        groq_client=None,
        custom_theme: Optional[Dict[str, Any]] = None,
        filename_prefix: str = "عرض",
    ) -> str:
        theme = self.templates.get_theme(theme_color, custom_theme=custom_theme)
        self.font_name = font_name or theme.get("font_name", "Traditional Arabic")
        self.body_font_size = int(body_font_size or 22)

        prs = Presentation()
        prs.slide_width = Inches(13.33)
        prs.slide_height = Inches(7.5)

        if cover_data:
            self._add_cover_slide(prs, cover_data, theme)

        for i, slide_data in enumerate(slides_data):
            stype = slide_data.get("slide_type", "bullets")
            if stype == "title":
                self._add_title_slide(prs, slide_data, theme)
            elif stype == "table" and slide_data.get("table_data"):
                self._add_table_slide(prs, slide_data, theme)
            elif stype == "chart":
                self._add_chart_slide(prs, slide_data, theme)
            elif stype == "conclusion":
                self._add_conclusion_slide(prs, slide_data, theme)
            else:
                img_path = None
                tmp_created = False
                if slide_data.get("images"):
                    img_path = self._save_temp_image(slide_data["images"][0])
                    tmp_created = bool(img_path)
                if not img_path and extracted_images and i < len(extracted_images):
                    img_path = extracted_images[i]
                if not img_path and ai_images:
                    try:
                        from pptx_app.modules.image_fetcher import get_slide_image
                        img_path = get_slide_image(
                            slide_title=slide_data.get("title", ""),
                            slide_bullets=slide_data.get("bullets", []),
                            slide_type=stype,
                            groq_client=groq_client,
                        )
                    except Exception:
                        img_path = None
                self._add_content_slide(prs, slide_data, theme, i, img_path)
                if tmp_created and img_path:
                    try:
                        os.unlink(img_path)
                    except Exception:
                        pass

        safe_prefix = re.sub(r"[^\w\u0600-\u06FF\-]", "_", filename_prefix or "عرض").strip("_") or "عرض"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
        output_path = str(OUTPUTS_DIR / f"{safe_prefix}_{timestamp}.pptx")
        prs.save(output_path)
        return output_path

    def _add_cover_slide(self, prs, cover_data, theme):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = _rgb(theme["primary"])

        rect = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.33), Inches(2.2))
        rect.fill.solid()
        rect.fill.fore_color.rgb = _rgb(theme["secondary"])
        rect.line.fill.background()

        # شريط لهجة كانفا جانبي أنيق
        accent_bar = slide.shapes.add_shape(1, Inches(0), Inches(2.2), Inches(13.33), Emu(45000))
        accent_bar.fill.solid()
        accent_bar.fill.fore_color.rgb = _rgb(theme["accent"])
        accent_bar.line.fill.background()

        logo_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(2), Inches(1.5))
        lp = logo_box.text_frame.paragraphs[0]
        lp.alignment = PP_ALIGN.CENTER
        lr = lp.add_run()
        lr.text = cover_data.get("logo", "📊") or "📊"
        lr.font.size = Pt(52)

        org = cover_data.get("organization", "")
        if org:
            _add_text_box(
                slide, 2.8, 0.55, 10.0, 1.0, org, 20, bold=True,
                color=theme["text_light"], align=PP_ALIGN.RIGHT, font_name=self.font_name,
            )

        fn = self.font_name
        _add_text_box(
            slide, 1.0, 2.6, 11.3, 1.8,
            cover_data.get("title", "العنوان الرئيسي"),
            42, bold=True, color=theme["text_light"],
            align=PP_ALIGN.CENTER, font_name=fn,
        )
        subtitle = cover_data.get("subtitle", "")
        if subtitle:
            _add_text_box(
                slide, 1.5, 4.4, 10.3, 0.9,
                subtitle, 22, color=(230, 236, 250),
                align=PP_ALIGN.CENTER, font_name=fn,
            )

        line = slide.shapes.add_shape(1, Inches(3.5), Inches(5.5), Inches(6.3), Emu(35000))
        line.fill.solid()
        line.fill.fore_color.rgb = _rgb(theme["accent"])
        line.line.fill.background()

        meta_parts = []
        if cover_data.get("presenter"):
            meta_parts.append(f"إعداد: {cover_data['presenter']}")
        if cover_data.get("date"):
            meta_parts.append(cover_data["date"])
        if meta_parts:
            _add_text_box(
                slide, 1.0, 5.9, 11.3, 0.7,
                "  |  ".join(meta_parts), 16,
                color=(220, 226, 240), align=PP_ALIGN.CENTER, font_name=fn,
            )
        note = cover_data.get("note", "")
        if note:
            _add_text_box(
                slide, 1.5, 6.6, 10.3, 0.7,
                note, 14, color=(205, 214, 235),
                align=PP_ALIGN.CENTER, font_name=fn,
            )

    def _add_title_slide(self, prs, data, theme):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = _rgb(theme["primary"])
        self._add_bottom_strip(slide, theme)

        # زخرفة هندسية مستوحاة من قوالب كانفا
        deco = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.28), Inches(6.8))
        deco.fill.solid()
        deco.fill.fore_color.rgb = _rgb(theme["accent"])
        deco.line.fill.background()

        fn = self.font_name
        _add_text_box(
            slide, 1.0, 2.0, 11.3, 1.8,
            data.get("title", "العنوان"),
            44, bold=True, color=theme["text_light"],
            align=PP_ALIGN.CENTER, font_name=fn,
        )
        line = slide.shapes.add_shape(1, Inches(4.5), Inches(4.0), Inches(4.3), Emu(40000))
        line.fill.solid()
        line.fill.fore_color.rgb = _rgb(theme["accent"])
        line.line.fill.background()

        subtitle = data.get("subtitle", "")
        if subtitle:
            _add_text_box(
                slide, 2.0, 4.3, 9.3, 1.1,
                subtitle, 24, color=(232, 238, 252),
                align=PP_ALIGN.CENTER, font_name=fn,
            )

    def _add_content_slide(self, prs, data, theme, index, img_path=None):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg_color = data.get("bg_color")
        rgb = self._parse_color(bg_color) if bg_color else None
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = rgb if rgb else _rgb(theme["bg"])

        layout_style = theme.get("layout", "header_banner")
        card_bg = theme.get("card_bg", (255, 255, 255))

        if layout_style == "split_accent":
            header = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.33), Inches(1.25))
            header.fill.solid()
            header.fill.fore_color.rgb = _rgb(theme["primary"])
            header.line.fill.background()
            strip = slide.shapes.add_shape(1, Inches(13.08), Inches(1.25), Inches(0.25), Inches(6.25))
            strip.fill.solid()
            strip.fill.fore_color.rgb = _rgb(theme["accent"])
            strip.line.fill.background()
            _add_text_box(
                slide, 0.5, 0.14, 12.1, 0.98, data.get("title", ""),
                27, bold=True, color=theme["text_light"],
                align=PP_ALIGN.RIGHT, font_name=self.font_name,
            )
        elif layout_style in ("modern_card", "dark_pitch"):
            header = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.33), Inches(1.25))
            header.fill.solid()
            header.fill.fore_color.rgb = _rgb(theme["secondary"])
            header.line.fill.background()
            underline = slide.shapes.add_shape(1, Inches(0), Inches(1.25), Inches(13.33), Emu(38000))
            underline.fill.solid()
            underline.fill.fore_color.rgb = _rgb(theme["accent"])
            underline.line.fill.background()
            # بطاقة خلفية للمحتوى بأسلوب كانفا
            card = slide.shapes.add_shape(5, Inches(0.45), Inches(1.55), Inches(12.43), Inches(5.35))
            card.fill.solid()
            card.fill.fore_color.rgb = _rgb(card_bg)
            card.line.color.rgb = _rgb(theme["accent"])
            card.line.width = Pt(1)
            _add_text_box(
                slide, 0.5, 0.14, 12.1, 0.98, data.get("title", ""),
                27, bold=True, color=theme["text_light"],
                align=PP_ALIGN.RIGHT, font_name=self.font_name,
            )
        else:
            header = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.33), Inches(1.32))
            header.fill.solid()
            header.fill.fore_color.rgb = _rgb(theme["primary"])
            header.line.fill.background()
            _add_text_box(
                slide, 0.4, 0.15, 12.2, 1.02, data.get("title", ""),
                27, bold=True, color=theme["text_light"],
                align=PP_ALIGN.RIGHT, font_name=self.font_name,
            )

        bullets = data.get("bullets", [])
        has_image = bool(img_path and Path(img_path).exists())
        if has_image:
            content_box = slide.shapes.add_textbox(Inches(4.85), Inches(1.72), Inches(7.75), Inches(5.0))
            self._fill_bullets(content_box.text_frame, bullets, theme)
            try:
                frame = slide.shapes.add_shape(1, Inches(0.55), Inches(1.75), Inches(4.08), Inches(4.9))
                frame.fill.solid()
                frame.fill.fore_color.rgb = _rgb(theme["accent"])
                frame.line.fill.background()
                slide.shapes.add_picture(img_path, Inches(0.62), Inches(1.82), Inches(3.94), Inches(4.76))
            except Exception:
                content_box2 = slide.shapes.add_textbox(Inches(0.65), Inches(1.72), Inches(12.0), Inches(5.0))
                self._fill_bullets(content_box2.text_frame, bullets, theme)
        else:
            content_box = slide.shapes.add_textbox(Inches(0.65), Inches(1.72), Inches(12.0), Inches(5.0))
            self._fill_bullets(content_box.text_frame, bullets, theme)

        # رقم الشريحة
        num_box = slide.shapes.add_textbox(Inches(12.45), Inches(6.95), Inches(0.75), Inches(0.45))
        np_ = num_box.text_frame.paragraphs[0]
        np_.alignment = PP_ALIGN.CENTER
        nr = np_.add_run()
        nr.text = str(index + 1)
        nr.font.size = Pt(11)
        nr.font.color.rgb = _rgb(theme["accent"] if layout_style == "dark_pitch" else theme["secondary"])

    def _fill_bullets(self, tf, bullets, theme):
        tf.word_wrap = True
        fs = self.body_font_size
        fn = self.font_name
        for i, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.RIGHT
            _set_rtl(p)
            p.space_before = Pt(10)
            p.space_after = Pt(4)
            run = p.add_run()
            run.text = f"◆ {bullet}"
            run.font.size = Pt(fs)
            run.font.color.rgb = _rgb(theme["text_dark"])
            _set_run_font(run, fn)

    def _add_table_slide(self, prs, data, theme):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = _rgb(theme["bg"])
        header = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.33), Inches(1.3))
        header.fill.solid()
        header.fill.fore_color.rgb = _rgb(theme["primary"])
        header.line.fill.background()
        _add_text_box(
            slide, 0.4, 0.15, 12.2, 1.0,
            data.get("title", "جدول البيانات"), 27, bold=True,
            color=theme["text_light"], align=PP_ALIGN.RIGHT, font_name=self.font_name,
        )

        table_data = data.get("table_data", [])
        if not table_data:
            return
        rows = len(table_data)
        cols = max(len(r) for r in table_data)
        if rows == 0 or cols == 0:
            return
        table = slide.shapes.add_table(
            rows, cols, Inches(0.5), Inches(1.6), Inches(12.3), Inches(min(5.5, 0.5 + rows * 0.55))
        ).table
        fn = self.font_name
        for r_idx, row in enumerate(table_data):
            for c_idx in range(cols):
                cell_data = row[c_idx] if c_idx < len(row) else ""
                if isinstance(cell_data, dict):
                    text = str(cell_data.get("text", ""))
                    bg_color = cell_data.get("bg")
                    align_val = cell_data.get("align", "center")
                    bold = cell_data.get("bold", False)
                else:
                    text = str(cell_data)
                    bg_color = None
                    align_val = "center"
                    bold = (r_idx == 0)
                cell = table.cell(r_idx, c_idx)
                cell.text = text
                tf = cell.text_frame
                par = tf.paragraphs[0]
                par.alignment = getattr(PP_ALIGN, str(align_val).upper(), PP_ALIGN.CENTER)
                _set_rtl(par)
                runs = par.runs
                if runs:
                    runs[0].font.size = Pt(15)
                    runs[0].font.bold = bold or (r_idx == 0)
                    runs[0].font.color.rgb = _rgb(
                        theme["text_light"] if r_idx == 0 else (15, 23, 42)
                    )
                    _set_run_font(runs[0], fn)
                parsed_bg = self._parse_color(bg_color) if bg_color else None
                if parsed_bg:
                    self._set_cell_bg(cell, (parsed_bg[0], parsed_bg[1], parsed_bg[2]))
                elif r_idx == 0:
                    self._set_cell_bg(cell, theme["primary"])
                elif r_idx % 2 == 0:
                    self._set_cell_bg(cell, (238, 242, 255))
                else:
                    self._set_cell_bg(cell, (255, 255, 255))

    def _set_cell_bg(self, cell, color_tuple: Tuple[int, int, int]):
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        sf = etree.SubElement(tcPr, qn("a:solidFill"))
        sc = etree.SubElement(sf, qn("a:srgbClr"))
        sc.set("val", "{:02X}{:02X}{:02X}".format(*color_tuple))

    def _add_chart_slide(self, prs, data, theme):
        from pptx_app.modules.chart_generator import create_chart_from_data
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = _rgb(theme["bg"])
        header = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.33), Inches(1.3))
        header.fill.solid()
        header.fill.fore_color.rgb = _rgb(theme["primary"])
        header.line.fill.background()
        _add_text_box(
            slide, 0.4, 0.15, 12.2, 1.0,
            data.get("title", "رسم بياني"), 27, bold=True,
            color=theme["text_light"], align=PP_ALIGN.RIGHT, font_name=self.font_name,
        )
        chart_type = data.get("chart_type", "bar")
        labels = data.get("chart_labels", [])
        values = data.get("chart_values", [])
        chart_title = data.get("chart_title", "")
        if not labels or not values:
            _add_text_box(
                slide, 1, 3, 11, 2, "لا توجد بيانات كافية للرسم البياني",
                20, color=theme["text_dark"], font_name=self.font_name,
            )
            return
        try:
            values_float = [float(v) for v in values]
        except Exception:
            values_float = [1.0] * len(labels)
        primary_hex = "#{:02x}{:02x}{:02x}".format(*theme["primary"])
        img_path = create_chart_from_data(chart_type, labels, values_float, chart_title, primary_hex)
        if img_path and Path(img_path).exists():
            slide.shapes.add_picture(img_path, Inches(1.5), Inches(1.6), Inches(10.3), Inches(5.6))
            try:
                os.unlink(img_path)
            except Exception:
                pass
        else:
            _add_text_box(
                slide, 1, 3, 11, 2, "تعذّر إنشاء الرسم البياني",
                20, color=theme["text_dark"], font_name=self.font_name,
            )

    def _add_conclusion_slide(self, prs, data, theme):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = _rgb(theme["secondary"])
        fn = self.font_name
        _add_text_box(
            slide, 1.0, 1.4, 11.3, 1.2,
            data.get("title", "الخلاصة والتوصيات"), 36, bold=True,
            color=theme["text_light"], align=PP_ALIGN.CENTER, font_name=fn,
        )
        line = slide.shapes.add_shape(1, Inches(3.5), Inches(2.8), Inches(6.3), Emu(35000))
        line.fill.solid()
        line.fill.fore_color.rgb = _rgb(theme["accent"])
        line.line.fill.background()

        bullets = data.get("bullets", [])
        cont_box = slide.shapes.add_textbox(Inches(1.5), Inches(3.2), Inches(10.3), Inches(3.8))
        tf = cont_box.text_frame
        tf.word_wrap = True
        for i, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.RIGHT
            _set_rtl(p)
            p.space_before = Pt(12)
            run = p.add_run()
            run.text = str(bullet)
            run.font.size = Pt(self.body_font_size)
            run.font.color.rgb = RGBColor(235, 240, 255)
            _set_run_font(run, fn)

    def _add_bottom_strip(self, slide, theme):
        rect = slide.shapes.add_shape(1, Inches(0), Inches(6.8), Inches(13.33), Inches(0.7))
        rect.fill.solid()
        rect.fill.fore_color.rgb = _rgb(theme["secondary"])
        rect.line.fill.background()
