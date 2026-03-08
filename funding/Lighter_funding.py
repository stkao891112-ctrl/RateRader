import httpx
import json
import time

def get_btc_price_raw():
    # 這是從 SDK 配置中挖出來的真實主網地址
    url = "https://mainnet.zklighter.elliot.ai/v1/tickers"
    
    # 模擬瀏覽器，防止 403 再次發生
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        # 使用 httpx 進行請求
        with httpx.Client(http2=True, headers=headers, timeout=10.0) as client:
            response = client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                # 解析回傳的列表
                tickers = data if isinstance(data, list) else data.get('tickers', [])
                
                print("\n" + "="*40)
                print(f"📡 zkLighter 實時行情 (連線時間: {time.strftime('%H:%M:%S')})")
                print("="*40)

                found = False
                for t in tickers:
                    symbol = t.get('symbol', 'Unknown')
                    # 鎖定 BTC 相關交易對
                    if 'BTC' in symbol.upper():
                        price = t.get('last_price', '0')
                        funding = t.get('funding_rate', '0')
                        
                        # 格式化輸出
                        print(f"💰 交易對: {symbol}")
                        print(f"💵 最新價: ${float(price):,.2f}")
                        print(f"📊 資金費: {funding}")
                        
                        # 計算年化收益 (利差核心)
                        apy = float(funding) * 3 * 365 * 100
                        print(f"📈 套利 APY: {apy:.2f}%")
                        print("-" * 40)
                        found = True
                
                if not found:
                    print("⚠️ 抓到資料了，但裡面沒有 BTC。")
                    print("目前所有幣種:", [t.get('symbol') for t in tickers[:5]], "...")
            else:
                print(f"❌ 請求失敗，代碼: {response.status_code}")
                
    except Exception as e:
        print(f"⚠️ 發生錯誤: {e}")

if __name__ == "__main__":
    get_btc_price_raw()