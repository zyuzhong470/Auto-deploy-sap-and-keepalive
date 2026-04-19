import time
import hmac
import hashlib
import base64
import requests
from datetime import datetime, timezone
import os

# =========================
# 🔐 从环境变量读取（GitHub/VPS用）
# =========================
API_KEY = os.environ.get("OKX_API_KEY")
SECRET_KEY = os.environ.get("OKX_SECRET_KEY")
PASSPHRASE = os.environ.get("OKX_PASSPHRASE")

BASE_URL = "https://www.okx.com"

# =========================
# ⏱ 正确UTC时间戳（关键）
# =========================
def get_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

# =========================
# 🔐 OKX签名生成
# =========================
def sign(message, secret):
    mac = hmac.new(
        bytes(secret, encoding='utf-8'),
        bytes(message, encoding='utf-8'),
        digestmod=hashlib.sha256
    )
    return base64.b64encode(mac.digest()).decode()

# =========================
# 🧪 测试 API（public endpoint）
# =========================
def test_api():
    if not API_KEY or not SECRET_KEY or not PASSPHRASE:
        print("❌ API Key / Secret / Passphrase 未加载")
        return

    timestamp = get_timestamp()

    method = "GET"
    request_path = "/api/v5/account/balance"
    body = ""

    prehash = timestamp + method + request_path + body
    signature = sign(prehash, SECRET_KEY)

    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

    url = BASE_URL + request_path

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.json())
    except Exception as e:
        print("❌ 请求失败:", str(e))

# =========================
# 🚀 运行
# =========================
if __name__ == "__main__":
    print("===== OKX AUTH TEST START =====")
    test_api()
    print("===== TEST END =====")
