#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import hmac
import hashlib
import base64
import requests
from datetime import datetime

# ================== 配置 ==================
API_KEY = os.getenv("OKX_API_KEY")
SECRET_KEY = os.getenv("OKX_SECRET_KEY")
PASSPHRASE = os.getenv("OKX_PASSPHRASE")
BASE_URL = "https://www.okx.com"

# 全局时间偏移（毫秒）
TIME_OFFSET = 0

# ================== 工具函数 ==================
def get_server_time_offset():
    """获取本地时间与OKX服务器时间的差值（毫秒）"""
    try:
        url = f"{BASE_URL}/api/v5/public/time"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            server_ts = int(data['data'][0]['ts'])
            local_ts = int(time.time() * 1000)
            offset = server_ts - local_ts
            print(f"[INFO] 时间偏移: {offset} ms")
            return offset
        else:
            print("[WARN] 获取服务器时间失败，使用本地时间")
            return 0
    except Exception as e:
        print(f"[WARN] 时间同步异常: {e}，使用本地时间")
        return 0

def get_timestamp():
    """生成带偏移的时间戳"""
    return str(int(time.time() * 1000) + TIME_OFFSET)

def sign(timestamp, method, request_path, body=""):
    """生成签名"""
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(
        SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    return base64.b64encode(mac).decode()

def get_headers(method, path, body=""):
    """构造请求头"""
    ts = get_timestamp()
    return {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": sign(ts, method, path, body),
        "OK-ACCESS-TIMESTAMP": ts,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

def log_message(msg, level="INFO"):
    """输出带时间戳的日志"""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{timestamp}] [{level}] {msg}")

# ================== 核心业务 ==================
def get_account_balance():
    """获取账户余额（USDT）"""
    path = "/api/v5/account/balance"
    url = BASE_URL + path
    headers = get_headers("GET", path)
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        result = resp.json()
        
        if resp.status_code == 200 and result.get("code") == "0":
            for detail in result['data'][0]['details']:
                if detail['ccy'] == 'USDT':
                    avail = detail.get('availBal', '0')
                    log_message(f"USDT 可用余额: {avail}")
                    return float(avail)
            log_message("未找到 USDT 余额")
            return 0.0
        else:
            error_msg = result.get('msg', 'Unknown error')
            log_message(f"API 错误: {error_msg} (code: {result.get('code')})", "ERROR")
            return None
    except Exception as e:
        log_message(f"请求异常: {e}", "ERROR")
        return None

def run_bot():
    """主流程"""
    log_message("===== SOP V2.1 BOT 启动 =====")
    
    # 1. 检查环境变量
    missing = []
    if not API_KEY:
        missing.append("OKX_API_KEY")
    if not SECRET_KEY:
        missing.append("OKX_SECRET_KEY")
    if not PASSPHRASE:
        missing.append("OKX_PASSPHRASE")
    if missing:
        log_message(f"缺少环境变量: {', '.join(missing)}", "ERROR")
        return False
    
    # 2. 同步服务器时间
    global TIME_OFFSET
    TIME_OFFSET = get_server_time_offset()
    
    # 3. 获取余额
    balance = get_account_balance()
    if balance is None:
        log_message("获取余额失败", "ERROR")
        return False
    
    log_message(f"✅ 执行成功，USDT 余额: {balance}")
    return True

if __name__ == "__main__":
    success = run_bot()
    exit(0 if success else 1)
