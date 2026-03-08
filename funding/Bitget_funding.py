import requests
import json
from decimal import Decimal, getcontext

# 設定精度
getcontext().prec = 10

def get_bitget_funding_rates(assets):
    """
    從 Bitget current-fund-rate 接口抓取費率與週期
    assets: ["BTC", "ETH", "HYPE"]
    """
    # 這是你提供的批量接口
    url = "https://api.bitget.com/api/v2/mix/market/current-fund-rate?productType=USDT-FUTURES"
    
    # 統一轉大寫
    target_assets = [a.upper() for a in assets]
    temp_map = {}

    try:
        # Bitget 有時會擋無 Header 的請求，建議加上 User-Agent
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '00000': # Bitget 成功的代碼是 00000
                all_items = data.get('data', [])
                
                for item in all_items:
                    symbol = item['symbol'] # 例如 "BTCUSDT"
                    
                    # 過濾出 USDT 結算的合約 (Bitget 格式通常為 BTCUSDT)
                    if not symbol.endswith("USDT"):
                        continue
                    
                    coin = symbol.replace("USDT", "")
                    
                    if coin in target_assets:
                        # --- 讀取 Bitget 原始數據 ---
                        raw_rate = Decimal(item['fundingRate'])
                        # 取得週期，若欄位不存在則預設為 8
                        interval_hrs = Decimal(item.get('fundingRateInterval', 8))
                        
                        # --- 標準化為 8H 邏輯 ---
                        # 若 interval 是 1, multiplier 就是 8 (8/1)
                        # 若 interval 是 8, multiplier 就是 1 (8/8)
                        multiplier = Decimal(8) / interval_hrs
                        standardized_rate = (raw_rate * multiplier * Decimal(100))
                        
                        temp_map[coin] = {
                            "exchange": "Bitget",
                            "symbol": coin,
                            "rate": float(standardized_rate.quantize(Decimal('0.00001'))),
                            "interval": "8H" # 統一顯示標準化後的週期
                        }
        else:
            print(f"❌ Bitget 請求失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Bitget 發生錯誤: {e}")

    # 按照傳入 assets 的順序回傳結果
    final_results = []
    for coin in target_assets:
        if coin in temp_map:
            final_results.append(temp_map[coin])
        else:
            # 若沒找到該幣種
            final_results.append({
                "exchange": "Bitget",
                "symbol": coin,
                "rate": "N/A",
                "interval": "8H"
            })
            
    return final_results

if __name__ == "__main__":
    # 測試執行
    test_assets = ["BTC", "ETH", "SOL", "HYPE"]
    result = get_bitget_funding_rates(test_assets)
    print(json.dumps(result, indent=4))