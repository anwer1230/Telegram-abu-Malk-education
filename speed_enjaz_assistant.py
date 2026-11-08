# -*- coding: utf-8 -*-
"""
محرك مساعد مركز سرعة إنجاز الذكي الشامل (Speed Enjaz AI Assistant)
===================================================================
- محادثة ذكية مباشرة ومفتوحة بدون قيود مع Google Gemini AI.
- إدارة المفاتيح الثابتة والدائمة مع التبديل التلقائي عند نفاد الرصيد أو الحصص (Sequential Failover).
- شريط ومؤشر استمرار الاستخدام اليومي مع تصفير وتهيئة تلقائية كل 24 ساعة (عند بداية كل يوم).
- توليد مستندات وملفات حقيقية قابلة للتحميل والفتح في الهواتف والجوالات (Word, Excel, PowerPoint, PDF, TXT).
- إمكانية رفع وتحليل الصور والمستندات (Vision & Document OCR/Analysis).
- استقلالية تامة دون التدخل في وظائف النظام الأخرى.
"""

import os
import re
import sys
import json
import time
import base64
import uuid
import logging
import urllib.request
import urllib.error
from datetime import datetime, date
from flask import Blueprint, request, jsonify, send_file, current_app

logger = logging.getLogger("SpeedEnjazAssistant")
logger.setLevel(logging.INFO)

speed_assistant_bp = Blueprint("speed_assistant_bp", __name__)

# المجلد المخصص لتخزين الملفات المولدة مؤقتاً للتحميل
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATED_FILES_DIR = os.path.join(BASE_DIR, "static", "generated_files")
os.makedirs(GENERATED_FILES_DIR, exist_ok=True)

DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
USAGE_FILE = os.path.join(DATA_DIR, "speed_enjaz_usage.json")

# ============================================================================
# 1. قائمة المفاتيح الدائمة والثابتة داخل الكود الرئيسي للنظام
# ============================================================================
_ENCODED_KEYS_DATA = [
    ("key_1", "QVEuQWI4Uk42TFNDZ0lKNEkyaUN2YWduN25KZU0tdXhnNDJxV3l4TU9BOVdzQV92dFRZTFE=", "...vtTYLQ", "مفتاح سرعة إنجاز الرئيسي (1)", 1),
    ("key_2", "QVEuQWI4Uk42THNnbWtDTUVxRHR2blV2MlhoNGJvNFNhbjVfbmdmeUpNTVpvS0RjZWJFWEE=", "...cebEXA", "مفتاح سرعة إنجاز المساعد (2)", 2),
    ("key_3", "QVEuQWI4Uk42Szh5OEtvek1pdEw1YjhIdmpLSjJJRHF0WnBjdXFhT2xFLXFaTXhUZVVzMEE=", "...TeUs0A", "مفتاح سرعة إنجاز الاحتياطي (3)", 3),
    ("key_4", "QVEuQWI4Uk42SnR4Y1lRZ3ExblZRd0FaNnlqZkFMU3hQcFpxRUE5TGtXVUlqWlA1UDB6MkE=", "...5P0z2A", "مفتاح سرعة إنجاز الإضافي (4)", 4),
    ("key_5", "QVEuQWI4Uk42S3JDWUVLMlRQbWRFOWFrUFdndFVDUG01bklJa1gzZXhCWVhUZjdsalU0WXc=", "...ljU4Yw", "مفتاح سرعة إنجاز الخامس (5)", 5),
    ("key_6", "QVEuQWI4Uk42TDIxcWJIX25CeDdBeEFCaklrdjY3bG81Wjh5TEtNNWZRU1ZJX1RMSEFpRVE=", "...LHAiEQ", "مفتاح سرعة إنجاز السادس (6)", 6),
    ("key_7", "QVEuQWI4Uk42S2dSakRWXzhsVUpLMHNBYUFGVVhNeFQ5b2JiSzRMV19xVWhPd0czY2VidkE=", "...3cebvA", "مفتاح سرعة إنجاز الاحتياطي (7)", 7),
    ("key_8", "QVEuQWI4Uk42S2hST0Q0VFQxYWpjWHFlWnpyRzVRMmc5aUJVRjNGcFNudUkwVkFPLWRqNnc=", "...O-dj6w", "مفتاح سرعة إنجاز الاحتياطي (8)", 8),
]

PERMANENT_GEMINI_KEYS = []
for _kid, _b64, _hint, _name, _prio in _ENCODED_KEYS_DATA:
    try:
        _decoded = base64.b64decode(_b64).decode("utf-8").strip()
        PERMANENT_GEMINI_KEYS.append({
            "id": _kid,
            "key": _decoded,
            "hint": _hint,
            "name": _name,
            "priority": _prio
        })
    except Exception as _e_dec:
        logger.error(f"خطأ في فك تشفير المفتاح {_kid}: {_e_dec}")

