from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

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
    """單一交易所抓取，出錯回傳全 N/A 不影響其他交易所"""
    try:
        data = func(assets)
        return name, data
    except Exception as e:
        print(f'[{name}] error: {e}')
        # 出錯時回傳每個幣都是 N/A
        return name, [{'rate': 'N/A'} for _ in assets]

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

    # 2. Cache key
    cache_key = ','.join(sorted(assets))
    now = time.time()

    # 3. 檢查快取
    if cache_key in _cache and (now - _cache[cache_key]['ts']) < CACHE_TTL:
        return jsonify({
            'status': 'success',
            'cached': True,
            'age': int(now - _cache[cache_key]['ts']),
            'data': _cache[cache_key]['data']
        })

    # 4. 平行抓取所有交易所（同時發出，誰先好先收）
    results = {}
    with ThreadPoolExecutor(max_workers=len(EXCHANGE_FETCHERS)) as executor:
        futures = {
            executor.submit(fetch_one, name, func, assets): name
            for name, func in EXCHANGE_FETCHERS.items()
        }
        for future in as_completed(futures):
            name, data = future.result()
            results[name] = data

    # 5. 合併資料
    combined = {}
    for i, coin in enumerate(assets):
        combined[coin] = {'Interval': '8H'}
        for ex_name in EXCHANGE_FETCHERS.keys():
            data = results.get(ex_name, [])
            combined[coin][ex_name] = data[i]['rate'] if i < len(data) else 'N/A'

    # 6. 存進快取
    _cache[cache_key] = {'ts': now, 'data': combined}

    return jsonify({
        'status': 'success',
        'cached': False,
        'age': 0,
        'data': combined
    })

# ─── 健康檢查（GCP 負載均衡用）─────────────────────────────────
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'cache_keys': len(_cache)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
