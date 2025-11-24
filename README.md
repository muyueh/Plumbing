# Plumbing

這個專案會把 `google-2025-11-24.csv` 與 `Scrape-details-from-google.com--4--2025-11-24.csv` 裡的水電行資料轉成 GitHub Pages 的靜態網站。`docs/` 目錄可直接設定成 Pages 的發佈來源：

- `docs/index.html`：所有水電行的索引卡片，包含評分、地址與營業狀態。
- `docs/businesses/<slug>.html`：每一家水電行的獨立頁面，提供地圖連結、電話與照片。
- `docs/assets/style.css`：深色系的共用樣式。
- `docs/businesses.json`：轉換後的原始資料，方便檢查與擴充。

## 如何重新生成網站

1. 安裝 Python 3（內建標準函式庫即可）。
2. 執行下列指令，即會重新解析 CSV 並覆寫 `docs/` 內容：

   ```bash
   python generate_site.py
   ```

3. 將 `docs/` 設為 GitHub Pages 發佈路徑後，索引與各家店面的獨立頁面就會自動上線。
