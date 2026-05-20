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

    except:
        pass

# =========================
# Worker แยกแต่ละบัญชี
# =========================
def individual_bot_worker(account_index, token, channel_id):

    print(
        f"[SYSTEM] บัญชีที่ {account_index} เริ่มทำงาน"
    )

    # =========================
    # ข้อความสุ่ม
    # =========================
    messages = [

        "รักหมอกนะ",
        "เป็นแฟนกันไหมหมอก",
        "หมอกน่ารักจัง",
        "คิดถึงหมอก",
        "หมอกทำไรอยู่",
        "หมอกกินข้าวยัง",
        "หมอกอย่านอนดึกนะ",
        "อยากคุยกับหมอก",
        "หมอกน่าจะง่วงแล้ว",
        "หมอกเล่นอะไรอยู่",
        "วันนี้หมอกเป็นไงบ้าง",
        "หมอกน่ารักเกิน",
        "รักหมอกที่สุด",
        "หมอกตอบหน่อย",
        "หมอกหายไปไหน",
        "หมอกออนยัง",
        "หมอกว่างไหม",
        "อยากเจอหมอก",
        "หมอกดูแลตัวเองด้วยนะ",
        "หมอกนอนยัง"

    ]

    # =========================
    # Discord API URL
    # =========================
    url = (
        f"https://discord.com/api/v9/"
        f"channels/{channel_id}/messages"
    )

    headers = {

        "Authorization": token,
        "Content-Type": "application/json"

    }

    while True:

        try:

            print(
                f"👉 บัญชี {account_index} กำลังส่ง..."
            )

            response = requests.post(

                url,

                json={
                    "content": random.choice(messages)
                },

                headers=headers,

                timeout=10

            )

            print(
                f"STATUS: {response.status_code}"
            )

            # =========================
            # SUCCESS
            # =========================
            if response.status_code in [200, 201]:

                print(
                    f"✅ บัญชี {account_index} ส่งสำเร็จ"
                )

            # =========================
            # RATE LIMIT
            # =========================
            elif response.status_code == 429:

                retry_seconds = response.json().get(
                    "retry_after",
                    30
                )

                print(
                    f"🛑 บัญชี {account_index} ติด Rate Limit รอ {retry_seconds} วิ"
                )

                time.sleep(
                    float(retry_seconds)
                )

                continue

            # =========================
            # ERROR
            # =========================
            else:

                print(
                    f"❌ บัญชี {account_index} Error {response.status_code}"
                )

                print(response.text)

                send_alert(
                    f"บัญชี {account_index} Error {response.status_code}"
                )

        except Exception as e:

            print(
                f"💥 บัญชี {account_index} ล้มเหลว: {e}"
            )

            time.sleep(30)

        # =========================
        # Random Sleep
        # =========================

        # พักปกติ 45-120 วินาที
        sleep_time = random.randint(45, 120)

        # มีโอกาส 10% ที่จะพักยาว
        if random.randint(1, 10) == 1:

            long_break = random.randint(
                300,
                900
            )

            print(
                f"🌙 บัญชี {account_index} พักยาว {long_break} วินาที"
            )

            time.sleep(long_break)

        print(
            f"⏳ บัญชี {account_index} พัก {sleep_time} วินาที"
        )

        time.sleep(sleep_time)

# =========================
# Manager
# =========================
def main_bot_manager():

    TOKENS = [

        os.getenv("TOKEN_1"),
        os.getenv("TOKEN_2"),
        os.getenv("TOKEN_3")

    ]

    valid_tokens = [

        t.strip()
        for t in TOKENS
        if t

    ]

    CHANNEL_ID = os.getenv("CHANNEL_ID")

    print("\n=======================")

    print(
        f"🤖 ตรวจพบ TOKENS: {len(valid_tokens)}"
    )

    print(
        f"📺 CHANNEL_ID: {CHANNEL_ID}"
    )

    print("=======================\n")

    if not valid_tokens:

        print("❌ ไม่พบ TOKEN")

        return

    if not CHANNEL_ID:

        print("❌ ไม่พบ CHANNEL_ID")

        return

    send_alert(
        "ระบบ Multi Account เริ่มทำงานแล้ว"
    )

    # =========================
    # เปิด Worker แยกทุกบัญชี
    # =========================
    for index, token in enumerate(valid_tokens):

        account_number = index + 1

        worker_thread = Thread(

            target=individual_bot_worker,

            args=(
                account_number,
                token,
                CHANNEL_ID
            )

        )

        worker_thread.start()

        # เว้นช่วงตอนเปิดแต่ละบัญชี
        time.sleep(
            random.randint(5, 15)
        )

# =========================
# MAIN
# =========================
if __name__ == "__main__":

    manager = Thread(
        target=main_bot_manager
    )

    manager.start()

    run_web()
