# -*- coding: utf-8 -*-
"""تطبيق قوالب وتصاميم كانفا على العروض التقديمية."""

from typing import Dict, Any, List, Optional

from pptx_app.modules.presentation_generator import PresentationGenerator
from pptx_app.modules.design_importer import DesignImporter


class DesignApplier:
    def __init__(self):
        self.generator = PresentationGenerator()
        self.importer = DesignImporter()

    def apply_design_to_presentation(
        self,
        slides_data: List[Dict[str, Any]],
        design_id: str = "canva_exec_navy",
        cover_data: Optional[Dict[str, str]] = None,
        font_name: str = "",
        body_font_size: int = 22,
        filename_prefix: str = "عرض_كانفا",
    ) -> tuple[str, Dict[str, Any]]:
        design = self.importer.get_design_by_id(design_id)
        if design:
            chosen_font = font_name or design.get("font_name", "Dubai")
            out = self.generator.create_presentation(
                slides_data=slides_data,
                theme_color=design.get("theme_color", "blue"),
                cover_data=cover_data,
                font_name=chosen_font,
                body_font_size=body_font_size,
                custom_theme=design,
                filename_prefix=filename_prefix,
            )
            return out, design

        out = self.generator.create_presentation(
            slides_data=slides_data,
            theme_color=design_id or "blue",
            cover_data=cover_data,
            font_name=font_name or "Traditional Arabic",
            body_font_size=body_font_size,
            filename_prefix=filename_prefix,
        )
        return out, {"id": design_id or "blue", "name": design_id or "أزرق احترافي"}
