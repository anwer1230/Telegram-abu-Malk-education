# -*- coding: utf-8 -*-
"""قوالب التصميم الاحترافية وقوالب كانفا (Canva Templates) للعروض التقديمية."""

from typing import Dict, List, Any, Tuple


def _hex_to_tuple(hex_str: str, fallback: Tuple[int, int, int] = (0x66, 0x7E, 0xEA)) -> Tuple[int, int, int]:
    s = (hex_str or "").strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) == 6:
        try:
            return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
        except Exception:
            pass
    return fallback


# القوالب الكلاسيكية الأساسية (متوافقة مع الكود الأصلي)
THEMES: Dict[str, Dict[str, Any]] = {
    "blue": {
        "id": "blue",
        "name": "أزرق احترافي",
        "primary": (0x66, 0x7E, 0xEA),
        "secondary": (0x76, 0x4B, 0xA2),
        "accent": (0xFF, 0xFF, 0xFF),
        "card_bg": (0xFF, 0xFF, 0xFF),
        "text_dark": (0x1A, 0x1A, 0x2E),
        "text_light": (0xFF, 0xFF, 0xFF),
        "bg": (0xF5, 0xF7, 0xFF),
        "layout": "header_banner",
        "font_name": "Traditional Arabic",
        "source": "مدمج",
        "category": "أعمال",
    },
    "green": {
        "id": "green",
        "name": "أخضر طبيعي",
        "primary": (0x11, 0x99, 0x55),
        "secondary": (0x00, 0x7A, 0x3D),
        "accent": (0xFF, 0xFF, 0xFF),
        "card_bg": (0xFF, 0xFF, 0xFF),
        "text_dark": (0x1A, 0x2E, 0x1A),
        "text_light": (0xFF, 0xFF, 0xFF),
        "bg": (0xF0, 0xFB, 0xF4),
        "layout": "header_banner",
        "font_name": "Traditional Arabic",
        "source": "مدمج",
        "category": "تعليمي",
    },
    "red": {
        "id": "red",
        "name": "أحمر حيوي",
        "primary": (0xE5, 0x39, 0x35),
        "secondary": (0xB7, 0x1C, 0x1C),
        "accent": (0xFF, 0xCC, 0x02),
        "card_bg": (0xFF, 0xFF, 0xFF),
        "text_dark": (0x2E, 0x1A, 0x1A),
        "text_light": (0xFF, 0xFF, 0xFF),
        "bg": (0xFD, 0xF2, 0xF2),
        "layout": "header_banner",
        "font_name": "Traditional Arabic",
        "source": "مدمج",
        "category": "تسويق",
    },
    "purple": {
        "id": "purple",
        "name": "بنفسجي ملكي",
        "primary": (0x6A, 0x1B, 0x9A),
        "secondary": (0x4A, 0x14, 0x8C),
        "accent": (0xFF, 0xD7, 0x00),
        "card_bg": (0xFF, 0xFF, 0xFF),
        "text_dark": (0x1A, 0x1A, 0x2E),
        "text_light": (0xFF, 0xFF, 0xFF),
        "bg": (0xF8, 0xF0, 0xFF),
        "layout": "header_banner",
        "font_name": "Traditional Arabic",
        "source": "مدمج",
        "category": "فاخر",
    },
}


