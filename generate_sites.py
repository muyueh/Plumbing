from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import csv
import html
import re
from typing import List, Optional

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "google-2025-11-24.csv"
IMAGES_FILE = ROOT / "Scrape-details-from-google.com--4--2025-11-24.csv"
DOCS_DIR = ROOT / "docs"


def _clean(text: str | None) -> str:
    return (text or "").strip()


def choose_first(row: dict[str, str], keys: List[str]) -> Optional[str]:
    for key in keys:
        value = _clean(row.get(key))
        if value and value != "·":
            return value
    return None


def extract_status(row: dict[str, str]) -> Optional[str]:
    for key in ["W4Efsd (4)", "W4Efsd (5)", "W4Efsd (6)"]:
        value = _clean(row.get(key))
        if any(token in value for token in ["營業", "打烊"]) and value:
            return value
    return None


def extract_address(row: dict[str, str]) -> Optional[str]:
    for key in ["W4Efsd (3)", "W4Efsd (4)", "W4Efsd (5)", "c2ePGf", "NlVald"]:
        value = _clean(row.get(key))
        if value and value != "·":
            return value
    return None


def slugify(value: str, existing: set[str]) -> str:
    value = re.sub(r"[^\w\- ]+", "", value, flags=re.UNICODE).strip().lower()
    value = re.sub(r"\s+", "-", value)
    base = value or "store"
    candidate = base
    counter = 2
    while candidate in existing:
        candidate = f"{base}-{counter}"
        counter += 1
    existing.add(candidate)
    return candidate


