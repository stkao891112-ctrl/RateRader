import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# 匯入工具函數 (請確保檔名與函數名完全正確)
from Binance_API import get_binance_rates
from Bybit_API import get_bybit_rates
from Bitget_API import get_bitget_rates  # 確保你已將 Bitget 函數存為此檔名

# --- 1. Github Actions 載入設定 (修改部分) ---
# 先嘗試從環境中直接讀取 (GitHub Actions 環境)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# 如果讀不到 (代表是在本地執行)，則載入 KEY.env
if not url or not key:
    print("ℹ️ 未偵測到系統環境變數，嘗試載入本地 KEY.env...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, "KEY.env")
    
    # 原本的 load_dotenv 邏輯保留並註解
    # load_dotenv(dotenv_path=env_path) 
    
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
    else:
        print("⚠️ 警告：找不到 KEY.env 且無環境變數設定")

# 2. 初始化 Supabase 連線
if not url or not key:
    print("❌ 錯誤：無法讀取 Supabase 連線資訊，請檢查 GitHub Secrets 或本地 KEY.env")
    exit()

supabase: Client = create_client(url, key)

#本地端
# # 1. 載入設定
# current_dir = os.path.dirname(os.path.abspath(__file__))
# env_path = os.path.join(current_dir, "KEY.env")
# load_dotenv(dotenv_path=env_path)

# url: str = os.getenv("SUPABASE_URL")
# key: str = os.getenv("SUPABASE_KEY")

# # 2. 初始化 Supabase 連線
# if not url or not key:
#     print("❌ 錯誤：無法讀取 Supabase 連線資訊，請檢查 KEY.env")
#     exit()

# supabase: Client = create_client(url, key)

def sync_all_exchanges():
    assets_to_fetch = ["USDT", "USDC"]
    all_data = []
    errors = []

    # --- 第一階段：抓取幣安 ---
    try:
        # 請確保 Binance 函數回傳格式也包含 period_type 與 period 欄位
        binance_data = get_binance_rates(assets_to_fetch)
        if binance_data:
            all_data.extend(binance_data)
            print(f"✅ Binance 資料抓取成功 ({len(binance_data)} 筆)")
    except Exception as e:
        error_msg = f"Binance 抓取失敗: {e}"
        errors.append(error_msg)
        print(f"❌ {error_msg}")

    # --- 第二階段：抓取 Bybit ---
    try:
        # 請確保 Bybit 函數回傳格式也包含 period_type 與 period 欄位
        bybit_data = get_bybit_rates(assets_to_fetch)
        if bybit_data:
            all_data.extend(bybit_data)
            print(f"✅ Bybit 資料抓取成功 ({len(bybit_data)} 筆)")
    except Exception as e:
        error_msg = f"Bybit 抓取失敗: {e}"
        errors.append(error_msg)
        print(f"❌ {error_msg}")

    # --- 第三階段：抓取 Bitget ---
    try:
        # 使用我們剛寫好的解析 apyList 與 productLevel 的函數
        bitget_data = get_bitget_rates(assets_to_fetch)
        if bitget_data:
            all_data.extend(bitget_data)
            print(f"✅ Bitget 資料抓取成功 ({len(bitget_data)} 筆)")
    except Exception as e:
        error_msg = f"Bitget 抓取失敗: {e}"
        errors.append(error_msg)
        print(f"❌ {error_msg}")

    # --- 第四階段：寫入 Supabase ---
    if not all_data:
        print("⚠️ 完全沒有資料可供寫入，停止同步。")
        return

    print(f"🚀 準備寫入總計 {len(all_data)} 筆數據至 Supabase...")

    try:
        # 1. 寫入歷史表 (記錄每一刻的變化)
        response = supabase.table("exchange_rates_history").insert(all_data).execute()
        
        if response.data:
            print(f"🎉 同步成功！資料庫已新增 {len(response.data)} 筆紀錄。")
        else:
            print("⚠️ 寫入未成功，請檢查 Supabase Table 名稱是否正確。")
            
    except Exception as e:
        print(f"❌ Supabase 寫入過程發生嚴重錯誤: {e}")

        # 2. 寫入即時表 (覆蓋舊資料，僅保留最新一筆)
    try:
        # 使用 upsert 功能，當 key 衝突時會自動執行 update
        # 注意：請確保 exchange_rates_now 表已建立唯一約束 (Unique Constraint)
        now_response = supabase.table("exchange_rates_now").upsert(
            all_data, 
            on_conflict="exchange_name,coin_type,period_Type,period"
        ).execute()
        
        if now_response.data:
            print(f"⚡ 即時利率已覆蓋更新 ({len(now_response.data)} 筆)。")
    except Exception as e:
        print(f"❌ 即時表 (exchange_rates_now) 更新失敗: {e}")

    # --- 第五階段：錯誤匯總報告 ---
    if errors:
        print("\n--- [運行警告] 部分項目發生錯誤 ---")
        for err in errors:
            print(f"• {err}")
    else:
        print("\n✨ 所有交易所資料同步圓滿完成！")

if __name__ == "__main__":
    sync_all_exchanges()