# إضافة المفتاح الموجود في البيئة إن وجد
_env_key = os.environ.get("GEMINI_API_KEY", "").strip()
if _env_key and not any(k["key"] == _env_key for k in PERMANENT_GEMINI_KEYS):
    PERMANENT_GEMINI_KEYS.insert(0, {
        "id": "env_key",
        "key": _env_key,
        "hint": "..." + _env_key[-6:],
        "name": "مفتاح بيئة النظام التلقائي",
        "priority": 0
    })

# النماذج المعتمدة بالترتيب (الأحدث والأسرع أولاً لتجنب الازدحام)
MODELS_PRIORITY = [
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-3.8-flash"
]

# الحد اليومي التقديري المريح لجميع المفاتيح مجتمعة (لحساب النسبة المئوية في الشريط)
DAILY_CAPACITY_ESTIMATE = len(PERMANENT_GEMINI_KEYS) * 250  # ~2000 طلب يومياً


# ============================================================================
# 2. إدارة الاستخدام اليومي والتهيئة كل 24 ساعة (Daily Usage & 24h Auto-Reset)
# ============================================================================
def get_today_str():
    return date.today().isoformat()

def load_usage_stats():
    """تحميل إحصائيات الاستخدام مع التحقق من مرور 24 ساعة للتهيئة التلقائية."""
    today = get_today_str()
    default_stats = {
        "date": today,
        "daily_requests": 0,
        "daily_limit_est": DAILY_CAPACITY_ESTIMATE,
        "active_key_index": 0,
        "total_files_generated": 0,
        "key_stats": {k["id"]: {"calls": 0, "errors": 0, "status": "active"} for k in PERMANENT_GEMINI_KEYS},
        "last_reset": datetime.now().isoformat()
    }

    if not os.path.exists(USAGE_FILE):
        save_usage_stats(default_stats)
        return default_stats

    try:
        with open(USAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # التحقق من بداية يوم جديد (كل 24 ساعة)
        if data.get("date") != today:
            logger.info(f"🔄 بداية يوم جديد ({today}) - جارٍ تهيئة شريط الاستخدام اليومي وتصفير العدادات...")
            data["date"] = today
            data["daily_requests"] = 0
            data["last_reset"] = datetime.now().isoformat()
            # إعادة تنشيط جميع المفاتيح
            for k in PERMANENT_GEMINI_KEYS:
                if k["id"] not in data["key_stats"]:
                    data["key_stats"][k["id"]] = {"calls": 0, "errors": 0, "status": "active"}
                else:
                    data["key_stats"][k["id"]]["status"] = "active"
                    data["key_stats"][k["id"]]["calls"] = 0
                    data["key_stats"][k["id"]]["errors"] = 0
            save_usage_stats(data)

        return data
    except Exception as e:
        logger.error(f"خطأ في قراءة إحصائيات الاستخدام: {e}")
        return default_stats

def save_usage_stats(stats):
    try:
        with open(USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"خطأ في حفظ إحصائيات الاستخدام: {e}")

def record_usage_success(key_id):
    stats = load_usage_stats()
    stats["daily_requests"] = stats.get("daily_requests", 0) + 1
    if "key_stats" not in stats:
        stats["key_stats"] = {}
    if key_id not in stats["key_stats"]:
        stats["key_stats"][key_id] = {"calls": 0, "errors": 0, "status": "active"}
    stats["key_stats"][key_id]["calls"] += 1
    stats["key_stats"][key_id]["status"] = "active"
    save_usage_stats(stats)

def record_usage_failure(key_id, reason="error"):
    stats = load_usage_stats()
    if "key_stats" not in stats:
        stats["key_stats"] = {}
    if key_id not in stats["key_stats"]:
        stats["key_stats"][key_id] = {"calls": 0, "errors": 0, "status": "active"}
    stats["key_stats"][key_id]["errors"] += 1
    if "quota" in reason.lower() or "429" in reason or "exhausted" in reason or "403" in reason:
        stats["key_stats"][key_id]["status"] = "quota_exceeded"
    save_usage_stats(stats)


# ============================================================================
# 3. محرك الاتصال بـ Gemini مع التبديل التلقائي للمفاتيح (Sequential Failover)
# ============================================================================
def call_gemini_api(contents, system_instruction=None):
    """
    إرسال الطلب إلى Gemini مع التدوير التلقائي السلس بين المفاتيح.
    إذا انتهى رصيد مفتاح أو حدث خطأ، ينتقل فوراً للمفتاح التالي بالترتيب.
    """
    stats = load_usage_stats()
    start_index = stats.get("active_key_index", 0) % len(PERMANENT_GEMINI_KEYS)
    total_keys = len(PERMANENT_GEMINI_KEYS)

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192
        }
    }
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    last_error = None

    # تجربة المفاتيح بالترتيب المتتالي
    for attempt in range(total_keys):
        current_idx = (start_index + attempt) % total_keys
        key_info = PERMANENT_GEMINI_KEYS[current_idx]
        api_key = key_info["key"]

        # تجربة النماذج المفضلة
        for model in MODELS_PRIORITY:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "X-goog-api-key": api_key
                }
            )

            try:
                with urllib.request.urlopen(req, timeout=14) as resp:
                    raw_data = resp.read().decode("utf-8")
                    result = json.loads(raw_data)

                    # استخراج الرد
                    candidates = result.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        text_response = "".join(p.get("text", "") for p in parts)

                        # نجاح الطلب: حفظ الفهرس النشط وتسجيل الاستخدام
                        stats["active_key_index"] = current_idx
                        save_usage_stats(stats)
                        record_usage_success(key_info["id"])

                        return {
                            "success": True,
                            "text": text_response,
                            "key_name": key_info["name"],
                            "key_hint": key_info["hint"],
                            "active_key_index": current_idx + 1,
                            "total_keys": total_keys,
                            "model": model
                        }
            except urllib.error.HTTPError as e:
                err_body = ""
                try:
                    err_body = e.read().decode("utf-8")
                except Exception:
                    pass
                last_error = f"HTTP {e.code}: {err_body[:200]}"
                logger.warning(f"⚠️ فشل المفتاح {key_info['hint']} على النموذج {model}: {last_error}")

                # إذا كان الخطأ متعلقاً بالحصص (429 أو 403 أو RESOURCE_EXHAUSTED)
                if e.code in (429, 403) or "QUOTA" in err_body.upper() or "RESOURCE_EXHAUSTED" in err_body.upper():
                    record_usage_failure(key_info["id"], f"quota_{e.code}")
                    # إذا كانت الحصة تخص هذا النموذج بالذات (per_model) نجرب النموذج التالي على نفس المفتاح
                    if "per_model" in err_body.lower() or "tokens_per_model" in err_body.lower():
                        continue
                    break  # التبديل إلى المفتاح التالي مباشرة

            except Exception as ex:
                last_error = str(ex)
                logger.warning(f"⚠️ خطأ غير متوقع في المفتاح {key_info['hint']}: {last_error}")
                break

    # في حال فشلت جميع المفاتيح
    return {
        "success": False,
        "error": f"تعذر الاتصال بجميع مفاتيح الذكاء الاصطناعي حالياً. آخر خطأ: {last_error}"
    }


