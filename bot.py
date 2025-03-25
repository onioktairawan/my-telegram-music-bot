from telethon.sync import TelegramClient, events
import requests
import os
import datetime
from dotenv import load_dotenv

# 🔹 Load konfigurasi dari .env
load_dotenv()

# 🔹 Konfigurasi Telegram
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

# 🔹 Konfigurasi WhatsApp UltraMSG
WHATSAPP_INSTANCE_ID = os.getenv("WHATSAPP_INSTANCE_ID")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_NUMBERS = os.getenv("WHATSAPP_NUMBERS").split(",")

# 🔹 File log
LOG_FILE = "log.txt"

# 🔹 Fungsi untuk mencatat log dengan format rapi
def write_log(message):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{now}] {message}\n"
    print(log_entry.strip())
    with open(LOG_FILE, "a") as file:
        file.write(log_entry)

# 🔹 Fungsi untuk mengirim teks ke WhatsApp & mencatat log
def send_whatsapp_text(message, sender_info):
    for number in WHATSAPP_NUMBERS:
        url = f"https://api.ultramsg.com/{WHATSAPP_INSTANCE_ID}/messages/chat"
        data = {
            "token": WHATSAPP_TOKEN,
            "to": number,
            "body": message
        }
        response = requests.post(url, json=data)
        status = "✅ Berhasil" if response.status_code == 200 else "❌ Gagal"
        write_log(f"{status} dikirim ke {number}")

# 🔹 Jalankan Telegram Client
client = TelegramClient(PHONE_NUMBER, API_ID, API_HASH)

# 🔹 Menangkap SEMUA pesan masuk (DM, Grup, Channel)
@client.on(events.NewMessage)
async def forward_to_whatsapp(event):
    message = event.message.message or ""
    sender = await event.get_sender()
    
    # 🔹 Ambil info pengirim (User atau Channel)
    if hasattr(sender, 'username') and sender.username:
        sender_info = f"{sender.username} (ID: {sender.id})"
    else:
        sender_info = f"ID: {sender.id}"

    # 🔹 Catat log pesan masuk
    write_log(f"📩 Pesan dari {sender_info}: \"{message}\"")

    # 🔹 Kirim ke WhatsApp
    if message:
        send_whatsapp_text(message, sender_info)

client.start()
write_log("🚀 Bot Telegram ke WhatsApp dimulai...")
client.run_until_disconnected()
