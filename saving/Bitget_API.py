import os
import time
import hmac
import hashlib
import base64
import requests
from dotenv import load_dotenv

# 1. 載入設定
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(current_dir, "KEY.env"))

API_KEY = os.getenv('BITGET_API_KEY')
SECRET_KEY = os.getenv('BITGET_SECRET_KEY')
PASSPHRASE = os.getenv('BITGET_PASSPHRASE')
BASE_URL = 'https://api.bitget.com'

def get_bitget_rates(assets=["USDT", "USDC"]):

    if isinstance(assets, str):
        assets = [assets]
    
    final_data_list = []

    for coin in assets:
        coin_upper = coin.upper()
        endpoint = '/api/v2/earn/savings/product'
        query_params = f"coin={coin_upper}&filter=all"
        request_path = f"{endpoint}?{query_params}"
        
        timestamp = str(int(time.time() * 1000))
        method = "GET"
        message = timestamp + method + request_path
        
        sig = hmac.new(SECRET_KEY.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
        signature = base64.b64encode(sig).decode()

        headers = {
            'ACCESS-KEY': API_KEY,
            'ACCESS-SIGN': signature,
            'ACCESS-PASSPHRASE': PASSPHRASE,
            'ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(f"{BASE_URL}{request_path}", headers=headers, timeout=10)
            res_json = response.json()

            if res_json.get('code') == '00000' and res_json.get('data'):
                products = res_json.get('data', [])
                
                for product in products:
                    if product.get("productLevel") == "normal" and product.get("status") == "in_progress":
                        
                        p_type = product.get("periodType", "")
                        apy_list = product.get("apyList", [])
                        
                        base_rate = 0.0
                        bonus_rate = 0.0
                        max_limit_str = "Unlimited"

                        if apy_list:
                            base_rate = float(apy_list[-1].get("currentApy", 0))
                            first_tier_apr = float(apy_list[0].get("currentApy", 0))
                            bonus_rate = max(0, first_tier_apr - base_rate)
                            
                            # --- 格式化 Max Limit (移除 .0 且不加空格) ---
                            max_val = apy_list[0].get("maxStepVal", "0")
                            clean_val = str(float(max_val)).replace('.0', '')
                            # 這裡直接拼接，不加空格
                            max_limit_str = f"0-{clean_val}{coin_upper}"

                        final_data_list.append({
                            "exchange_name": "Bitget",
                            "coin_type": coin_upper,
                            "period_Type": p_type,  # 嚴格遵守大寫 T
                            "period": product.get("period", 0) if p_type == "fixed" else 0,
                            "base_rate": round(base_rate, 2),
                            "bonus_rate": round(bonus_rate, 2),
                            "max_limit": max_limit_str
                        })
            
        except Exception as e:
            print(f"❌ Bitget 抓取 {coin} 出錯: {e}")

    return final_data_list

if __name__ == "__main__":
    test_assets = ["USDT", "USDC"]
    result = get_bitget_rates(test_assets)
    import json
    print(json.dumps(result, ensure_ascii=False, indent=4))