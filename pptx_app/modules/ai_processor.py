# -*- coding: utf-8 -*-
"""معالج الذكاء الاصطناعي للعروض التقديمية (يستخدم مفاتيح Gemini الدائمة + Groq احتياطي)."""

import json
import os
import re
from typing import List, Dict, Any, Optional

from pptx_app.modules.templates import CANVA_TEMPLATES

GROQ_MODEL = "llama-3.3-70b-versatile"


def _call_gemini(prompt: str, system_instruction: str = "", model: str = "gemini-3.1-flash-lite-preview") -> Optional[str]:
    """استدعاء Gemini سريع مع تدوير تلقائي على المفاتيح الدائمة وسقف زمني مضمون."""
    import time
    import requests
    try:
        import config as _cfg
        keys = _cfg.get_all_gemini_keys()
    except Exception:
        keys = []
    if not keys:
        return None

    models = [model, "gemini-flash-lite-latest", "gemini-3-flash-preview"]
    ordered_models = []
    for m in models:
        if m and m not in ordered_models:
            ordered_models.append(m)

    payload: Dict[str, Any] = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.25, "maxOutputTokens": 4096},
    }
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    deadline = time.time() + 18.0
    for key in keys[:5]:
        if time.time() >= deadline:
            break
        for curr_model in ordered_models:
            rem = deadline - time.time()
            if rem <= 1.0:
                break
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{curr_model}:generateContent"
                resp = requests.post(
                    url,
                    headers={"Content-Type": "application/json", "X-goog-api-key": key},
                    json=payload,
                    timeout=min(10.0, rem),
                )
                if resp.status_code == 200:
                    data = resp.json()
                    cands = data.get("candidates") or []
                    if cands and cands[0].get("content", {}).get("parts"):
                        txt = cands[0]["content"]["parts"][0].get("text", "")
                        if txt:
                            return str(txt).strip()
                elif resp.status_code in (429, 403, 500, 502, 503, 504):
                    break  # جرّب المفتاح التالي فوراً
            except Exception:
                continue
    return None


