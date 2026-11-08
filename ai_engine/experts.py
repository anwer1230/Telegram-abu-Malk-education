"""خبراء الذكاء الاصطناعي التخصصيين"""
from ai_engine.ollama_client import chat
from ai_engine.config import MODEL_TEXT, MODEL_LOGIC, MODEL_CODE
from ai_engine.rag import search as rag_search


def expert_text(task: str) -> str:
    """خبير المحادثة والشرح العام والصياغة اللغوية"""
    system_prompt = (
        "أنت مساعد ذكي ولطيف ومحترف باللغة العربية. "
        "أجب بوضوح وإيجاز ودقة على استفسار المستخدم."
    )
    return chat(model=MODEL_TEXT, prompt=task, system=system_prompt)


def expert_logic(task: str) -> str:
    """خبير الحسابات والتحليل المنطقي والرياضي"""
    system_prompt = (
        "أنت خبير في التحليل المنطقي والعمليات الحسابية والمالية. "
        "قدم إجابات دقيقة ومنظمة باللغة العربية مع توضيح الخطوات إن لزم."
    )
    return chat(model=MODEL_LOGIC, prompt=task, system=system_prompt)


def expert_code(task: str) -> str:
    """خبير البرمجة والأكواد التقنية"""
    system_prompt = (
        "أنت مهندس برمجيات محترف وخبير بالأكواد والتقنية. "
        "قدم حلولاً برمجية نظيفة مع شرح موجز بالعربية."
    )
    return chat(model=MODEL_CODE, prompt=task, system=system_prompt)


def expert_rag(task: str) -> str:
    """خبير البحث في المستندات والملفات المرفوعة"""
    docs = rag_search(task, limit=4)
    if not docs:
        return expert_text(task)

    context = "\n\n---\n\n".join(
        f"[{d['source']}]\n{d['text']}" for d in docs
    )

    prompt = f"""أجب على السؤال بالاعتماد على المستندات التالية فقط.

المستندات:
{context}

السؤال: {task}

أجب بالعربية مع ذكر اسم المصدر إن أمكن وبدقة كاملة."""

    return chat(model=MODEL_TEXT, prompt=prompt)


REGISTRY = {
    "TEXT": expert_text,
    "LOGIC": expert_logic,
    "CODE": expert_code,
    "RAG": expert_rag,
}
