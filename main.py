from flask import Flask
from threading import Thread
import requests
import time
import random
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "System running!"

def run_web():

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port,
        use_reloader=False
    )

# =========================
# แจ้งเตือนผ่าน Webhook
# =========================
def send_alert(message):

    WEBHOOK_URL = os.getenv("WEBHOOK_URL")

    if WEBHOOK_URL:

        try:

            requests.post(
                WEBHOOK_URL,
                json={
                    "content": f"⚠️ {message}"
                },
                timeout=10
            )

        except Exception as e:

            print("Webhook Error:", e)

# =========================
# ระบบส่งข้อความ
# =========================
def bot_loop():

    # =========================
    # ดึง Token จาก Environment
    # =========================
    TOKENS = [

        os.getenv("TOKEN_1"),
        os.getenv("TOKEN_2"),
        os.getenv("TOKEN_3")

    ]

    # ลบค่า None ออก
    TOKENS = [t for t in TOKENS if t]

    CHANNEL_ID = os.getenv("CHANNEL_ID")

    # =========================
    # ข้อความสุ่ม
    # =========================
    MESSAGES = [

        "hello",
        "hi",
        "yo",
        "sup",
        "gg",
        "lol",
        "nice",
        "wow",
        "ok",
        "bruh",
        "ez",

        "มีคนไหม",
        "เล่นไรอยู่",
        "หวัดดี",
        "มาแล้ว",
        "เดี๋ยวมา",
        "แปป",
        "หิวข้าว",
        "นอนยัง",
        "555",
        "55555",
        "จริงดิ",
        "สุดจัด",
        "โอเค",
        "จัดไป",
        "อืม",
        "ไปๆ",
        "เอ้า",
        "ได้อยู่",
        "เทส",
        "test",
        "p2",
        "pokemon",
        "anyone here?",
        "hello there",
        "วันนี้เป็นไงบ้าง",
        "กำลังทำอะไร",
        "เงียบจัง",
        "มาเล่นกัน",
        "ว่างไหม",
        "สวัสดีทุกคน",
        "โย่ว",
        "อรุณสวัสดิ์",
        "ราตรีสวัสดิ์",
        "กินข้าวยัง",
        "เยส",
        "โอ้โห",
        "ชิวๆ",
        "5555555"

    ]

    # =========================
    # เช็กค่าเริ่มต้น
    # =========================
    if not TOKENS:

        print("ไม่พบ TOKEN")

        return

    if not CHANNEL_ID:

        print("ไม่พบ CHANNEL_ID")

        return

    url_send = (
        f"https://discord.com/api/v9/"
        f"channels/{CHANNEL_ID}/messages"
    )

    print("System started")

    send_alert("ระบบเริ่มทำงานแล้ว")

    while True:

        token = random.choice(TOKENS)

        headers = {

            "Authorization": token,
            "Content-Type": "application/json"

        }

        payload = {

            "content": random.choice(MESSAGES)

        }

        try:

            response = requests.post(
                url_send,
                json=payload,
                headers=headers,
                timeout=10
            )

            # ส่งสำเร็จ
            if response.status_code == 201:

                print(
                    f"[{time.strftime('%H:%M:%S')}] ส่งสำเร็จ"
                )

            # โดน Rate Limit
            elif response.status_code == 429:

                retry = response.json().get(
                    "retry_after",
                    30
                )

                print(
                    f"Rate limited รอ {retry} วินาที"
                )

                send_alert(
                    f"โดน Rate Limit รอ {retry} วินาที"
                )

                time.sleep(float(retry))

            # Token ใช้ไม่ได้
            elif response.status_code in [401, 403]:

                print("Token ใช้งานไม่ได้")

                send_alert(
                    "พบ Token ใช้งานไม่ได้"
                )

                time.sleep(60)

            else:

                print(
                    f"Error {response.status_code}"
                )

                print(response.text)

        except Exception as e:

            print("Request Error:", e)

            send_alert(
                f"ระบบเกิดข้อผิดพลาด: {e}"
            )

            time.sleep(30)

        # =========================
        # หน่วงเวลาแบบสุ่ม
        # =========================
        sleep_time = random.randint(45, 90)

        print(
            f"พัก {sleep_time} วินาที"
        )

        time.sleep(sleep_time)

# =========================
# Main
# =========================
if __name__ == "__main__":

    thread = Thread(
        target=bot_loop
    )

    thread.start()

    run_web()