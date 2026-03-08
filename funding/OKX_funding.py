import requests
import json
from decimal import Decimal, getcontext

# 設定全局精度（例如保留 10 位有效數字）
getcontext().prec = 10

def get_okx_funding_rates(assets):
    url = "https://www.okx.com/api/v5/public/funding-rate?instId=ANY"
    target_assets = [a.upper() for a in assets]
    temp_map = {}

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            raw_data = response.json()
            if raw_data.get('code') == '0':
                for item in raw_data.get('data', []):
                    inst_id = item['instId']
                    if not inst_id.endswith("-USDT-SWAP"):
                        continue
                        
                    coin = inst_id.split('-')[0]
                    if coin in target_assets:
                        # 使用 Decimal 處理時間與費率
                        next_f = Decimal(item['nextFundingTime'])
                        curr_f = Decimal(item['fundingTime'])
                        
                        # 精準計算週期
                        diff_ms = next_f - curr_f
                        interval_hrs = diff_ms / Decimal(3600000)
                        
                        if interval_hrs <= 0: interval_hrs = Decimal(8)
                        
                        # 精準標準化計算
                        multiplier = Decimal(8) / interval_hrs
                        raw_rate = Decimal(item['fundingRate'])
                        
                        # 最終百分比：raw_rate * multiplier * 100
                        standardized_rate = (raw_rate * multiplier * Decimal(100))
                        
                        # 格式化為字串或四捨五入後的 float 供 JSON 回傳
                        temp_map[coin] = {
                            "exchange": "OKX",
                            "symbol": coin,
                            "rate": float(standardized_rate.quantize(Decimal('0.00001'))), # 保留 5 位小數
                            "interval": "8H"
                        }
    except Exception as e:
        print(f"❌ 精度計算錯誤: {e}")

    # 依序回傳
    return [temp_map.get(coin, {"symbol": coin, "rate": "N/A"}) for coin in target_assets]
# --- 這裡就是你要加入的地方 ---

if __name__ == "__main__":
    # 1. 定義你想抓取的代幣清單
    my_assets = ["BTC", "ETH", "SOL", "HYPE"]
    
    
    # 2. 呼叫你寫好的函式
    results = get_okx_funding_rates(my_assets)
    
    # 3. 將結果印出來看
    print("\n--- 抓取結果 ---")
    print(json.dumps(results, indent=4))
    
    # 為了防止視窗秒縮，可以加這行（選用）
    # input("\n按 Enter 鍵結束程式...")