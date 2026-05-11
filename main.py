import os
import requests
import json

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
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body)

    print("LINE:", response.status_code)
    print(response.text)


def get_cash_ratio(etf_code):

    url = f"https://www.pocket.tw/api/etf/{etf_code}/fundholding"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=20)

    print(etf_code, "HTTP:", response.status_code)

    if response.status_code != 200:
        return None

    try:
        data = response.json()

        holdings = data.get("data", [])

        for item in holdings:

            name = str(item.get("name", "")).upper()

            if "CASH" in name or "現金" in name:

                ratio = float(item.get("weight", 0))

                print(etf_code, "CASH:", ratio)

                return ratio

    except Exception as e:
        print(etf_code, "ERROR:", e)

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

    print("RESULTS")

    for r in results:
        print(r)

    if alerts:

        msg = "⚠️ ETF 現金比例異常\n\n"

        msg += f"觸發條件：現金比例 ≥ {THRESHOLD:.1f}%\n\n"

        msg += "\n".join(alerts)

        send_line_message(msg)

    else:

        print("沒有 ETF 超過門檻")


if __name__ == "__main__":
    main()
