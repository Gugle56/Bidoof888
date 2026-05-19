from flask import Flask
from threading import Thread
import requests
import time
import random
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running!"

# =========================
# Web Server
# =========================
def run_web():
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port,
        use_reloader=False
    )

# =========================
# Webhook Alert
# =========================
def send_alert(msg):

    webhook = os.getenv("WEBHOOK_URL")

    if not webhook:
        return

    try:
        requests.post(
            webhook,
            json={"content": f"⚠️ {msg}"},
            timeout=10
        )

    except Exception as e:
        print("Webhook Error:", e)

# =========================
# Bot Loop
# =========================
def bot_loop():

    print("BOT LOOP STARTED")

    TOKENS = [
        os.getenv("TOKEN_1"),
        os.getenv("TOKEN_2"),
        os.getenv("TOKEN_3")
    ]

    # ลบ None และช่องว่าง
    TOKENS = [t.strip() for t in TOKENS if t]

    CHANNEL_ID = os.getenv("CHANNEL_ID")

    print("TOKENS FOUND:", len(TOKENS))
    print("CHANNEL:", CHANNEL_ID)

    if not TOKENS:
        print("ไม่พบ TOKEN")
        return

    if not CHANNEL_ID:
        print("ไม่พบ CHANNEL_ID")
        return

    messages = [
        "hello",
        "hi",
        "yo",
        "gg",
        "lol",
        "wow",
        "test",
        "pokemon",
        "555",
        "หวัดดี",
        "มีคนไหม",
        "เล่นไรอยู่"
    ]

    # =========================
    # Discord API URL
    # =========================
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"

    print("SYSTEM STARTED")

    send_alert("ระบบเริ่มทำงานแล้ว")

    while True:

        for index, token in enumerate(TOKENS):

            print(f"\n====== ACCOUNT {index + 1} ======")

            # debug token
            print("TOKEN PREFIX:", token[:20])

            headers = {
                "Authorization": token.strip(),
                "Content-Type": "application/json"
            }

            payload = {
                "content": random.choice(messages)
            }

            try:

                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=10
                )

                print("STATUS:", response.status_code)

                # ส่งสำเร็จ
                if response.status_code == 200:

                    print(
                        f"[{time.strftime('%H:%M:%S')}] ส่งสำเร็จ"
                    )

                # Rate Limit
                elif response.status_code == 429:

                    retry = response.json().get(
                        "retry_after",
                        30
                    )

                    print(
                        f"ติด Rate Limit รอ {retry} วินาที"
                    )

                    time.sleep(float(retry))

                # Error อื่น
                else:

                    print("ERROR RESPONSE:")
                    print(response.text)

                    send_alert(
                        f"บัญชี {index + 1} ERROR {response.status_code}"
                    )

            except Exception as e:

                print("REQUEST ERROR:", e)

                send_alert(
                    f"Request Error: {e}"
                )

                time.sleep(10)

            # พักก่อนสลับบัญชี
            delay_between_accounts = random.randint(20, 40)

            print(
                f"พัก {delay_between_accounts} วินาที"
            )

            time.sleep(delay_between_accounts)

        # พักรอบใหญ่
        long_sleep_time = random.randint(180, 300)

        print(
            f"\n=== พักรอบใหญ่ {long_sleep_time} วินาที ==="
        )

        time.sleep(long_sleep_time)

# =========================
# MAIN
# =========================
if __name__ == "__main__":

    t = Thread(target=bot_loop)

    t.start()

    run_web()
