"""جسر الأوامر الصوتية — فرع احتياطي فقط عند عدم تطابق أي أمر صوتي محدد"""
import os
from loguru import logger
from ai_engine.config import AI_VOICE_ENABLED

ENABLE = AI_VOICE_ENABLED
MIN_LEN = int(os.getenv("AI_VOICE_MIN_LEN", "3"))
MAX_LEN = int(os.getenv("AI_VOICE_MAX_LEN", "400"))


def should_use_ai(transcript: str) -> bool:
    if not ENABLE:
        return False
    t = (transcript or "").strip()
    return MIN_LEN <= len(t) <= MAX_LEN


def generate_reply(transcript: str) -> str | None:
    """توليد رد صوتي ذكي"""
    if not should_use_ai(transcript):
        return None
    try:
        from ai_engine.pipeline import ask
        result = ask(transcript)
        if result.get("success") and result.get("response"):
            logger.info(f"🎙️ Voice→AI: {transcript[:50]}")
            return result["response"].strip()
    except Exception as e:
        logger.error(f"فشل AI في الصوت: {e}")
    return None
