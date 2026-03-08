import requests
import json
from decimal import Decimal, getcontext

# 設定精度
getcontext().prec = 10

def get_bybit_funding_rates(assets):
    """
    從 Bybit Tickers 接口抓取費率與週期
    assets: ["BTC", "ETH", "HYPE"]
    """
    url = "https://api.bybit.com/v5/market/tickers?category=linear"
    
    # 統一轉大寫
    target_assets = [a.upper() for a in assets]
    temp_map = {}

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('retCode') == 0:
                # 遍歷 Bybit 回傳的所有合約
                all_items = data['result'].get('list', [])
                
                for item in all_items:
                    symbol = item['symbol'] # 例如 "BTCUSDT"
                    
                    # 只過濾 USDT 永續合約
                    if not symbol.endswith("USDT"):
                        continue
                    
                    # 取得幣種名稱 (去掉 USDT)
                    coin = symbol.replace("USDT", "")
                    
                    if coin in target_assets:
                        # --- 讀取 Bybit 提供的原始數據 ---
                        raw_rate = Decimal(item['fundingRate'])
                        interval_hrs = Decimal(item.get('fundingIntervalHour', 8)) # 抓取週期，預設 8
                        
                        # --- 標準化為 8H 邏輯 ---
                        # 如果是 8H，multiplier = 1
                        # 如果是 1H，multiplier = 8
                        multiplier = Decimal(8) / interval_hrs
                        standardized_rate = (raw_rate * multiplier * Decimal(100))
                        
                        temp_map[coin] = {
                            "exchange": "Bybit",
                            "symbol": coin,
                            "rate": float(standardized_rate.quantize(Decimal('0.00001'))),
                            "interval": "8H" # 統一顯示標準化後的週期
                        }
        else:
            print(f"❌ Bybit 請求失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Bybit 發生錯誤: {e}")

    # 按照傳入 assets 的順序回傳
    final_results = []
    for coin in target_assets:
        if coin in temp_map:
            final_results.append(temp_map[coin])
        else:
            final_results.append({
                "exchange": "Bybit",
                "symbol": coin,
                "rate": "N/A",
                "interval": "8H"
            })
            
    return final_results

if __name__ == "__main__":
    # 測試執行
    test_assets = ["BTC", "ETH", "SOL", "HYPE"]
    print(json.dumps(get_bybit_funding_rates(test_assets), indent=4))