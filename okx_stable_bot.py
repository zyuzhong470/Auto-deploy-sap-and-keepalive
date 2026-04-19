import time
import hmac
import base64
import hashlib
import requests
import json

# ======================
# 🔐 填你的 API
# ======================
API_KEY = "你的API_KEY"
API_SECRET = "你的API_SECRET"
PASSPHRASE = "你的PASSPHRASE"

BASE_URL = "https://www.okx.com"

# ======================
# ⏱ 时间同步（关键修复）
# ======================
def get_okx_time():
    try:
        url = BASE_URL + "/api/v5/public/time"
        res = requests.get(url, timeout=5).json()
        return res["data"][0]["ts"]  # 毫秒时间戳（字符串）
    except:
        return str(int(time.time() * 1000))


# ======================
# 🔐 签名函数
# ======================
def sign(timestamp, method, request_path, body=""):
    message = str(timestamp) + method + request_path + body
    mac = hmac.new(
        bytes(API_SECRET, encoding="utf-8"),
        bytes(message, encoding="utf-8"),
        digestmod=hashlib.sha256,
    )
    return base64.b64encode(mac.digest()).decode()


# ======================
# 📡 API 请求测试
# ======================
def get_balance():
    timestamp = get_okx_time()
    method = "GET"
    request_path = "/api/v5/account/balance"
    body = ""

    signature = sign(timestamp, method, request_path, body)

    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

    url = BASE_URL + request_path
    response = requests.get(url, headers=headers)

    print("===== OKX TEST START =====")
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
    print("===== TEST END =====")


# ======================
# 🚀 RUN
# ======================
if __name__ == "__main__":
    get_balance()
