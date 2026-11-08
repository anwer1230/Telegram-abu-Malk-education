# -*- coding: utf-8 -*-
"""
HTML to Word Studio Engine (محرك تحويل HTML إلى مستندات Word الاحترافية)
دعم فائق الدقة للتصميمات، الألوان، الجداول، الصور، واتجاه RTL بالذكاء الاصطناعي
"""

import os
import re
import io
import base64
import logging
import requests
from typing import Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup, Tag, NavigableString
from PIL import Image

import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

logger = logging.getLogger("html_word_engine")
logger.setLevel(logging.INFO)

# الألوان المسماة الشائعة في CSS
CSS_NAMED_COLORS: Dict[str, Tuple[int, int, int]] = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (220, 53, 69),
    'green': (40, 167, 69),
    'blue': (0, 123, 255),
    'yellow': (255, 193, 7),
    'orange': (253, 126, 20),
    'purple': (111, 66, 193),
    'teal': (32, 201, 151),
    'cyan': (23, 162, 184),
    'gray': (108, 117, 125),
    'grey': (108, 117, 125),
    'lightgray': (211, 211, 211),
    'lightgrey': (211, 211, 211),
    'darkgray': (169, 169, 169),
    'darkgrey': (169, 169, 169),
    'navy': (0, 31, 63),
    'darkblue': (0, 0, 139),
    'indigo': (75, 0, 130),
    'maroon': (128, 0, 0),
    'gold': (255, 215, 0),
    'silver': (192, 192, 192),
    'emerald': (16, 185, 129),
    'slate': (100, 116, 139),
    'rose': (244, 63, 94),
    'sky': (14, 165, 233),
    'amber': (245, 158, 11),
    'crimson': (220, 20, 60),
    'royalblue': (65, 105, 225)
}

def parse_css_color(color_val: Optional[str]) -> Optional[Tuple[int, int, int]]:
    """تحويل لون CSS (hex, rgb, rgba, named) إلى tuple (r, g, b)"""
    if not color_val:
        return None
    s = color_val.strip().lower()
    if s in ('transparent', 'inherit', 'initial', 'currentcolor', 'none', ''):
        return None
    
    # Hex
    if s.startswith('#'):
        c = s.lstrip('#')
        if len(c) == 3:
            c = ''.join([ch * 2 for ch in c])
        if len(c) >= 6:
            try:
                return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
            except ValueError:
                return None
    
    # RGB / RGBA
    if s.startswith('rgb'):
        nums = re.findall(r'[\d.]+', s)
        if len(nums) >= 3:
            try:
                r = int(float(nums[0]))
                g = int(float(nums[1]))
                b = int(float(nums[2]))
                return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            except Exception:
                return None
    
    # Named colors
    if s in CSS_NAMED_COLORS:
        return CSS_NAMED_COLORS[s]
    
    return None

def color_to_hex(color_tuple: Optional[Tuple[int, int, int]]) -> Optional[str]:
    """تحويل tuple (r, g, b) إلى hex string من 6 أحرف مثل '007BFF'"""
    if not color_tuple:
        return None
    return f"{color_tuple[0]:02X}{color_tuple[1]:02X}{color_tuple[2]:02X}"

def parse_style_attr(style_str: Optional[str]) -> Dict[str, str]:
    """تحليل style attribute إلى قاموس مفاتيح وقيم"""
    res = {}
    if not style_str:
        return res
    for item in style_str.split(';'):
        item = item.strip()
        if ':' in item:
            k, v = item.split(':', 1)
            res[k.strip().lower()] = v.strip()
    return res

def inline_css_rules(html_content: str) -> str:
    """
    دمج قواعد CSS الموجودة داخل وسوم <style> وتحويلها إلى أنماط مضمنة style="..."
    على العناصر المطابقة لضمان عدم ضياع التنسيقات عند التصدير لملف Word.
    """
    if not html_content or '<style' not in html_content:
        return html_content

    soup = BeautifulSoup(html_content, 'html.parser')
    style_tags = soup.find_all('style')

    for st in style_tags:
        css_text = st.string or ''
        # إزالة التعليقات
        css_text = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)
        # استخراج القواعد: selector { properties }
        rules = re.findall(r'([^{]+)\{([^}]+)\}', css_text)
        for selector_group, props in rules:
            selectors = [s.strip() for s in selector_group.split(',') if s.strip()]
            props_clean = props.strip().rstrip(';')
            for sel in selectors:
                # تجنب المحددات غير المدعومة مثل :hover, @media, ::after
                if any(pseudo in sel for pseudo in (':hover', ':active', ':focus', '::before', '::after', '@')):
                    continue
                try:
                    matched_elements = soup.select(sel)
                    for el in matched_elements:
                        existing_style = el.get('style', '')
                        if existing_style:
                            # دمج الأنماط مع إعطاء الأولوية للنمط المضمن الأصلي
                            merged = f"{props_clean}; {existing_style}"
                        else:
                            merged = props_clean
                        el['style'] = merged
                except Exception:
                    continue
        st.decompose()

    return str(soup)

