import requests
import datetime
import hmac
import hashlib
import base64
import socket
import requests.packages.urllib3.util.connection as urllib3_cn



# --- 請填入你的 OKX API 資訊 ---
API_KEY = '042d3fb0-4d14-4a71-8c06-9998fca5d001'
SECRET_KEY = 'B7A95CBEEDC2C02C4CDDB654A0B0C9C8'
PASSPHRASE = 'ILoveZoe7879@'
BASE_URL = 'https://www.okx.com'


def test_okx():

    """測試 OKX 連接 (需要 Key 驗證身分)"""
    print("\n--- 正在測試 OKX ---")
    # 獲取帳戶餘額作為測試（這是最快的驗證方法）
    timestamp = datetime.datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
    method = 'GET'
    path = '/api/v5/account/balance?ccy=USDT'
    
    # 生成簽名
    message = timestamp + method + path
    mac = hmac.new(bytes(SECRET_KEY, 'utf8'), bytes(message, 'utf8'), digestmod='sha256')
    signature = base64.b64encode(mac.digest()).decode('utf8')

    headers = {
        'OK-ACCESS-KEY': API_KEY,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': PASSPHRASE,
        'Content-Type': 'application/json'
    }

    try:
        res = requests.get(f"https://www.okx.com{path}", headers=headers, timeout=5)
        data = res.json()
        if data.get('code') == '0':
            print("✅ OKX 連線成功！API Key 驗證通過。")
        else:
            print(f"❌ OKX 驗證失敗: {data.get('msg')}")
    except Exception as e:
        print(f"❌ OKX 連線出錯: {e}")



def get_timestamp():
    """獲取符合官方格式的 ISO 毫秒時間戳 (UTC)"""
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def get_usdt_savings_balance():
    """獲取帳戶中 USDT 賺幣 (Simple Earn) 的餘額與收益資訊"""
    
   # 1. 定義請求資訊
    method = 'GET'
    request_path = '/api/v5/finance/savings/lending-rate-summary?ccy=USDT'
    timestamp = get_timestamp()
    
    # 2. 生成簽名 (timestamp + method + requestPath)
    message = timestamp + method + request_path
    mac = hmac.new(bytes(SECRET_KEY, 'utf-8'), bytes(message, 'utf-8'), digestmod=hashlib.sha256)
    signature = base64.b64encode(mac.digest()).decode('utf-8')

    # 3. 設置 Headers
    headers = {
        'OK-ACCESS-KEY': API_KEY,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': PASSPHRASE,
        'Content-Type': 'application/json'
    }

    try:
        url = f"{BASE_URL}{request_path}"
        response = requests.get(url, headers=headers, timeout=10)
        
        # 直接回傳並打印 JSON 內容
        result = response.json()
        print(result)
        return result
        
    except Exception as e:
        print(f"請求出錯: {e}")

if __name__ == "__main__":
    get_usdt_savings_balance()