# ============================================================================
# 4. محرك توليد الملفات الحقيقية المتوافقة 100% مع الجوال (Word, Excel, PPTX, PDF, TXT)
# ============================================================================

def create_word_document(title, content_markdown, output_filename=None):
    """توليد ملف وورد (.docx) حقيقي ومنسق واحترافي يدعم اللغة العربية للجوال."""
    import docx
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    doc = docx.Document()

    # هوامش مريحة
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    def set_rtl(p):
        pPr = p._p.get_or_add_pPr()
        bidi = OxmlElement('w:bidi')
        bidi.set(qn('w:val'), '1')
        pPr.append(bidi)

    # عنوان رئيسي أنيق
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_rtl(title_p)
    title_run = title_p.add_run(title)
    title_run.font.name = 'Arial'
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(30, 64, 175) # Blue

    # ترويسة مركز سرعة إنجاز
    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_rtl(sub_p)
    sub_run = sub_p.add_run(f"تم الإعداد بواسطة: مركز سرعة إنجاز الشامل للخدمات • {datetime.now().strftime('%Y-%m-%d')}")
    sub_run.font.name = 'Arial'
    sub_run.font.size = Pt(10)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph("―" * 40).alignment = WD_ALIGN_PARAGRAPH.CENTER

    # معالجة محتوى الماركداون والفقرات
    lines = content_markdown.split("\n")
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        if line_clean.startswith("# "):
            h = doc.add_heading(level=1)
            set_rtl(h)
            r = h.add_run(line_clean[2:])
            r.font.name = 'Arial'
            r.font.size = Pt(16)
            r.font.bold = True
            r.font.color.rgb = RGBColor(30, 58, 138)
        elif line_clean.startswith("## "):
            h = doc.add_heading(level=2)
            set_rtl(h)
            r = h.add_run(line_clean[3:])
            r.font.name = 'Arial'
            r.font.size = Pt(14)
            r.font.bold = True
            r.font.color.rgb = RGBColor(3, 105, 161)
        elif line_clean.startswith("### "):
            h = doc.add_heading(level=3)
            set_rtl(h)
            r = h.add_run(line_clean[4:])
            r.font.name = 'Arial'
            r.font.size = Pt(12)
            r.font.bold = True
            r.font.color.rgb = RGBColor(71, 85, 105)
        elif line_clean.startswith("- ") or line_clean.startswith("* "):
            p = doc.add_paragraph(style='List Bullet')
            set_rtl(p)
            r = p.add_run(line_clean[2:])
            r.font.name = 'Arial'
            r.font.size = Pt(11)
        else:
            p = doc.add_paragraph()
            set_rtl(p)
            # تنسيق النص الغامق **نص**
            parts = re.split(r'(\*\*.*?\*\*)', line_clean)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    r = p.add_run(part[2:-2])
                    r.font.name = 'Arial'
                    r.font.size = Pt(11)
                    r.font.bold = True
                else:
                    r = p.add_run(part)
                    r.font.name = 'Arial'
                    r.font.size = Pt(11)

    if not output_filename:
        output_filename = f"speed_enjaz_doc_{uuid.uuid4().hex[:8]}.docx"
    filepath = os.path.join(GENERATED_FILES_DIR, output_filename)
    doc.save(filepath)
    return filepath, output_filename


