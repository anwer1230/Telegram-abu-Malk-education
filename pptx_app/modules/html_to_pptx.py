# -*- coding: utf-8 -*-
"""محول HTML إلى PowerPoint الاحترافي."""

import re
from typing import List, Dict, Any, Optional

from bs4 import BeautifulSoup
from pptx_app.modules.presentation_generator import PresentationGenerator


def _extract_css_vars(html: str) -> Dict[str, str]:
    css_blocks = re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL | re.IGNORECASE)
    css_text = " ".join(css_blocks)
    vars_map: Dict[str, str] = {}
    for m in re.finditer(r"--([\w-]+)\s*:\s*([^;]+);", css_text):
        vars_map[f"--{m.group(1)}"] = m.group(2).strip()
    return vars_map


def _split_by_headings(soup) -> List[Any]:
    sections = []
    current = None
    body = soup.body or soup
    for el in body.children:
        if not hasattr(el, "name") or not el.name:
            continue
        if el.name in ("h1", "h2", "h3"):
            if current:
                sections.append(current)
            current = [el]
        elif current is not None:
            current.append(el)
    if current:
        sections.append(current)

    wrappers = []
    for group in sections:
        w = BeautifulSoup("<div></div>", "lxml").div
        for item in group:
            w.append(item.__copy__())
        wrappers.append(w)
    return wrappers


def parse_html_to_slides(html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(["script", "noscript"]):
        tag.decompose()
    _ = _extract_css_vars(html)

    slide_candidates = (
        soup.find_all("section")
        or soup.find_all(class_=re.compile(r"slide|page|frame", re.I))
        or soup.find_all(attrs={"data-slide": True})
        or soup.find_all("article")
    )
    if not slide_candidates:
        slide_candidates = _split_by_headings(soup)

    def _extract_slide(el) -> Dict[str, Any]:
        sd: Dict[str, Any] = {
            "title": "",
            "subtitle": "",
            "bullets": [],
            "slide_type": "bullets",
            "bg_color": None,
            "text_color": None,
            "table_data": None,
            "images": [],
            "is_title_slide": False,
        }
        title_el = el.find(class_="slide-title")
        if title_el:
            sd["title"] = title_el.get_text(strip=True)
        else:
            for htag in ("h1", "h2", "h3", "h4"):
                h = el.find(htag)
                if h:
                    sd["title"] = h.get_text(strip=True)
                    sd["is_title_slide"] = (htag == "h1")
                    break

        style_attr = el.get("style", "")
        bg_match = re.search(r"background(?:-color)?\s*:\s*([^;]+)", style_attr)
        if bg_match:
            sd["bg_color"] = bg_match.group(1).strip()

        bullets_el = el.find(class_="list-items")
        if bullets_el:
            sd["bullets"] = [li.get_text(strip=True) for li in bullets_el.find_all("li") if li.get_text(strip=True)]
        else:
            lis = el.find_all("li")
            if lis:
                sd["bullets"] = [li.get_text(strip=True) for li in lis if li.get_text(strip=True)]
            else:
                sd["bullets"] = [
                    p.get_text(strip=True)
                    for p in el.find_all("p")
                    if p.get_text(strip=True) and p.get_text(strip=True) != sd["title"] and len(p.get_text(strip=True)) > 3
                ]
        sd["bullets"] = sd["bullets"][:8]

        tbl = el.find("table")
        if tbl:
            rows = []
            for tr in tbl.find_all("tr"):
                cells = []
                for td in tr.find_all(["td", "th"]):
                    cell_style = td.get("style", "")
                    bg = re.search(r"background(?:-color)?\s*:\s*([^;]+)", cell_style)
                    align = re.search(r"text-align\s*:\s*([^;]+)", cell_style)
                    cells.append({
                        "text": td.get_text(strip=True),
                        "bg": bg.group(1).strip() if bg else None,
                        "align": align.group(1).strip() if align else "center",
                        "bold": (td.name == "th") or ("font-weight" in cell_style and "bold" in cell_style),
                    })
                if cells:
                    rows.append(cells)
            if rows:
                sd["table_data"] = rows
                sd["slide_type"] = "table"

        for img in el.find_all("img"):
            src = img.get("src", "")
            if src and (src.startswith("data:") or src.startswith("http")):
                sd["images"].append(src)

        classes = " ".join(el.get("class", []))
        if re.search(r"title|cover|first|intro", classes, re.I) or sd["is_title_slide"]:
            sd["slide_type"] = "title"
        elif re.search(r"end|outro|thank|conclusion", classes, re.I):
            sd["slide_type"] = "conclusion"
        return sd

    slides = []
    for el in slide_candidates:
        d = _extract_slide(el)
        if d.get("title") or d.get("bullets") or d.get("table_data"):
            slides.append(d)
    if not slides:
        slides = [_extract_slide(soup.body or soup)]
    return slides


def convert_html_to_pptx(
    html: str,
    override_title: str = "",
    theme_color: str = "blue",
    font_name: str = "Traditional Arabic",
    body_font_size: int = 22,
    cover_data: Optional[Dict[str, str]] = None,
    custom_theme: Optional[Dict[str, Any]] = None,
) -> tuple[str, List[Dict[str, Any]]]:
    slides_data = parse_html_to_slides(html)
    if not slides_data:
        raise ValueError("لم يتم العثور على محتوى شرائح قابل للتحويل في كود HTML")
    if override_title and slides_data:
        slides_data[0]["title"] = override_title
    gen = PresentationGenerator()
    out_path = gen.create_presentation(
        slides_data=slides_data,
        theme_color=theme_color,
        cover_data=cover_data,
        extracted_images=[],
        font_name=font_name,
        body_font_size=body_font_size,
        ai_images=False,
        custom_theme=custom_theme,
        filename_prefix=override_title or "عرض_HTML",
    )
    return out_path, slides_data
