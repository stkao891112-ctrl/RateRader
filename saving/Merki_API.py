import requests
import json

def get_merkl_rewards_json(symbol, protocol_id, chain_id=1):
    """
    抓取並格式化 Merkl 獎勵為 JSON 結構
    結構：Symbol -> ChainID -> Protocol -> Market
    """
    url = "https://api.merkl.xyz/v4/opportunities"
    params = {
        "chainId": chain_id,
        "mainProtocolId": protocol_id.lower(),
        "status": "LIVE"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        opportunities = response.json()
        
        structured_data = {}
        target_symbol = symbol.upper()

        for opp in opportunities:
            if opp.get("action") == "LEND":
                name = opp.get("name", "")
                tokens = opp.get("tokens", [])
                
                # 幣種匹配
                match = (target_symbol in name.upper()) or \
                        any(target_symbol in t.get("symbol", "").upper() for t in tokens)
                
                if match:
                    # 1. 識別協議名稱 (例如: Aave)
                    # 優先使用 API 回傳的協議名稱，若無則使用傳入的 ID 並首字母大寫
                    protocol_name = opp.get("protocol", {}).get("name", protocol_id.capitalize())
                    
                    # 2. 識別市場標籤 (Market Tag)
                    market_tag = "Core"
                    full_name_upper = name.upper()
                    if "CORE" in full_name_upper:
                        market_tag = "Core"
                    elif "HORIZON" in full_name_upper:
                        market_tag = "Horizon"                  

                    # 3. 建立 JSON 層級結構
                    chain_key = str(chain_id)
                    
                    # 初始化 Symbol 層
                    if target_symbol not in structured_data:
                        structured_data[target_symbol] = {}
                    
                    # 初始化 Chain 層
                    if chain_key not in structured_data[target_symbol]:
                        structured_data[target_symbol][chain_key] = {}

                    # 初始化 Protocol 層 (這是你要求的新增層級)
                    if protocol_name not in structured_data[target_symbol][chain_key]:
                        structured_data[target_symbol][chain_key][protocol_name] = {}

                    # 4. 存入市場數據
                    structured_data[target_symbol][chain_key][protocol_name][market_tag] = {
                        "apr": round(opp.get("apr", 0), 2),
                        "tvl": round(opp.get("tvl", 0), 2),
                        "opportunity_id": opp.get("id"),
                        "last_updated_at": opp.get("lastCampaignCreatedAt"),
                        "deposit_url": opp.get("depositUrl")
                    }
        
        return structured_data

    except Exception as e:
        return {"error": str(e)}

# --- 測試輸出 ---
if __name__ == "__main__":
    result = get_merkl_rewards_json("PYUSD", "aave", chain_id=1)
    print(json.dumps(result, indent=4, ensure_ascii=False))