from __future__ import annotations

import csv
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

DATA_FILE = Path("google-2025-11-24.csv")
PHOTO_FILE = Path("Scrape-details-from-google.com--4--2025-11-24.csv")
OUTPUT_DIR = Path("docs")
ASSET_DIR = OUTPUT_DIR / "assets"
STORE_DIR = OUTPUT_DIR / "stores"


@dataclass
class PlumbingShop:
    name: str
    slug: str
    maps_url: str
    rating: str
    reviews: str
    category: str
    address: str
    status: str
    hours_note: str
    phone: str
    website: str
    services: List[str]
    photo: str


def sanitize_slug(name: str, existing: set, index: int) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    if not base:
        base = f"store-{index}"
    slug = base
    suffix = 2
    while slug in existing:
        slug = f"{base}-{suffix}"
        suffix += 1
    existing.add(slug)
    return slug


def load_photos() -> Dict[str, str]:
    photos: Dict[str, str] = {}
    if not PHOTO_FILE.exists():
        return photos
    with PHOTO_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            href = (row.get("hfpxzc href") or "").strip()
            src = (row.get("aoRNLd src") or "").strip()
            if href:
                photos[href] = src
    return photos


def load_shops() -> List[PlumbingShop]:
    photos = load_photos()
    shops: List[PlumbingShop] = []
    seen_slugs: set = set()

    def pick_address(row: Dict[str, str]) -> str:
        candidates = [
            row.get("W4Efsd (2)"),
            row.get("W4Efsd (3)"),
            row.get("W4Efsd (4)"),
            row.get("W4Efsd (5)"),
        ]
        for value in candidates:
            cleaned = (value or "").strip()
            if not cleaned or cleaned in {"·", "⋅"}:
                continue
            if any(token in cleaned for token in ("營業", "打烊")):
                continue
            return cleaned
        return ""

    def pick_status(row: Dict[str, str]) -> str:
        candidates = [row.get("W4Efsd (4)"), row.get("W4Efsd (5)"), row.get("W4Efsd (6)")]
        for value in candidates:
            cleaned = (value or "").strip()
            if not cleaned or cleaned in {"·", "⋅"}:
                continue
            if any(token in cleaned for token in ("營業", "打烊")):
                return cleaned
        return ""

    def pick_hours(row: Dict[str, str], status: str) -> str:
        candidates = [row.get("W4Efsd (5)"), row.get("W4Efsd (6)")]
        for value in candidates:
            cleaned = (value or "").strip()
            if not cleaned or cleaned in {"·", "⋅"}:
                continue
            if cleaned == status:
                continue
            return cleaned
        return ""

    with DATA_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            name = (row.get("qBF1Pd") or "").strip()
            if not name:
                continue
            slug = sanitize_slug(name, seen_slugs, idx)
            maps_url = (row.get("hfpxzc href") or "").strip()
            rating = (row.get("MW4etd") or "").strip()
            reviews = (row.get("UY7F9") or "").strip().strip("()")
            category = (row.get("W4Efsd") or "").strip()
            address = pick_address(row)
            status = pick_status(row)
            hours_note = pick_hours(row, status)
            phone = (row.get("UsdlK") or "").strip()
            website = (row.get("lcr4fd href") or "").strip()

            services = [
                (row.get("R8c4Qb") or "").strip(),
                (row.get("R8c4Qb (2)") or "").strip(),
                (row.get("ah5Ghc") or "").strip(),
                (row.get("ah5Ghc (2)") or "").strip(),
            ]
            services = [s for s in services if s]

            photo = photos.get(maps_url, "")

            shops.append(
                PlumbingShop(
                    name=name,
                    slug=slug,
                    maps_url=maps_url,
                    rating=rating,
                    reviews=reviews,
                    category=category,
                    address=address,
                    status=status,
                    hours_note=hours_note,
                    phone=phone,
                    website=website,
                    services=services,
                    photo=photo,
                )
            )
    return shops


