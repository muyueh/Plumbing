# Plumbing GitHub Pages

此專案將 `google-2025-11-24.csv` 與 `Scrape-details-from-google.com--4--2025-11-24.csv` 內的水電行資料，轉成可直接部署到 GitHub Pages 的靜態網站。

## 產出內容
- `docs/index.html`：水電行總覽頁，列出每一間店的名稱、評分、地址與進入該店網站的連結。
- `docs/<店名slug>/index.html`：每間水電行的獨立頁面，包含圖片、評分/評論數、地址、營業資訊、電話、網站與地圖、路線按鈕。

## 如何重新產生頁面
1. 確認 CSV 資料檔存在於專案根目錄：
   - `google-2025-11-24.csv`
   - `Scrape-details-from-google.com--4--2025-11-24.csv`
2. 執行產生器：
   ```bash
   python generate_sites.py
   ```
3. 完成後新的靜態頁面會寫入 `docs/` 目錄，可直接用 GitHub Pages 的 `docs/` 模式發佈。

## GitHub Pages 設定提示
- 在 GitHub 專案設定的 **Pages** 中，將來源設為 `Deploy from a branch`，資料夾選擇 `main` 分支的 `/docs`。
- 佈署完成後，`docs/index.html` 會成為首頁，各店家子頁面則依自動產生的 slug 形成網址（如 `.../修繕家水電冷氣保哥/`）。
