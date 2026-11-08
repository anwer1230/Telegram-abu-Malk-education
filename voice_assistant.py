"""
مساعد التحكم الصوتي الشامل والذكي لتطبيق Abu Malk - Anwer Telegram Services
يدعم العمل بالذكاء الاصطناعي (Gemini / Groq) وبدونه محلياً عبر محرك تحليل الأنماط العربية
"""

import os
import re
import json
import logging
import urllib.request
import urllib.error

try:
    import requests
except ImportError:
    requests = None

try:
    from flask import request, jsonify, session
except ImportError:
    request = jsonify = session = None

logger = logging.getLogger('voice_assistant')

# خريطة تحويل الأرقام المنطوقة بالعربية إلى أرقام عددية
ARABIC_DIGITS_MAP = {
    'صفر': '0',
    'واحد': '1', 'واحده': '1', 'واحدة': '1',
    'اثنين': '2', 'إثنين': '2', 'اثنان': '2', 'إثنان': '2', 'تنين': '2',
    'ثلاثة': '3', 'تلاتة': '3', 'ثلاث': '3', 'تلات': '3',
    'أربعة': '4', 'اربعة': '4', 'أربع': '4', 'اربع': '4',
    'خمسة': '5', 'خمس': '5',
    'ستة': '6', 'ست': '6',
    'سبعة': '7', 'سبع': '7',
    'ثمانية': '8', 'تمانية': '8', 'ثمان': '8', 'تمن': '8',
    'تسعة': '9', 'تسع': '9',
    'عشرة': '10', 'عشر': '10',
    'عشرين': '20', 'عشرون': '20',
    'ثلاثين': '30', 'ثلاثون': '30', 'تلاتين': '30',
    'أربعين': '40', 'اربعين': '40', 'أربعون': '40', 'اربعون': '40',
    'خمسين': '50', 'خمسون': '50',
    'ستين': '60', 'ستون': '60',
    'سبعين': '70', 'سبعون': '70',
    'ثمانين': '80', 'تمانين': '80', 'ثمانون': '80',
    'تسعين': '90', 'تسعون': '90',
    'مائة': '100', 'مئة': '100', 'ميه': '100',
}

EASTERN_TO_WESTERN = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')

def normalize_arabic_text(text: str) -> str:
    """تنظيف وتوحيد الأحرف العربية لإجراء المطابقة الدقيقة"""
    if not text:
        return ""
    text = text.translate(EASTERN_TO_WESTERN)
    # توحيد الهمزات والألف والتاء المربوطة
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ة\b', 'ه', text)
    text = re.sub(r'ى\b', 'ي', text)
    text = re.sub(r'[ًٌٍَُِّْـ]', '', text)  # إزالة التشكيل والتطويل
    return text.strip()

def extract_spoken_digits(text: str) -> str:
    """استخراج سلسلة الأرقام من النص المنطوق بالعربية سواء كانت كلمات أو أرقاماً"""
    if not text:
        return ""
    working = text.translate(EASTERN_TO_WESTERN)
    # استبدال الكلمات الرقمية بالرموز
    for word, digit in ARABIC_DIGITS_MAP.items():
        working = re.sub(r'\b' + word + r'\b', digit, working)
    # استخراج كل الأرقام المتتالية
    digits = re.findall(r'\d+', working)
    return ''.join(digits)

def extract_time_seconds(text: str) -> int:
    """استخراج الفاصل الزمني بالثواني من النص المنطوق"""
    norm = normalize_arabic_text(text)
    
    # حالات خاصة
    if 'ساعتين' in norm or 'ساعتان' in norm:
        return 7200
    if 'ساعه' in norm:
        return 3600
    if 'نصف ساعه' in norm or 'نص ساعه' in norm:
        return 1800
    if 'دقيقتين' in norm or 'دقيقتان' in norm:
        return 120
    if 'دقيقه' in norm and not re.search(r'\d+', norm):
        return 60

    # البحث عن نمط: رقم + (ثانية / ثواني / دقيقة / دقائق / ساعة / ساعات)
    working = norm
    for word, digit in ARABIC_DIGITS_MAP.items():
        working = re.sub(r'\b' + word + r'\b', digit, working)
    
    # ثواني
    sec_match = re.search(r'(\d+)\s*(ثانيه|ثواني|ثانية)', working)
    if sec_match:
        return int(sec_match.group(1))
    
    # دقائق
    min_match = re.search(r'(\d+)\s*(دقيقه|دقايق|دقائق|دقيقة)', working)
    if min_match:
        return int(min_match.group(1)) * 60
        
    # ساعات
    hr_match = re.search(r'(\d+)\s*(ساعه|ساعات|ساعة)', working)
    if hr_match:
        return int(hr_match.group(1)) * 3600

    # إذا وجد رقماً مفرداً بعد كلمة فاصل أو كل
    num_match = re.search(r'(?:فاصل|كل|وقت)\s*(\d+)', working)
    if num_match:
        val = int(num_match.group(1))
        return val if val >= 10 else val * 60

    return 0

