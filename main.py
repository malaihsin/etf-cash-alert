import os
import re
import requests
from bs4 import BeautifulSoup

ETF_LIST = ["00981A", "00881", "00878", "009816", "00757", "0056"]
THRESHOLD = 0.1

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")


def send_line_message(message):
    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }

    body = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": message}]
    }

    response = requests.post(url, headers=headers, json=body)

    print("LINE status:", response.status_code)
    print("LINE response:", response.text)


def get_cash_ratio(etf_code):
    url = f"https://www.pocket.tw/etf/tw/{etf_code}/fundholding"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=20)
    print(f"{etf_code} HTTP status:", response.status_code)

    html = response.text

    # 方法1：直接從網頁文字找 CASH / 現金
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    patterns = [
        r"CASH\s*([0-9]+(?:\.[0-9]+)?)\s*%",
        r"現金\s*([0-9]+(?:\.[0-9]+)?)\s*%",
        r"Cash\s*([0-9]+(?:\.[0-9]+)?)\s*%",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))

    # 方法2：從 HTML 原始碼找 CASH 附近的百分比
    cash_index = html.upper().find("CASH")

    if cash_index != -1:
        nearby = html[cash_index:cash_index + 1000]
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%", nearby)

        if match:
            return float(match.group(1))

    print(f"{etf_code} 找不到 CASH / 現金比例")
    return None


def main():
    alerts = []
    results = []

    for etf in ETF_LIST:
        ratio = get_cash_ratio(etf)

        if ratio is None:
            results.append(f"{etf}：抓不到資料")
            continue

        results.append(f"{etf}：{ratio:.2f}%")

        if ratio >= THRESHOLD:
            alerts.append(f"{etf}：{ratio:.2f}%")

    print("全部結果：")
    for item in results:
        print(item)

    if alerts:
        message = "⚠️ ETF 現金比例異常\n\n"
        message += f"觸發條件：現金比例 ≥ {THRESHOLD:.1f}%\n\n"
        message += "\n".join(alerts)

        send_line_message(message)
    else:
        print("沒有 ETF 超過門檻，不發送 LINE")


if __name__ == "__main__":
    main()
