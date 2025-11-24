import csv
import json
import re
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "google-2025-11-24.csv"
DETAIL_FILE = ROOT / "Scrape-details-from-google.com--4--2025-11-24.csv"
DOCS_DIR = ROOT / "docs"
BUSINESS_DIR = DOCS_DIR / "businesses"
ASSETS_DIR = DOCS_DIR / "assets"


def slugify(name: str, fallback: str) -> str:
    ascii_name = name.lower().encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-")
    return slug or fallback


def parse_review_count(text: str) -> int:
    digits = re.sub(r"[^0-9]", "", text)
    return int(digits) if digits else 0


def load_images() -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    with DETAIL_FILE.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        for row in reader:
            if len(row) < 2:
                continue
            map_url, image_url = row[0].strip(), row[1].strip()
            if map_url and image_url:
                mapping[map_url] = image_url
    return mapping


def load_businesses(image_map: Dict[str, str]) -> List[dict]:
    businesses: List[dict] = []
    with DATA_FILE.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if not row or len(row) < 14:
                continue
            map_url = row[1].strip()
            name = row[3].strip()
            if not map_url or not name:
                continue
            rating = row[4].strip()
            reviews = parse_review_count(row[5])
            category = row[6].strip()
            address = row[8].strip()
            status = row[9].strip()
            hours_note = row[10].strip()
            phone = row[12].strip()
            website = row[13].strip()
            highlight = row[2].strip()

            slug = slugify(name, f"business-{len(businesses) + 1}")
            image_url = image_map.get(map_url, "")

            businesses.append(
                {
                    "slug": slug,
                    "name": name,
                    "map_url": map_url,
                    "rating": rating,
                    "reviews": reviews,
                    "category": category,
                    "address": address,
                    "status": status,
                    "hours_note": hours_note,
                    "phone": phone,
                    "website": website,
                    "image_url": image_url,
                    "highlight": highlight,
                }
            )
    return businesses


def render_index(businesses: List[dict]) -> str:
    cards = []
    for biz in businesses:
        badge = f"<span class=\"badge\">{biz['highlight']}</span>" if biz["highlight"] else ""
        image_section = (
            f"<div class=\"card-image\" style=\"background-image:url('{biz['image_url']}')\"></div>"
            if biz["image_url"]
            else "<div class=\"card-image placeholder\">無照片</div>"
        )
        cards.append(
            f"""
            <article class=\"card\">
              {badge}
              {image_section}
              <div class=\"card-body\">
                <h2>{biz['name']}</h2>
                <p class=\"meta\">{biz['category']}</p>
                <p class=\"rating\">⭐ {biz['rating']} ({biz['reviews']} 則評論)</p>
                <p class=\"address\">📍 {biz['address']}</p>
                <p class=\"status\">{biz['status']} {biz['hours_note']}</p>
                <a class=\"button\" href=\"businesses/{biz['slug']}.html\">查看店家網站</a>
              </div>
            </article>
            """
        )
    cards_html = "\n".join(cards)
    return f"""<!doctype html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>台北水電行地圖 | Plumbing Directory</title>
  <link rel=\"stylesheet\" href=\"assets/style.css\">
</head>
<body>
  <header class=\"hero\">
    <h1>台北水電行索引</h1>
    <p>為每一家店家打造的 GitHub Pages 靜態網站，快速找到水電服務、電話與位置連結。</p>
  </header>
  <main class=\"grid\">
    {cards_html}
  </main>
  <footer class=\"footer\">資料來源：google-2025-11-24.csv</footer>
</body>
</html>
"""


def render_detail(biz: dict) -> str:
    website_link = (
        f"<a class=\"button secondary\" href=\"{biz['website']}\" target=\"_blank\" rel=\"noopener noreferrer\">官方網站</a>"
        if biz["website"]
        else ""
    )
    phone_line = f"<p class=\"info\">📞 {biz['phone']}</p>" if biz["phone"] else ""
    image_section = (
        f"<img class=\"hero-image\" src=\"{biz['image_url']}\" alt=\"{biz['name']} 外觀\">"
        if biz["image_url"]
        else "<div class=\"hero-image placeholder\">尚無照片</div>"
    )
    highlight = f"<p class=\"badge\">{biz['highlight']}</p>" if biz["highlight"] else ""

    return f"""<!doctype html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{biz['name']} | 台北水電行</title>
  <link rel=\"stylesheet\" href=\"../assets/style.css\">
</head>
<body>
  <header class=\"sub-hero\">
    <a class=\"back-link\" href=\"../index.html\">← 返回索引</a>
    <h1>{biz['name']}</h1>
    <p class=\"meta\">{biz['category']}</p>
    {highlight}
  </header>
  <main class=\"detail\">
    {image_section}
    <section class=\"details\">
      <p class=\"rating\">⭐ {biz['rating']} ({biz['reviews']} 則評論)</p>
      <p class=\"info\">📍 地址：{biz['address']}</p>
      <p class=\"info\">⏰ {biz['status']} {biz['hours_note']}</p>
      {phone_line}
      <div class=\"actions\">
        <a class=\"button\" href=\"{biz['map_url']}\" target=\"_blank\" rel=\"noopener noreferrer\">查看地圖</a>
        {website_link}
      </div>
    </section>
  </main>
</body>
</html>
"""


