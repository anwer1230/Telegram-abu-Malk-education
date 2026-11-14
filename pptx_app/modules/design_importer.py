# -*- coding: utf-8 -*-
"""إدارة واستيراد قوالب كانفا (Canva) وعروضها، وحسابات Google المرتبطة."""

import hashlib
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup

import config as _cfg
from pptx_app.modules.templates import CANVA_TEMPLATES

CANVA_CACHE_FILE = os.path.join(_cfg.DATA_DIR, "canva_imported_templates.json")
GOOGLE_ACCOUNTS_FILE = os.path.join(_cfg.DATA_DIR, "canva_google_accounts.json")


def _load_json(path: str, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def _save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class DesignImporter:
    def get_all_designs(self, category: str = "all", keyword: str = "") -> List[Dict[str, Any]]:
        """إرجاع جميع قوالب كانفا المدمجة + القوالب والعروض المستوردة من كانفا."""
        custom = _load_json(CANVA_CACHE_FILE, [])
        if not isinstance(custom, list):
            custom = []
        combined = custom + list(CANVA_TEMPLATES)

        kw = (keyword or "").strip().lower()
        cat = (category or "all").strip()
        results = []
        for d in combined:
            if cat != "all" and d.get("category", "") != cat:
                continue
            if kw:
                hay = f"{d.get('name','')} {d.get('category','')} {d.get('source','')} {d.get('description','')}".lower()
                if kw not in hay:
                    continue
            results.append(d)
        return results

    def get_design_by_id(self, design_id: str) -> Optional[Dict[str, Any]]:
        if not design_id:
            return None
        for d in self.get_all_designs():
            if d.get("id") == design_id:
                return d
        return None

    def import_canva_url(
        self,
        url: str,
        custom_name: str = "",
        category: str = "أعمال",
    ) -> Dict[str, Any]:
        """استيراد رابط تصميم أو قالب من كانفا وتحويله لقالب قابل للتطبيق المباشر."""
        clean_url = (url or "").strip()
        if not clean_url.startswith(("http://", "https://")):
            raise ValueError("يرجى إدخال رابط كانفا صحيح يبدأ بـ https://")

        title = (custom_name or "").strip()
        preview_image = ""
        extracted_theme_color = None

        try:
            resp = requests.get(
                clean_url,
                timeout=8,
                headers={"User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36"},
                allow_redirects=True,
            )
            if resp.ok and resp.text:
                soup = BeautifulSoup(resp.text[:120000], "lxml")
                if not title:
                    og_t = soup.find("meta", property="og:title")
                    if og_t and og_t.get("content"):
                        title = og_t["content"].replace("| Canva", "").replace("- Canva", "").strip()
                    elif soup.find("title"):
                        title = soup.find("title").get_text(strip=True)[:80]
                og_img = soup.find("meta", property="og:image")
                if og_img and og_img.get("content"):
                    preview_image = og_img["content"].strip()
                theme_meta = soup.find("meta", attrs={"name": "theme-color"})
                if theme_meta and theme_meta.get("content"):
                    extracted_theme_color = theme_meta["content"].strip()
        except Exception:
            pass

        if not title:
            title = "قالب كانفا مستورد"

        # لوحة ألوان تلقائية مستخرجة أو منسّقة
        primary = extracted_theme_color if (extracted_theme_color and extracted_theme_color.startswith("#")) else "#008B94"
        item_id = "canva_url_" + hashlib.md5(clean_url.encode("utf-8")).hexdigest()[:8]
        tpl = {
            "id": item_id,
            "name": title[:70],
            "category": category or "أعمال",
            "source": "رابط Canva مستورد",
            "theme_color": "blue",
            "layout": "modern_card",
            "font_name": "Dubai",
            "description": f"تصميم مستورد مباشرة من كانفا ({clean_url[:60]}...)",
            "colors": {
                "primary": primary,
                "secondary": "#0F2942",
                "accent": "#00C4CC",
                "bg": "#F4F8FB",
                "card_bg": "#FFFFFF",
                "text_dark": "#0F172A",
                "text_light": "#FFFFFF",
            },
            "canva_url": clean_url,
            "preview_image": preview_image,
            "imported_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        existing = _load_json(CANVA_CACHE_FILE, [])
        if not isinstance(existing, list):
            existing = []
        existing = [x for x in existing if x.get("id") != item_id]
        existing.insert(0, tpl)
        _save_json(CANVA_CACHE_FILE, existing[:30])
        return tpl

    def fetch_canva_api_designs(self, access_token: str) -> List[Dict[str, Any]]:
        """جلب تصاميم المستخدم الفعلية من Canva Connect API عند توفر رمز OAuth."""
        tok = (access_token or "").strip()
        if not tok:
            raise ValueError("رمز الوصول (Canva Access Token) مطلوب")
        resp = requests.get(
            "https://api.canva.com/rest/v1/designs",
            headers={"Authorization": f"Bearer {tok}", "Accept": "application/json"},
            timeout=12,
        )
        if not resp.ok:
            raise ValueError(f"رفضت واجهة Canva API الطلب (HTTP {resp.status_code})")
        payload = resp.json() or {}
        items = payload.get("items") or []
        fetched: List[Dict[str, Any]] = []
        palettes = [
            ("#0F2942", "#1D4E89", "#F59E0B", "#F8FAFC"),
            ("#008B94", "#0F3D5E", "#00C4CC", "#F0FDFA"),
            ("#4C1D95", "#2E1065", "#F59E0B", "#FAF5FF"),
            ("#E11D48", "#9F1239", "#FB7185", "#FFF1F2"),
        ]
        for idx, it in enumerate(items[:20]):
            did = str(it.get("id", f"canva_api_{idx}"))
            title = (it.get("title") or "تصميم كانفا بدون عنوان").strip()
            urls = it.get("urls") or {}
            edit_url = urls.get("edit_url") or urls.get("view_url") or "https://www.canva.com/"
            thumb = ((it.get("thumbnail") or {}).get("url") or "").strip()
            p_col, s_col, a_col, bg_col = palettes[idx % len(palettes)]
            fetched.append({
                "id": f"canva_api_{did}",
                "name": f"{title} (حسابي في كانفا)",
                "category": "تصاميمي",
                "source": "حساب Canva المتصل",
                "theme_color": "blue",
                "layout": "modern_card",
                "font_name": "Dubai",
                "description": "عرض مجلوب مباشرة من حسابك في كانفا",
                "colors": {
                    "primary": p_col,
                    "secondary": s_col,
                    "accent": a_col,
                    "bg": bg_col,
                    "card_bg": "#FFFFFF",
                    "text_dark": "#0F172A",
                    "text_light": "#FFFFFF",
                },
                "canva_url": edit_url,
                "preview_image": thumb,
                "imported_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })

        if fetched:
            existing = _load_json(CANVA_CACHE_FILE, [])
            if not isinstance(existing, list):
                existing = []
            fetched_ids = {x["id"] for x in fetched}
            kept = [x for x in existing if x.get("id") not in fetched_ids]
            _save_json(CANVA_CACHE_FILE, (fetched + kept)[:40])
        return fetched

    # ── إدارة حسابات Google المتصلة للدخول السريع إلى كانفا ──
    def get_google_accounts(self) -> Dict[str, Any]:
        data = _load_json(GOOGLE_ACCOUNTS_FILE, {"accounts": [], "active_email": ""})
        if not isinstance(data, dict):
            data = {"accounts": [], "active_email": ""}
        data.setdefault("accounts", [])
        data.setdefault("active_email", "")
        return data

    def save_google_account(
        self,
        email: str,
        name: str = "",
        photo_url: str = "",
        provider: str = "google",
        set_active: bool = True,
    ) -> Dict[str, Any]:
        clean_email = (email or "").strip().lower()
        if not clean_email or "@" not in clean_email:
            raise ValueError("البريد الإلكتروني لحساب Google غير صحيح")

        store = self.get_google_accounts()
        accounts = [a for a in store["accounts"] if a.get("email", "").lower() != clean_email]
        display_name = (name or "").strip() or clean_email.split("@")[0]
        entry = {
            "email": clean_email,
            "name": display_name,
            "photo_url": (photo_url or "").strip(),
            "provider": provider or "google",
            "last_used": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        accounts.insert(0, entry)
        store["accounts"] = accounts[:15]
        if set_active or not store.get("active_email"):
            store["active_email"] = clean_email
        _save_json(GOOGLE_ACCOUNTS_FILE, store)
        return store

    def select_google_account(self, email: str) -> Dict[str, Any]:
        clean_email = (email or "").strip().lower()
        store = self.get_google_accounts()
        found = next((a for a in store["accounts"] if a.get("email", "").lower() == clean_email), None)
        if not found:
            raise ValueError("الحساب غير موجود في القائمة المحفوظة")
        found["last_used"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        store["active_email"] = clean_email
        _save_json(GOOGLE_ACCOUNTS_FILE, store)
        return store

    def remove_google_account(self, email: str) -> Dict[str, Any]:
        clean_email = (email or "").strip().lower()
        store = self.get_google_accounts()
        store["accounts"] = [a for a in store["accounts"] if a.get("email", "").lower() != clean_email]
        if store.get("active_email", "").lower() == clean_email:
            store["active_email"] = store["accounts"][0]["email"] if store["accounts"] else ""
        _save_json(GOOGLE_ACCOUNTS_FILE, store)
        return store