def create_excel_document(title, table_data, output_filename=None):
    """توليد ملف إكسل (.xlsx) حقيقي وجداول منسقة ملونة للجوال."""
    import xlsxwriter

    if not output_filename:
        output_filename = f"speed_enjaz_sheet_{uuid.uuid4().hex[:8]}.xlsx"
    filepath = os.path.join(GENERATED_FILES_DIR, output_filename)

    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet("مركز سرعة إنجاز")
    worksheet.right_to_left()

    # تنسيقات
    title_fmt = workbook.add_format({
        'bold': True, 'font_size': 16, 'font_name': 'Arial',
        'font_color': '#1e3a8a', 'align': 'center', 'valign': 'vcenter'
    })
    header_fmt = workbook.add_format({
        'bold': True, 'font_size': 11, 'font_name': 'Arial',
        'bg_color': '#2563eb', 'font_color': '#ffffff',
        'align': 'center', 'valign': 'vcenter', 'border': 1
    })
    cell_fmt = workbook.add_format({
        'font_size': 10, 'font_name': 'Arial',
        'align': 'right', 'valign': 'vcenter', 'border': 1
    })

    worksheet.merge_range('A1:E1', title, title_fmt)
    worksheet.set_row(0, 30)

    # صفوف البيانات
    if isinstance(table_data, list) and len(table_data) > 0:
        headers = table_data[0]
        worksheet.set_row(2, 25)
        for col_num, h in enumerate(headers):
            worksheet.write(2, col_num, str(h), header_fmt)
            worksheet.set_column(col_num, col_num, max(len(str(h)) * 3, 16))

        for row_num, row_data in enumerate(table_data[1:], start=3):
            for col_num, val in enumerate(row_data):
                worksheet.write(row_num, col_num, val, cell_fmt)
    else:
        # جدول افتراضي إذا لم يتوفر هيكل
        headers = ["الرقم", "البيان / الخدمة", "التفاصيل", "الحالة", "ملاحظات"]
        for col_num, h in enumerate(headers):
            worksheet.write(2, col_num, h, header_fmt)
            worksheet.set_column(col_num, col_num, 18)

    workbook.close()
    return filepath, output_filename


def create_pptx_presentation(title, slides_content, output_filename=None):
    """توليد عرض تقديمي احترافي PowerPoint (.pptx) متوافق مع تطبيقات الجوال."""
    import pptx
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor

    prs = pptx.Presentation()
    # شرائح 16:9
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # الشريحة الأولى (شريحة العنوان)
    title_slide = prs.slides.add_slide(blank_layout)
    txBox = title_slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11.333), Inches(3.5))
    tf = txBox.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = title
    p.font.name = 'Arial'
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = RGBColor(30, 58, 138)

    p2 = tf.add_paragraph()
    p2.text = f"مركز سرعة إنجاز الشامل • {datetime.now().strftime('%Y-%m-%d')}"
    p2.font.name = 'Arial'
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(100, 116, 139)

    # الشرائح التالية
    for item in slides_content:
        slide = prs.slides.add_slide(blank_layout)
        # عنوان الشريحة
        head_box = slide.shapes.add_textbox(Inches(1), Inches(0.8), Inches(11.333), Inches(1.2))
        htf = head_box.text_frame
        hp = htf.paragraphs[0]
        hp.text = item.get("title", "شريحة")
        hp.font.name = 'Arial'
        hp.font.size = Pt(28)
        hp.font.bold = True
        hp.font.color.rgb = RGBColor(37, 99, 235)

        # نقاط الشريحة
        body_box = slide.shapes.add_textbox(Inches(1), Inches(2.2), Inches(11.333), Inches(4.5))
        btf = body_box.text_frame
        btf.word_wrap = True

        bullets = item.get("bullets", [])
        for b in bullets:
            bp = btf.add_paragraph()
            bp.text = f"• {b}"
            bp.font.name = 'Arial'
            bp.font.size = Pt(20)
            bp.font.color.rgb = RGBColor(30, 41, 59)

    if not output_filename:
        output_filename = f"speed_enjaz_slides_{uuid.uuid4().hex[:8]}.pptx"
    filepath = os.path.join(GENERATED_FILES_DIR, output_filename)
    prs.save(filepath)
    return filepath, output_filename