def call_gemini_nlu(transcript: str, active_step: str, context: dict) -> dict:
    """استدعاء نموذج Gemini لفهم النوايا صوتياً إذا توفر المفتاح"""
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not gemini_key:
        return None
        
    prompt = f"""
أنت مساعد صوتي ذكي لمنصة تيليجرام "مركز سرعة إنجاز".
المستخدم نطق الأمر التالي باللغة العربية:
"{transcript}"

السياق الحالي:
- الخطوة الحالية للنظام: {active_step} (مثلاً: awaiting_code أو awaiting_password أو normal)
- الحساب النشط: {context.get('current_user', 'user_1')}

قم بتحليل النص وتحديد النية والبيانات بدقة، وأجب بصيغة JSON حصراً بهذا الهيكل:
{{
  "intent": "login | verify_code | verify_password | set_message | set_interval | set_target | save_settings | start_broadcast | stop_broadcast | switch_account | get_status | unknown",
  "spoken_response": "جملة عربية قصيرة وواضحة ومباشرة ينطقها المساعد للمستخدم لتأكيد الإجراء",
  "data": {{
    "phone": "رقم الهاتف بصيغة دولية إن وجد",
    "code": "كود التحقق إن وجد",
    "password": "كلمة المرور إن وجدت",
    "message": "نص الرسالة إن وجد",
    "interval_seconds": عدد الثواني إن وجد,
    "target_user_id": "معرف الحساب إن وجد مثل user_1 أو user_2",
    "groups": "المجموعات أو المعرفات إن وجدت"
  }}
}}
لا تكتب أي نص خارج كائن JSON.
"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }
        if requests is not None:
            res = requests.post(url, json=payload, headers=headers, timeout=6)
            if res.status_code == 200:
                data = res.json()
                text_resp = data['candidates'][0]['content']['parts'][0]['text']
                return json.loads(text_resp)
        else:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode('utf-8'))
                text_resp = data['candidates'][0]['content']['parts'][0]['text']
                return json.loads(text_resp)
    except Exception as e:
        logger.warning(f"Gemini NLU failed or timed out: {e}")
    return None

def call_groq_nlu(transcript: str, active_step: str, context: dict) -> dict:
    """استدعاء Groq API لفهم النوايا كبديل ثانٍ إذا توفر المفتاح"""
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not groq_key:
        return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
        prompt = f"""حلل أمر صوتي عربي لمنصة تيليجرام: "{transcript}". الخطوة الحالية: {active_step}.