def is_arabic_text(text: str) -> bool:
    """فحص ما إذا كان النص يحتوي على حروف عربية"""
    if not text:
        return False
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    return bool(arabic_pattern.search(text))

def apply_paragraph_rtl(paragraph, force_rtl: bool = True):
    """تطبيق اتجاه اليمين لليسار RTL وعلامة bidi على الفقرة"""
    try:
        pPr = paragraph._element.get_or_add_pPr()
        bidi = parse_xml(f'<w:bidi {nsdecls("w")}/>')
        pPr.append(bidi)
        if force_rtl and paragraph.alignment == WD_ALIGN_PARAGRAPH.LEFT:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    except Exception as e:
        logger.debug(f"apply_paragraph_rtl error: {e}")

def apply_paragraph_shading(paragraph, hex_color: str):
    """تلوين خلفية الفقرة كاملة بلون محدد"""
    try:
        pPr = paragraph._element.get_or_add_pPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{hex_color}"/>')
        pPr.append(shd)
    except Exception as e:
        logger.debug(f"apply_paragraph_shading error: {e}")

def apply_cell_shading(cell, hex_color: str):
    """تلوين خلفية خلية الجدول"""
    try:
        tcPr = cell._tc.get_or_add_tcPr()
        # حذف أي تظليل سابق
        for shd in tcPr.findall(qn('w:shd')):
            tcPr.remove(shd)
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{hex_color}"/>')
        tcPr.append(shd)
    except Exception as e:
        logger.debug(f"apply_cell_shading error: {e}")

def apply_cell_borders(cell, border_color: str = "CBD5E1", border_size: int = 4):
    """تطبيق حدود متناسقة على الخلية"""
    try:
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="{border_size}" w:space="0" w:color="{border_color}"/>'
            f'<w:bottom w:val="single" w:sz="{border_size}" w:space="0" w:color="{border_color}"/>'
            f'<w:left w:val="single" w:sz="{border_size}" w:space="0" w:color="{border_color}"/>'
            f'<w:right w:val="single" w:sz="{border_size}" w:space="0" w:color="{border_color}"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)
    except Exception as e:
        logger.debug(f"apply_cell_borders error: {e}")

def apply_cell_margins(cell, top: int = 120, bottom: int = 120, left: int = 160, right: int = 160):
    """تحديد هوامش داخلية للخلية لتبدو مرتبة ومريحة للقراءة"""
    try:
        tcPr = cell._tc.get_or_add_tcPr()
        mar = parse_xml(
            f'<w:tcMar {nsdecls("w")}>'
            f'<w:top w:w="{top}" w:type="dxa"/>'
            f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
            f'<w:left w:w="{left}" w:type="dxa"/>'
            f'<w:right w:w="{right}" w:type="dxa"/>'
            f'</w:tcMar>'
        )
        tcPr.append(mar)
    except Exception as e:
        logger.debug(f"apply_cell_margins error: {e}")

