import time
import hmac
import hashlib
import base64
import requests
import os
from datetime import datetime

# ========== OKX CONFIG ==========
API_KEY = os.getenv("OKX_API_KEY")
SECRET_KEY = os.getenv("OKX_SECRET_KEY")
PASSPHRASE = os.getenv("OKX_PASSPHRASE")

BASE_URL = "https://www.okx.com"

# 全局时间偏移量（毫秒）
TIME_OFFSET = 0

# ========== 获取服务器时间偏移 ==========
def get_server_time_offset():
    """获取本地时间与OKX服务器时间的差值（毫秒）"""
    try:
        url = BASE_URL + "/api/v5/public/time"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            server_ts = int(data['data'][0]['ts'])
            local_ts = int(time.time() * 1000)
            offset = server_ts - local_ts
            print(f"[INFO] 时间偏移: {offset} ms (若偏移过大请同步系统时间)")
            return offset
        else:
            print("[WARN] 获取服务器时间失败，使用本地时间（偏移=0）")
            return 0
    except Exception as e:
        print(f"[WARN] 时间同步异常: {e}，使用本地时间")
        return 0

# ========== 带偏移的时间戳 ==========
def get_timestamp():
    return str(int(time.time() * 1000) + TIME_OFFSET)

# ========== 签名 ==========
def sign(timestamp, method, request_path, body=""):
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(
        SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    return base64.b64encode(mac).decode()

# ========== HEADERS ==========
def get_headers(method, path, body=""):
    ts = get_timestamp()
    return {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": sign(ts, method, path, body),
        "OK-ACCESS-TIMESTAMP": ts,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

# ========== 测试账户余额（带重试） ==========
def test_account(retry=2):
    path = "/api/v5/account/balance"
    url = BASE_URL + path

    for attempt in range(retry + 1):
        headers = get_headers("GET", path)
        try:
            r = requests.get(url, headers=headers, timeout=10)
            result = r.json()
            if r.status_code == 200 and result.get('code') == '0':
                print("✅ 认证成功！账户信息如下：")
                # 提取 USDT 余额展示
                for detail in result['data'][0]['details']:
                    if detail['ccy'] == 'USDT':
                        print(f"   USDT 可用余额: {detail['availBal']}")
                return True
            else:
                print(f"[ATTEMPT {attempt+1}] HTTP {r.status_code}, CODE: {result.get('code')}, MSG: {result.get('msg')}")
                if result.get('code') in ('50112', '50111') and attempt < retry:
                    print("   等待 2 秒后重试...")
                    time.sleep(2)
                    # 重试前重新同步一次时间
                    global TIME_OFFSET
                    TIME_OFFSET = get_server_time_offset()
                else:
                    return False
        except Exception as e:
            print(f"[ATTEMPT {attempt+1}] 请求异常: {e}")
            if attempt < retry:
                time.sleep(2)
            else:
                return False
    return False

# ========== 主入口 ==========
if __name__ == "__main__":
    print("===== OKX 增强稳定版测试 =====")
    
    # 1. 检查环境变量
    missing = []
    if not API_KEY:
        missing.append("OKX_API_KEY")
    if not SECRET_KEY:
        missing.append("OKX_SECRET_KEY")
    if not PASSPHRASE:
        missing.append("OKX_PASSPHRASE")
    if missing:
        print(f"❌ 缺少环境变量: {', '.join(missing)}")
        print("   请设置后再运行，例如：")
        print("   export OKX_API_KEY='your_key'")
        print("   export OKX_SECRET_KEY='your_secret'")
        print("   export OKX_PASSPHRASE='your_passphrase'")
        exit(1)
    
    # 2. 同步服务器时间
    TIME_OFFSET = get_server_time_offset()
    
    # 3. 测试连接
    success = test_account(retry=2)
    if success:
        print("🎉 测试通过，机器人可正常运行")
    else:
        print("❌ 测试失败，请检查网络、API权限或系统时间")
        exit(1)
