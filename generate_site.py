import csv
import html
import json
import pathlib
import re
from typing import Dict, List

ROOT = pathlib.Path(__file__).parent
GOOGLE_CSV = ROOT / "google-2025-11-24.csv"
IMAGES_CSV = ROOT / "Scrape-details-from-google.com--4--2025-11-24.csv"
DATA_DIR = ROOT / "data"
STORES_DIR = ROOT / "stores"


def slugify(name: str) -> str:
    cleaned = name.strip().lower()
    slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", cleaned).strip("-")
    return slug or "store"


def load_images() -> Dict[str, str]:
    images: Dict[str, str] = {}
    if not IMAGES_CSV.exists():
        return images
    with IMAGES_CSV.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            link = row.get("hfpxzc href", "").strip()
            image = row.get("aoRNLd src", "").strip()
            if link and image:
                images[link] = image
    return images


def choose_address(row: Dict[str, str]) -> str:
    candidates = [row.get("W4Efsd (3)", ""), row.get("W4Efsd (4)", ""), row.get("UsdlK", "")]
    for candidate in candidates:
        if candidate and candidate not in {"·", ""}:
            return candidate.strip()
    return ""


def normalize_store(row: Dict[str, str], images: Dict[str, str]) -> Dict[str, str]:
    name = row.get("qBF1Pd", "").strip()
    if not name:
        return {}

    map_link = row.get("hfpxzc href", "").strip()
    status = row.get("W4Efsd (4)", "").strip()
    hours = row.get("W4Efsd (5)", "").strip()
    directions = row.get("R8c4Qb (2)", "").strip() or "規劃路線"
    category = row.get("W4Efsd", "").strip()
    website_link = row.get("lcr4fd href", "").strip()

    store = {
        "name": name,
        "slug": slugify(name),
        "rating": row.get("MW4etd", "").strip(),
        "reviews": row.get("UY7F9", "").strip().strip("()"),
        "category": category,
        "address": choose_address(row),
        "status": status,
        "hours": hours,
        "phone": row.get("UsdlK", "").strip(),
        "mapLink": map_link,
        "websiteLink": website_link,
        "image": images.get(map_link, ""),
        "directionsLabel": directions or "規劃路線",
        "services": row.get("ah5Ghc", "").strip(),
    }
    return store


def load_stores() -> List[Dict[str, str]]:
    images = load_images()
    stores: List[Dict[str, str]] = []
    slug_counts: Dict[str, int] = {}
    with GOOGLE_CSV.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            store = normalize_store(row, images)
            if store:
                base_slug = store["slug"]
                count = slug_counts.get(base_slug, 0)
                if count:
                    store["slug"] = f"{base_slug}-{count + 1}"
                slug_counts[base_slug] = count + 1
                stores.append(store)
    stores.sort(key=lambda s: s["name"])
    return stores