def write_assets():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / "style.css").write_text(
        """
:root {
  --bg: #0f172a;
  --card: #111827;
  --text: #e5e7eb;
  --muted: #94a3b8;
  --accent: #38bdf8;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background: radial-gradient(circle at 10% 20%, #1e293b, #0f172a 35%);
  color: var(--text);
  min-height: 100vh;
}
.hero, .sub-hero {
  text-align: center;
  padding: 3rem 1.5rem 2rem;
}
.hero h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
.hero p { max-width: 720px; margin: 0 auto; color: var(--muted); }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  padding: 0 1.5rem 2.5rem;
  max-width: 1200px;
  margin: 0 auto;
}
.card {
  background: linear-gradient(135deg, #0b1221, #0f172a);
  border: 1px solid #1f2937;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.45);
  position: relative;
}
.card-image {
  height: 180px;
  background-size: cover;
  background-position: center;
}
.card-image.placeholder,
.hero-image.placeholder {
  display: grid;
  place-items: center;
  color: var(--muted);
  background: #0b1221;
}
.card-body { padding: 1.25rem; }
.card h2 { margin: 0 0 0.35rem; font-size: 1.2rem; }
.card .meta { color: var(--muted); margin: 0 0 0.25rem; }
.card .rating { margin: 0 0 0.35rem; }
.card .address, .card .status { margin: 0 0 0.25rem; color: var(--muted); }
.button {
  display: inline-block;
  margin-top: 0.6rem;
  padding: 0.6rem 1rem;
  background: linear-gradient(135deg, #0ea5e9, #38bdf8);
  color: #0b1221;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  transition: transform 120ms ease, box-shadow 120ms ease;
}
.button.secondary {
  background: linear-gradient(135deg, #a855f7, #8b5cf6);
  color: #0b1221;
}
.button:hover { transform: translateY(-2px); box-shadow: 0 15px 30px -12px rgba(56,189,248,0.6); }
.footer {
  text-align: center;
  color: var(--muted);
  padding: 1rem 0 2rem;
  font-size: 0.9rem;
}
.badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(248, 113, 113, 0.15);
  color: #fca5a5;
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  border: 1px solid rgba(248, 113, 113, 0.4);
}
.sub-hero {
  padding-bottom: 1rem;
}
.sub-hero h1 { margin: 0.35rem 0; font-size: 2rem; }
.sub-hero .meta { color: var(--muted); margin: 0; }
.back-link {
  color: var(--accent);
  text-decoration: none;
}
.detail {
  max-width: 960px;
  margin: 0 auto;
  padding: 1.5rem;
  display: grid;
  gap: 1.25rem;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}
.hero-image {
  width: 100%;
  border-radius: 14px;
  border: 1px solid #1f2937;
  box-shadow: 0 20px 35px -18px rgba(0,0,0,0.55);
}
.details .info { color: var(--muted); margin: 0.25rem 0; }
.details .rating { margin: 0 0 0.35rem; }
.actions { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.75rem; }
@media (max-width: 640px) {
  .hero h1 { font-size: 2rem; }
}
""",
        encoding="utf-8",
    )


def write_pages(businesses: List[dict]):
    DOCS_DIR.mkdir(exist_ok=True)
    BUSINESS_DIR.mkdir(exist_ok=True)
    (DOCS_DIR / "index.html").write_text(render_index(businesses), encoding="utf-8")
    for biz in businesses:
        (BUSINESS_DIR / f"{biz['slug']}.html").write_text(render_detail(biz), encoding="utf-8")
    # also export raw data for reference
    (DOCS_DIR / "businesses.json").write_text(json.dumps(businesses, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    image_map = load_images()
    businesses = load_businesses(image_map)
    write_assets()
    write_pages(businesses)


if __name__ == "__main__":
    main()
