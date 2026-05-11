import os
import re
import time
import requests
from playwright.sync_api import sync_playwright

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
    r"(CASH|現金|現金及約當現金|Cash)[\s\S]{0,50}?([0-9]+(?:\.[0-9]+)?)%",
    text,
    re.IGNORECASE
)

    if cash_match:

        ratio = float(cash_match.group(2))

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

                results.append(f"{etf}：抓不到資料")

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

        msg = "⚠️ ETF 現金比例異常\n\n"

        msg += f"觸發條件：現金比例 ≥ {THRESHOLD:.1f}%\n\n"

        msg += "\n".join(alerts)

        send_line_message(msg)

    else:

        print("沒有 ETF 超過門檻，不發 LINE")


if __name__ == "__main__":
    main()
