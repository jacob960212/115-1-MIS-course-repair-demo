# 校園設備報修系統

這是一個適合 MIS 課堂使用的最小前後端範例。學生透過網頁表單建立報修單，可選擇附上一張問題圖片。Flask 後端接收表單與圖片、產生案件編號，再將結果回傳網頁。

## 系統需求

- Windows 10/11
- Python 3.13.x
- 瀏覽器（Edge、Chrome 皆可）

## 第一次啟動

在此專案資料夾開啟 PowerShell，依序執行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

看到下列訊息後，以瀏覽器開啟 <http://127.0.0.1:5000>：

```text
Running on http://127.0.0.1:5000
```

按 `Ctrl + C` 可停止伺服器。

管理後台位址為 <http://127.0.0.1:5000/admin>。可在此查看案件並更新狀態。

## 第二次以後啟動

```powershell
.\.venv\Scripts\python.exe app.py
```

## 觀察重點

1. 在 `templates/index.html` 找到表單欄位。
2. 在 `static/app.js` 找到 `fetch("/api/tickets")`：前端在這裡呼叫後端 API。
3. 在 `app.py` 找到 `@app.post("/api/tickets")`：Python 在這裡接收、驗證並回傳資料。
4. 在 `templates/admin.html` 與 `static/admin.js` 看管理員如何透過 `PATCH /api/tickets/<案件編號>` 更新狀態。

## 注意事項

本範例把案件資料存在 Python 的記憶體中，停止或重啟程式後，資料會清空。
圖片保存在 `static/uploads/`，重啟後不會自動刪除；此目錄已排除版本控制。

## 問題圖片功能

- 每張報修單可選填一張 JPG/JPEG、PNG、GIF 或 WebP 圖片，上限 5 MB（5 × 1024 × 1024 bytes）。
- 前端以 `FormData` 傳送 `multipart/form-data`，不要手動設定 Content-Type，瀏覽器會加上必要的 boundary。
- 後端先驗證必填欄位，再檢查圖片大小、副檔名及實際圖片內容；未通過時不建立案件、不保存圖片。
- 使用 UUID 產生儲存檔名，`ticket.image` 回傳 `/static/uploads/...`；未附圖片時為 `null`。
- 前台與管理後台顯示縮圖，點擊可開啟原圖；無圖片顯示「未附圖片」。
- 原有 JSON 建立案件及 PATCH 更新狀態 API 仍可使用。

若已建立虛擬環境，更新後請先重新執行 ` .\.venv\Scripts\python.exe -m pip install -r requirements.txt` 安裝 Pillow，再啟動程式。

資料流：報修表單 → FormData → POST /api/tickets → 欄位與圖片驗證 → static/uploads 儲存 → ticket.image → 前台／管理後台縮圖。

影響檔案：`app.py`、`requirements.txt`、`.gitignore`、`templates/index.html`、`templates/admin.html`、`static/app.js`、`static/admin.js`、`static/images.js`、`static/style.css`、`README.md`。

### 驗收操作

1. 填妥欄位並附上合法圖片：案件成功建立，前台與後台可顯示縮圖並開啟原圖。
2. 不附圖片送出：案件成功建立，顯示「未附圖片」。
3. 選取不支援格式、改副檔名的假圖片或損壞圖片：拒絕建立並顯示錯誤。
4. 選取超過 5 MB 的圖片：提示大小上限，不建立案件。
5. 重新整理前後台：案件與圖片仍可查看；更新案件狀態不影響圖片。

案件仍屬教學用記憶體儲存，沒有帳號與存取控制，上傳圖片可透過靜態網址存取。
