import requests
import json
import time

def get_binance_funding_rates(assets, retries=3, retry_delay=1):
    premium_url = 'https://fapi.binance.com/fapi/v1/premiumIndex'
    info_url    = 'https://fapi.binance.com/fapi/v1/fundingInfo'

    if isinstance(assets, str):
        assets = [assets.upper()]
    else:
        assets = [a.upper() for a in assets]

    for attempt in range(1, retries + 1):
        try:
            p_res = requests.get(premium_url, timeout=10)
            i_res = requests.get(info_url, timeout=10)

            if p_res.status_code == 200 and i_res.status_code == 200:
                p_data = p_res.json()
                i_data = i_res.json()

                interval_map = {item['symbol']: item['fundingIntervalHours'] for item in i_data}

                data_map = {}
                for item in p_data:
                    symbol = item['symbol']
                    if symbol.endswith("USDT"):
                        coin = symbol.replace("USDT", "")
                        data_map[coin] = item

                final_data_list = []
                for coin in assets:
                    symbol = f"{coin}USDT"
                    if coin in data_map:
                        item = data_map[coin]
                        raw_rate   = float(item.get('lastFundingRate', 0))
                        interval   = interval_map.get(symbol, 8)
                        multiplier = 8 / interval
                        standardized_rate = raw_rate * multiplier * 100
                        final_data_list.append({
                            "exchange": "Binance",
                            "symbol":   coin,
                            "rate":     round(standardized_rate, 5),
                        })
                    else:
                        final_data_list.append({
                            "exchange": "Binance",
                            "symbol":   coin,
                            "rate":     "N/A",
                        })

                return final_data_list  # 成功直接回傳

            else:
                print(f"[Binance] 第 {attempt} 次請求失敗，狀態碼 p={p_res.status_code} i={i_res.status_code}")

        except Exception as e:
            print(f"[Binance] 第 {attempt} 次錯誤: {e}")

        if attempt < retries:
            time.sleep(retry_delay)  # 等一下再重試

    # 全部重試失敗，回傳全 N/A
    print(f"[Binance] 重試 {retries} 次全部失敗，回傳 N/A")
    return [{"exchange": "Binance", "symbol": coin, "rate": "N/A"} for coin in assets]


if __name__ == "__main__":
    test_assets = ["BTC", "ETH", "SOL", "HYPE"]
    result = get_binance_funding_rates(test_assets)
    print(json.dumps(result, indent=4))