def create_pdf_document(title, text_content, output_filename=None):
    """توليد ملف PDF احترافي للجوال بواسطة ReportLab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib import colors

    if not output_filename:
        output_filename = f"speed_enjaz_report_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(GENERATED_FILES_DIR, output_filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    story = []
    # عنوان
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e40af'),
        alignment=1, # Center
        spaceAfter=15
    )
    story.append(Paragraph(title, title_style))

    sub_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748b'),
        alignment=1,
        spaceAfter=20
    )
    story.append(Paragraph(f"مركز سرعة إنجاز الشامل • {datetime.now().strftime('%Y-%m-%d')}", sub_style))

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=10
    )

    for line in text_content.split("\n"):
        clean = line.strip()
        if clean:
            story.append(Paragraph(clean.replace("<", "&lt;").replace(">", "&gt;"), body_style))
        else:
            story.append(Spacer(1, 10))

    doc.build(story)
    return filepath, output_filename


def create_plain_text_file(content, filename_ext="txt", output_filename=None):
    """توليد ملف نصي أو كود أو HTML."""
    if not output_filename:
        output_filename = f"speed_enjaz_file_{uuid.uuid4().hex[:8]}.{filename_ext}"
    filepath = os.path.join(GENERATED_FILES_DIR, output_filename)
    with open(filepath, "w", encoding="utf-8-sig") as f:
        f.write(content)
    return filepath, output_filename


# ============================================================================
# 5. استخراج وتحليل الملفات والمستندات المرفوعة (Images & Docs Extraction)
# ============================================================================
def extract_uploaded_file_data(uploaded_file):
    """استخراج محتوى الملف المرفوع سواء صورة أو مستند PDF أو Word أو نص."""
    filename = uploaded_file.filename or "file"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    file_bytes = uploaded_file.read()

    # صور: تجهيزها لـ Gemini Vision
    if ext in ["jpg", "jpeg", "png", "webp", "gif"]:
        mime_map = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
            "gif": "image/gif"
        }
        b64_data = base64.b64encode(file_bytes).decode("utf-8")
        return {
            "type": "image",
            "filename": filename,
            "mime_type": mime_map.get(ext, "image/jpeg"),
            "data": b64_data
        }

    # ملفات صوتية: تجهيزها لـ Gemini Audio Analysis & Transcription
    audio_exts = ["mp3", "wav", "ogg", "m4a", "aac", "webm", "flac", "opus", "amr"]
    if ext in audio_exts or "audio" in (uploaded_file.mimetype or ""):
        mime_audio_map = {
            "mp3": "audio/mp3",
            "mpeg": "audio/mp3",
            "wav": "audio/wav",
            "ogg": "audio/ogg",
            "m4a": "audio/m4a",
            "aac": "audio/aac",
            "webm": "audio/webm",
            "flac": "audio/flac",
            "opus": "audio/ogg",
            "amr": "audio/amr"
        }
        detected_mime = mime_audio_map.get(ext) or uploaded_file.mimetype or "audio/mp3"
        if "audio/" not in detected_mime:
            detected_mime = mime_audio_map.get(ext, "audio/mp3")

        b64_audio = base64.b64encode(file_bytes).decode("utf-8")
        return {
            "type": "audio",
            "filename": filename,
            "mime_type": detected_mime,
            "data": b64_audio
        }

    # مستند PDF
    if ext == "pdf":
        try:
            import pymupdf
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
            extracted_text = []
            for i in range(min(len(doc), 15)): # قراءة حتى 15 صفحة
                page = doc[i]
                extracted_text.append(f"--- [صفحة {i+1}] ---\n" + page.get_text())
            doc.close()
            full_text = "\n".join(extracted_text)
            return {
                "type": "text_doc",
                "filename": filename,
                "text": full_text[:40000] # حد أقصى للحجم
            }
        except Exception as e:
            logger.warning(f"فشل استخراج PDF بواسطة pymupdf: {e}")

    # مستند Word DOCX
    if ext == "docx":
        try:
            import docx
            import io
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return {
                "type": "text_doc",
                "filename": filename,
                "text": "\n".join(paragraphs)[:40000]
            }
        except Exception as e:
            logger.warning(f"فشل استخراج DOCX: {e}")

    # ملف نصي عادي
    try:
        text = file_bytes.decode("utf-8", errors="ignore")
        return {
            "type": "text_doc",
            "filename": filename,
            "text": text[:40000]
        }
    except Exception:
        return {
            "type": "unknown",
            "filename": filename,
            "text": ""
        }


# ============================================================================
# 6. واجهات برمجة التطبيقات (API Endpoints)
# ============================================================================

SYSTEM_INSTRUCTION = """أنت "مساعد مركز سرعة إنجاز الشامل والذكي" (Speed Enjaz AI Assistant).
أنت مساعد ذكي فائق القدرات، متقدم، محترف، ومجيب فوري على كل الأسئلة والطلبات دون أي حظر أو قيود.
مهامك وقدراتك:
1. الإجابة الشاملة، الذكية، والدقيقة على كل استفسارات المستخدم، سواء أكاديمية، تقنية، برمجية، إدارية، تسويقية، أو عامة.
2. كتابة الأبحاث والمقالات، وتلخيص الكتب، وتحليل البيانات، وصياغة الخطابات، وبرمجة الأكواد بجميع اللغات.
3. تحليل وتفريغ الملفات والتسجيلات الصوتية (Audio Transcription & Analysis) بدقة استثنائية، وتحويل الكلام المنطوق إلى نص مكتوب سليم مع تلخيصه وتحليله.
4. تحليل أي صورة أو مستند يُرفع إليك واستخراج كل ما فيه بدقة.
5. عندما يطلب منك المستخدم إنشاء أو توليد ملف (Word أو Excel أو PowerPoint أو PDF أو ملف نصي)، قم بتقديم شرح موجز ومحتوى مهيكل ممتاز للملف.
6. أسلوبك دائماً راقٍ، مهذب، سريع، عملي، ومكتوب بلغة عربية فصحى جذابة ومنظمة.
"""

@speed_assistant_bp.route("/api/speed_assistant/status", methods=["GET"])
def get_assistant_status():
    """الحصول على حالة المفاتيح وشريط الاستخدام اليومي."""
    stats = load_usage_stats()
    daily_req = stats.get("daily_requests", 0)
    daily_limit = stats.get("daily_limit_est", DAILY_CAPACITY_ESTIMATE)
    pct = min(100, int((daily_req / max(daily_limit, 1)) * 100))
    active_idx = stats.get("active_key_index", 0) + 1

    return jsonify({
        "success": True,
        "date": stats.get("date"),
        "daily_requests": daily_req,
        "daily_limit_est": daily_limit,
        "usage_percentage": pct,
        "active_key_index": active_idx,
        "total_keys": len(PERMANENT_GEMINI_KEYS),
        "keys_info": [
            {
                "id": k["id"],
                "name": k["name"],
                "hint": k["hint"],
                "priority": k["priority"],
                "status": stats.get("key_stats", {}).get(k["id"], {}).get("status", "active"),
                "calls": stats.get("key_stats", {}).get(k["id"], {}).get("calls", 0)
            } for k in PERMANENT_GEMINI_KEYS
        ],
        "last_reset": stats.get("last_reset")
    })


@speed_assistant_bp.route("/api/speed_assistant/chat", methods=["POST"])
def assistant_chat():
    """المحادثة المباشرة مع المساعد الذكي، مع دعم رفع الصور والمستندات وتوليد الملفات."""
    user_prompt = request.form.get("prompt", "").strip() if request.form else ""
    chat_history_raw = request.form.get("history", "[]") if request.form else "[]"
    request_file_type = request.form.get("file_type", "").strip().lower() if request.form else ""

    # دعم JSON أيضاً
    if not user_prompt and request.is_json:
        data = request.get_json() or {}
        user_prompt = data.get("prompt", "").strip()
        chat_history_raw = json.dumps(data.get("history", []))
        request_file_type = data.get("file_type", "").strip().lower()

    if not user_prompt and "file" not in request.files:
        return jsonify({"success": False, "error": "يرجى كتابة رسالة أو إرفاق ملف."}), 400

    # معالجة الملف المرفوع إن وجد
    attached_file_info = None
    if "file" in request.files:
        up_file = request.files["file"]
        if up_file and up_file.filename:
            attached_file_info = extract_uploaded_file_data(up_file)

    # بناء أجزاء الرسالة (Contents)
    user_parts = []

    # إذا كانت صورة مرفقة
    if attached_file_info and attached_file_info.get("type") == "image":
        user_parts.append({
            "inlineData": {
                "mimeType": attached_file_info["mime_type"],
                "data": attached_file_info["data"]
            }
        })
        user_prompt = f"[تم إرفاق صورة: {attached_file_info['filename']}]\n" + (user_prompt or "يرجى تحليل هذه الصورة وشرح كل ما فيها بالتفصيل واستخراج أي نصوص أو بيانات.")

    # إذا كان تسجيلاً أو ملفاً صوتياً مرفوعاً
    elif attached_file_info and attached_file_info.get("type") == "audio":
        user_parts.append({
            "inlineData": {
                "mimeType": attached_file_info["mime_type"],
                "data": attached_file_info["data"]
            }
        })
        user_prompt = f"[تم إرفاق تسجيل صوتي: {attached_file_info['filename']}]\n" + (user_prompt or "يرجى الاستماع لهذا التسجيل الصوتي بدقة، وتفريغه كاملاً إلى نص مكتوب واضح ومنسق، ثم تقديم تلخيص وتحليل شامل لأهم النقاط والأفكار والقرارات الواردة فيه.")

    # إذا كان مستند نصي / PDF / Word مرفوعاً
    elif attached_file_info and attached_file_info.get("type") == "text_doc":
        doc_text = attached_file_info.get("text", "")
        user_prompt = f"[تم إرفاق مستند: {attached_file_info['filename']}]\nمحتوى المستند المستخرج:\n```\n{doc_text}\n```\n\nطلب المستخدم حول هذا المستند:\n" + (user_prompt or "يرجى تلخيص المستند واستخراج النقاط الأساسية.")

    user_parts.append({"text": user_prompt})

    # تجهيز سجل المحادثة (History)
    contents = []
    try:
        history = json.loads(chat_history_raw) if isinstance(chat_history_raw, str) else chat_history_raw
        for h in history[-8:]: # آخر 8 رسائل لسياق سريع ومثالي
            role = "user" if h.get("role") == "user" else "model"
            txt = h.get("content") or h.get("text") or ""
            if txt:
                contents.append({"role": role, "parts": [{"text": txt}]})
    except Exception:
        pass

    contents.append({"role": "user", "parts": user_parts})

    # استدعاء Gemini مع التدوير التلقائي
    ai_result = call_gemini_api(contents, SYSTEM_INSTRUCTION)
    if not ai_result.get("success"):
        return jsonify({"success": False, "error": ai_result.get("error")}), 500

    ai_reply_text = ai_result.get("text", "")

    # فحص ما إذا كان المستخدم يطلب توليد ملف حقيقي (Word, Excel, PowerPoint, PDF)
    generated_file_info = None

    # الكشف التلقائي عن طلبات إنشاء الملفات
    auto_detect_file = False
    lower_p = user_prompt.lower()
    if request_file_type:
        auto_detect_file = True
    elif any(kw in lower_p for kw in ["ملف وورد", "مستند وورد", "بصيغة word", "بصيغة docx", "ملف docx"]):
        request_file_type = "docx"
        auto_detect_file = True
    elif any(kw in lower_p for kw in ["ملف إكسل", "جدول إكسل", "بصيغة excel", "بصيغة xlsx", "ملف xlsx"]):
        request_file_type = "xlsx"
        auto_detect_file = True
    elif any(kw in lower_p for kw in ["عرض بوربوينت", "ملف بوربوينت", "شرايح", "شرائح", "بصيغة pptx", "عرض تقديمي"]):
        request_file_type = "pptx"
        auto_detect_file = True
    elif any(kw in lower_p for kw in ["ملف pdf", "تقرير pdf", "بصيغة pdf"]):
        request_file_type = "pdf"
        auto_detect_file = True

    if auto_detect_file and request_file_type:
        try:
            # استخراج عنوان مناسب
            title_match = re.search(r'^(?:#+\s*)?([^\n]+)', ai_reply_text)
            doc_title = title_match.group(1).replace("#", "").strip() if title_match else "مستند مركز سرعة إنجاز"
            doc_title = doc_title[:60]

            if request_file_type == "docx":
                fpath, fname = create_word_document(doc_title, ai_reply_text)
                generated_file_info = {
                    "type": "docx",
                    "filename": fname,
                    "download_url": f"/api/speed_assistant/download/{fname}",
                    "name_display": f"{doc_title}.docx",
                    "size_bytes": os.path.getsize(fpath)
                }
            elif request_file_type == "xlsx":
                # محاولة استخراج جداول إن وجدت
                lines = ai_reply_text.split("\n")
                table_rows = []
                for l in lines:
                    if "|" in l:
                        parts = [p.strip() for p in l.split("|") if p.strip()]
                        if parts and not all(c in "-: " for c in "".join(parts)):
                            table_rows.append(parts)
                if not table_rows:
                    table_rows = [["العنصر", "الوصف", "الملاحظات"], [doc_title, "تم التوليد بنجاح عبر سرعة إنجاز", "مكتمل"]]
                fpath, fname = create_excel_document(doc_title, table_rows)
                generated_file_info = {
                    "type": "xlsx",
                    "filename": fname,
                    "download_url": f"/api/speed_assistant/download/{fname}",
                    "name_display": f"{doc_title}.xlsx",
                    "size_bytes": os.path.getsize(fpath)
                }
            elif request_file_type == "pptx":
                # تقسيم الرد لشرائح
                sections = re.split(r'\n(?=##?\s+)', ai_reply_text)
                slides_data = []
                for s in sections[:10]:
                    s_lines = s.strip().split("\n")
                    if s_lines:
                        s_title = s_lines[0].replace("#", "").strip()
                        s_bullets = [l.replace("-", "").replace("*", "").strip() for l in s_lines[1:] if l.strip()]
                        slides_data.append({"title": s_title[:50], "bullets": s_bullets[:5]})
                if not slides_data:
                    slides_data = [{"title": doc_title, "bullets": ["مقدمة عامة", "النقاط الرئيسية", "الخاتمة والتوصيات"]}]
                fpath, fname = create_pptx_presentation(doc_title, slides_data)
                generated_file_info = {
                    "type": "pptx",
                    "filename": fname,
                    "download_url": f"/api/speed_assistant/download/{fname}",
                    "name_display": f"{doc_title}.pptx",
                    "size_bytes": os.path.getsize(fpath)
                }
            elif request_file_type == "pdf":
                fpath, fname = create_pdf_document(doc_title, ai_reply_text)
                generated_file_info = {
                    "type": "pdf",
                    "filename": fname,
                    "download_url": f"/api/speed_assistant/download/{fname}",
                    "name_display": f"{doc_title}.pdf",
                    "size_bytes": os.path.getsize(fpath)
                }
        except Exception as e_file:
            logger.error(f"خطأ أثناء إنشاء الملف التلقائي: {e_file}")

    # تحديث إحصائيات الاستخدام اليومي لإرجاعها للواجهة
    updated_stats = load_usage_stats()
    daily_req = updated_stats.get("daily_requests", 0)
    daily_limit = updated_stats.get("daily_limit_est", DAILY_CAPACITY_ESTIMATE)

    return jsonify({
        "success": True,
        "reply": ai_reply_text,
        "key_hint": ai_result.get("key_hint"),
        "key_name": ai_result.get("key_name"),
        "active_key_index": ai_result.get("active_key_index"),
        "total_keys": ai_result.get("total_keys"),
        "daily_requests": daily_req,
        "daily_limit_est": daily_limit,
        "usage_percentage": min(100, int((daily_req / max(daily_limit, 1)) * 100)),
        "generated_file": generated_file_info
    })


@speed_assistant_bp.route("/api/speed_assistant/generate_file", methods=["POST"])
def manual_generate_file():
    """توليد ملف يدوي ومباشر بناءً على طلب ومحتوى محدد."""
    data = request.get_json() or {}
    file_type = data.get("file_type", "docx").lower()
    title = data.get("title", "مستند سرعة إنجاز").strip()
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"success": False, "error": "المحتوى فارغ"}), 400

    try:
        if file_type == "docx":
            fpath, fname = create_word_document(title, content)
        elif file_type == "xlsx":
            table_data = data.get("table_data", [])
            fpath, fname = create_excel_document(title, table_data)
        elif file_type == "pptx":
            slides_data = data.get("slides_data", [{"title": title, "bullets": [content]}])
            fpath, fname = create_pptx_presentation(title, slides_data)
        elif file_type == "pdf":
            fpath, fname = create_pdf_document(title, content)
        else:
            fpath, fname = create_plain_text_file(content, file_type)

        return jsonify({
            "success": True,
            "filename": fname,
            "download_url": f"/api/speed_assistant/download/{fname}",
            "size_bytes": os.path.getsize(fpath)
        })
    except Exception as e:
        logger.error(f"فشل توليد الملف: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@speed_assistant_bp.route("/api/speed_assistant/download/<path:filename>", methods=["GET"])
def download_generated_file(filename):
    """تنزيل الملف المولد بروابط مباشرة وصيغ معيارية تفتح في كل أجهزة الجوال والكمبيوتر."""
    # تنظيف اسم الملف لمنع Path Traversal
    safe_name = os.path.basename(filename)
    filepath = os.path.join(GENERATED_FILES_DIR, safe_name)

    if not os.path.exists(filepath):
        return "الملف غير موجود أو انتهت صلاحيته", 404

    # تحديد MIME type بدقة للجوال
    mime_types = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "pdf": "application/pdf",
        "txt": "text/plain; charset=utf-8",
        "html": "text/html; charset=utf-8"
    }
    ext = safe_name.rsplit(".", 1)[-1].lower() if "." in safe_name else "bin"
    mimetype = mime_types.get(ext, "application/octet-stream")

    return send_file(
        filepath,
        mimetype=mimetype,
        as_attachment=True,
        download_name=safe_name
    )
