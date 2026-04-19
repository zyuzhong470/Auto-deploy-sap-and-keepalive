import time
import hmac
import hashlib
import requests
import json
import os

# =========================
# 🔐 API CONFIG
# =========================
API_KEY = os.getenv("OKX_API_KEY")
API_SECRET = os.getenv("OKX_API_SECRET")
API_PASSPHRASE = os.getenv("OKX_API_PASSPHRASE")

BASE_URL = "https://www.okx.com"

# =========================
# 🧠 GLOBAL TIME OFFSET
# =========================
TIME_OFFSET = 0

# =========================
# 🧠 LOG SYSTEM
# =========================
def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{t}] {msg}")

# =========================
# 🧠 TIME SYNC (OKX 返回毫秒时间戳)
# =========================
def sync_time():
    global TIME_OFFSET
    try:
        res = requests.get(f"{BASE_URL}/api/v5/public/time", timeout=5).json()
        # OKX 返回的 ts 是毫秒时间戳字符串
        server_ts_ms = int(res['data'][0]['ts'])
        local_ts_ms = int(time.time() * 1000)
        TIME_OFFSET = (server_ts_ms - local_ts_ms) / 1000.0
        log(f"⏱ 时间同步成功 OFFSET={TIME_OFFSET:.3f}s")
    except Exception as e:
        log(f"❌ 时间同步失败: {e}")

def get_timestamp_ms():
    """返回带偏移的毫秒时间戳 (OKX 要求 ISO 格式，但签名用的是毫秒字符串)"""
    return str(int((time.time() + TIME_OFFSET) * 1000))

# =========================
# 🔐 OKX 签名
# =========================
def sign(timestamp, method, request_path, body):
    # 拼接：timestamp + method + requestPath + body (GET 时 body 为空字符串)
    message = timestamp + method.upper() + request_path + body
    mac = hmac.new(
        bytes(API_SECRET, encoding='utf8'),
        bytes(message, encoding='utf-8'),
        hashlib.sha256
    )
    return mac.hexdigest()

# =========================
# 🚀 REQUEST (带重试)
# =========================
def request(method, endpoint, params=None):
    """
    method: "GET" 或 "POST"
    endpoint: API 路径，如 "/api/v5/account/balance"
    params: 对于 GET 为 dict (查询参数)，对于 POST 为 dict (请求体)
    """
    for i in range(3):
        try:
            timestamp = get_timestamp_ms()  # 毫秒字符串

            # 处理请求路径和 body
            request_path = endpoint
            body = ""

            if method == "GET":
                if params:
                    # 将参数按 key 排序并拼接到 URL
                    sorted_keys = sorted(params.keys())
                    query = "&".join([f"{k}={params[k]}" for k in sorted_keys])
                    request_path = f"{endpoint}?{query}"
                # GET 请求 body 为空字符串
                body = ""
                url = BASE_URL + request_path
                response = requests.get(url, timeout=5)
            else:  # POST
                body = json.dumps(params) if params else ""
                url = BASE_URL + endpoint
                headers = {
                    "Content-Type": "application/json"
                }
                response = requests.post(url, headers=headers, data=body, timeout=5)

            # 构造签名
            sign_str = sign(timestamp, method, request_path, body)

            # 请求头
            headers = {
                "OK-ACCESS-KEY": API_KEY,
                "OK-ACCESS-SIGN": sign_str,
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": API_PASSPHRASE,
            }
            if method == "POST":
                headers["Content-Type"] = "application/json"

            # 重新发送带正确签名的请求
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=5)
            else:
                r = requests.post(url, headers=headers, data=body, timeout=5)

            data = r.json()

            # OKX 返回码：code 为 "0" 表示成功
            if data.get("code") == "0":
                return data
            else:
                log(f"⚠️ API错误: {data}")
                time.sleep(1)

        except Exception as e:
            log(f"❌ 请求失败(第{i+1}次): {e}")
            time.sleep(1)

    return None

# =========================
# 🧪 测试：账户余额 (统一账户)
# =========================
def get_balance():
    endpoint = "/api/v5/account/balance"
    # OKX 余额接口可选参数 ccy，不传则返回所有币种
    params = None   # 或 {"ccy": "USDT"} 指定币种
    return request("GET", endpoint, params)

# =========================
# 🚀 MAIN
# =========================
if __name__ == "__main__":
    log("🚀 启动 OKX 稳定版 v1")

    # 检查必要环境变量
    if not API_KEY or not API_SECRET or not API_PASSPHRASE:
        log("❌ 请设置环境变量 OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSPHRASE")
        exit(1)

    sync_time()  # 启动时同步一次

    while True:
        res = get_balance()

        if res:
            log("✅ 获取余额成功")
            print(json.dumps(res, indent=2))
        else:
            log("❌ 获取失败")

        time.sleep(30)
