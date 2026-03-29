from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# 確保這些文件中的函數都已經回傳 {"USDT_rate": ..., "USDC_rate": ..., "USD_rate": ...}
from funding.Binance_funding import get_binance_funding_rates
from funding.OKX_funding import get_okx_funding_rates
from funding.Bybit_funding import get_bybit_funding_rates
from funding.Bitget_funding import get_bitget_funding_rates
from funding.Backpack_funding import get_backpack_funding_rates
from funding.Hyperliquid_funding import get_hyperliquid_funding_rates

app = Flask(__name__, static_folder='static')
app.json.sort_keys = False
CORS(app)

# ─── Cache 設定 ────────────────────────────────────────────────
_cache = {}
CACHE_TTL = 30  # 秒

# ─── 各交易所抓取函數對應表 ────────────────────────────────────
EXCHANGE_FETCHERS = {
    'Binance':     get_binance_funding_rates,
    'OKX':         get_okx_funding_rates,
    'Bybit':       get_bybit_funding_rates,
    'Bitget':      get_bitget_funding_rates,
    'Backpack':    get_backpack_funding_rates,
    'Hyperliquid': get_hyperliquid_funding_rates,
}

def fetch_one(name, func, assets):
    """單一交易所抓取，出錯時回傳 None 格式避免崩潰"""
    try:
        data = func(assets)
        return name, data
    except Exception as e:
        print(f'[{name}] 全局抓取錯誤: {e}')
        # 構造錯誤時的空數據結構
        error_data = [{
            "USDT_rate": None,
            "USDC_rate": None,
            "USD_rate": None
        } for _ in assets]
        return name, error_data

# ─── 首頁 ──────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# ─── 主要 API ──────────────────────────────────────────────────
@app.route('/api/funding')
def funding():
    # 1. 取得並清理幣種參數
    assets_raw = request.args.get('assets', 'BTC,ETH,SOL,HYPE')
    assets = [a.strip().upper() for a in assets_raw.split(',') if a.strip()]

    if not assets:
        return jsonify({'status': 'error', 'message': 'No assets provided'}), 400

    # 2. Cache key & 現在時間
    cache_key = ','.join(sorted(assets))
    now = time.time()

    # 3. 檢查快取
    if cache_key in _cache:
        cache_age = now - _cache[cache_key]['ts']
        if cache_age < CACHE_TTL:
            return jsonify({
                'status': 'success',
                'cached': True,
                'age': int(cache_age),
                'data': _cache[cache_key]['data']
            })

    # 4. 平行抓取所有交易所
    results = {}
    with ThreadPoolExecutor(max_workers=len(EXCHANGE_FETCHERS)) as executor:
        futures = {
            executor.submit(fetch_one, name, func, assets): name
            for name, func in EXCHANGE_FETCHERS.items()
        }
        for future in as_completed(futures):
            name, data = future.result()
            results[name] = data

    # 5. 合併資料 (對齊各交易所的 USDT/USDC/USD)
    combined = {}
    for i, coin in enumerate(assets):
        combined[coin] = {
            'Interval': '8H',
            'Exchanges': {}
        }
        
        for ex_name in EXCHANGE_FETCHERS.keys():
            ex_data_list = results.get(ex_name, [])
            
            # 安全取出該幣種在該交易所的數據
            if i < len(ex_data_list):
                item = ex_data_list[i]
                # 兼容處理：有些舊腳本可能還沒改掉，增加預設值 get
                combined[coin]['Exchanges'][ex_name] = {
                    "USDT": item.get("USDT_rate"),
                    "USDC": item.get("USDC_rate"),
                    "USD":  item.get("USD_rate")
                }
            else:
                combined[coin]['Exchanges'][ex_name] = {
                    "USDT": None, "USDC": None, "USD": None
                }

    # 6. 存進快取並回傳
    _cache[cache_key] = {'ts': now, 'data': combined}

    return jsonify({
        'status': 'success',
        'cached': False,
        'age': 0,
        'data': combined
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'cache_keys': len(_cache)})

if __name__ == '__main__':
    # GCP 或一般生產環境建議 debug=False
    app.run(host='0.0.0.0', port=8080, debug=False)