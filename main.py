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

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

def send_alert(msg):
    webhook = os.getenv("WEBHOOK_URL")
    if not webhook: return
    try:
        requests.post(webhook, json={"content": f"⚠️ {msg}"}, timeout=10)
    except:
        pass

# ==========================================
# ฟังก์ชันทำงานแยกรายบัญชี (ไม่ขัดขวางกันเอง)
# ==========================================
def individual_bot_worker(account_index, token, channel_id):
    print(f"[SYSTEM] บัญชีที่ {account_index} เริ่มเปิดระบบแยกทำงานอิสระแล้ว...")
    
    messages = [
        "hello", "hi", "yo", "gg", "lol", "wow", 
        "test", "pokemon", "555", "หวัดดี", "มีคนไหม", "เล่นไรอยู่"
    ]
    url = f"https://discord.com{channel_id}/messages"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    while True:
        try:
            print(f"👉 บัญชีที่ {account_index} กำลังส่งข้อความ... (Prefix: {token[:15]})")
            response = requests.post(
                url, 
                json={"content": random.choice(messages)}, 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ บัญชีที่ {account_index} ส่งสำเร็จ! [Status 200]")
            
            elif response.status_code == 429: # ติดลิมิต Discord
                retry_seconds = response.json().get("retry_after", 30)
                print(f"🛑 บัญชีที่ {account_index} ติด Rate Limit! ต้องรอ {retry_seconds} วินาที (บัญชีอื่นไม่รอกับคุณนะ)")
                time.sleep(float(retry_seconds))
                continue
                
            else:
                print(f"❌ บัญชีที่ {account_index} เกิดข้อผิดพลาด รหัส: {response.status_code} - {response.text}")
                send_alert(f"บัญชีที่ {account_index} ส่งไม่ผ่าน รหัส {response.status_code}")

        except Exception as e:
            print(f"💥 บัญชีที่ {account_index} เชื่อมต่อล้มเหลว: {e}")
            time.sleep(10)

        # ตั้งเวลาเว้นระยะการส่งของ "บัญชีนี้" (ปรับเวลาส่งถี่-ห่าง ได้ตามใจชอบตรงนี้)
        # เช่น ส่งเสร็จแล้วให้บัญชีนี้พัก 15 ถึง 30 วินาที ก่อนส่งคำต่อไป
        sleep_time = random.randint(15, 30)
        print(f"⏳ บัญชีที่ {account_index} พักรอส่งรอบต่อไปในอีก {sleep_time} วินาที...")
        time.sleep(sleep_time)

# ==========================================
# ฟังก์ชันหลักในการกระจายงาน
# ==========================================
def main_bot_manager():
    TOKENS = [
        os.getenv("TOKEN_1"),
        os.getenv("TOKEN_2"),
        os.getenv("TOKEN_3")
    ]
    # กรองเอาเฉพาะ Token ที่มีอยู่จริง
    valid_tokens = [t.strip() for t in TOKENS if t]
    CHANNEL_ID = os.getenv("CHANNEL_ID")

    print(f"\n=======================")
    print(f"🤖 [MANAGER] ตรวจพบ TOKENS ทั้งหมด: {len(valid_tokens)} ตัว")
    print(f"📺 [MANAGER]เป้าหมาย CHANNEL_ID: {CHANNEL_ID}")
    print(f"=======================\n")

    if not valid_tokens or not CHANNEL_ID:
        print("❌ ข้อมูลไม่ครบถ้วน ตัวจัดการบอทไม่ทำงาน")
        return

    send_alert("ระบบ Multi-Account เริ่มทำงานแล้ว")

    # สั่งให้ทกุบัญชีแตกลูกน้องออกมารันแยกพร้อมๆ กันทันที
    for index, token in enumerate(valid_tokens):
        account_number = index + 1
        # สร้าง Thread แยกขาดจากกันในแต่ละ Token
        worker_thread = Thread(
            target=individual_bot_worker, 
            args=(account_number, token, CHANNEL_ID)
        )
        worker_thread.start()
        
        # เว้นจังหวะตอนเปิดตัวนิดหน่อยไม่ให้เปิดพร้อมกันเกินไป
        time.sleep(2) 

if __name__ == "__main__":
    # เริ่มต้นระบบจัดการบอทแบบแยก Thread
    manager = Thread(target=main_bot_manager)
    manager.start()
    
    # รันเว็บเซิร์ฟเวอร์เคียงคู่กันไป
    run_web()

