import requests
import json

def get_binance_funding_rates(assets):
    # 1. 抓取費率 (原本的 API，更新最快)
    premium_url = 'https://fapi.binance.com/fapi/v1/premiumIndex'
    # 2. 抓取週期資訊 (新的 API)
    info_url = 'https://fapi.binance.com/fapi/v1/fundingInfo'
    
    if isinstance(assets, str):
        assets = [assets.upper()]
    else:
        assets = [a.upper() for a in assets]

    final_data_list = []
    
    try:
        # 同時請求兩個接口
        p_res = requests.get(premium_url, timeout=10)
        i_res = requests.get(info_url, timeout=10)
        
        if p_res.status_code == 200 and i_res.status_code == 200:
            p_data = p_res.json()
            i_data = i_res.json()
            
            # 建立週期字典 { "HYPEUSDT": 4, "BTCUSDT": 8 ... }
            interval_map = {item['symbol']: item['fundingIntervalHours'] for item in i_data}
            
            # 建立費率字典 { "HYPE": {...} }
            data_map = {}
            for item in p_data:
                symbol = item['symbol']
                if symbol.endswith("USDT"):
                    coin = symbol.replace("USDT", "")
                    data_map[coin] = item
            
            # 按照 assets 順序提取
            for coin in assets:
                symbol = f"{coin}USDT"
                if coin in data_map:
                    item = data_map[coin]
                    raw_rate = float(item.get('lastFundingRate', 0))
                    
                    # 從另一個 API 拿到週期，如果找不到則預設為 8
                    interval = interval_map.get(symbol, 8)
                    
                    # --- 標準化邏輯 ---
                    # 如果 interval 是 4, multiplier 就是 2 (8/4)
                    # 把利率調整為 8 小時基準
                    multiplier = 8 / interval
                    standardized_rate = raw_rate * multiplier * 100
                    
                    percentage_rate = round(standardized_rate, 5)
                    
                    final_data_list.append({
                        "exchange": "Binance",
                        "symbol": coin,
                        "rate": percentage_rate,
                    })
        else:
            print("❌ 請求失敗")
            
    except Exception as e:
        print(f"❌ 抓取錯誤: {e}")

    return final_data_list

if __name__ == "__main__":
    test_assets = ["BTC", "ETH", "SOL", "HYPE"]
    result = get_binance_funding_rates(test_assets)
    print(json.dumps(result, indent=4))