class AIProcessor:
    def __init__(self):
        self.groq_available = False
        self.gemini_available = False
        self.client = None
        self.gemini_keys_count = 0
        self._init_providers()

    def _init_providers(self):
        try:
            import config as _cfg
            keys = _cfg.get_all_gemini_keys()
            self.gemini_keys_count = len(keys)
            self.gemini_available = len(keys) > 0
        except Exception:
            self.gemini_available = False

        try:
            from groq import Groq
            api_key = os.environ.get("GROQ_API_KEY", "").strip()
            if api_key:
                self.client = Groq(api_key=api_key)
                self.groq_available = True
        except Exception:
            self.groq_available = False

    @property
    def is_ai_available(self) -> bool:
        return self.gemini_available or self.groq_available

    def get_provider_label(self) -> str:
        if self.gemini_available:
            return f"Gemini AI ({self.gemini_keys_count} مفاتيح نشطة)"
        if self.groq_available:
            return "Groq AI (Llama 3.3)"
        return "معالجة محلية ذكية"

    def text_to_presentation_structure(
        self,
        text: str,
        num_slides: int = 6,
        presentation_type: str = "general",
        title_override: str = "",
        include_tables: bool = False,
        include_charts: bool = False,
        extracted_tables: Optional[List] = None,
    ) -> List[Dict[str, Any]]:
        slides = None
        if self.gemini_available:
            slides = self._process_with_gemini(
                text, num_slides, presentation_type, include_tables, include_charts
            )
        if not slides and self.groq_available:
            slides = self._process_with_groq(
                text, num_slides, presentation_type, include_tables, include_charts
            )
        if not slides:
            slides = self._process_locally(
                text, num_slides, presentation_type, extracted_tables or []
            )
        if title_override and slides:
            slides[0]["title"] = title_override
        return slides

    def _build_generation_prompt(
        self, text: str, num_slides: int, ptype: str, include_tables: bool, include_charts: bool
    ) -> str:
        type_labels = {
            "general": "عام", "business": "تجاري",
            "educational": "تعليمي", "sales": "تسويقي",
        }
        label = type_labels.get(ptype, "عام")
        extras = ""
        if include_tables:
            extras += '\n- أضف شريحة جدول واحدة على الأقل بنوع "table" مع مفتاح "table_data" (مصفوفة من صفوف نصية)'
        if include_charts:
            extras += '\n- أضف شريحة رسم بياني بنوع "chart" مع مفاتيح "chart_type" (bar/pie/line) و"chart_labels" و"chart_values" (أرقام)'

        return f"""حلّل النص التالي وأنشئ هيكل عرض تقديمي {label} احترافي مكوّن من {num_slides} شرائح بالضبط.{extras}

النص:
{text[:5000]}

القواعد:
- الشريحة الأولى: نوع "title" مع عنوان رئيسي وعنوان فرعي
- الشريحة الأخيرة: نوع "conclusion" مع 3-4 نقاط خلاصة وتوصيات
- الشرائح الوسطى: نوع "bullets" مع 3-5 نقاط واضحة ومكثفة لكل شريحة
- كل المحتوى باللغة العربية الفصحى السليمة
- أرجع مصفوفة JSON صالحة فقط بدون أي شرح خارجها:
[
  {{
    "title": "عنوان الشريحة",
    "subtitle": "عنوان فرعي",
    "bullets": ["نقطة 1", "نقطة 2", "نقطة 3"],
    "slide_type": "title|bullets|table|chart|conclusion",
    "table_data": [["العمود 1", "العمود 2"], ["قيمة 1", "قيمة 2"]],
    "chart_type": "bar",
    "chart_labels": ["عنصر 1", "عنصر 2"],
    "chart_values": [10, 20],
    "chart_title": "عنوان الرسم"
  }}
]"""

    def _process_with_gemini(
        self, text: str, num_slides: int, ptype: str, include_tables: bool, include_charts: bool
    ) -> Optional[List[Dict[str, Any]]]:
        prompt = self._build_generation_prompt(text, num_slides, ptype, include_tables, include_charts)
        content = _call_gemini(
            prompt,
            system_instruction="أنت خبير عروض تقديمية احترافية بالعربية. تُرجع مصفوفة JSON صالحة فقط.",
        )
        if not content:
            return None
        try:
            match = re.search(r"\[.*\]", content, re.DOTALL)
            if match:
                slides = json.loads(match.group())
                if isinstance(slides, list) and slides:
                    return slides
        except Exception as e:
            print(f"[Gemini parse slides error] {e}")
        return None

    def _process_with_groq(
        self, text: str, num_slides: int, ptype: str, include_tables: bool, include_charts: bool
    ) -> Optional[List[Dict[str, Any]]]:
        try:
            prompt = self._build_generation_prompt(text, num_slides, ptype, include_tables, include_charts)
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "أنت خبير محترف في إنشاء العروض التقديمية باللغة العربية. تُنتج دائماً JSON صحيحاً وكاملاً فقط."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=3000,
                temperature=0.65,
            )
            content = response.choices[0].message.content.strip()
            match = re.search(r"\[.*\]", content, re.DOTALL)
            if match:
                slides = json.loads(match.group())
                if isinstance(slides, list) and slides:
                    return slides
        except Exception as e:
            print(f"[Groq request error] {e}")
        return None

    def analyze_pptx_presentation(
        self,
        extracted: Dict[str, Any],
        canva_templates: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """تحليل ملف PowerPoint (.pptx) حالي وتقديم اقتراحات تحسين المحتوى والتصميم بقوالب كانفا."""
        slides = extracted.get("slides") or []
        templates_list = canva_templates or CANVA_TEMPLATES
        tpl_summary = "\n".join(
            f"- {t['id']}: {t['name']} ({t.get('category','')}) — {t.get('description','')}"
            for t in templates_list
        )
        slides_summary = "\n".join(
            f"شريحة {s.get('slide_number', i+1)} ({s.get('slide_type','bullets')}): العنوان: {s.get('title','')} | النقاط: {' ؛ '.join(s.get('bullets',[])[:6])}"
            for i, s in enumerate(slides[:20])
        )

        prompt = f"""أنت مستشار خبير في تصميم وتحرير العروض التقديمية الاحترافية (PowerPoint & Canva).
قم بتحليل العرض التقديمي التالي المكوّن من {len(slides)} شريحة (إجمالي {len((extracted.get('full_text') or '').split())} كلمة، خطوط: {', '.join(extracted.get('fonts_used') or ['غير محدد'])}):

محتوى الشرائح الحالية:
{slides_summary[:6500]}

قوالب كانفا المتاحة للتحديث:
{tpl_summary}

المطلوب إرجاع كائن JSON صالح فقط بهذه البنية:
{{
  "overall_summary": "تقييم شامل واضح لمستوى العرض الحالي وملاءمته للجمهور",
  "strengths": ["نقطة قوة 1", "نقطة قوة 2"],
  "weaknesses": ["فرصة تحسين 1", "فرصة تحسين 2", "فرصة تحسين 3"],
  "recommended_templates": [
    {{"id": "معرف القالب من القائمة أعلاه", "reason": "سبب ملاءمة هذا القالب للعرض"}}
  ],
  "slide_suggestions": [
    {{
      "slide_number": 1,
      "current_title": "العنوان الحالي",
      "improved_title": "عنوان محسّن أقوى وأوضح",
      "improved_bullets": ["نقطة محسّنة 1", "نقطة محسّنة 2", "نقطة محسّنة 3"],
      "content_advice": "توصية عملية لتحسين الصياغة والإيجاز",
      "visual_advice": "اقتراح للتنسيق البصري أو التخطيط"
    }}
  ]
}}"""

        parsed = None
        raw = None
        if self.gemini_available:
            raw = _call_gemini(
                prompt,
                system_instruction="أنت محلل عروض تقديمية خبير. أرجع كائن JSON صالحاً فقط باللغة العربية.",
            )
        if not raw and self.groq_available:
            try:
                resp = self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "أرجع JSON صالحاً فقط باللغة العربية."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=3500,
                    temperature=0.4,
                )
                raw = resp.choices[0].message.content.strip()
            except Exception:
                raw = None

        if raw:
            try:
                match = re.search(r"\{.*\}", raw, re.DOTALL)
                if match:
                    parsed = json.loads(match.group())
            except Exception:
                parsed = None

        if not isinstance(parsed, dict) or not parsed.get("slide_suggestions"):
            parsed = self._analyze_locally(extracted, templates_list)

        # تأكيد وجود المعرفات الصالحة لقوالب كانفا
        valid_ids = {t["id"]: t for t in templates_list}
        recs = []
        for rec in (parsed.get("recommended_templates") or []):
            tid = rec.get("id")
            if tid in valid_ids:
                t = valid_ids[tid]
                recs.append({
                    "id": tid,
                    "name": t["name"],
                    "category": t.get("category", ""),
                    "colors": t.get("colors", {}),
                    "reason": rec.get("reason", t.get("description", "")),
                })
        if not recs:
            for t in templates_list[:3]:
                recs.append({
                    "id": t["id"],
                    "name": t["name"],
                    "category": t.get("category", ""),
                    "colors": t.get("colors", {}),
                    "reason": t.get("description", "قالب احترافي متناسق الألوان"),
                })
        parsed["recommended_templates"] = recs[:4]
        if not parsed.get("summary") and parsed.get("overall_summary"):
            parsed["summary"] = parsed["overall_summary"]
        if not parsed.get("overall_summary") and parsed.get("summary"):
            parsed["overall_summary"] = parsed["summary"]
        if not parsed.get("overall_score"):
            parsed["overall_score"] = 8 if len(slides) >= 3 else 7
        for s_item in (parsed.get("slide_suggestions") or []):
            if not s_item.get("original_title") and s_item.get("current_title"):
                s_item["original_title"] = s_item["current_title"]
            if not s_item.get("improvement_reason") and s_item.get("content_advice"):
                s_item["improvement_reason"] = s_item["content_advice"]
            if not s_item.get("design_tip") and s_item.get("visual_advice"):
                s_item["design_tip"] = s_item["visual_advice"]
        return parsed

    def _analyze_locally(self, extracted: Dict[str, Any], templates_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        slides = extracted.get("slides") or []
        slide_suggestions = []
        weaknesses = []
        long_slides = 0
        for idx, s in enumerate(slides, start=1):
            bullets = s.get("bullets") or []
            if len(bullets) > 5 or any(len(b) > 120 for b in bullets):
                long_slides += 1
            improved_bullets = [b[:110].strip() for b in bullets[:5]] if bullets else ["أضف 3 نقاط رئيسية مركّزة تدعم عنوان الشريحة"]
            advice = "اختصر الجمل الطويلة إلى نقاط موجزة (أقل من 15 كلمة لكل نقطة)." if len(bullets) > 5 or any(len(b) > 100 for b in bullets) else "الهيكلة متوازنة؛ يُنصح بإبراز الكلمات المفتاحية."
            slide_suggestions.append({
                "slide_number": idx,
                "current_title": s.get("title", f"شريحة {idx}"),
                "improved_title": s.get("title", f"شريحة {idx}"),
                "improved_bullets": improved_bullets,
                "content_advice": advice,
                "visual_advice": "تطبيق تباين لوني حديث من كانفا مع خط عربي موحّد (Dubai أو Traditional Arabic).",
            })
        if long_slides:
            weaknesses.append(f"تحتوي {long_slides} شريحة على كثافة نصية عالية يُستحسن اختصارها.")
        if len(extracted.get("fonts_used") or []) > 2:
            weaknesses.append("تعدّد الخطوط المستخدمة يقلل من التناسق البصري؛ يُنصح بتوحيد الخط.")
        if not weaknesses:
            weaknesses.append("يمكن ترقية الهوية البصرية وتوحيد الألوان باستخدام قوالب كانفا الحديثة.")

        return {
            "overall_summary": f"تم تحليل العرض المكوّن من {len(slides)} شريحة. المحتوى متماسك ويمكن رفع جاذبيته عبر اختصار النقاط وتطبيق قالب كانفا متناسق.",
            "strengths": [
                f"تسلسل واضح عبر {len(slides)} شريحة.",
                "قابلية مباشرة لإعادة التنسيق دون فقدان الجداول أو النقاط الأساسية.",
            ],
            "weaknesses": weaknesses,
            "recommended_templates": [
                {"id": templates_list[0]["id"], "reason": "مناسب للعروض الرسمية والملخصات التنفيذية."},
                {"id": templates_list[2]["id"], "reason": "مريح للقراءة الأكاديمية والشرائح ذات النصوص المتعددة."},
                {"id": templates_list[4]["id"], "reason": "خيار عصري عالي التباين للعروض التقنية والتفاعلية."},
            ],
            "slide_suggestions": slide_suggestions,
        }

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """محادثة ذكية حول العروض التقديمية عبر Gemini ثم Groq."""
        sys_inst = "أنت مساعد ذكي متخصص في إنشاء وتحسين العروض التقديمية PowerPoint وقوالب كانفا والمحتوى الأكاديمي. أجب باللغة العربية بأسلوب عملي ومرتب."
        if self.gemini_available:
            convo = "\n".join(
                f"{'المستخدم' if m.get('role') == 'user' else 'المساعد'}: {m.get('content', '')}"
                for m in messages[-12:]
            )
            res = _call_gemini(convo, system_instruction=sys_inst)
            if res:
                return res
        if self.groq_available and self.client:
            try:
                history = [{"role": "system", "content": sys_inst}] + messages[-12:]
                resp = self.client.chat.completions.create(
                    model=GROQ_MODEL, messages=history, max_tokens=1500
                )
                return resp.choices[0].message.content
            except Exception as e:
                return f"❌ خطأ في الاتصال: {e}"
        return "⚠️ تعذّر الوصول لمزود الذكاء الاصطناعي حالياً. تأكد من الاتصال بالإنترنت أو صلاحية المفاتيح."

    def _process_locally(
        self, text: str, num_slides: int, ptype: str, extracted_tables: List
    ) -> List[Dict[str, Any]]:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        sentences = []
        for line in lines:
            parts = re.split(r"[.،,;؛]", line)
            sentences.extend([p.strip() for p in parts if len(p.strip()) > 5])

        title = sentences[0][:70] if sentences else "العرض التقديمي"
        slides: List[Dict[str, Any]] = [{
            "title": title,
            "subtitle": _subtitle(ptype),
            "bullets": [],
            "slide_type": "title",
        }]
        remaining = sentences[1:] if len(sentences) > 1 else ["محتوى العرض"]
        content_count = max(1, num_slides - 2)
        chunk_size = max(1, len(remaining) // max(1, content_count))
        sec_titles = _section_titles(ptype)
        tables_used = 0
        for i in range(content_count):
            chunk = remaining[i * chunk_size:(i + 1) * chunk_size]
            bullets = [b[:120] for b in chunk if b][:5]
            if not bullets:
                bullets = [f"النقطة الرئيسية {i+1}", "التفاصيل والمعلومات", "الخلاصة الجزئية"]
            slide: Dict[str, Any] = {
                "title": sec_titles[i % len(sec_titles)],
                "subtitle": "",
                "bullets": bullets,
                "slide_type": "bullets",
            }
            if extracted_tables and tables_used < len(extracted_tables) and i == content_count // 2:
                slide["slide_type"] = "table"
                slide["table_data"] = extracted_tables[tables_used]
                tables_used += 1
            slides.append(slide)

        slides.append({
            "title": "الخلاصة والتوصيات",
            "subtitle": "",
            "bullets": [
                "✅ " + (sentences[-1][:90] if sentences else "تم عرض أهم النقاط"),
                "📌 نرحب بأسئلتكم واستفساراتكم",
                "🙏 شكراً لاهتمامكم",
            ],
            "slide_type": "conclusion",
        })
        return slides[:num_slides]


def _subtitle(ptype: str) -> str:
    return {
        "business": "عرض تجاري احترافي",
        "educational": "مواد تعليمية متميزة",
        "sales": "عرض تسويقي متكامل",
        "general": "عرض تقديمي شامل",
    }.get(ptype, "عرض تقديمي")


def _section_titles(ptype: str) -> List[str]:
    return {
        "business": ["نظرة عامة", "الأهداف الاستراتيجية", "الخطة التنفيذية", "الميزانية والموارد", "مؤشرات النجاح"],
        "educational": ["المقدمة", "المفاهيم الأساسية", "التطبيقات العملية", "الأمثلة والتدريبات", "التقييم"],
        "sales": ["المشكلة", "الحل المقترح", "المميزات والفوائد", "الأسعار والعروض", "لماذا نحن؟"],
        "general": ["المقدمة", "المحتوى الرئيسي", "التفاصيل", "النتائج", "التوصيات"],
    }.get(ptype, ["المقدمة", "المحتوى", "التفاصيل", "النتائج", "الخلاصة"])