def embed_image_to_doc(doc, src: str, width_in: float = 5.5, caption: str = ""):
    """
    تحميل وتضمين صورة في المستند:
    - يدعم data URIs (base64)
    - يدعم روابط الإنترنت المباشرة HTTP/HTTPS
    - يدعم المسارات المحلية
    - يعالج الصيغ المختلفة (PNG, JPEG, WebP, GIF) عبر Pillow
    """
    try:
        img_bytes = None
        if src.startswith('data:image/'):
            # Base64 data URI
            header, data_str = src.split(',', 1)
            img_bytes = base64.b64decode(data_str)
        elif src.startswith(('http://', 'https://')):
            # Remote image download
            resp = requests.get(src, timeout=8, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            if resp.status_code == 200:
                img_bytes = resp.content
        elif os.path.exists(src):
            with open(src, 'rb') as f:
                img_bytes = f.read()

        if not img_bytes:
            return False

        # معالجة وتحويل الصورة لـ PNG/JPEG متوافق مع Word
        pil_img = Image.open(io.BytesIO(img_bytes))
        orig_w, orig_h = pil_img.size

        # التحويل لصيغة قياسية تدعم Word دائماً
        buf = io.BytesIO()
        if pil_img.mode in ('RGBA', 'LA') or (pil_img.mode == 'P' and 'transparency' in pil_img.info):
            pil_img.convert('RGBA').save(buf, format='PNG')
        else:
            pil_img.convert('RGB').save(buf, format='JPEG', quality=95)
        buf.seek(0)

        # حساب العرض المناسب مع الحفاظ على التناسب
        max_width = 6.2
        calc_width = min(width_in, max_width)
        
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run()
        run.add_picture(buf, width=Inches(calc_width))
        
        if caption:
            cap_para = doc.add_paragraph()
            cap_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap_run = cap_para.add_run(f"شكل: {caption}")
            cap_run.italic = True
            cap_run.font.size = Pt(9.5)
            cap_run.font.color.rgb = RGBColor(100, 116, 139)

        return True

    except Exception as e:
        logger.warning(f"Error embedding image ({src[:50]}): {e}")
        # وضع إشارة نصية بديلة أنيقة بدلاً من تعطل المستند
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(f"🖼️ [صورة: {caption or 'صورة مضمنة'}]")
        r.italic = True
        r.font.color.rgb = RGBColor(148, 163, 184)
        return False

def render_node(node, doc, default_font: str = "Cairo", default_size: float = 12.0, parent_para=None):
    """معالجة عنصر HTML متكرراً وإضافته لمستند Word"""
    if isinstance(node, NavigableString):
        txt = str(node)
        if not txt:
            return
        if parent_para:
            run = parent_para.add_run(txt)
            run.font.name = default_font
            run.font.size = Pt(default_size)
        elif txt.strip():
            p = doc.add_paragraph()
            if is_arabic_text(txt):
                apply_paragraph_rtl(p, True)
            run = p.add_run(txt)
            run.font.name = default_font
            run.font.size = Pt(default_size)
        return

    if not isinstance(node, Tag):
        return

    tag = (node.name or '').lower()
    style = parse_style_attr(node.get('style', ''))

    # إهمال العناصر المخفية
    if tag in ('script', 'style', 'noscript', 'meta', 'link', 'head'):
        return

    # فواصل الصفحات
    if style.get('page-break-after') == 'always' or style.get('page-break-before') == 'always' or 'page-break' in node.get('class', []):
        doc.add_page_break()

    # خط أفقي
    if tag == 'hr':
        p = doc.add_paragraph()
        p_border = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="CBD5E1"/></w:pBdr>')
        p._element.get_or_add_pPr().append(p_border)
        return

    # العناوين H1 - H6
    if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
        level = int(tag[1])
        sizes = {1: 22, 2: 18, 3: 15, 4: 13, 5: 12, 6: 11}
        p = doc.add_paragraph()
        
        # ألوان العنوان
        fg_col = parse_css_color(style.get('color'))
        bg_col = parse_css_color(style.get('background-color') or style.get('background'))
        
        if bg_col:
            apply_paragraph_shading(p, color_to_hex(bg_col))
        
        # الاتجاه
        align_str = style.get('text-align', '').lower()
        if align_str == 'center':
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif align_str == 'left':
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        if is_arabic_text(node.get_text()):
            apply_paragraph_rtl(p, True)
            
        run = p.add_run(node.get_text().strip())
        run.bold = True
        run.font.name = default_font
        run.font.size = Pt(sizes.get(level, 14))
        if fg_col:
            run.font.color.rgb = RGBColor(*fg_col)
        elif not bg_col:
            # لون قياسي أنيق للعناوين
            title_colors = {1: (15, 23, 42), 2: (30, 58, 138), 3: (13, 148, 136), 4: (51, 65, 85)}
            run.font.color.rgb = RGBColor(*title_colors.get(level, (30, 41, 59)))
        return

    # الفقرات والنصوص p, blockquote
    if tag in ('p', 'blockquote', 'pre'):
        p = doc.add_paragraph()
        align_str = style.get('text-align', '').lower()
        if align_str == 'center':
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif align_str == 'left':
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif align_str == 'justify':
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # تظليل أو خلفية للفقرة
        bg_col = parse_css_color(style.get('background-color') or style.get('background'))
        if bg_col:
            apply_paragraph_shading(p, color_to_hex(bg_col))

        if tag == 'blockquote':
            apply_paragraph_shading(p, "F8FAFC")
            p_border = parse_xml(f'<w:pBdr {nsdecls("w")}><w:right w:val="single" w:sz="18" w:space="4" w:color="0284C7"/></w:pBdr>')
            p._element.get_or_add_pPr().append(p_border)

        if is_arabic_text(node.get_text()):
            apply_paragraph_rtl(p, True)

        render_inline_contents(node, p, default_font, default_size, style)
        return

    # الجداول table
    if tag == 'table':
        render_table(node, doc, default_font, default_size)
        return

    # الصور img
    if tag == 'img':
        src = node.get('src', '')
        alt = node.get('alt', '')
        w_val = style.get('width', '') or node.get('width', '')
        width_in = 5.5
        if w_val:
            try:
                num = float(re.findall(r'[\d.]+', str(w_val))[0])
                if 'px' in str(w_val) or str(w_val).isdigit():
                    width_in = min(6.0, max(1.5, num / 96.0))
                elif 'in' in str(w_val):
                    width_in = min(6.0, num)
            except Exception:
                width_in = 5.5
        embed_image_to_doc(doc, src, width_in=width_in, caption=alt)
        return

    # القوائم ul, ol
    if tag in ('ul', 'ol'):
        is_ordered = (tag == 'ol')
        for idx, li in enumerate(node.find_all('li', recursive=False), 1):
            p = doc.add_paragraph()
            if is_arabic_text(li.get_text()):
                apply_paragraph_rtl(p, True)
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            bullet = f"{idx}. " if is_ordered else "● "
            run_b = p.add_run(bullet)
            run_b.bold = True
            run_b.font.name = default_font
            run_b.font.color.rgb = RGBColor(37, 99, 235) if is_ordered else RGBColor(16, 185, 129)
            render_inline_contents(li, p, default_font, default_size)
        return

    # صناديق البطاقات والحاويات div, section
    bg_col = parse_css_color(style.get('background-color') or style.get('background'))
    border_val = style.get('border', '') or style.get('border-color', '')
    border_col = parse_css_color(border_val)
    
    # إذا كان الـ div بمثابة بطاقة ملونة ومميزة، ننشئ جدولاً أحادي الخلية (Callout Card)
    if (bg_col or border_col) and ('card' in node.get('class', []) or 'box' in node.get('class', []) or bg_col):
        card_table = doc.add_table(rows=1, cols=1)
        card_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        card_cell = card_table.cell(0, 0)
        
        if bg_col:
            apply_cell_shading(card_cell, color_to_hex(bg_col))
        b_hex = color_to_hex(border_col) if border_col else "E2E8F0"
        apply_cell_borders(card_cell, border_color=b_hex, border_size=8)
        apply_cell_margins(card_cell, top=140, bottom=140, left=180, right=180)
        
        # تفريغ الفقرة الافتراضية للخلية
        p_cell = card_cell.paragraphs[0]
        if is_arabic_text(node.get_text()):
            apply_paragraph_rtl(p_cell, True)
            p_cell.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        render_inline_contents(node, p_cell, default_font, default_size, style)
        return

    # الحاويات العادية
    for child in node.children:
        render_node(child, doc, default_font, default_size, parent_para)

def render_inline_contents(node, paragraph, default_font: str, default_size: float, parent_style: Dict[str, str] = None):
    """معالجة النصوص الداخلية مع الوسوم المضمنة (span, strong, b, em, i, u, a, code, mark)"""
    if parent_style is None:
        parent_style = {}

    for child in node.children:
        if isinstance(child, NavigableString):
            txt = str(child)
            if not txt:
                continue
            run = paragraph.add_run(txt)
            run.font.name = default_font
            run.font.size = Pt(default_size)
            
            # تطبيق لون الوالد إذا وجد
            fg = parse_css_color(parent_style.get('color'))
            if fg:
                run.font.color.rgb = RGBColor(*fg)
        elif isinstance(child, Tag):
            c_tag = (child.name or '').lower()
            c_style = parse_style_attr(child.get('style', ''))
            
            # دمج أنماط الابن مع الوالد
            merged_style = {**parent_style, **c_style}
            
            if c_tag in ('strong', 'b'):
                r = paragraph.add_run(child.get_text())
                r.bold = True
            elif c_tag in ('em', 'i'):
                r = paragraph.add_run(child.get_text())
                r.italic = True
            elif c_tag == 'u':
                r = paragraph.add_run(child.get_text())
                r.underline = True
            elif c_tag in ('code', 'kbd'):
                r = paragraph.add_run(child.get_text())
                r.font.name = 'Consolas'
                r.font.size = Pt(default_size - 1)
                r.font.color.rgb = RGBColor(199, 37, 78)
            elif c_tag == 'mark':
                r = paragraph.add_run(child.get_text())
                r.bold = True
                r.font.color.rgb = RGBColor(180, 83, 9)
            elif c_tag == 'a':
                r = paragraph.add_run(child.get_text())
                r.font.color.rgb = RGBColor(2, 132, 199)
                r.underline = True
            elif c_tag == 'br':
                paragraph.add_run('\n')
                continue
            else:
                # span أو غيرها
                r = paragraph.add_run(child.get_text())

            r.font.name = default_font
            r.font.size = Pt(default_size)

            # فحص وزن وحجم الخط المخصص
            if 'bold' in merged_style.get('font-weight', ''):
                r.bold = True
            if 'italic' in merged_style.get('font-style', ''):
                r.italic = True
            if 'underline' in merged_style.get('text-decoration', ''):
                r.underline = True

            # اللون
            col = parse_css_color(merged_style.get('color'))
            if col:
                r.font.color.rgb = RGBColor(*col)

def render_table(table_node, doc, default_font: str, default_size: float):
    """
    تحويل <table> إلى جدول Word احترافي مع الحفاظ على:
    - ألوان خلفية الخلايا وthead
    - الحدود والتنسيق الفاخر
    - اتجاه اليمين لليسار (RTL Table)
    - محاذاة وتوزيع الأعمدة
    """
    rows = table_node.find_all('tr')
    if not rows:
        return

    # حساب عدد الأعمدة مع مراعاة colspan
    col_counts = []
    for r in rows:
        c_count = 0
        for cell in r.find_all(['td', 'th'], recursive=False):
            c_count += int(cell.get('colspan', 1) or 1)
        col_counts.append(c_count)

    max_cols = max(col_counts) if col_counts else 1
    num_rows = len(rows)

    word_table = doc.add_table(rows=num_rows, cols=max_cols)
    word_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    word_table.style = 'Table Grid'

    # تعيين جدول RTL في Word
    try:
        tblPr = word_table._tbl.tblPr
        bidi = parse_xml(f'<w:bidiVisual {nsdecls("w")}/>')
        tblPr.append(bidi)
    except Exception as e:
        logger.debug(f"Error setting bidiVisual: {e}")

    for row_idx, tr in enumerate(rows):
        word_row = word_table.rows[row_idx]
        is_header_row = bool(tr.find('th')) or tr.parent.name == 'thead'
        
        # تكرار ترويسة الجدول على رأس كل صفحة
        if is_header_row and row_idx == 0:
            try:
                trPr = word_row._tr.get_or_add_trPr()
                trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
            except Exception:
                pass

        col_cursor = 0
        cells = tr.find_all(['td', 'th'], recursive=False)
        for cell_node in cells:
            if col_cursor >= max_cols:
                break
                
            cell = word_row.cells[col_cursor]
            colspan = int(cell_node.get('colspan', 1) or 1)
            
            # دمج الخلايا أفقياً إذا وجد colspan
            if colspan > 1 and (col_cursor + colspan - 1) < max_cols:
                end_cell = word_row.cells[col_cursor + colspan - 1]
                cell = cell.merge(end_cell)

            cell_style = parse_style_attr(cell_node.get('style', ''))
            bg_col = parse_css_color(cell_style.get('background-color') or cell_style.get('background') or cell_node.get('bgcolor'))
            
            # لون خلفية افتراضي للترويسة إن لم يكن محدداً
            if not bg_col and (is_header_row or cell_node.name == 'th'):
                bg_col = (30, 41, 59) # Slate 800
                
            if bg_col:
                apply_cell_shading(cell, color_to_hex(bg_col))
                
            # حدود الخلية
            b_val = cell_style.get('border-color') or cell_style.get('border')
            b_hex = color_to_hex(parse_css_color(b_val)) if b_val else "CBD5E1"
            apply_cell_borders(cell, border_color=b_hex, border_size=4)
            apply_cell_margins(cell, top=100, bottom=100, left=140, right=140)

            # النص داخل الخلية
            p = cell.paragraphs[0]
            if is_arabic_text(cell_node.get_text()):
                apply_paragraph_rtl(p, True)
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # لون النص الافتراضي
            text_color = parse_css_color(cell_style.get('color'))
            if not text_color and (is_header_row or cell_node.name == 'th') and bg_col and sum(bg_col) < 380:
                text_color = (255, 255, 255) # أبيض فوق الخلفيات الداكنة

            cell_parent_style = {**cell_style}
            if text_color:
                cell_parent_style['color'] = f"rgb({text_color[0]},{text_color[1]},{text_color[2]})"
            if is_header_row or cell_node.name == 'th':
                cell_parent_style['font-weight'] = 'bold'

            render_inline_contents(cell_node, p, default_font, default_size, cell_parent_style)

            col_cursor += colspan

def convert_html_to_docx(
    html_content: str,
    output_target,
    filename: str = "document",
    font_family: str = "Cairo",
    font_size: float = 12.0,
    margin_inches: float = 1.0,
    rtl_doc: bool = True
) -> bool:
    """
    تحويل كود HTML إلى ملف DOCX عالي الجودة متوافق مع كافة برامج Word.
    - output_target: مسار ملف (str) أو io.BytesIO
    """
    try:
        # دمج قواعد الأنماط CSS
        inlined_html = inline_css_rules(html_content)
        soup = BeautifulSoup(inlined_html, 'html.parser')

        doc = docx.Document()

        # إعدادات الصفحة والهوامش
        for sec in doc.sections:
            sec.top_margin = Inches(margin_inches)
            sec.bottom_margin = Inches(margin_inches)
            sec.left_margin = Inches(margin_inches)
            sec.right_margin = Inches(margin_inches)
            if rtl_doc:
                try:
                    sectPr = sec._sectPr
                    bidi_xml = f'<w:bidi {nsdecls("w")}/>'
                    sectPr.append(parse_xml(bidi_xml))
                except Exception as e:
                    logger.debug(f"Failed to set section bidi: {e}")

        # ضبط النمط العادي Normal
        style_normal = doc.styles['Normal']
        style_normal.font.name = font_family
        style_normal.font.size = Pt(font_size)

        # تفريغ الرأس واستخراج المحتوى الرئيسي
        body = soup.find('body') or soup
        
        # تنظيف العناصر غير الضرورية
        for el in body.find_all(['script', 'style', 'noscript', 'head'], recursive=True):
            el.decompose()

        for child in body.children:
            render_node(child, doc, default_font=font_family, default_size=font_size)

        # حفظ المستند
        if isinstance(output_target, str):
            doc.save(output_target)
        else:
            doc.save(output_target)

        return True

    except Exception as e:
        logger.error(f"Error in convert_html_to_docx: {e}", exc_info=True)
        raise e

# ══════════════════════════════════════════════════════
# الذكاء الاصطناعي (Gemini AI Processing Engine)
# ══════════════════════════════════════════════════════

def call_gemini_api(prompt: str, system_instruction: str = "") -> Optional[str]:
    """استدعاء Gemini API عبر مفاتيح وموديلات متعددة مع إعادة المحاولة التلقائية"""
    import time
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        logger.warning("No GEMINI_API_KEY available in environment")
        return None

    # قائمة الموديلات الموصى بها حسب الترتيب
    models_to_try = ["gemini-3.8-flash", "gemini-3.1-flash-lite", "gemini-flash-latest"]
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 8192
        }
    }
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        for attempt in range(2):
            try:
                resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get('candidates', [])
                    if candidates and candidates[0].get('content', {}).get('parts'):
                        txt = candidates[0]['content']['parts'][0].get('text', '')
                        if txt:
                            logger.info(f"Gemini API call succeeded with model {model}")
                            return txt
                elif resp.status_code in (429, 503):
                    logger.warning(f"Gemini model {model} returned {resp.status_code}, backing off...")
                    time.sleep(1.0)
                    continue
                else:
                    logger.warning(f"Gemini API ({model}) returned status {resp.status_code}: {resp.text[:120]}")
                    break
            except Exception as e:
                logger.warning(f"Gemini call exception with {model}: {e}")
                time.sleep(0.5)

    return None

