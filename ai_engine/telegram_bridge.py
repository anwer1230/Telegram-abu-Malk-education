"""جسر التيليجرام — يدعو AI فقط عند فشل القواعد العادية"""
import os
from loguru import logger
from ai_engine.config import AI_TELEGRAM_ENABLED

ENABLE = AI_TELEGRAM_ENABLED
MIN_LEN = int(os.getenv("AI_TELEGRAM_MIN_LEN", "5"))
MAX_LEN = int(os.getenv("AI_TELEGRAM_MAX_LEN", "800"))

SKIP_KEYWORDS = {
    "الغاء", "إلغاء", "الغِ", "stop", "ايقاف", "إيقاف",
    "حظر", "block", "تقرير", "احصائيات", "إحصائيات",
}


def should_use_ai(text: str) -> bool:
    """هل نرسل هذه الرسالة إلى AI؟"""
    if not ENABLE:
        return False
    text = (text or "").strip()
    if not (MIN_LEN <= len(text) <= MAX_LEN):
        return False
    low = text.lower()
    if any(k in low for k in SKIP_KEYWORDS):
        return False
    return True


def generate_reply(user_text: str, sender_name: str = "") -> str | None:
    """توليد رد AI لتيليجرام — يعيد None إذا فشل أو تم تعطيله"""
    if not should_use_ai(user_text):
        return None
    try:
        from ai_engine.pipeline import ask
        ctx = f"المرسل: {sender_name}\nالرسالة: {user_text}" if sender_name else user_text
        result = ask(ctx)
        if result.get("success") and result.get("response"):
            logger.info(f"🤖 Telegram→AI: {user_text[:50]}")
            return result["response"].strip()
    except Exception as e:
        logger.error(f"فشل AI في التيليجرام: {e}")
    return None
