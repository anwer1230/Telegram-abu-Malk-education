"""صياغة وتنسيق الرد النهائي"""


def synthesize(task: str, raw_response: str, expert_name: str) -> str:
    """تنظيف وتنسيق رد الخبير لتقديمه بشكل متكامل"""
    if not raw_response:
        return "لم أتمكن من الحصول على إجابة دقيقة في الوقت الحالي."

    clean = raw_response.strip()
    return clean
