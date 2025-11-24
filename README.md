# Plumbing

這個專案利用現有的 Google Maps 抓取資料，幫每一家水電行產生一個可直接部署到 GitHub Pages 的靜態網站。產生的頁面位於 `docs/` 底下，首頁會列出所有店家卡片並連結到獨立介紹頁。

## 如何重新產生網站
1. 確認兩份資料檔都放在專案根目錄：
   - `google-2025-11-24.csv`
   - `Scrape-details-from-google.com--4--2025-11-24.csv`
2. 執行下列指令產出 `docs/` 內的頁面與樣式檔：

   ```bash
   python generate_sites.py
   ```

完成後即可將 repo 的 GitHub Pages 指向 `docs/`，每間水電行都會有一個獨立介紹頁面。