# كتالوج قوالب كانفا الاحترافية القابلة للتطبيق المباشر والحقيقي على شرائح PowerPoint
CANVA_TEMPLATES: List[Dict[str, Any]] = [
    {
        "id": "canva_exec_navy",
        "name": "كانفا — العرض التنفيذي الكلاسيكي",
        "category": "أعمال",
        "source": "Canva Presentations",
        "theme_color": "blue",
        "layout": "split_accent",
        "font_name": "Dubai",
        "description": "تصميم مؤسسي أنيق بدرجات الكحلي والذهبي الدافئ مثالي لتقارير الإدارة والخطط الاستراتيجية.",
        "colors": {
            "primary": "#0F2942",
            "secondary": "#1D4E89",
            "accent": "#F59E0B",
            "bg": "#F8FAFC",
            "card_bg": "#FFFFFF",
            "text_dark": "#0F172A",
            "text_light": "#FFFFFF",
        },
        "canva_url": "https://www.canva.com/presentations/templates/business/",
    },
    {
        "id": "canva_coral_pitch",
        "name": "كانفا — عرض الشركات الناشئة المرجاني",
        "category": "تسويق",
        "source": "Canva Pitch Deck",
        "theme_color": "red",
        "layout": "modern_card",
        "font_name": "Dubai",
        "description": "أسلوب Pitch Deck حيوي ومقنع مناسب للعروض التسويقية وإطلاق المنتجات والخدمات.",
        "colors": {
            "primary": "#E11D48",
            "secondary": "#9F1239",
            "accent": "#FB7185",
            "bg": "#FFF1F2",
            "card_bg": "#FFFFFF",
            "text_dark": "#1F2937",
            "text_light": "#FFFFFF",
        },
        "canva_url": "https://www.canva.com/presentations/templates/pitch-deck/",
    },
    {
        "id": "canva_sage_academic",
        "name": "كانفا — الأكاديمي الهادئ (Sage)",
        "category": "تعليمي",
        "source": "Canva Education",
        "theme_color": "green",
        "layout": "minimal_clean",
        "font_name": "Traditional Arabic",
        "description": "تنسيق تعليمي وبحثي مريح للعين مع وضوح عالٍ للنصوص والجداول الأكاديمية.",
        "colors": {
            "primary": "#166534",
            "secondary": "#14532D",
            "accent": "#10B981",
            "bg": "#F2FBF5",
            "card_bg": "#FFFFFF",
            "text_dark": "#14261C",
            "text_light": "#FFFFFF",
        },
        "canva_url": "https://www.canva.com/presentations/templates/education/",
    },
    {
        "id": "canva_teal_modern",
        "name": "كانفا — كانفا فيروزي تقني حديث",
        "category": "تقنية",
        "source": "Canva Creative",
        "theme_color": "blue",
        "layout": "modern_card",
        "font_name": "Dubai",
        "description": "هوية كانفا الفيروزية الممزوجة بالأزرق العميق للعروض التقنية والتحول الرقمي.",
        "colors": {
            "primary": "#008B94",
            "secondary": "#0F3D5E",
            "accent": "#00C4CC",
            "bg": "#F0FDFA",
            "card_bg": "#FFFFFF",
            "text_dark": "#0F172A",
            "text_light": "#FFFFFF",
        },
        "canva_url": "https://www.canva.com/presentations/templates/technology/",
    },
    {
        "id": "canva_dark_midnight",
        "name": "كانفا — الليلي الاحترافي (Dark Pitch)",
        "category": "تقنية",
        "source": "Canva Dark Studio",
        "theme_color": "purple",
        "layout": "dark_pitch",
        "font_name": "Dubai",
        "description": "خلفية داكنة فاخرة تبرز النصوص البيضاء والبنفسجية بوضوح درامي مبهر.",
        "colors": {
            "primary": "#6366F1",
            "secondary": "#1E1B4B",
            "accent": "#38BDF8",
            "bg": "#0F172A",
            "card_bg": "#1E293B",
            "text_dark": "#F8FAFC",
            "text_light": "#FFFFFF",
        },
        "canva_url": "https://www.canva.com/presentations/templates/modern/",
    },
    {
        "id": "canva_royal_gold",
        "name": "كانفا — الملكي الفاخر والذهبي",
        "category": "فاخر",
        "source": "Canva Luxury",
        "theme_color": "purple",
        "layout": "split_accent",
        "font_name": "Traditional Arabic",
        "description": "تنسيق رسمي راقٍ بالبنفسجي العميق ولمسات ذهبية للمناسبات والتقارير العليا.",
        "colors": {
            "primary": "#4C1D95",
            "secondary": "#2E1065",
            "accent": "#F59E0B",
            "bg": "#FAF5FF",
            "card_bg": "#FFFFFF",
            "text_dark": "#1E1B4B",
            "text_light": "#FFFFFF",
        },
        "canva_url": "https://www.canva.com/presentations/templates/creative/",
    },
    {
        "id": "canva_minimal_editorial",
        "name": "كانفا — المينيمال التحريري الأنيق",
        "category": "أعمال",
        "source": "Canva Minimalist",
        "theme_color": "blue",
        "layout": "minimal_clean",
        "font_name": "Simplified Arabic",
        "description": "مساحات بيضاء واسعة مع خطوط عربية واضحة وشريط جانبي هادئ للتركيز على الأفكار.",
        "colors": {
            "primary": "#1E293B",
            "secondary": "#334155",
            "accent": "#2563EB",
            "bg": "#FFFFFF",
            "card_bg": "#F8FAFC",
            "text_dark": "#0F172A",
            "text_light": "#FFFFFF",
        },
        "canva_url": "https://www.canva.com/presentations/templates/minimalist/",
    },
    {
        "id": "canva_sunset_creative",
        "name": "كانفا — الإبداعي الدافئ (Sunset)",
        "category": "إبداعي",
        "source": "Canva Creative",
        "theme_color": "red",
        "layout": "modern_card",
        "font_name": "Dubai",
        "description": "ألوان دافئة مشرقة بالبرتقالي والمرجاني تجذب الانتباه في ورش العمل والمبادرات.",
        "colors": {
            "primary": "#EA580C",
            "secondary": "#9A3412",
            "accent": "#FBBF24",
            "bg": "#FFF7ED",
            "card_bg": "#FFFFFF",
            "text_dark": "#27150A",
            "text_light": "#FFFFFF",
        },
        "canva_url": "https://www.canva.com/presentations/templates/aesthetic/",
    },
    {
        "id": "canva_data_infographic",
        "name": "كانفا — تحليل البيانات والإنفوجرافيك",
        "category": "أعمال",
        "source": "Canva Data Deck",
        "theme_color": "blue",
        "layout": "modern_card",
        "font_name": "Dubai",
        "description": "مخصص لعرض الإحصائيات والجداول والمؤشرات المالية والرسوم البيانية بوضوح فائق.",
        "colors": {
            "primary": "#2563EB",
            "secondary": "#1E40AF",
            "accent": "#06B6D4",
            "bg": "#EFF6FF",
            "card_bg": "#FFFFFF",
            "text_dark": "#1E293B",
            "text_light": "#FFFFFF",
        },
        "canva_url": "https://www.canva.com/presentations/templates/infographic/",
    },
    {
        "id": "canva_islamic_heritage",
        "name": "كانفا — التراث العربي والوقار",
        "category": "تعليمي",
        "source": "Canva Arabic",
        "theme_color": "green",
        "layout": "split_accent",
        "font_name": "Traditional Arabic",
        "description": "مستوحى من الزمردي والذهبي العربي للبحوث الإسلامية والتاريخية والأدبية.",
        "colors": {
            "primary": "#065F46",
            "secondary": "#064E3B",
            "accent": "#D97706",
            "bg": "#FBFBF7",
            "card_bg": "#FFFFFF",
            "text_dark": "#1C241E",
            "text_light": "#FFFFFF",
        },
        "canva_url": "https://www.canva.com/presentations/",
    },
]


