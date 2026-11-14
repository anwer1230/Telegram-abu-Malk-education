# -*- coding: utf-8 -*-
"""جالب الصور الذكي للشرائح مع تخزين مؤقت محلي."""

import hashlib
import requests
from pathlib import Path
from typing import Optional

CACHE_DIR = Path(__file__).resolve().parent.parent / "outputs" / "img_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

TIMEOUT = 8

_ARABIC_TO_EN = {
    "تعليم": "education", "مدرسة": "school", "جامعة": "university", "طالب": "students",
    "تدريب": "training", "تعلم": "learning", "مناهج": "curriculum", "اختبار": "exam",
    "تقنية": "technology", "ذكاء اصطناعي": "artificial intelligence", "برمجة": "coding",
    "حاسوب": "computer", "شبكة": "network", "أمن": "cybersecurity",
    "بيانات": "data analytics", "سحابة": "cloud computing", "ابتكار": "innovation",
    "أعمال": "business", "شركة": "corporate office", "تجارة": "commerce",
    "سوق": "market", "مبيعات": "sales", "تسويق": "marketing", "إدارة": "management",
    "قيادة": "leadership", "فريق": "team", "اجتماع": "meeting", "عمل": "workplace",
    "استراتيجية": "strategy", "خطة": "planning", "ميزانية": "finance", "استثمار": "investment",
    "صحة": "healthcare", "طب": "medicine", "مستشفى": "hospital", "رياضة": "sports",
    "بيئة": "environment", "طاقة": "renewable energy", "طبيعة": "nature landscape",
    "بناء": "architecture", "مشروع": "project", "تصميم": "design", "هندسة": "engineering",
    "خلاصة": "success achievement", "نتائج": "results", "هدف": "goal target", "نجاح": "success",
}

_SLIDE_TYPE_DEFAULTS = {
    "title": "professional presentation",
    "conclusion": "success achievement team",
    "table": "data analytics chart",
    "chart": "business graph analytics",
    "bullets": "professional business",
}


def get_slide_image(
    slide_title: str,
    slide_bullets: list,
    slide_type: str = "bullets",
    groq_client=None,
) -> Optional[str]:
    keywords = _extract_keywords(slide_title, slide_bullets, slide_type, groq_client)
    if not keywords:
        return None
    return _download_image(keywords)


def _extract_keywords(title: str, bullets: list, slide_type: str, groq_client) -> str:
    if groq_client:
        try:
            content = title + "\n" + "\n".join(bullets[:3])
            resp = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": (
                        "Extract 2-3 English keywords suitable for image search from this Arabic text. "
                        "Return ONLY keywords separated by commas.\n\n" + content
                    ),
                }],
                max_tokens=25,
                temperature=0.2,
            )
            kw = resp.choices[0].message.content.strip().replace("\n", ",").replace(" ", ",")
            kw = ",".join([k.strip() for k in kw.split(",") if k.strip()])
            if kw and len(kw) > 2:
                return kw
        except Exception:
            pass

    full_text = title + " " + " ".join(bullets[:3])
    for arabic, english in _ARABIC_TO_EN.items():
        if arabic in full_text:
            return english.replace(" ", ",")
    return _SLIDE_TYPE_DEFAULTS.get(slide_type, "professional business")


def _download_image(keywords: str) -> Optional[str]:
    safe_kw = keywords.strip()[:80]
    cache_key = hashlib.md5(safe_kw.encode()).hexdigest()[:10]
    cache_path = CACHE_DIR / f"{cache_key}.jpg"
    if cache_path.exists() and cache_path.stat().st_size > 4000:
        return str(cache_path)
    try:
        url = f"https://loremflickr.com/900/550/{safe_kw}"
        resp = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
        if resp.status_code == 200 and len(resp.content) > 4000:
            cache_path.write_bytes(resp.content)
            return str(cache_path)
    except Exception:
        pass
    return None