def write_assets():
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    style = """
:root {
  --bg: #0f172a;
  --card: #111827;
  --text: #e2e8f0;
  --muted: #cbd5e1;
  --accent: #38bdf8;
  --border: #1f2937;
}

* { box-sizing: border-box; }

body {
  font-family: 'Noto Sans TC', 'Inter', system-ui, -apple-system, sans-serif;
  margin: 0;
  background: linear-gradient(180deg, #0f172a 0%, #0b1220 100%);
  color: var(--text);
}

a { color: var(--accent); text-decoration: none; }

.header {
  padding: 48px 24px 24px;
  text-align: center;
}

.header h1 { margin: 0; font-size: 2.4rem; letter-spacing: 0.02em; }

.header p { margin: 12px 0 0; color: var(--muted); }

.container { max-width: 1100px; margin: 0 auto; padding: 0 24px 48px; }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, border-color 0.2s ease;
  box-shadow: 0 15px 35px rgba(0,0,0,0.25);
}

.card:hover { transform: translateY(-4px); border-color: #2dd4bf; }

.card img { width: 100%; height: 160px; object-fit: cover; background: #0b1220; }

.card-body { padding: 16px; display: flex; flex-direction: column; gap: 8px; }

.card .category { color: var(--accent); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.85rem; }

.card h2 { margin: 0; font-size: 1.2rem; }

.card .meta { color: var(--muted); font-size: 0.95rem; }

.card .actions { margin-top: auto; display: flex; gap: 10px; flex-wrap: wrap; }

.btn {
  background: #1e293b;
  color: var(--text);
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  font-weight: 600;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.btn:hover { background: #152033; border-color: var(--accent); }

.detail-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 15px 35px rgba(0,0,0,0.25);
}

.detail-header { display: flex; flex-direction: column; gap: 12px; }

.detail-header h1 { margin: 0; font-size: 2rem; }

.tag { display: inline-block; background: #1f2937; color: var(--muted); padding: 6px 10px; border-radius: 999px; font-size: 0.9rem; margin-right: 8px; }

.contact-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-top: 16px; }

.info-row { display: flex; gap: 10px; align-items: flex-start; color: var(--muted); }

.photo { width: 100%; border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 10px 30px rgba(0,0,0,0.25); object-fit: cover; }

.section { margin-top: 32px; }

.section h3 { margin: 0 0 12px; }

ul { padding-left: 18px; color: var(--muted); }

.footer { text-align: center; color: var(--muted); padding: 32px 0; font-size: 0.9rem; }
"""
    (ASSET_DIR / "style.css").write_text(style, encoding="utf-8")


def render_index(shops: List[PlumbingShop]):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cards = []
    for shop in shops:
        photo_tag = (
            f'<img src="{html.escape(shop.photo)}" alt="{html.escape(shop.name)} 的照片">'
            if shop.photo
            else '<div style="height:160px;background:#0b1220"></div>'
        )
        review_text = f"{shop.reviews} 則評論" if shop.reviews else "尚無評論數"
        address_text = shop.address or "尚未提供地址"
        cards.append(
            f"""
            <article class=\"card\">
              {photo_tag}
              <div class=\"card-body\">
                <div class=\"category\">{html.escape(shop.category or '水電行')}</div>
                <h2><a href=\"stores/{shop.slug}.html\">{html.escape(shop.name)}</a></h2>
                <div class=\"meta\">⭐ {html.escape(shop.rating or 'N/A')} ・ {html.escape(review_text)}</div>
                <div class=\"meta\">📍 {html.escape(address_text)}</div>
                <div class=\"actions\">
                  <a class=\"btn\" href=\"stores/{shop.slug}.html\">查看詳細</a>
                  <a class=\"btn\" href=\"{html.escape(shop.maps_url)}\" target=\"_blank\" rel=\"noreferrer\">Google Maps</a>
                </div>
              </div>
            </article>
            """
        )

    content = f"""<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>水電行名錄 - GitHub Pages</title>
  <link rel=\"stylesheet\" href=\"assets/style.css\">
</head>
<body>
  <header class=\"header\">
    <h1>台北水電行名錄</h1>
    <p>共 {len(shops)} 間店家，點擊即可查看獨立介紹頁面。</p>
  </header>
  <main class=\"container\">
    <section class=\"grid\">
      {''.join(cards)}
    </section>
  </main>
  <div class=\"footer\">由資料檔自動產生，適用於 GitHub Pages 靜態網站。</div>
</body>
</html>
"""

    (OUTPUT_DIR / "index.html").write_text(content, encoding="utf-8")