def resolve_theme_spec(
    theme_color: str = "blue",
    custom_theme: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """تحويل اسم القالب الكلاسيكي أو معرف قالب كانفا أو الألوان المخصصة إلى مواصفات RGB كاملة."""
    if custom_theme and isinstance(custom_theme, dict):
        colors = custom_theme.get("colors") if isinstance(custom_theme.get("colors"), dict) else custom_theme
        return {
            "id": custom_theme.get("id", theme_color or "custom"),
            "name": custom_theme.get("name", "قالب كانفا مخصص"),
            "primary": _hex_to_tuple(str(colors.get("primary", "#0F2942"))),
            "secondary": _hex_to_tuple(str(colors.get("secondary", colors.get("primary", "#1D4E89")))),
            "accent": _hex_to_tuple(str(colors.get("accent", "#F59E0B")), (0xF5, 0x9E, 0x0B)),
            "card_bg": _hex_to_tuple(str(colors.get("card_bg", "#FFFFFF")), (0xFF, 0xFF, 0xFF)),
            "text_dark": _hex_to_tuple(str(colors.get("text_dark", "#0F172A")), (0x0F, 0x17, 0x2A)),
            "text_light": _hex_to_tuple(str(colors.get("text_light", "#FFFFFF")), (0xFF, 0xFF, 0xFF)),
            "bg": _hex_to_tuple(str(colors.get("bg", "#F8FAFC")), (0xF8, 0xFA, 0xFC)),
            "layout": custom_theme.get("layout", "modern_card"),
            "font_name": custom_theme.get("font_name", "Dubai"),
        }

    key = (theme_color or "blue").strip()
    for tpl in CANVA_TEMPLATES:
        if tpl["id"] == key:
            return resolve_theme_spec(key, tpl)

    base = THEMES.get(key, THEMES["blue"])
    return dict(base)


class ProfessionalTemplates:
    def get_theme(self, color: str, custom_theme: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return resolve_theme_spec(color, custom_theme)

    def list_themes(self) -> List[Dict[str, Any]]:
        return [{"key": k, "name": v["name"]} for k, v in THEMES.items()]

    def list_canva_templates(self) -> List[Dict[str, Any]]:
        return [dict(t) for t in CANVA_TEMPLATES]
