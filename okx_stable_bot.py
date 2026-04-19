import time
import requests
import hmac
import hashlib
import base64

# =========================
# ⚙️ CONFIG
# =========================
API_KEY = "你的_OKX_API_KEY"
SECRET_KEY = "你的_OKX_SECRET_KEY"
PASSPHRASE = "你的_API_PASSPHRASE"

BASE_URL = "https://www.okx.com"

# =========================
# 🧱 TIME SYNC LAYER（核心稳定层）
# =========================
class TimeSync:
    def __init__(self):
        self.offset = 0

    def get_server_time(self):
        try:
            url = BASE_URL + "/api/v5/public/time"
            res = requests.get(url, timeout=5).json()
            return int(res["data"][0]["ts"])
        except:
            return None

    def sync(self):
        server = self.get_server_time()
        if server:
            local = int(time.time() * 1000)
            self.offset = server - local
            print(f"[TIME SYNC] offset = {self.offset} ms")
            return True
        return False

    def ts(self):
        return str(int(time.time() * 1000 + self.offset))


# =========================
# 🔐 SIGNATURE
# =========================
def sign(timestamp, method, path, body, secret):
    message = timestamp + method + path + body
    mac = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    )
    return base64.b64encode(mac.digest()).decode()


# =========================
# 📡 REQUEST WRAPPER
# =========================
def okx_request(method, path, body=""):
    ts = tsync.ts()

    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": sign(ts, method, path, body, SECRET_KEY),
        "OK-ACCESS-TIMESTAMP": ts,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

    url = BASE_URL + path

    try:
        if method == "GET":
            res = requests.get(url, headers=headers, timeout=10)
        else:
            res = requests.post(url, headers=headers, data=body, timeout=10)

        return res.json()

    except Exception as e:
        return {"error": str(e)}


# =========================
# 💰 ACCOUNT TEST
# =========================
def get_balance():
    path = "/api/v5/account/balance?ccy=USDT"
    return okx_request("GET", path)


# =========================
# 🚀 MAIN
# =========================
if __name__ == "__main__":

    print("===== OKX STABLE BOT START =====")

    tsync = TimeSync()

    # 🔧 自动同步时间（关键）
    if not tsync.sync():
        print("⚠️ TIME SYNC FAILED - USING LOCAL TIME")

    # =========================
    # 🧪 TEST 1: ACCOUNT
    # =========================
    print("\n===== BALANCE TEST =====")
    result = get_balance()
    print(result)

    # =========================
    # 🧪 DEBUG INFO
    # =========================
    print("\n===== DEBUG =====")
    print("timestamp:", tsync.ts())
    print("offset(ms):", tsync.offset)

    print("\n===== END =====")