def render_detail(shop: PlumbingShop):
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    services_list = "".join(f"<li>{html.escape(s)}</li>" for s in shop.services) or "<li>尚未提供服務說明</li>"
    photo_block = (
        f'<img class="photo" src="{html.escape(shop.photo)}" alt="{html.escape(shop.name)} 的照片">'
        if shop.photo else "<div class=\"photo\" style=\"height:260px; display:flex; align-items:center; justify-content:center; color:#64748b;\">無可用照片</div>"
    )
    contact_rows = []
    if shop.address:
        contact_rows.append(f"<div class=\"info-row\">📍 {html.escape(shop.address)}</div>")
    if shop.phone:
        contact_rows.append(f"<div class=\"info-row\">📞 <a href=\"tel:{html.escape(shop.phone)}\">{html.escape(shop.phone)}</a></div>")
    if shop.status:
        contact_rows.append(f"<div class=\"info-row\">⏰ {html.escape(shop.status)} {html.escape(shop.hours_note)}</div>")
    elif shop.hours_note:
        contact_rows.append(f"<div class=\"info-row\">⏰ {html.escape(shop.hours_note)}</div>")

    link_buttons = []
    if shop.website:
        link_buttons.append(f"<a class=\"btn\" href=\"{html.escape(shop.website)}\" target=\"_blank\" rel=\"noreferrer\">官方網站</a>")
    if shop.maps_url:
        link_buttons.append(f"<a class=\"btn\" href=\"{html.escape(shop.maps_url)}\" target=\"_blank\" rel=\"noreferrer\">Google Maps</a>")

    rating_text = f"⭐ {html.escape(shop.rating or 'N/A')}" + (f"（{html.escape(shop.reviews)} 則評論）" if shop.reviews else "")

    content = f"""<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{html.escape(shop.name)} - 水電行介紹</title>
  <link rel=\"stylesheet\" href=\"../assets/style.css\">
</head>
<body>
  <header class=\"header\">
    <p><a href=\"../index.html\">← 返回總覽</a></p>
    <h1>{html.escape(shop.name)}</h1>
    <div class=\"tag\">{html.escape(shop.category or '水電行')}</div>
    <div class=\"tag\">{rating_text}</div>
  </header>
  <main class=\"container\">
    <section class=\"detail-card\">
      <div class=\"detail-header\">
        {photo_block}
        <div class=\"contact-grid\">
          {''.join(contact_rows) or '<div class="info-row">暫無聯絡資訊</div>'}
        </div>
        <div class=\"actions\" style=\"margin-top:12px;\">{''.join(link_buttons)}</div>
      </div>
      <div class=\"section\">
        <h3>服務資訊</h3>
        <ul>{services_list}</ul>
      </div>
    </section>
  </main>
  <div class=\"footer\">此頁面由資料集自動產生，可直接部署於 GitHub Pages。</div>
</body>
</html>
"""
    (STORE_DIR / f"{shop.slug}.html").write_text(content, encoding="utf-8")


def build_site():
    shops = load_shops()
    write_assets()
    render_index(shops)
    for shop in shops:
        render_detail(shop)


if __name__ == "__main__":
    build_site()
