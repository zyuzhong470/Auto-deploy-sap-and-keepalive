import time
import os
import json
import requests
import base64
import hmac
import hashlib
from datetime import datetime

# =========================
# 🔐 API CONFIG
# =========================
API_KEY = os.getenv("OKX_API_KEY", "").strip()
SECRET_KEY = os.getenv("OKX_SECRET_KEY", "").strip()
PASSPHRASE = os.getenv("OKX_PASSPHRASE", "").strip()

BASE_URL = "https://www.okx.com"

# =========================
# 📁 日志目录
# =========================
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = f"{LOG_DIR}/log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

# =========================
# 🧾 日志函数（文件 + 控制台）
# =========================
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"

    print(line)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# =========================
# 🔒 执行锁
# =========================
LOCK_FILE = "run.lock"

def acquire_lock():
    if os.path.exists(LOCK_FILE):
        log("⚠️ 任务已在运行，退出防重复执行")
        return False

    with open(LOCK_FILE, "w") as f:
        f.write(str(time.time()))

    return True

def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

# =========================
# 🔐 签名
# =========================
def sign(timestamp, method, path, body=""):
    msg = f"{timestamp}{method}{path}{body}"
    mac = hmac.new(
        SECRET_KEY.encode(),
        msg.encode(),
        hashlib.sha256
    )
    return base64.b64encode(mac.digest()).decode()

# =========================
# 📦 headers
# =========================
def get_headers(method, path, body=""):
    ts = str(time.time())
    body_str = json.dumps(body) if body else ""

    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": sign(ts, method, path, body_str),
        "OK-ACCESS-TIMESTAMP": ts,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
        "User-Agent": "SOP-OKX-V2.1"
    }

    return headers, body_str

# =========================
# 🌐 请求
# =========================
def request(method, path, body=None):
    url = BASE_URL + path
    headers, body_str = get_headers(method, path, body)

    try:
        if method == "GET":
            res = requests.get(url, headers=headers, timeout=10)
        else:
            res = requests.post(url, headers=headers, data=body_str, timeout=10)

        log(f"HTTP {res.status_code}")

        try:
            data = res.json()
            log(f"RESPONSE: {data}")
        except:
            log("RESPONSE decode failed")

        return res.json()

    except Exception as e:
        log(f"ERROR: {str(e)}")
        return None

# =========================
# 📊 示例接口
# =========================
def get_balance():
    return request("GET", "/api/v5/account/balance")

# =========================
# 🚀 主程序
# =========================
if __name__ == "__main__":

    log("🚀 START SOP V2.1 BOT")

    if not acquire_lock():
        exit()

    try:
        get_balance()
        log("✅ EXECUTION SUCCESS")

    except Exception as e:
        log(f"❌ FATAL ERROR: {str(e)}")

    finally:
        release_lock()
        log("🔓 LOCK RELEASED")
        log(f"📁 LOG SAVED: {LOG_FILE}")

