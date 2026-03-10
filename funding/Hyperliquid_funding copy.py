import requests
import json

url = "https://api.hyperliquid.xyz/info"
payload = {"type": "predictedFundings"}

response = requests.post(url, json=payload, timeout=5)
raw_data = response.json()

# 指定你要的幣種
target_coins = ["BTC", "ETH", "SOL", "HYPE"]

# 過濾出目標幣種
filtered = [
    entry for entry in raw_data
    if isinstance(entry, list) and entry[0].upper() in target_coins
]

print(json.dumps(filtered, indent=2))