from flask import Flask, jsonify, request
from flask_cors import CORS  # 記得加這一行
from Binance_funding import get_binance_funding_rates
from OKX_funding import get_okx_funding_rates
from Bybit_funding import get_bybit_funding_rates
from Bitget_funding import get_bitget_funding_rates
from Backpack_funding import get_backpack_funding_rates
from Hyperliquid_funding import get_hyperliquid_funding_rates

app = Flask(__name__)
# 加入下面這行，禁止 Flask 自動對 JSON 的 Key 進行字母排序
app.json.sort_keys = False
CORS(app)  # 允許所有來源連線，開發最方便

@app.route('/api/funding')
def funding():
    # 1. 取得參數並清理
    assets_raw = request.args.get('assets', 'BTC,ETH')
    assets = [a.strip().upper() for a in assets_raw.split(',')]
    
    # 2. 向所有交易所抓取數據
    binance_data = get_binance_funding_rates(assets)
    okx_data = get_okx_funding_rates(assets)
    bybit_data = get_bybit_funding_rates(assets)
    bitget_data = get_bitget_funding_rates(assets)
    backpack_data = get_backpack_funding_rates(assets)
    hyperliquid_data = get_hyperliquid_funding_rates(assets)

    # 3. 合併數據
    combined_results = {}

    for i, coin in enumerate(assets):
        combined_results[coin] = {
            "Binance":     binance_data[i]['rate']     if i < len(binance_data)     else "N/A",
            "OKX":         okx_data[i]['rate']         if i < len(okx_data)         else "N/A",
            "Bybit":       bybit_data[i]['rate']       if i < len(bybit_data)       else "N/A",
            "Bitget":      bitget_data[i]['rate']      if i < len(bitget_data)      else "N/A",
            "Backpack":    backpack_data[i]['rate']    if i < len(backpack_data)    else "N/A",
            "Hyperliquid": hyperliquid_data[i]['rate'] if i < len(hyperliquid_data) else "N/A",
            "Interval": "8H"
        }

    return jsonify({
        "status": "success",
        "data": combined_results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)