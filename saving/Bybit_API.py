import time
import os
from pybit.unified_trading import HTTP

def get_bybit_rates(assets):
    # --- 修正 1：更換 domain 以繞過 GitHub Actions 的美國 IP 限制 ---
    # 使用 domain="bytick" 會自動連線至 https://api.bytick.com
    session = HTTP(testnet=False, domain="bytick")
    
    if isinstance(assets, str):
        assets = [assets]
        
    final_data_list = []

    for coin in assets:
        try:
            response = session.get_earn_product_info(
                category="FlexibleSaving",
                coin=coin.upper()
            )

            if response['retCode'] == 0 and response['result']['list']:
                product = response['result']['list'][0]
                coin_name = product.get('coin')
                
                def clean_rate(rate_str):
                    if not rate_str: return 0.0
                    if isinstance(rate_str, str):
                        return float(rate_str.strip('%'))
                    return float(rate_str)

                raw_base_apr = product.get('estimateApr', "0")
                if '%' in str(raw_base_apr):
                    base_rate = clean_rate(raw_base_apr)
                else:
                    base_rate = clean_rate(raw_base_apr) * 100
                
                bonus_rate = 0.0
                max_limit_str = "Unlimited"

                tiered_details = product.get('tierAprDetails', [])
                if tiered_details:
                    first_tier = tiered_details[0]
                    raw_tier_apr = first_tier.get('estimateApr', "0")
                    
                    if '%' in str(raw_tier_apr):
                        bonus_rate = clean_rate(raw_tier_apr)
                    else:
                        bonus_rate = clean_rate(raw_tier_apr) * 100
                    
                    min_val = first_tier.get('min')
                    max_val = first_tier.get('max')
                    max_limit_str = f"{min_val}-{max_val}{coin_name}"

                final_data_list.append({
                    "exchange_name": "Bybit",
                    "coin_type": coin_name,
                    "period_Type": "flexible",
                    # --- 修正 2：確保為字串 "0" 以對應資料庫 text 欄位 ---
                    "period": "0", 
                    "base_rate": round(base_rate, 2),
                    "bonus_rate": round(bonus_rate, 2),
                    "max_limit": max_limit_str
                })
            else:
                print(f"⚠️ Bybit 找不到幣種 {coin} 的理財資料")
                
        except Exception as e:
            # 如果還是報 403，這裡會印出詳細訊息
            print(f"❌ Bybit 抓取 {coin} 出錯: {e}")

    return final_data_list

# --- 測試程式碼 ---
if __name__ == "__main__":
    test_assets = ["USDT", "USDC"]
    result = get_bybit_rates(test_assets)
    import json
    print(json.dumps(result, ensure_ascii=False, indent=4))