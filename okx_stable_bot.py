import time
import hmac
import hashlib
import base64
import requests
import os

# ========== OKX CONFIG ==========
API_KEY = os.getenv("OKX_API_KEY")
SECRET_KEY = os.getenv("OKX_SECRET_KEY")
PASSPHRASE = os.getenv("OKX_PASSPHRASE")

BASE_URL = "https://www.okx.com"

# ========== STABLE TIMESTAMP ==========
def get_timestamp():
    return str(int(time.time() * 1000))

# ========== SIGN ==========
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

# ========== TEST ACCOUNT ==========
def test_account():
    path = "/api/v5/account/balance"
    url = BASE_URL + path

    headers = get_headers("GET", path)

    r = requests.get(url, headers=headers, timeout=10)
    print("STATUS:", r.status_code)
    print(r.json())

if __name__ == "__main__":
    print("===== OKX STABLE TEST =====")
    test_account()
