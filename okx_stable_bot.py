import time
import os
import hmac
import hashlib
import base64
import requests
from datetime import datetime

# =========================
# 🔐 ENV 安全读取
# =========================
def load_env(key):
    value = os.environ.get(key)
    if not value or value.strip() == "":
        raise Exception(f"[CRITICAL] Missing ENV: {key}")
    return value.strip()

API_KEY = load_env("OKX_API_KEY")
SECRET_KEY = load_env("OKX_SECRET_KEY")
PASSPHRASE = load_env("OKX_PASSPHRASE")

# =========================
# ⏱️ 时间戳稳定层
# =========================
def okx_timestamp():
    return str(int(time.time() * 1000))

# =========================
# 🔐 签名生成
# =========================
def sign(message):
    mac = hmac.new(
        bytes(SECRET_KEY, encoding="utf8"),
        bytes(message, encoding="utf-8"),
        digestmod=hashlib.sha256,
    )
    return base64.b64encode(mac.digest()).decode()

# =========================
# 📦 Header 构建
# =========================
def build_headers(method, path, body=""):
    timestamp = okx_timestamp()
    message = timestamp + method + path + body
    signature = sign(message)

    return {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

# =========================
# 🔁 安全请求（重试机制）
# =========================
def safe_request(method, url, path, max_retry=3):
    for i in range(max_retry):
        try:
            headers = build_headers(method, path)

            if method == "GET":
                res = requests.get(url, headers=headers, timeout=10)
            else:
                res = requests.post(url, headers=headers, timeout=10)

            if res.status_code == 200:
                return res.json()

            print(f"[RETRY {i+1}] HTTP {res.status_code} {res.text}")

        except Exception as e:
            print(f"[RETRY {i+1}] ERROR {str(e)}")

        time.sleep(2 ** i)

    return None

# =========================
# 🧪 OKX 账户测试
# =========================
def test_okx():
    print("===== OKX STABLE TEST START =====")

    url = "https://www.okx.com/api/v5/account/balance"
    path = "/api/v5/account/balance"

    data = safe_request("GET", url, path)

    if data and data.get("code") == "0":
        print("✅ CONNECT SUCCESS")

        balances = data["data"][0]["details"]
        for b in balances:
            if b["ccy"] in ["USDT", "SOL"]:
                print(f"{b['ccy']}:", b["availBal"])

        return True

    print("❌ CONNECT FAILED")
    print(data)
    return False

# =========================
# 🚀 MAIN
# =========================
if __name__ == "__main__":
    try:
        print("===== RUN =====")
        print("TIME:", datetime.utcnow().isoformat())

        ok = test_okx()

        print("===== RESULT =====")
        print(ok)

    except Exception as e:
        print("FATAL ERROR:", str(e))
