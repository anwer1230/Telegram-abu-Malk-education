"""عميل الاستدلال للذكاء الاصطناعي — يدعم Groq API ونماذج Ollama"""
import os
import httpx
from loguru import logger
from ai_engine.config import GROQ_API_KEY, OLLAMA_URL, MODEL_TEXT, FALLBACK_MODELS

try:
    from groq import Groq
    _groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except Exception as _e:
    logger.warning(f"Groq import error: {_e}")
    _groq_client = None


def chat(model: str = None, prompt: str = None, messages: list = None, system: str = None, temperature: float = 0.5) -> str:
    """إرسال محادثة والحصول على الرد من Groq أو Ollama مع معالجة الأخطاء والتكرار البديل"""
    target_model = model or MODEL_TEXT

    # إعداد الرسائل
    conv_messages = []
    if system:
        conv_messages.append({"role": "system", "content": system})
    if messages:
        conv_messages.extend(messages)
    elif prompt:
        conv_messages.append({"role": "user", "content": prompt})

    if not conv_messages:
        return ""

    # 1) محاولة الاستدعاء عبر Groq Client
    if _groq_client:
        models_to_try = [target_model] + [m for m in FALLBACK_MODELS if m != target_model]
        for m in models_to_try:
            try:
                completion = _groq_client.chat.completions.create(
                    model=m,
                    messages=conv_messages,
                    temperature=temperature,
                    max_tokens=1500,
                )
                if completion.choices and completion.choices[0].message:
                    return completion.choices[0].message.content or ""
            except Exception as e:
                logger.warning(f"فشل الطلب مع نموذج Groq ({m}): {e}")

    # 2) محاولة مباشرة عبر HTTP إلى Groq إن كان الكلاينت غير مهيأ
    if GROQ_API_KEY:
        try:
            with httpx.Client(timeout=30) as client:
                res = client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    json={
                        "model": target_model,
                        "messages": conv_messages,
                        "temperature": temperature,
                        "max_tokens": 1500,
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"فشل الاتصال المباشر بـ Groq: {e}")

    # 3) محاولة عبر Ollama إن كان هناك سيرفر مخصص
    if OLLAMA_URL:
        try:
            with httpx.Client(timeout=40) as client:
                res = client.post(
                    f"{OLLAMA_URL.rstrip('/')}/api/chat",
                    json={"model": target_model, "messages": conv_messages, "stream": False}
                )
                if res.status_code == 200:
                    return res.json().get("message", {}).get("content", "")
        except Exception as e:
            logger.warning(f"فشل الاتصال بـ Ollama: {e}")

    return "عذراً، لم أستطع معالجة طلبك حالياً يرجى المحاولة بعد قليل."


def health() -> dict:
    """فحص جاهزية المحرك"""
    has_groq = bool(GROQ_API_KEY)
    has_ollama = bool(OLLAMA_URL)
    status = "available" if (has_groq or has_ollama) else "no_provider"
    return {
        "engine": "groq-hybrid-ai",
        "available": status == "available",
        "provider": "groq" if has_groq else ("ollama" if has_ollama else "none"),
        "default_model": MODEL_TEXT,
    }