def read_rows() -> list[dict[str, str]]:
    with DATA_FILE.open(newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def read_images() -> list[dict[str, str]]:
    with IMAGES_FILE.open(newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


@dataclass
class Listing:
    name: str
    rating: Optional[str]
    reviews: Optional[str]
    category: Optional[str]
    address: Optional[str]
    status: Optional[str]
    hours: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    map_link: Optional[str]
    directions_link: Optional[str]
    image: Optional[str]
    slug: str

    @property
    def review_count(self) -> Optional[str]:
        value = _clean(self.reviews)
        return value.strip("()") if value else None


STYLE = """
:root {
  --bg: #f5f7fb;
  --card: #ffffff;
  --text: #1f2933;
  --accent: #0c7bdc;
  --muted: #5f6b7c;
}
* { box-sizing: border-box; }
body {
  font-family: 'Segoe UI', 'Noto Sans TC', system-ui, sans-serif;
  margin: 0;
  background: var(--bg);
  color: var(--text);
}
header {
  background: linear-gradient(120deg, #0c7bdc, #14a3d9);
  color: white;
  padding: 2.5rem 1.5rem;
  text-align: center;
  box-shadow: 0 3px 12px rgba(0,0,0,0.15);
}
header h1 { margin: 0 0 0.5rem; font-size: 2.3rem; }
header p { margin: 0; font-size: 1.1rem; color: rgba(255,255,255,0.9); }
main { padding: 2rem 1.5rem 3rem; max-width: 1100px; margin: 0 auto; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.5rem; }
.card {
  background: var(--card);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 18px rgba(15,23,42,0.08);
  display: flex;
  flex-direction: column;
  transition: transform 120ms ease, box-shadow 120ms ease;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 26px rgba(15,23,42,0.12);
}
.card img { width: 100%; height: 180px; object-fit: cover; background: #dce4ef; }
.card .content { padding: 1.1rem 1.25rem 1.25rem; display: flex; flex-direction: column; gap: 0.35rem; flex: 1; }
.card h2 { margin: 0; font-size: 1.2rem; color: var(--text); }
.meta { color: var(--muted); font-size: 0.95rem; }
.badge { display: inline-flex; align-items: center; gap: 0.25rem; background: #e8f3ff; color: var(--accent); padding: 0.25rem 0.6rem; border-radius: 999px; font-weight: 600; font-size: 0.9rem; }
.actions { margin-top: auto; display: flex; gap: 0.6rem; flex-wrap: wrap; }
.actions a { flex: 1; text-align: center; text-decoration: none; color: white; background: var(--accent); padding: 0.55rem 0.7rem; border-radius: 10px; font-weight: 600; }
.actions a.secondary { background: #e5ebf3; color: var(--text); }
.section { background: var(--card); padding: 1.5rem; border-radius: 16px; box-shadow: 0 4px 18px rgba(15,23,42,0.08); margin-top: 1.5rem; }
.section h3 { margin-top: 0; }
dt { font-weight: 700; color: var(--muted); }
dd { margin: 0 0 0.75rem; }
.footer { text-align: center; color: var(--muted); margin-top: 2rem; font-size: 0.9rem; }
@media (max-width: 640px) {
  header h1 { font-size: 1.8rem; }
  .card img { height: 150px; }
}
"""


def render_listing(listing: Listing) -> str:
    def fmt(label: str, value: Optional[str]) -> str:
        return f"<dt>{html.escape(label)}</dt><dd>{html.escape(value)}</dd>" if value else ""

    image_tag = f"<img src='{html.escape(listing.image)}' alt='{html.escape(listing.name)}'>" if listing.image else ""
    return f"""
<!DOCTYPE html>
<html lang='zh-Hant'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>{html.escape(listing.name)} | 台北水電行索引</title>
  <style>{STYLE}</style>
</head>
<body>
  <header>
    <h1>{html.escape(listing.name)}</h1>
    <p>來自 Google 地圖的聯絡資訊彙整</p>
  </header>
  <main>
    <div class='section'>
      {image_tag}
      <div class='content'>
        <div class='badge'>評分 {html.escape(listing.rating or '無')} · {html.escape(listing.review_count or '0')} 則評論</div>
        <p class='meta'>{html.escape(listing.category or '未提供分類')}</p>
        <dl>
          {fmt('地址', listing.address)}
          {fmt('營業狀態', listing.status)}
          {fmt('營業時間', listing.hours)}
          {fmt('電話', listing.phone)}
          {fmt('官方網站', listing.website)}
        </dl>
        <div class='actions'>
          {f"<a href='{html.escape(listing.map_link)}' target='_blank' rel='noopener'>查看地圖</a>" if listing.map_link else ''}
          {f"<a class='secondary' href='{html.escape(listing.directions_link)}' target='_blank' rel='noopener'>規劃路線</a>" if listing.directions_link else ''}
        </div>
      </div>
    </div>
    <div class='footer'>返回 <a href='../index.html'>水電行列表</a></div>
  </main>
</body>
</html>
"""


def render_index(listings: list[Listing]) -> str:
    cards = []
    for listing in listings:
        image = f"<img src='{html.escape(listing.image)}' alt='{html.escape(listing.name)}'>" if listing.image else ""
        rating = html.escape(listing.rating or "N/A")
        reviews = html.escape(listing.review_count or "0")
        cards.append(
            f"""
            <article class='card'>
              {image}
              <div class='content'>
                <h2>{html.escape(listing.name)}</h2>
                <div class='meta'>評分 {rating} · {reviews} 則評論</div>
                <p class='meta'>{html.escape(listing.address or listing.category or '未提供地址')}</p>
                <div class='actions'>
                  <a href='{listing.slug}/index.html'>開啟網站</a>
                  {f"<a class='secondary' href='{html.escape(listing.map_link)}' target='_blank' rel='noopener'>地圖</a>" if listing.map_link else ''}
                </div>
              </div>
            </article>
            """
        )
    cards_html = "\n".join(cards)
    return f"""
<!DOCTYPE html>
<html lang='zh-Hant'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>台北水電行索引</title>
  <style>{STYLE}</style>
</head>
<body>
  <header>
    <h1>台北水電行索引</h1>
    <p>來自資料檔案的 {len(listings)} 間水電行資訊，每一間都有專屬的 GitHub Pages</p>
  </header>
  <main>
    <div class='grid'>
      {cards_html}
    </div>
  </main>
</body>
</html>
"""


def build() -> list[Listing]:
    rows = read_rows()
    images = read_images()
    slugs: set[str] = set()
    listings: list[Listing] = []

    for row, image_row in zip(rows, images):
        name = _clean(row.get("qBF1Pd"))
        if not name:
            continue
        listing = Listing(
            name=name,
            rating=_clean(row.get("MW4etd")) or None,
            reviews=_clean(row.get("UY7F9")) or None,
            category=choose_first(row, ["W4Efsd", "ah5Ghc", "ah5Ghc (2)"]),
            address=extract_address(row),
            status=extract_status(row),
            hours=choose_first(row, ["W4Efsd (5)", "W4Efsd (6)", "M4A5Cf"]),
            phone=_clean(row.get("UsdlK")) or None,
            website=choose_first(row, ["lcr4fd href", "bm892c href"]),
            map_link=_clean(row.get("hfpxzc href")) or None,
            directions_link=_clean(row.get("bm892c href")) or None,
            image=_clean(image_row.get("aoRNLd src")) or None,
            slug=slugify(name, slugs),
        )
        listings.append(listing)

    DOCS_DIR.mkdir(exist_ok=True)
    for listing in listings:
        store_dir = DOCS_DIR / listing.slug
        store_dir.mkdir(parents=True, exist_ok=True)
        (store_dir / "index.html").write_text(render_listing(listing), encoding="utf-8")

    (DOCS_DIR / "index.html").write_text(render_index(listings), encoding="utf-8")
    return listings


if __name__ == "__main__":
    listings = build()
    print(f"Generated {len(listings)} pages in docs/")
