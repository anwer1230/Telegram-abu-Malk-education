# -*- coding: utf-8 -*-
"""توليد الرسوم البيانية (يدعم matplotlib + بديل رسم عالي الدقة بـ Pillow دائماً)."""

import tempfile
from typing import List, Optional

COLORS_LIST = [
    "#667eea", "#764ba2", "#11aa55", "#e53935",
    "#ff6b35", "#00bcd4", "#ffc107", "#9c27b0",
]


def _draw_chart_with_pillow(
    chart_type: str,
    labels: List[str],
    values: List[float],
    title: str = "",
    color: str = "#667eea",
) -> Optional[str]:
    try:
        from PIL import Image, ImageDraw
        w, h = 1000, 620
        img = Image.new("RGB", (w, h), "#f8fafc")
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, w - 20, h - 20], outline="#e2e8f0", width=2)
        if title:
            draw.text((40, 32), str(title)[:60], fill="#0f172a")

        n = max(1, len(values))
        max_v = max(max(values), 1.0)
        pad_l, pad_r, pad_t, pad_b = 90, 50, 90, 90
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b

        if chart_type == "pie":
            total = sum(abs(v) for v in values) or 1.0
            cx, cy, radius = w // 2 - 90, h // 2 + 10, min(plot_w, plot_h) // 2 - 20
            bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
            start_angle = 0.0
            for idx, (lbl, val) in enumerate(zip(labels, values)):
                sweep = (abs(val) / total) * 360.0
                c = COLORS_LIST[idx % len(COLORS_LIST)]
                draw.pieslice(bbox, start_angle, start_angle + sweep, fill=c, outline="#ffffff", width=2)
                ly = 110 + idx * 36
                if ly < h - 40:
                    draw.rectangle([w - 270, ly, w - 250, ly + 18], fill=c)
                    pct = (abs(val) / total) * 100.0
                    draw.text((w - 240, ly + 2), f"{str(lbl)[:16]} ({pct:.1f}%)", fill="#1e293b")
                start_angle += sweep
        elif chart_type == "line":
            draw.line([pad_l, pad_t, pad_l, h - pad_b], fill="#94a3b8", width=2)
            draw.line([pad_l, h - pad_b, w - pad_r, h - pad_b], fill="#94a3b8", width=2)
            pts = []
            for idx, val in enumerate(values):
                x = pad_l + int((idx / max(1, n - 1)) * plot_w) if n > 1 else pad_l + plot_w // 2
                y = (h - pad_b) - int((val / max_v) * (plot_h - 20))
                pts.append((x, y))
            if len(pts) >= 2:
                draw.line(pts, fill=color, width=5)
            for idx, (x, y) in enumerate(pts):
                draw.ellipse([x - 7, y - 7, x + 7, y + 7], fill=color, outline="#ffffff", width=2)
                draw.text((x - 15, h - pad_b + 14), str(labels[idx])[:12], fill="#334155")
                draw.text((x - 12, max(pad_t, y - 22)), f"{values[idx]:g}", fill="#0f172a")
        else:
            # bar / horizontal_bar
            draw.line([pad_l, pad_t, pad_l, h - pad_b], fill="#94a3b8", width=2)
            draw.line([pad_l, h - pad_b, w - pad_r, h - pad_b], fill="#94a3b8", width=2)
            slot = plot_w // n
            bw = max(18, int(slot * 0.58))
            for idx, (lbl, val) in enumerate(zip(labels, values)):
                bh = max(4, int((val / max_v) * (plot_h - 25)))
                x0 = pad_l + idx * slot + (slot - bw) // 2
                y0 = (h - pad_b) - bh
                x1 = x0 + bw
                y1 = h - pad_b
                c = COLORS_LIST[idx % len(COLORS_LIST)]
                draw.rectangle([x0, y0, x1, y1], fill=c)
                draw.text((x0, max(pad_t, y0 - 20)), f"{val:,.0f}", fill="#0f172a")
                draw.text((x0, y1 + 12), str(lbl)[:14], fill="#334155")

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img.save(tmp.name, format="PNG")
        return tmp.name
    except Exception:
        return None


def create_chart_from_data(
    chart_type: str,
    labels: List[str],
    values: List[float],
    title: str = "",
    color: str = "#667eea",
) -> Optional[str]:
    """ينشئ صورة رسم بياني ويعيد مسار الملف."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor("#f8f9ff")
        ax.set_facecolor("#f8f9ff")

        if chart_type == "bar":
            bars = ax.bar(labels, values, color=COLORS_LIST[:len(labels)])
            top_v = max(values) if values else 1
            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + top_v * 0.01,
                    f"{val:,.0f}",
                    ha="center", va="bottom", fontsize=9, fontweight="bold",
                )
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
        elif chart_type == "pie":
            ax.pie(
                values, labels=labels, autopct="%1.1f%%",
                colors=COLORS_LIST[:len(labels)], startangle=90, pctdistance=0.85,
            )
        elif chart_type == "line":
            ax.plot(labels, values, color=color, linewidth=2.5, marker="o", markersize=7)
            ax.fill_between(range(len(labels)), values, alpha=0.15, color=color)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
        elif chart_type == "horizontal_bar":
            ax.barh(labels, values, color=COLORS_LIST[:len(labels)])
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        if title:
            ax.set_title(title, fontsize=13, fontweight="bold", pad=12)

        plt.tight_layout()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(tmp.name, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        return tmp.name
    except Exception:
        return _draw_chart_with_pillow(chart_type, labels, values, title, color)
