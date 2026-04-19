import time
import hmac
import hashlib
import base64
import requests
import json

# =========================
# ⚙️ CONFIG
# =========================
BASE_URL = "https://www.okx.com"


# =========================
# ⏱️ 时间戳（稳定版）
# =========================
def get_timestamp():
    return str(int(time.time() * 1000))


# =========================
# 🔐 签名
# =========================
def sign_okx(timestamp, method, path, body, secret):
    message = f"{timestamp}{method}{path}{body}"

    mac = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    )

    return base64.b64encode(mac.digest()).decode()


# =========================
# 🌐 请求核心（稳定版）
# =========================
def okx_request(api_key, secret, passphrase, method, path, body=""):
    url = BASE_URL + path

    timestamp = get_timestamp()
    sign = sign_okx(timestamp, method, path, body, secret)

    headers = {
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SIGN": sign,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json"
    }

    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=10)
        else:
            r = requests.post(url, headers=headers, data=body, timeout=10)

        try:
            data = r.json()
        except:
            return False, {"error": "invalid json"}

        if r.status_code != 200:
            return False, data

        if data.get("code") != "0":
            return False, data

        return True, data

    except Exception as e:
        return False, {"error": str(e)}


# =========================
# 🔁 自动重试
# =========================
def safe_request(api_key, secret, passphrase, method, path, body="", retry=3):
    for i in range(retry):
        ok, res = okx_request(api_key, secret, passphrase, method, path, body)

        if ok:
            return True, res

        print(f"[RETRY {i+1}] {res}")
        time.sleep(1.5)

    return False, res


# =========================
# 📊 示例：账户余额
# =========================
if __name__ == "__main__":

    API_KEY = "YOUR_API_KEY"
    SECRET = "YOUR_SECRET"
    PASSPHRASE = "YOUR_PASSPHRASE"

    ok, data = safe_request(
        API_KEY,
        SECRET,
        PASSPHRASE,
        "GET",
        "/api/v5/account/balance"
    )

    print("RESULT:", ok)
    print(json.dumps(data, indent=2))
