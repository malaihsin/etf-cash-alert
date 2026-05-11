import requests
import os
import re
import time

from playwright.sync_api import sync_playwright

ETF_LIST = ["00981A", "00757"]

THRESHOLD = 10

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

    print("LINE status:", response.status_code)
    print("LINE response:", response.text)


def get_cash_ratio(etf_code):

    url = f"https://www.pocket.tw/etf/tw/{etf_code}/fundholding/"

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        print("OPEN:", url)

        page.goto(url, timeout=60000)

        time.sleep(5)

        text = page.inner_text("body")

        browser.close()

    print(etf_code, "TEXT LENGTH:", len(text))

    cash_match = re.search(
        r"CASH[\s\S]{0,100}?([0-9]+(?:\.[0-9]+)?)%",
        text,
        re.IGNORECASE
    )

    if cash_match:

        ratio = float(cash_match.group(1))

        print(etf_code, "CASH:", ratio)

        return ratio

    print(etf_code, "找不到 CASH")

    return None


def main():

    alerts = []

    results = []

    for etf in ETF_LIST:

        try:

            ratio = get_cash_ratio(etf)

            if ratio is None:

                results.append(f"{etf}：抓不到 CASH")

                continue

            results.append(f"{etf}：{ratio:.2f}%")

            if ratio >= THRESHOLD:

                alerts.append(f"{etf}：{ratio:.2f}%")

        except Exception as e:

            print(etf, "ERROR:", str(e))

            results.append(f"{etf}：錯誤")

    print("RESULTS")

    for r in results:
        print(r)

    if alerts:

        msg = "⚠️ ETF CASH 比例異常\n\n"

        msg += f"觸發條件：CASH ≥ {THRESHOLD:.1f}%\n\n"

        msg += "\n".join(alerts)

        send_line_message(msg)

    else:

        print("沒有 ETF 超過門檻，不發送 LINE")


if __name__ == "__main__":
    main()