def _smart_offline_fallback(html_code: str, action: str) -> str:
    """بديل فوري وذكي في حال تعذر الاتصال بالشبكة لضمان عدم توقف المستخدم إطلاقاً"""
    inlined = inline_css_rules(html_code)
    soup = BeautifulSoup(inlined, 'html.parser')

    if action == "optimize":
        # تعزيز التوافق مع Word
        for tbl in soup.find_all('table'):
            tbl['style'] = (tbl.get('style', '') + '; width:100%; border-collapse:collapse; margin:15px 0;').strip(';')
            for th in tbl.find_all('th'):
                th['style'] = (th.get('style', '') + '; background-color:#1e293b; color:#ffffff; padding:10px; border:1px solid #334155; font-weight:bold; text-align:center;').strip(';')
            for td in tbl.find_all('td'):
                td['style'] = (td.get('style', '') + '; padding:8px 12px; border:1px solid #cbd5e1;').strip(';')
        for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            if is_arabic_text(p.get_text()):
                p['dir'] = 'rtl'
        return str(soup)

    elif action == "academic":
        header_banner = (
            '<div style="background: linear-gradient(135deg, #0f172a, #1e3a8a); color: #ffffff; padding: 25px; border-radius: 10px; text-align: center; margin-bottom: 25px;">'
            '<h1 style="color: #ffffff; margin: 0; font-size: 22pt;">تقرير أكاديمي رسمي موحد</h1>'
            '<p style="color: #93c5fd; margin-top: 8px; font-size: 12pt;">مركز سرعة إنجاز للخدمات الأكاديمية والطلابية</p>'
            '</div>'
        )
        body = soup.find('body') or soup
        # تجميل الجداول
        for tbl in body.find_all('table'):
            tbl['style'] = 'width:100%; border-collapse:collapse; margin:20px 0;'
            for th in tbl.find_all('th'):
                th['style'] = 'background-color:#1e293b; color:#ffffff; padding:12px; border:1px solid #475569; font-weight:bold; text-align:center;'
            for r_idx, tr in enumerate(tbl.find_all('tr')):
                if not tr.find('th'):
                    bg = '#f8fafc' if r_idx % 2 == 0 else '#ffffff'
                    tr['style'] = f'background-color:{bg};'
                    for td in tr.find_all('td'):
                        td['style'] = (td.get('style', '') + '; padding:9px 12px; border:1px solid #cbd5e1;').strip(';')
        return f"{header_banner}\n{str(body)}"

    elif action == "add_toc_cover":
        # استخراج العناوين لعمل الفهرس
        headings = soup.find_all(['h1', 'h2', 'h3'])
        toc_items = []
        for idx, h in enumerate(headings, 1):
            toc_items.append(f"<tr><td style='padding:8px 12px; border:1px solid #cbd5e1;'>{h.get_text().strip()}</td><td style='text-align:center; padding:8px 12px; border:1px solid #cbd5e1;'>{idx}</td></tr>")
        
        toc_table = ""
        if toc_items:
            toc_table = (
                '<div style="margin: 30px 0;">'
                '<h2 style="color: #1e3a8a; border-bottom: 2px solid #3b82f6; padding-bottom: 8px;">📑 جدول المحتويات والفهرس العام</h2>'
                '<table style="width:100%; border-collapse:collapse; margin-top:15px;">'
                '<thead><tr style="background:#1e293b; color:#fff;"><th>عنوان الموضوع / المحور</th><th>الصفحة التقديرية</th></tr></thead>'
                f'<tbody>{"".join(toc_items)}</tbody>'
                '</table>'
                '<div style="page-break-after: always; height: 1px; margin: 20px 0;"></div>'
                '</div>'
            )

        cover_page = (
            '<div style="min-height: 800px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 60px 20px; background: #ffffff; border: 3px double #1e3a8a; margin-bottom: 40px;">'
            '<h4 style="color: #64748b; letter-spacing: 1px;">المملكة العربية السعودية • مركز سرعة إنجاز للخدمات الأكاديمية</h4>'
            '<div style="margin: 80px 0 40px 0;">'
            '<h1 style="color: #0f172a; font-size: 28pt; font-weight: 800; line-height: 1.4;">مستند التقرير والأداء التنفيذي</h1>'
            '<h3 style="color: #2563eb; font-weight: 600; margin-top: 15px;">وثيقة رسمية منسقة ومعتمدة</h3>'
            '</div>'
            '<div style="margin-top: 120px; border-top: 1px solid #cbd5e1; padding-top: 25px; width: 80%;">'
            '<p style="font-size: 13pt; margin: 5px 0;"><strong>إعداد:</strong> فريق التحليل الأكاديمي والمهني</p>'
            '<p style="font-size: 12pt; color: #64748b;">تاريخ التصدير: موثق إلكترونياً</p>'
            '</div>'
            '<div style="page-break-after: always; height: 1px; margin: 20px 0;"></div>'
            '</div>'
        )
        return f"{cover_page}\n{toc_table}\n{str(soup)}"

    return inlined