def write_json(stores: List[Dict[str, str]]):
    DATA_DIR.mkdir(exist_ok=True)
    output = DATA_DIR / "stores.json"
    output.write_text(json.dumps(stores, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output.relative_to(ROOT)} with {len(stores)} stores")


def base_template(title: str, body: str, back_link: str = "") -> str:
    back_html = f'<a class="back" href="{back_link}">← 返回列表</a>' if back_link else ""
    return f"""
<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{html.escape(title)}</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
  <link href=\"https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;600;700&display=swap\" rel=\"stylesheet\">
  <style>
    :root {{
      --bg: #f6f8fb;
      --card: #ffffff;
      --primary: #1f7a8c;
      --text: #1a1a1a;
      --muted: #5f6a86;
      --shadow: 0 10px 30px rgba(0,0,0,0.08);
      --radius: 16px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Noto Sans TC', system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
    }}
    header {{
      padding: 48px 24px 32px;
      text-align: center;
    }}
    h1 {{ margin: 0; font-size: 32px; }}
    p.subtitle {{ color: var(--muted); margin-top: 8px; }}
    .grid {{
      display: grid;
      gap: 20px;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      padding: 0 24px 48px;
      max-width: 1100px;
      margin: 0 auto;
    }}
    .card {{
      background: var(--card);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
      transition: transform 0.12s ease, box-shadow 0.12s ease;
      display: flex;
      flex-direction: column;
    }}
    .card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 14px 36px rgba(0,0,0,0.12);
    }}
    .card img {{ width: 100%; height: 180px; object-fit: cover; background: #e5eaf1; }}
    .card .content {{ padding: 16px 18px 18px; flex: 1; display: flex; flex-direction: column; gap: 6px; }}
    .meta {{ color: var(--muted); font-size: 14px; display: flex; gap: 10px; flex-wrap: wrap; }}
    .pill {{ background: #e5f6ff; color: var(--primary); padding: 3px 8px; border-radius: 12px; font-weight: 600; font-size: 12px; display: inline-flex; gap: 4px; align-items: center; }}
    a.button {{
      display: inline-flex;
      justify-content: center;
      align-items: center;
      gap: 8px;
      background: var(--primary);
      color: white;
      padding: 12px 16px;
      border-radius: 12px;
      text-decoration: none;
      font-weight: 700;
      margin-top: auto;
      transition: background 0.1s ease;
    }}
    a.button:hover {{ background: #155f70; }}
    .details {{
      max-width: 820px;
      margin: 0 auto;
      background: var(--card);
      padding: 24px;
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      display: grid;
      grid-template-columns: 1fr;
      gap: 18px;
    }}
    .hero img {{ width: 100%; border-radius: var(--radius); max-height: 320px; object-fit: cover; background: #e5eaf1; }}
    .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px 18px; }}
    .label {{ color: var(--muted); font-size: 14px; margin-bottom: 2px; }}
    .value {{ font-weight: 600; }}
    .back {{ color: var(--primary); text-decoration: none; font-weight: 700; display: inline-flex; gap: 6px; align-items: center; margin-bottom: 10px; }}
    footer {{ text-align: center; color: var(--muted); padding: 24px; font-size: 14px; }}
  </style>
</head>
<body>
  <header>
    {back_html}
    <h1>{html.escape(title)}</h1>
    <p class=\"subtitle\">水電行資料整理，方便快速找到合適的服務店家</p>
  </header>
  {body}
  <footer>資料來源：repo 提供的 Google 列表</footer>
</body>
</html>
"""


def render_index(stores: List[Dict[str, str]]):
    cards = []
    for store in stores:
        image_html = f"<img src=\"{html.escape(store['image'])}\" alt=\"{html.escape(store['name'])}\" />" if store["image"] else ""
        rating = store["rating"]
        reviews = store["reviews"]
        meta_parts = []
        if rating:
            meta_parts.append(f"⭐ {rating}")
        if reviews:
            meta_parts.append(f"{reviews} 則評論")
        if store["status"]:
            meta_parts.append(store["status"])
        meta = " · ".join(meta_parts)
        address = store["address"] or "地址未提供"
        card = f"""
        <article class=\"card\">
          {image_html}
          <div class=\"content\">
            <div class=\"pill\">{html.escape(store['category'] or '水電服務')}</div>
            <h2>{html.escape(store['name'])}</h2>
            <div class=\"meta\">{html.escape(meta)}</div>
            <div class=\"meta\">📍 {html.escape(address)}</div>
            <a class=\"button\" href=\"stores/{store['slug']}.html\">查看詳情</a>
          </div>
        </article>
        """
        cards.append(card)
    grid = "<section class=\"grid\">" + "\n".join(cards) + "</section>"
    html_text = base_template("水電行一覽", grid)
    (ROOT / "index.html").write_text(html_text, encoding="utf-8")
    print("Wrote index.html")


def render_store_page(store: Dict[str, str]):
    image_html = f"<div class=\"hero\"><img src=\"{html.escape(store['image'])}\" alt=\"{html.escape(store['name'])}\"></div>" if store["image"] else ""
    info_rows = []
    fields = [
        ("評價", store["rating"] and f"{store['rating']} ★ ({store['reviews']} 則評論)" or "暫無評價"),
        ("店家類型", store["category"] or "水電服務"),
        ("地址", store["address"] or "地址未提供"),
        ("電話", store["phone"] or "未提供"),
        ("營業資訊", store["hours"] or store["status"] or "未提供"),
        ("服務項目", store["services"] or "未提供"),
    ]
    for label, value in fields:
        info_rows.append(f"<div><div class=\"label\">{html.escape(label)}</div><div class=\"value\">{html.escape(value)}</div></div>")
    buttons = []
    if store["mapLink"]:
        buttons.append(f"<a class=\"button\" href=\"{html.escape(store['mapLink'])}\" target=\"_blank\">地圖 / {html.escape(store['directionsLabel'])}</a>")
    if store["websiteLink"]:
        buttons.append(f"<a class=\"button\" href=\"{html.escape(store['websiteLink'])}\" target=\"_blank\">官方網站</a>")
    buttons_html = "\n".join(buttons) or "<p class=\"meta\">尚無外部連結</p>"

    body = f"""
    <section class=\"details\">
      {image_html}
      <div class=\"info-grid\">{''.join(info_rows)}</div>
      <div>{buttons_html}</div>
    </section>
    """
    html_text = base_template(store["name"], body, "../index.html")
    (STORES_DIR / f"{store['slug']}.html").write_text(html_text, encoding="utf-8")


def render_stores(stores: List[Dict[str, str]]):
    STORES_DIR.mkdir(exist_ok=True)
    for store in stores:
        render_store_page(store)
    print(f"Generated {len(stores)} store pages")


def main():
    stores = load_stores()
    write_json(stores)
    render_index(stores)
    render_stores(stores)


if __name__ == "__main__":
    main()