أرجع JSON فقط:
{{
  "intent": "login | verify_code | verify_password | set_message | set_interval | set_target | save_settings | start_broadcast | stop_broadcast | switch_account | get_status | unknown",
  "spoken_response": "رد صوتي باللغة العربية",
  "data": {{ "phone": "", "code": "", "password": "", "message": "", "interval_seconds": 0, "target_user_id": "" }}
}}"""
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        if requests is not None:
            res = requests.post(url, json=payload, headers=headers, timeout=6)
            if res.status_code == 200:
                return json.loads(res.json()['choices'][0]['message']['content'])
        else:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode('utf-8'))
                return json.loads(data['choices'][0]['message']['content'])
    except Exception as e:
        logger.warning(f"Groq NLU failed: {e}")
    return None

def extract_voice_logout_account(norm: str, raw_text: str):
    """استخراج الحساب المستهدف بتسجيل الخروج من النص المنطوق"""
    ordinals = {
        '1': 'user_1', 'واحد': 'user_1', 'اول': 'user_1', 'الاول': 'user_1',
        '2': 'user_2', 'اثنين': 'user_2', 'اثنان': 'user_2', 'تاني': 'user_2', 'الثاني': 'user_2',
        '3': 'user_3', 'ثلاثة': 'user_3', 'ثلاثه': 'user_3', 'تالت': 'user_3', 'الثالث': 'user_3',
        '4': 'user_4', 'اربعة': 'user_4', 'اربعه': 'user_4', 'رابع': 'user_4', 'الرابع': 'user_4',
        '5': 'user_5', 'خمسة': 'user_5', 'خمسه': 'user_5', 'خامس': 'user_5', 'الخامس': 'user_5',
    }
    for k, uid in ordinals.items():
        if f'حساب {k}' in norm or f'الحساب {k}' in norm or f'رقم {k}' in norm or (k in norm and 'حساب' in norm):
            return uid, f'الحساب {k}'
            
    if 'لميس' in norm:
        return 'user_1', 'لميس'
    if 'امل' in norm or 'amal' in raw_text.lower():
        return 'user_1', 'أمل'
        
    m = re.search(r'حساب\s+([^\s]+)', norm)
    if m:
        extracted = m.group(1).strip()
        if extracted not in ['هذا', 'حالي', 'الحالي', 'لي', 'جديد']:
            return 'user_1', extracted

    return 'user_1', 'الحالي'

def parse_local_voice_intent(transcript: str, active_step: str = 'idle', context: dict = None) -> dict:
    """
    محرك التحليل الصوتي المحلي القوي (بدون ذكاء اصطناعي):
    يعتمد على قواعد القواعد اللغوية والمطابقة المرنة للأوامر واللهجات العربية.
    """
    if not transcript:
        return {
            "intent": "unknown",
            "spoken_response": "لم أسمع أي أمر، يرجى التحدث مرة أخرى.",
            "data": {}
        }
    
    context = context or {}
    raw_text = transcript.strip()
    norm = normalize_arabic_text(raw_text)
    digits = extract_spoken_digits(raw_text)

    # أ. أمر إيقاف الإرسال
    if (any(w in norm for w in ['اوقف', 'وقف', 'ايقاف', 'توقف']) and
        any(w in norm for w in ['ارسال', 'عمليه الارسال', 'عملية الارسال', 'نشر', 'بث'])):
        return {
            "intent": "stop_broadcast",
            "spoken_response": "تم إيقاف الإرسال",
            "data": {}
        }

    # ب. أمر تسجيل الخروج من حساب محدد أو الحساب الحالي
    if (any(w in norm for w in ['خروج', 'اخرج']) or 'سجل الخروج' in norm or 'تسجيل الخروج' in norm or 'سجل خروج' in norm or 'تسجيل خروج' in norm) and not ('دخول' in norm and not 'خروج' in norm):
        uid, label = extract_voice_logout_account(norm, raw_text)
        return {
            "intent": "logout_account",
            "spoken_response": f"تم تسجيل الخروج من حساب {label}",
            "data": {
                "target_user_id": uid,
                "account_label": label
            }
        }


    # 1. إذا كان النظام ينتظر كود التحقق وكان هناك أرقام منطوقة
    if active_step == 'awaiting_code' or ('كود' in norm or 'رمز' in norm or 'تحقق' in norm and len(digits) >= 4):
        if len(digits) >= 4:
            return {
                "intent": "verify_code",
                "spoken_response": f"جاري إدخال كود التحقق {digits} والتحقق من الحساب.",
                "data": {"code": digits}
            }
        else:
            return {
                "intent": "verify_code",
                "spoken_response": "يرجى نطق كود التحقق كاملاً المكون من خمسة أو ستة أرقام.",
                "data": {}
            }

    # 2. إذا كان النظام ينتظر كلمة المرور (2FA)
    if active_step == 'awaiting_password' or ('كلمه المرور' in norm or 'كلمه السر' in norm or 'باسورد' in norm or 'تحقق بخطوتين' in norm):
        pwd = raw_text
        for prefix in ['كلمة المرور هي', 'كلمه المرور هي', 'كلمة السر هي', 'كلمه السر هي', 'كلمة المرور', 'كلمه المرور', 'كلمة السر', 'كلمه السر', 'باسورد']:
            if prefix in pwd:
                pwd = pwd.split(prefix, 1)[1].strip()
                break
        pwd = pwd.strip(': -_')
        return {
            "intent": "verify_password",
            "spoken_response": "جاري التحقق من كلمة مرور التحقق بخطوتين.",
            "data": {"password": pwd or raw_text}
        }

    # 3. تسجيل الدخول بالرقم أو بالحساب
    if any(k in norm for k in ['سجل الدخول', 'تسجيل الدخول', 'تسجيل دخول', 'سجل دخول', 'ادخل بالرقم', 'ادخل بالحساب', 'دخول برقم', 'دخول بحساب']):
        # فحص إذا كان المطلوب تبديل إلى حساب باسم معين
        if 'حساب' in norm or 'مستخدم' in norm:
            for i in range(1, 6):
                if str(i) in norm or ARABIC_DIGITS_MAP.get(['واحد', 'اثنين', 'ثلاثة', 'اربعة', 'خمسة'][i-1], '') == str(i):
                    target_uid = f"user_{i}"
                    return {
                        "intent": "switch_account",
                        "spoken_response": f"جاري التبديل إلى الحساب رقم {i}.",
                        "data": {"target_user_id": target_uid}
                    }
        # استخراج رقم الهاتف
        if digits and len(digits) >= 8:
            phone = digits
            if not phone.startswith('+') and not phone.startswith('00'):
                # إذا لم يكن به رمز دولي ويبدأ بـ 7 أو 967
                if phone.startswith('967'):
                    phone = '+' + phone
                elif len(phone) == 9 and phone.startswith('7'):
                    phone = '+967' + phone
                elif phone.startswith('0'):
                    phone = '+' + phone.lstrip('0')
                else:
                    phone = '+' + phone
            return {
                "intent": "login",
                "spoken_response": f"جاري طلب كود التحقق لرقم الهاتف {phone}.",
                "data": {"phone": phone}
            }
        else:
            return {
                "intent": "login",
                "spoken_response": "يرجى ذكر رقم الهاتف بوضوح مع رمز الدولة للبدء.",
                "data": {}
            }

    # 4. ضبط نص الرسالة
    if any(k in norm for k in ['نص الرساله', 'اكتب رساله', 'اضبط الرساله', 'غير الرساله', 'رساله جديده', 'رساله الارسال']):
        msg = raw_text
        for prefix in ['نص الرسالة هو', 'نص الرساله هو', 'نص الرسالة:', 'نص الرساله:', 'نص الرسالة', 'نص الرساله', 'اكتب رسالة', 'اكتب رساله', 'اضبط الرسالة', 'اضبط الرساله']:
            if prefix in msg:
                msg = msg.split(prefix, 1)[1].strip()
                break
        msg = msg.strip(': -_')
        return {
            "intent": "set_message",
            "spoken_response": f"تم اعتماد نص الرسالة الجديد بنجاح.",
            "data": {"message": msg}
        }

    # 5. ضبط الفاصل الزمني أو الوقت
    if any(k in norm for k in ['فاصل زمني', 'الفاصل الزمني', 'الوقت المحدد', 'كل دقيقه', 'كل ثانيه', 'كل ساعه', 'وقت الارسال', 'فاصل الارسال', 'فاصل', 'فترة', 'دقائق', 'ثواني']) or (extract_time_seconds(raw_text) > 0 and any(w in norm for w in ['كل', 'ارسال', 'وقت'])):
        seconds = extract_time_seconds(raw_text)
        if seconds > 0:
            return {
                "intent": "set_interval",
                "spoken_response": f"تم ضبط الفاصل الزمني إلى {seconds} ثانية.",
                "data": {"interval_seconds": seconds}
            }
        else:
            return {
                "intent": "set_interval",
                "spoken_response": "يرجى تحديد الفاصل الزمني بالثواني أو الدقائق.",
                "data": {}
            }

    # 6. حفظ الإعدادات
    if any(k in norm for k in ['احفظ الاعدادات', 'حفظ الاعدادات', 'احفظ التعديلات', 'حفظ التعديلات', 'احفظ كل شيء', 'احفظ']):
        return {
            "intent": "save_settings",
            "spoken_response": "جاري حفظ كافة الإعدادات والبيانات بنجاح.",
            "data": {}
        }

    # 6.5. استئناف أو إلغاء الإرسال
    if any(k in norm for k in ['استئناف', 'استأنف', 'واصل الارسال', 'تابع الارسال', 'كمل الارسال']):
        return {
            "intent": "resume_broadcast",
            "spoken_response": "تم استئناف مهمة الإرسال الفوري بنجاح.",
            "data": {}
        }

    if any(k in norm for k in ['الغاء', 'انهاء']) and any(k in norm for k in ['ارسال', 'نشر', 'بث', 'مهمه']):
        return {
            "intent": "cancel_broadcast",
            "spoken_response": "تم إلغاء مهمة الإرسال نهائياً بنجاح.",
            "data": {}
        }

    # 6.6. تبديل ميزات النظام والجدولة الدائرية
    if any(k in norm for k in ['جدوله', 'دائريه', 'دائري']):
        en = not any(k in norm for k in ['ايقاف', 'تعطيل', 'عطل', 'اوقف', 'وقف'])
        return {
            "intent": "toggle_circular_schedule",
            "spoken_response": "تم تفعيل نظام الجدولة الدائرية الآلية بنجاح." if en else "تم إيقاف الجدولة الدائرية بنجاح.",
            "data": {"enable": en}
        }

    if any(k in norm for k in ['تنبيهاتي', 'التنبيهات']):
        en = not any(k in norm for k in ['ايقاف', 'تعطيل', 'عطل', 'اوقف', 'وقف'])
        return {
            "intent": "toggle_alerts",
            "spoken_response": "تم تفعيل نظام تنبيهاتي الذكية بنجاح." if en else "تم إيقاف نظام تنبيهاتي الذكية بنجاح.",
            "data": {"enable": en}
        }

    if any(k in norm for k in ['رادار']):
        en = not any(k in norm for k in ['ايقاف', 'تعطيل', 'عطل', 'اوقف', 'وقف'])
        return {
            "intent": "toggle_link_radar",
            "spoken_response": "تم تفعيل رادار الروابط بنجاح." if en else "تم إيقاف رادار الروابط بنجاح.",
            "data": {"enable": en}
        }

    if any(k in norm for k in ['انضمام']):
        en = not any(k in norm for k in ['ايقاف', 'تعطيل', 'عطل', 'اوقف', 'وقف'])
        return {
            "intent": "toggle_auto_join",
            "spoken_response": "تم تفعيل الانضمام التلقائي للمجموعات بنجاح." if en else "تم إيقاف الانضمام التلقائي للمجموعات بنجاح.",
            "data": {"enable": en}
        }

    if any(k in norm for k in ['الردود العامه', 'محرك الردود']):
        en = not any(k in norm for k in ['ايقاف', 'تعطيل', 'عطل', 'اوقف', 'وقف'])
        return {
            "intent": "toggle_auto_reply",
            "spoken_response": "تم تفعيل محرك الردود التلقائية العامة بنجاح." if en else "تم إيقاف محرك الردود التلقائية العامة بنجاح.",
            "data": {"enable": en}
        }

    if any(k in norm for k in ['اقتباس', 'اعاده توجيه']):
        en = not any(k in norm for k in ['ايقاف', 'تعطيل', 'عطل', 'اوقف', 'وقف', 'بدون'])
        return {
            "intent": "toggle_forward_quote",
            "spoken_response": "تم تفعيل وضع الاقتباس الرسمي بنجاح." if en else "تم إيقاف وضع الاقتباس الرسمي بنجاح.",
            "data": {"enable": en}
        }

    # 7. بدء الإرسال الفعلي
    if any(k in norm for k in ['ابدا الارسال', 'ابدء الارسال', 'شغل الارسال', 'ارسال فوري', 'ارسل الان', 'ابدا النشر', 'شغل النشر', 'ابدا الان']):
        return {
            "intent": "start_broadcast",
            "spoken_response": "تم إصدار أمر البدء، جاري تشغيل الإرسال الفعلي الآن.",
            "data": {}
        }

    # 8. بدء المراقبة والجدولة
    if any(k in norm for k in ['شغل المراقبه', 'ابدا المراقبه', 'تفعيل المراقبه', 'جدوله الارسال', 'ارسال مجدول']):
        return {
            "intent": "start_monitoring",
            "spoken_response": "تم تفعيل محرك المراقبة بنجاح.",
            "data": {}
        }

    # 9. إيقاف الإرسال أو المراقبة
    if any(k in norm for k in ['اوقف الارسال', 'وقف الارسال', 'ايقاف الارسال', 'اوقف النشر', 'وقف النشر', 'اوقف المراقبه', 'وقف المراقبه', 'ايقاف مؤقت', 'توقف']):
        return {
            "intent": "stop_broadcast",
            "spoken_response": "تم إيقاف الإرسال بنجاح.",
            "data": {}
        }

    # 10. الاستعلام عن الحالة والإحصائيات
    if any(k in norm for k in ['ما هي الحاله', 'حاله الحساب', 'كم ارسلت', 'فحص الحساب', 'الاحصائيات', 'هل الحساب شغال', 'حاله الاتصال']):
        return {
            "intent": "get_status",
            "spoken_response": "جاري استرجاع الحالة اللحظية للحساب والإحصائيات.",
            "data": {}
        }

    # 11. تبديل الحساب
    if any(k in norm for k in ['بدل الحساب', 'تبديل الحساب', 'الحساب الثاني', 'الحساب الاول', 'الحساب الثالث', 'المستخدم']):
        for i in range(1, 6):
            if str(i) in norm or ARABIC_DIGITS_MAP.get(['واحد', 'اثنين', 'ثلاثة', 'اربعة', 'خمسة'][i-1], '') == str(i):
                return {
                    "intent": "switch_account",
                    "spoken_response": f"جاري التبديل إلى الحساب رقم {i}.",
                    "data": {"target_user_id": f"user_{i}"}
                }

    # إذا لم يتم التعرف بدقة
    return {
        "intent": "unknown",
        "spoken_response": f"سمعتك تقول: {raw_text}. يمكنك إعطائي أوامر مثل: سجل الدخول بالرقم، أو احفظ الإعدادات، أو ابدأ الإرسال.",
        "data": {"raw_transcript": raw_text}
    }


def register_voice_assistant_routes(app, telegram_manager, USERS, PREDEFINED_USERS, load_settings, save_settings):
    """تسجيل مسارات API الخاصة بالتحكم الصوتي في خادم Flask"""

    @app.route("/api/voice_command", methods=["POST"])
    def api_voice_command():
        req_data = request.get_json() or {}
        transcript = (req_data.get("transcript") or "").strip()
        active_step = req_data.get("active_step") or "idle"
        user_id = req_data.get("user_id") or session.get("user_id") or "user_1"
        execute = req_data.get("execute", True)

        if not transcript:
            return jsonify({
                "success": False,
                "spoken_response": "يرجى التحدث وذكر الأمر الصوتي.",
                "intent": "none"
            })

        # محاولة التحليل بالذكاء الاصطناعي (Gemini أولاً ثم Groq)، ثم الرجوع للمحرك المحلي
        context = {"current_user": user_id}
        parsed = None
        
        # نستخدم الذكاء الاصطناعي إذا لم تكن الحالة محددة بالأرقام البسيطة
        if active_step not in ['awaiting_code', 'awaiting_password']:
            parsed = call_gemini_nlu(transcript, active_step, context)
            if not parsed:
                parsed = call_groq_nlu(transcript, active_step, context)

        # إذا لم يتوفر الذكاء الاصطناعي أو فشل أو للأوامر المباشرة: المحرك المحلي
        if not parsed or parsed.get("intent") == "unknown":
            parsed = parse_local_voice_intent(transcript, active_step, context)

        intent = parsed.get("intent")
        spoken_response = parsed.get("spoken_response", "تم استلام الأمر.")
        intent_data = parsed.get("data", {})
        execution_result = {}

        # التنفيذ الفعلي للأمر إذا طلب ذلك (Execute = True)
        if execute:
            try:
                # أ. تسجيل الدخول برقم الهاتف
                if intent == "login" and intent_data.get("phone"):
                    phone = intent_data["phone"]
                    # استدعاء دالة طلب الكود من التليجرام
                    st = load_settings(user_id) or {}
                    st['phone'] = phone
                    save_settings(user_id, st)
                    
                    # بدء تسجيل الدخول
                    login_res = telegram_manager.send_code(user_id, phone)
                    execution_result = login_res
                    if login_res.get("success"):
                        spoken_response = f"تم إرسال كود التحقق بنجاح إلى هاتفك {phone}. تفضل بنطق الكود الآن."
                        execution_result["next_step"] = "awaiting_code"
                    else:
                        spoken_response = f"تعذر إرسال الكود: {login_res.get('message', 'خطأ في الاتصال')}"

                # ب. التحقق من كود التحقق
                elif intent == "verify_code" and intent_data.get("code"):
                    code = intent_data["code"]
                    verify_res = telegram_manager.verify_code(user_id, code)
                    execution_result = verify_res
                    if verify_res.get("status") == "success":
                        name = verify_res.get("account_name", "")
                        spoken_response = f"تم التحقق بنجاح! مرحباً بك {name}، الحساب الآن نشط ومتصل."
                        execution_result["next_step"] = "idle"
                    elif verify_res.get("status") == "password_required":
                        spoken_response = "الحساب محمي بكلمة مرور التحقق بخطوتين. تفضل بنطق كلمة المرور الآن."
                        execution_result["next_step"] = "awaiting_password"
                    else:
                        spoken_response = f"كود التحقق غير صحيح: {verify_res.get('message', 'حاول مرة أخرى')}"

                # ج. التحقق من كلمة المرور 2FA
                elif intent == "verify_password" and intent_data.get("password"):
                    pwd = intent_data["password"]
                    pwd_res = telegram_manager.verify_password(user_id, pwd)
                    execution_result = pwd_res
                    if pwd_res.get("status") == "success":
                        name = pwd_res.get("account_name", "")
                        spoken_response = f"تم قبول كلمة المرور وتسجيل الدخول بنجاح! مرحباً {name}."
                        execution_result["next_step"] = "idle"
                    else:
                        spoken_response = f"كلمة المرور غير صحيحة: {pwd_res.get('message', 'يرجى الإعادة')}"

                # د. حفظ الإعدادات
                elif intent == "save_settings":
                    st = load_settings(user_id) or {}
                    save_settings(user_id, st)
                    spoken_response = "تم حفظ جميع الإعدادات والخيارات بنجاح."

                # هـ. ضبط نص الرسالة
                elif intent == "set_message" and intent_data.get("message"):
                    st = load_settings(user_id) or {}
                    st['message'] = intent_data['message']
                    save_settings(user_id, st)
                    spoken_response = "تم تحديث نص رسالة الإرسال وحفظها بنجاح."

                # و. ضبط الفاصل الزمني
                elif intent == "set_interval" and intent_data.get("interval_seconds"):
                    st = load_settings(user_id) or {}
                    st['interval_seconds'] = int(intent_data['interval_seconds'])
                    save_settings(user_id, st)
                    spoken_response = f"تم ضبط الفاصل الزمني إلى {intent_data['interval_seconds']} ثانية بنجاح."

                # ز. بدء الإرسال الفعلي
                elif intent == "start_broadcast":
                    is_auth = False
                    if user_id in USERS and USERS[user_id].get('authenticated'):
                        is_auth = True
                    execution_result["authenticated"] = is_auth
                    if is_auth:
                        spoken_response = "تم إطلاق أمر بدء الإرسال الفعلي لجميع المجموعات المحددة."
                        execution_result["action"] = "trigger_send_now"
                    else:
                        spoken_response = "يجب تسجيل الدخول أولاً قبل بدء الإرسال. قل: سجل الدخول بالرقم..."

                # ح. بدء المراقبة
                elif intent == "start_monitoring":
                    spoken_response = "تم تفعيل محرك المراقبة والإرسال المجدول."
                    execution_result["action"] = "trigger_start_monitoring"

                # ط. إيقاف الإرسال الفوري
                elif intent == "stop_broadcast":
                    try:
                        import app as _main_app
                        if hasattr(_main_app, 'BATCH_CANCEL_EVENTS') and user_id in _main_app.BATCH_CANCEL_EVENTS:
                            _main_app.BATCH_CANCEL_EVENTS[user_id].set()
                        if hasattr(_main_app, 'BATCH_SENDER_STATES') and user_id in _main_app.BATCH_SENDER_STATES:
                            _main_app.BATCH_SENDER_STATES[user_id]['status'] = 'paused'
                    except Exception as _p_err:
                        logger.warning(f"Error pausing broadcast in voice: {_p_err}")
                    spoken_response = "تم إيقاف الإرسال مؤقتاً بنجاح."
                    execution_result["action"] = "trigger_stop_broadcast"

                # ط-1. استئناف الإرسال
                elif intent == "resume_broadcast":
                    spoken_response = "تم استئناف الإرسال الفوري بنجاح، وجارٍ إرسال المجموعات المتبقية."
                    execution_result["action"] = "trigger_resume_broadcast"

                # ط-1.1. إلغاء الإرسال
                elif intent == "cancel_broadcast":
                    spoken_response = "تم إلغاء مهمة الإرسال نهائياً بنجاح."
                    execution_result["action"] = "trigger_cancel_broadcast"

                # ط-1.2. تبديل الجدولة الدائرية
                elif intent == "toggle_circular_schedule":
                    en = intent_data.get("enable", True)
                    st = load_settings(user_id) or {}
                    st['send_type'] = 'scheduled' if en else 'instant'
                    save_settings(user_id, st)
                    spoken_response = "تم تفعيل نظام الجدولة الدائرية الآلية بنجاح." if en else "تم إيقاف الجدولة الدائرية بنجاح."
                    execution_result["action"] = "toggle_circular_schedule"
                    execution_result["enabled"] = en

                # ط-1.3. تبديل التنبيهات
                elif intent == "toggle_alerts":
                    en = intent_data.get("enable", True)
                    st = load_settings(user_id) or {}
                    st['my_alerts_enabled'] = en
                    save_settings(user_id, st)
                    spoken_response = "تم تشغيل وتفعيل نظام تنبيهاتي بنجاح." if en else "تم إيقاف نظام تنبيهاتي بنجاح."
                    execution_result["action"] = "toggle_alerts"
                    execution_result["enabled"] = en

                # ط-1.4. تبديل رادار الروابط
                elif intent == "toggle_link_radar":
                    en = intent_data.get("enable", True)
                    spoken_response = "تم تشغيل وتفعيل رادار الروابط بنجاح." if en else "تم إيقاف رادار الروابط بنجاح."
                    execution_result["action"] = "toggle_link_radar"
                    execution_result["enabled"] = en

                # ط-1.5. تبديل الانضمام التلقائي
                elif intent == "toggle_auto_join":
                    en = intent_data.get("enable", True)
                    spoken_response = "تم تفعيل الانضمام التلقائي للمجموعات بنجاح." if en else "تم إيقاف الانضمام التلقائي للمجموعات بنجاح."
                    execution_result["action"] = "toggle_auto_join"
                    execution_result["enabled"] = en

                # ط-1.6. تبديل الردود العامة
                elif intent == "toggle_auto_reply":
                    en = intent_data.get("enable", True)
                    spoken_response = "تم تفعيل محرك الردود التلقائية العامة بنجاح." if en else "تم إيقاف محرك الردود التلقائية العامة بنجاح."
                    execution_result["action"] = "toggle_auto_reply"
                    execution_result["enabled"] = en

                # ط-1.7. تبديل الاقتباس
                elif intent == "toggle_forward_quote":
                    en = intent_data.get("enable", True)
                    st = load_settings(user_id) or {}
                    st['keyword_auto_reply_forward'] = en
                    save_settings(user_id, st)
                    spoken_response = "تم تفعيل وضع الاقتباس الرسمي بنجاح." if en else "تم إيقاف وضع الاقتباس الرسمي بنجاح."
                    execution_result["action"] = "toggle_forward_quote"
                    execution_result["enabled"] = en

                # ط-2. تسجيل الخروج من حساب
                elif intent == "logout_account":
                    target_uid = intent_data.get("target_user_id") or user_id
                    label = intent_data.get("account_label") or target_uid
                    try:
                        with USERS_LOCK:
                            if target_uid in USERS:
                                cm = USERS[target_uid].get('client_manager')
                                if cm:
                                    try:
                                        if hasattr(cm, 'client') and cm.client:
                                            cm.client.disconnect()
                                        if hasattr(cm, 'stop'):
                                            cm.stop()
                                    except Exception:
                                        pass
                                del USERS[target_uid]
                        session_file = os.path.join(SESSIONS_DIR, f"{target_uid}_session.session")
                        if os.path.exists(session_file):
                            try: os.remove(session_file)
                            except Exception: pass
                        st = load_settings(target_uid) or {}
                        st['authenticated'] = False
                        st['connected'] = False
                        save_settings(target_uid, st)
                    except Exception as _lo_err:
                        logger.warning(f"Error logging out in voice: {_lo_err}")
                    spoken_response = f"تم تسجيل الخروج من حساب {label}."
                    execution_result["action"] = "logged_out"
                    execution_result["target_user_id"] = target_uid

                # ي. الاستعلام عن الحالة
                elif intent == "get_status":
                    u_info = USERS.get(user_id, {})
                    is_auth = u_info.get('authenticated', False)
                    name = u_info.get('account_name') or 'غير متصل'
                    phone = u_info.get('account_phone') or 'لا يوجد'
                    stats = u_info.get('stats', {})
                    sent_cnt = stats.get('messages_sent', 0)
                    if is_auth:
                        spoken_response = f"الحساب {name} متصل وجاهز. تم إرسال {sent_cnt} رسالة."
                    else:
                        spoken_response = "الحساب الحالي غير متصل. يمكنك طلب تسجيل الدخول بالصوت."
                    execution_result["status"] = {
                        "authenticated": is_auth,
                        "name": name,
                        "phone": phone,
                        "sent_count": sent_cnt
                    }

                # ك. تبديل الحساب
                elif intent == "switch_account" and intent_data.get("target_user_id"):
                    target_uid = intent_data["target_user_id"]
                    session['user_id'] = target_uid
                    session.permanent = True
                    spoken_response = f"تم التبديل إلى الحساب {target_uid}."
                    execution_result["action"] = "switch_account"
                    execution_result["target_user_id"] = target_uid

            except Exception as ex:
                logger.error(f"Error executing voice intent {intent}: {ex}")
        # تصنيف الأوامر الحساسة وتحديد خصائص الإضاءة الجانبية والوميض
        sensitive_configs = {
            "start_broadcast": {
                "title": "بدء النشر والإرسال الفعلي في المجموعات",
                "theme": "emerald",
                "color": "rgba(16, 185, 129, 0.85)",
                "border": "#10b981",
                "icon": "fa-paper-plane"
            },
            "stop_broadcast": {
                "title": "إيقاف طوارئ فوري لعمليات الإرسال والمراقبة",
                "theme": "crimson",
                "color": "rgba(239, 68, 68, 0.9)",
                "border": "#ef4444",
                "icon": "fa-circle-stop"
            },
            "start_monitoring": {
                "title": "تشغيل المراقبة التلقائية الحية للرسائل",
                "theme": "cyan",
                "color": "rgba(6, 182, 212, 0.85)",
                "border": "#06b6d4",
                "icon": "fa-satellite-dish"
            },
            "login": {
                "title": "طلب تسجيل دخول برقم هاتف جديد",
                "theme": "amber",
                "color": "rgba(245, 158, 11, 0.85)",
                "border": "#f59e0b",
                "icon": "fa-user-lock"
            },
            "verify_code": {
                "title": "التحقق الأمني بكود الدخول السري",
                "theme": "purple",
                "color": "rgba(168, 85, 247, 0.9)",
                "border": "#a855f7",
                "icon": "fa-shield-halved"
            },
            "verify_password": {
                "title": "التحقق بكلمة المرور الثنائية 2FA",
                "theme": "pink",
                "color": "rgba(236, 72, 153, 0.9)",
                "border": "#ec4899",
                "icon": "fa-key"
            },
            "save_settings": {
                "title": "حفظ واعتماد تعديلات النظام",
                "theme": "blue",
                "color": "rgba(59, 130, 246, 0.85)",
                "border": "#3b82f6",
                "icon": "fa-floppy-disk"
            },
            "switch_account": {
                "title": "تبديل الحساب النشط",
                "theme": "indigo",
                "color": "rgba(99, 102, 241, 0.85)",
                "border": "#6366f1",
                "icon": "fa-users-cog"
            }
        }
        sensitive_meta = sensitive_configs.get(intent)
        is_sensitive = sensitive_meta is not None

        return jsonify({
            "success": True,
            "intent": intent,
            "spoken_response": spoken_response,
            "data": intent_data,
            "execution": execution_result,
            "is_sensitive": is_sensitive,
            "sensitive_meta": sensitive_meta
        })

    @app.route("/api/voice_help", methods=["GET"])
    def api_voice_help():
        return jsonify({
            "success": True,
            "commands": [
                {"text": "سجل الدخول بالرقم +967xxxxxxxxx", "action": "تسجيل دخول وإرسال الرمز"},
                {"text": "الكود هو 12345", "action": "إدخال كود التحقق المرسل وتأكيد الدخول"},
                {"text": "كلمة المرور هي xxxxxx", "action": "إدخال كلمة مرور التحقق بخطوتين (2FA)"},
                {"text": "اضبط الرسالة: نرحب بكم...", "action": "تغيير نص رسالة الإرسال"},
                {"text": "اجعل الفاصل 30 ثانية / 5 دقائق", "action": "تحديد الفاصل الزمني بين الرسائل"},
                {"text": "احفظ الإعدادات", "action": "حفظ جميع البيانات والتغييرات"},
                {"text": "ابدأ الإرسال الآن", "action": "بدء النشر الفوري في المجموعات"},
                {"text": "شغل المراقبة والجدولة", "action": "بدء المراقبة التلقائية للرسائل"},
                {"text": "أوقف الإرسال", "action": "إيقاف الإرسال والمراقبة الحالية"},
                {"text": "ما هي حالة الحساب؟", "action": "الاستعلام الصوتي عن الإحصائيات والاتصال"},
                {"text": "بدل إلى الحساب 2", "action": "التبديل بين الحسابات المتعددة"}
            ]
        })
