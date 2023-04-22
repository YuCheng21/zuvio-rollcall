# Zuvio 自動點名

![overview](static/overview.png)

## Overview

這是一個大學生懶得去上課而做的在家自動點名程式。

透過 Selenium 套件模擬瀏覽器動作，自動登入 Zuvio 開啟點名網址，並且隨機重新整理網頁，查看點名是否已經開放。

當課程開啟點名後，將自動點擊按鈕，確認點名成功後退出程式。

## Environment

- python 3.9 or later

```bash
 pip install -r requirements.txt
 ```

## Run

 ```bash
 python app.py
 ```

啟動圖形應用程式，軟體操作步驟：

1. 輸入個人自訂配置
2. 點選`啟動點名`按鈕，開始自動化點名。

## Build

```bash
python setup.py build
```

打包成可執行檔案，輸出在 `./build` 目錄下，根據不同作業系統打包在相應的目錄名稱中，執行目錄中的 `./app.exe` 啟動圖形應用程式。

> 注意：Windows 11 必須使用 Python 3.9 以上版本構建。

## Structure

- `app.py`: 匯入 `app.ui` 樣式表並註冊介面元件，呼叫 `web_crawler.py` 執行程式邏輯。
- `app.ui`: 使用 QT Designer 產生的 GUI 樣式表，並使用 `app.py` 匯入，若使用 cx-freeze 打包則必須放在根目錄使用。
- `web_crawler.py`: Zuvio 自動點名類別，提供 `app.py` 呼叫。
- `settings.py`: 程式配置設定
- `setup.py`: 提供 `cx-freeze` 打包的腳本，配置構建應用程式的相關設定、路徑等。