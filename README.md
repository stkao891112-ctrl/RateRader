專案簡介
<br>
<br>
###使用此網址訪問作品 http://35.206.235.178:8080/                                                  
<br>
RateRadar
是一個高效能的加密貨幣數據聚合工具，專為解決不同交易平台 API 格式不一的問題。本專案能同時監控多個主流交易所（Binance, OKX, Bybit, Bitget, Backpack, Hyperliquid）的永續合約資金費率（Funding Rate），並將異質數據清洗、標準化，最後透過 Flask API 提供統一的數據介面供前端調用。
<br>
<br>
<br>

核心技術棧
語言: Python

框架: Flask (RESTful API 實作)

數據處理: Requests (HTTP 請求), JSON (數據標準化)
<br>
<br>

專案特色與亮點
1. 多源數據標準化 (Data Normalization)
針對不同交易所的 API 結構（如欄位命名、時間戳格式、數值精度）設計轉換邏輯，將異質數據統一封裝為標準 JSON 格式。

支援平台: Binance, OKX, Bybit, Bitget, Backpack, Hyperliquid。

2. 資金費率即時監控
自動對接各家交易所的 Restful API，計算並比較不同幣種間的資金費率差異，幫助使用者快速捕捉套利機會或避險資訊。

3. 輕量化 API 接口
利用 Flask 建構輕量化後端，前端僅需發送一個 HTTP 請求即可獲取所有平台的彙整數據，大幅減少前端的開發複雜度與網路請求次數。
