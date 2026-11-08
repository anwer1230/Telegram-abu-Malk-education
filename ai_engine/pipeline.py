"""خط أنابيب المعالجة المتكاملة — يربط المنسق والخبراء والصياغة"""
import time
from loguru import logger
from ai_engine.orchestrator import route
from ai_engine.experts import REGISTRY
from ai_engine.synthesis import synthesize
from ai_engine.ollama_client import health as client_health


def ask(query: str, context: dict = None) -> dict:
    """تنفيذ خط معالجة السؤال وتوليد الإجابة"""
    start_time = time.time()
    query = (query or "").strip()
    if not query:
        return {"success": False, "error": "نص السؤال فارغ", "response": ""}

    try:
        expert_name = route(query)
        expert_fn = REGISTRY.get(expert_name, REGISTRY["TEXT"])

        raw_result = expert_fn(query)
        final_answer = synthesize(query, raw_result, expert_name)

        elapsed = round(time.time() - start_time, 3)
        return {
            "success": True,
            "response": final_answer,
            "expert": expert_name,
            "latency": elapsed,
        }
    except Exception as e:
        logger.error(f"خطأ في خط أنابيب الذكاء الاصطناعي: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "response": "حدث خطأ أثناء معالجة طلبك.",
            "latency": round(time.time() - start_time, 3),
        }


def health() -> dict:
    """فحص جاهزية النظام ككل"""
    return client_health()
