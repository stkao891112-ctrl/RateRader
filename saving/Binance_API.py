import os
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

# 載入設定
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(current_dir, "KEY.env"))

def clean_key(key):
    if not key: return ""
    return str(key).strip().encode('ascii', 'ignore').decode('ascii')

API_KEY = clean_key(os.getenv('BINANCE_API_KEY'))
SECRET_KEY = clean_key(os.getenv('BINANCE_SECRET_KEY'))
BASE_URL = 'https://api.binance.com'

def get_binance_rates(assets):
    if isinstance(assets, str):
        assets = [assets]
    
    final_data_list = []
    headers = {'X-MBX-APIKEY': API_KEY}
    
    for coin in assets:
        coin = coin.upper()
        timestamp = int(time.time() * 1000) # 每次迴圈更新時間戳防止簽章過期
        
        # --- 1. 抓取活期 (Flexible) ---
        flex_endpoint = '/sapi/v1/simple-earn/flexible/list'
        flex_params = {'asset': coin, 'timestamp': timestamp}
        flex_query = urlencode(flex_params)
        flex_sig = hmac.new(SECRET_KEY.encode('utf-8'), flex_query.encode('utf-8'), hashlib.sha256).hexdigest()
        
        try:
            flex_res = requests.get(f"{BASE_URL}{flex_endpoint}?{flex_query}&signature={flex_sig}", headers=headers, timeout=10)
            flex_data = flex_res.json()

            if flex_res.status_code == 200 and flex_data.get('rows'):
                for row in flex_data['rows']:
                    base_rate = float(row.get('latestAnnualPercentageRate', 0)) * 100
                    tier_data = row.get('tierAnnualPercentageRate', {})
                    bonus_rate = 0.0
                    max_limit_str = "Unlimited"

                    if tier_data:
                        first_range = list(tier_data.keys())[0]
                        bonus_rate = float(list(tier_data.values())[0]) * 100
                        max_limit_str = first_range

                    final_data_list.append({
                        "exchange_name": "Binance",
                        "coin_type": coin,
                        "period_Type": "flexible",
                        "period": 0,
                        "base_rate": round(base_rate, 2),
                        "bonus_rate": round(bonus_rate, 2),
                        "max_limit": max_limit_str
                    })
        except Exception as e:
            print(f"❌ 幣安活期抓取 {coin} 出錯: {e}")

        # --- 2. 抓取定期 (Locked) ---
        locked_endpoint = '/sapi/v1/simple-earn/locked/list'
        # 重新取時間戳確保連續請求不被拒絕
        timestamp = int(time.time() * 1000) 
        locked_params = {'asset': coin, 'timestamp': timestamp}
        locked_query = urlencode(locked_params)
        locked_sig = hmac.new(SECRET_KEY.encode('utf-8'), locked_query.encode('utf-8'), hashlib.sha256).hexdigest()

        try:
            locked_res = requests.get(f"{BASE_URL}{locked_endpoint}?{locked_query}&signature={locked_sig}", headers=headers, timeout=10)
            locked_data = locked_res.json()

            # 只有當 status 為 200 且 rows 有資料時才處理
            if locked_res.status_code == 200 and locked_data.get('rows'):
                for row in locked_data['rows']:
                    # 根據你提供的 JSON 結構進行深度解析 (從 detail 拿數據)
                    detail = row.get('detail', {})
                    quota = row.get('quota', {})
                    
                    if not detail: continue # 如果沒有詳細資料就跳過
                    
                    apr = float(detail.get('apr', 0)) * 100
                    duration = detail.get('duration')
                    min_purchase = quota.get('minimum', '0')

                    final_data_list.append({
                        "exchange_name": "Binance",
                        "coin_type": coin,
                        "period_Type": "fixed",
                        "period": str(duration),
                        "base_rate": round(apr, 2),
                        "bonus_rate": 0.0,
                        "max_limit": f"Min: {min_purchase} {coin}"
                    })
        except Exception as e:
            print(f"❌ 幣安定期抓取 {coin} 出錯: {e}")

    return final_data_list

if __name__ == "__main__":
    test_assets = ["USDT", "USDC"]
    result = get_binance_rates(test_assets)
    import json
    print(json.dumps(result, ensure_ascii=False, indent=4))