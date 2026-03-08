import requests
import json
# 確保 Merki_API.py 在同目錄下
from Merki_API import get_merkl_rewards_json 

def get_stablecoin_yields_json():
    aave_url = "https://api.v3.aave.com/graphql"
    headers = {"Content-Type": "application/json"}

    # 定義 Chain ID 對應表
    chain_map = {1: "Ethereum", 8453: "Base", 42161: "Arbitrum"}

    # 定義監控市場 (包含地址與鏈 ID)
    markets = [
        {"name": "Core instance", "id": 1, "addr": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"},
        {"name": "Horizon RWA Market", "id": 1, "addr": "0xAe05Cd22df81871bc7cC2a04BeCfb516bFe332C8"},
        {"name": "Base Market", "id": 8453, "addr": "0xA238Dd80C259a72e81d7e4674A96177701cb5d4c"},
        {"name": "Arbitrum Market", "id": 42161, "addr": "0x794a61358D6845594F94dc1DB02A252b5b4814aD"}
    ]

    # 設定關鍵字過濾清單
    KEYWORDS = ["USD", "DAI", "GHO", "EUR"]

    query = """
    query GetMarketData($address: EvmAddress!, $chainId: ChainId!) {
      market(request: { address: $address, chainId: $chainId }) {
        reserves {
          underlyingToken { symbol }
          supplyInfo { apy { value } }
        }
      }
    }
    """

    final_results = []

    for m in markets:
        try:
            variables = {"address": m['addr'], "chainId": m['id']}
            response = requests.post(aave_url, json={'query': query, 'variables': variables}, headers=headers).json()
            
            # 安全取得儲備資產列表
            reserves = response.get('data', {}).get('market', {}).get('reserves', [])
            if not reserves: continue

            for res in reserves:
                symbol = res['underlyingToken']['symbol'].upper()
                
                # --- 執行名稱過濾 ---
                # 只要 symbol 包含過濾清單中的任何一個字眼，就執行抓取
                if any(key in symbol for key in KEYWORDS):
                    # 1. Aave 基礎存款年化
                    base_apy = round(float(res['supplyInfo']['apy']['value']) * 100, 2)
                    
                    # 2. 呼叫 Merkl API 抓取獎勵 (這裡 protocol_id 用 'aave')
                    merkl_data = get_merkl_rewards_json(symbol, "aave", m['id'])
                    
                    # 3. 判定市場類型 (從你的 m['name'] 判斷是要 Core 還是 Horizon)
                    merkl_lookup = "Horizon" if "Horizon" in m['name'] else "Core"
                    
                    # 從 Merkl 結構中安全取值
                    chain_str = str(m['id'])
                    market_reward = merkl_data.get(symbol, {}).get(chain_str, {}).get("Aave", {}).get(merkl_lookup, {})
                    reward_apr = round(market_reward.get('apr', 0.0), 2)

                    # 4. 封裝數據
                    final_results.append({
                        "symbol": symbol,
                        "protocol": "Aave",
                        "base_apy": base_apy,
                        "reward_apr": reward_apr,
                        "total_apr": round(base_apy + reward_apr, 2),
                        "chain": chain_map.get(m['id'], f"Chain-{m['id']}"),
                        "market": m['name']
                    })
                    
        except Exception:
            continue

    # 5. 回傳最終 JSON
    return json.dumps(final_results, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    print(get_stablecoin_yields_json())