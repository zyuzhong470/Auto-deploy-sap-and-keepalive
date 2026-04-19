import time
import base64
import hmac
import hashlib
import requests
import os
import json

# =========================
# 🔐 API CONFIG (GitHub Secrets)
# =========================
API_KEY = os.getenv("OKX_API_KEY", "").strip()
SECRET_KEY = os.getenv("OKX_SECRET_KEY", "").strip()
PASSPHRASE = os.getenv("OKX_PASSPHRASE", "").strip()

BASE_URL = "https://www.okx.com"

# =========================
# 🧼 安全字符处理（防 latin-1 报错）
# =========================
def safe_str(v):
    return str(v).encode("ascii", "ignore").decode()

# =========================
# 🔐 OKX 签名函数
# =========================
def sign(timestamp, method, request_path, body=""):
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(
        bytes(SECRET_KEY, encoding="utf-8"),
        bytes(message, encoding="utf-8"),
        digestmod=hashlib.sha256
    )
    return base64.b64encode(mac.digest()).decode()

# =========================
# 📦 Header 构建（核心安全层）
# =========================
def get_headers(method, request_path, body=""):
    timestamp = str(time.time())

    body_str = json.dumps(body) if body else ""

    signature = sign(timestamp, method, request_path, body_str)

    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
        "User-Agent": "SOP-OKX-BOT/1.0"
    }

    # 强制 ASCII 清洗（防炸）
    safe_headers = {}
    for k, v in headers.items():
        safe_headers[safe_str(k)] = safe_str(v)

    return safe_headers, body_str

# =========================
# 🌐 通用请求函数
# =========================
def request(method, path, body=None):
    url = BASE_URL + path

    headers, body_str = get_headers(method, path, body)

    try:
        if method == "GET":
            res = requests.get(url, headers=headers, timeout=10)
        else:
            res = requests.post(url, headers=headers, data=body_str, timeout=10)

        print("STATUS:", res.status_code)

        try:
            print(res.json())
        except:
            print(res.text)

        return res.json()

    except Exception as e:
        print("REQUEST ERROR:", str(e).encode("ascii", "ignore").decode())
        return None

# =========================
# 📊 示例：账户信息
# =========================
def get_balance():
    return request("GET", "/api/v5/account/balance")

# =========================
# 🚀 主执行
# =========================
if __name__ == "__main__":
    print("START OKX SOP BOT")

    balance = get_balance()

    print("DONE")

