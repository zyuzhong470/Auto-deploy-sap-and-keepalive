import time
import hmac
import hashlib
import base64
import requests

# =========================
# 🔐 CONFIG
# =========================
API_KEY = "你的_API_KEY"
SECRET_KEY = "你的_SECRET_KEY"
PASSPHRASE = "你的_PASSPHRASE"

BASE_URL = "https://www.okx.com"

# =========================
# ⏱️ 统一时间源（核心修复）
# =========================
def get_okx_timestamp():
    return str(int(time.time() * 1000))

# =========================
# ✍️ 签名函数
# =========================
def sign(timestamp, method, request_path, body=""):
    message = timestamp + method + request_path + body
    mac = hmac.new(
        bytes(SECRET_KEY, encoding="utf-8"),
        bytes(message, encoding="utf-8"),
        digestmod=hashlib.sha256,
    )
    return base64.b64encode(mac.digest()).decode()

# =========================
# 📡 API 请求测试（账户余额）
# =========================
def test_account():
    method = "GET"
    request_path = "/api/v5/account/balance"
    body = ""

    timestamp = get_okx_timestamp()
    signature = sign(timestamp, method, request_path, body)

    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
    }

    url = BASE_URL + request_path
    response = requests.get(url, headers=headers)

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())

# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    print("===== OKX TIME FIX TEST START =====")
    test_account()
    print("===== TEST END =====")