def ai_process_html(html_code: str, action: str = "optimize", custom_prompt: str = "") -> Dict[str, Any]:
    """
    معالجة كود الـ HTML باستخدام الذكاء الاصطناعي:
    1. optimize: تحسين التوافق مع Word وتحويل الكلاسات لـ Inline styles وضبط الجداول
    2. academic: تنسيق المحتوى بطابع أكاديمي رسمي أنيق مع جداول ليكرت وتنسيق موحد
    3. add_toc_cover: إضافة صفحة غلاف رسمية وفهرس محتويات
    4. custom: تطبيق أمر مخصص من المستخدم
    """
    if not html_code.strip():
        return {"success": False, "error": "كود HTML فارغ"}

    sys_inst = (
        "أنت مهندس وخبير متخصص في هندسة مستندات الويب وبرامج معالجة النصوص (Microsoft Word / Office OpenXML). "
        "مهمتك فحص وتحسين كود HTML ليكون فائق الجمال والدقة عند تصديره لملف وورد (.docx). "
        "قواعد صارمة: "
        "1. يجب أن تعيد كود HTML فقط، صالح ونظيف وبدون أي تعليقات خارجية أو شروحات جانبية. "
        "2. استخدم الأنماط المضمنة style='...' مباشرة على العناصر، خصوصاً الألوان وخلفيات الجداول والحدود. "
        "3. اضبط اتجاه النصوص العربية dir='rtl' ومحاذاة اليمين. "
        "4. حافظ على كافة البيانات والجداول والصور كما هي تماماً دون حذف أي محتوى أصلي."
    )

    if action == "optimize":
        prompt = (
            "قم بتحسين كود HTML التالي لضمان التوافق المطلق بنسبة 100% مع تصدير Word (DOCX):\n"
            "- تأكد من أن كل الجداول <table> لها حدود وخلفيات واضحة ومسافات بادئة padding.\n"
            "- حول فئات CSS إلى خصائص style مضمنة بألوان HEX واضحة.\n"
            "- اضبط العناوين بنسب متناسقة وألوان أنيقة.\n\n"
            f"الكود:\n{html_code}"
        )
    elif action == "academic":
        prompt = (
            "قم بإعادة تنسيق كود HTML التالي بنمط أكاديمي ومهني فاخر:\n"
            "- رأس تقرير رسمي فاخر مع عنوان البحث وتاريخ الإعداد.\n"
            "- جداول منسقة بأسلوب التقارير الأكاديمية (ترويسة كحلية غامقة #1e293b بنص أبيض، صفوف متناوبة هادئة).\n"
            "- صناديق ملاحظات ونتائج بحدود أنيقة (Callout Boxes).\n"
            "- خطوط وألوان مريحة للعين ومطابقة للمستندات الرسمية.\n\n"
            f"الكود:\n{html_code}"
        )
    elif action == "add_toc_cover":
        prompt = (
            "قم بإضافة صفحة غلاف رسمية احترافية (Cover Page) تليها صفحة فهرس محتويات (Table of Contents) "
            "في بداية كود الـ HTML التالي مع الحفاظ التام على كامل المحتوى الأصلي أدناه:\n"
            "- صفحة الغلاف تحتوي على: عنوان رئيسي بارز، عنوان فرعي، إعداد الباحث/المؤلف، والتاريخ.\n"
            "- فاصل صفحة <div style='page-break-after: always;'></div> بين الغلاف والفهرس والمحتوى.\n"
            "- فهرس محتويات جذاب وجدول منظم.\n\n"
            f"الكود:\n{html_code}"
        )
    elif action == "custom" and custom_prompt:
        prompt = f"المطلوب: {custom_prompt}\n\nطبق المطلوب بدقة تامة على كود HTML التالي وأعد فقط الكود الناتج:\n{html_code}"
    else:
        prompt = f"قم بفحص وتنسيق كود HTML التالي وتحسينه:\n{html_code}"

    output = call_gemini_api(prompt, system_instruction=sys_inst)
    if not output:
        logger.info("Using smart offline heuristic fallback for HTML styling")
        fallback_res = _smart_offline_fallback(html_code, action)
        return {"success": True, "processed_html": fallback_res}

    # تنظيف markdown codeblocks if present
    cleaned = output.strip()
    if cleaned.startswith("```html"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    return {"success": True, "processed_html": cleaned.strip()}
