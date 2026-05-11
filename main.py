import requests
from bs4 import BeautifulSoup
import os

ETF_LIST = ["00981A", "0050", "006208", "00878", "00919"]

THRESHOLD = 10.0

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")


def get_cash_ratio(etf_code):
    url = f"https://www.pocket.tw/etf/tw/{etf_code}/fundholding"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text()

    lines = text.split("\n")

    for i, line in enumerate(lines):
        if "CASH" in line.upper():
            try:
                ratio = lines[i + 1].replace("%", "").strip()
                return float(ratio)
            except:
                return None

    return None


def send_line_message(message):
    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }

    body = {
        "to": LINE_USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    requests.post(url, headers=headers, json=body)


alerts = []

for etf in ETF_LIST:
    ratio = get_cash_ratio(etf)

    print(etf, ratio)

    if ratio and ratio >= THRESHOLD:
        alerts.append(f"{etf}：{ratio:.2f}%")

if alerts:
    msg = "⚠️ ETF 現金比例異常\n\n"
    msg += "\n".join(alerts)

    send_line_message(msg)

    print("LINE sent")
else:
    print("No alerts")
