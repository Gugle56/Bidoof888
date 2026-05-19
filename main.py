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
            json={
                "content": f"⚠️ {msg}"
            },
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

        "รักหมอกนะ",
        "รักหมอกมาก",
        "รักนัท",
        "poketwo บอทกาก",
        "หมอกๆ",
        "เบื่อ",
        "มีไรจะบอก",
        "Bidoof เก่งที่สุด",
        "อาเซอุสกาก",
        "หวัดดี",
        "มีคนไหม",
        "เล่นไรอยู่"

    ]

    url = (
        f"https://discord.com/api/v9/"
        f"channels/{CHANNEL_ID}/messages"
    )

    print("SYSTEM STARTED")

    send_alert("ระบบเริ่มทำงานแล้ว")

    while True:

        token = random.choice(TOKENS)

        headers = {

            "Authorization": token,
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

            # =========================
            # SUCCESS
            # =========================
            if response.status_code == 200:

                print(
                    f"[{time.strftime('%H:%M:%S')}] ส่งสำเร็จ"
                )

            # =========================
            # RATE LIMIT
            # =========================
            elif response.status_code == 429:

                retry = response.json().get(
                    "retry_after",
                    30
                )

                print(
                    f"Rate limit รอ {retry}"
                )

                time.sleep(float(retry))

            # =========================
            # ERROR
            # =========================
            else:

                print("ERROR:")
                print(response.text)

                send_alert(
                    f"Error {response.status_code}"
                )

        except Exception as e:

            print("REQUEST ERROR:", e)

            send_alert(
                f"Request Error: {e}"
            )

            time.sleep(30)

        # =========================
        # RANDOM SLEEP
        # =========================
        sleep_time = random.randint(45, 90)

        print(
            f"พัก {sleep_time} วินาที"
        )

        time.sleep(sleep_time)

# =========================
# MAIN
# =========================
if __name__ == "__main__":

    t = Thread(target=bot_loop)

    t.start()

    run_web()