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
# Bot Loop (แก้ไขระบบส่งและเวลาพักใหม่)
# =========================
def bot_loop():
    print("BOT LOOP STARTED")

    TOKENS = [
        os.getenv("TOKEN_1"),
        os.getenv("TOKEN_2"),
        os.getenv("TOKEN_3")
    ]
    # กรองเฉพาะ Token ที่ใช้งานได้จริงและตัดช่องว่างออก
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
        "hello", "hi", "yo", "gg", "lol", "wow", 
        "test", "pokemon", "555", "หวัดดี", "มีคนไหม", "เล่นไรอยู่"
    ]

    # [แก้ไขตรงนี้แล้ว] เปลี่ยนเป็นโครงสร้าง URL ที่ถูกต้องของ Discord API
    url = f"https://discord.com{CHANNEL_ID}/messages"
    print("SYSTEM STARTED")
    send_alert("ระบบเริ่มทำงานแล้ว")

    # เริ่มลูปทำงานตลอด 24 ชั่วโมง
    while True:
        
        # เปลี่ยนเป็นโครงสร้าง For เพื่อบังคับให้ทุก Token ส่งเรียงลำดับ 1 -> 2 -> 3 ไม่สุ่มทับกัน
        for index, token in enumerate(TOKENS):
            
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

                print(f"[ไอดีที่ {index + 1}] STATUS:", response.status_code)

                # ส่งสำเร็จ
                if response.status_code == 200:
                    print(f"[{time.strftime('%H:%M:%S')}] บัญชีที่ {index + 1} ส่งสำเร็จ")

                # ติดลิมิตความถี่ (Rate Limit)
                elif response.status_code == 429:
                    retry = response.json().get("retry_after", 30)
                    print(f"Rate limit เจอแจ็คพอต! ต้องรอ {retry} วินาที")
                    time.sleep(float(retry))

                # เกิดปัญหาอื่นๆ (เช่น 401 รหัสผิด/บิน)
                else:
                    print(f"ERROR บนบัญชีที่ {index + 1}:")
                    print(response.text)
                    send_alert(f"บัญชีที่ {index + 1} เกิดข้อผิดพลาดรหัส {response.status_code}")

            except Exception as e:
                print("REQUEST ERROR:", e)
                send_alert(f"Request Error: {e}")
                time.sleep(10)

            # พักระยะสั้นระหว่างรอสลับไอดีถัดไป (เช่น ส่งเสร็จไอดี 1 พักแป๊บหนึ่งค่อยส่งไอดี 2)
            # ตั้งสุ่มไว้ที่ 20 ถึง 40 วินาที เพื่อความเป็นธรรมชาติ
            delay_between_accounts = random.randint(20, 40)
            print(f"--> พัก {delay_between_accounts} วินาที ก่อนสลับให้ไอดีถัดไปทำงาน...")
            time.sleep(delay_between_accounts)

        # เมื่อส่งครบหมดทุกไอดีแล้ว (1, 2, และ 3) จะมาเข้าสู่ช่วงพักรอบใหญ่
        # เปลี่ยนเป็นสุ่มพักยาวขึ้น (3 ถึง 5 นาที) เพื่อป้องกันไม่ให้ AI มองว่าเป็นบอทสแปมถี่เกินไป
        long_sleep_time = random.randint(180, 300)
        print(f"=== ส่งครบทุกบัญชีแล้ว สั่งพักรอบใหญ่ {long_sleep_time} วินาที (ประมาณ {long_sleep_time//60} นาที) ===")
        time.sleep(long_sleep_time)

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.start()
    run_web()
