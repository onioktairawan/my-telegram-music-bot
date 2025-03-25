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

# 🔹 ID Grup yang Akan Dipantau
TELEGRAM_GROUP_IDS = list(map(int, os.getenv("TELEGRAM_GROUP_IDS").split(",")))

# 🔹 File log
LOG_FILE = "log.txt"

# 🔹 Fungsi untuk mencatat log dengan format rapi
def write_log(message):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{now}] {message}\n"
    print(log_entry.strip())
    with open(LOG_FILE, "a") as file:
        file.write(log_entry)

# 🔹 Fungsi untuk mengirim teks ke WhatsApp
def send_whatsapp_text(message):
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

# 🔹 Fungsi untuk mengirim media ke WhatsApp
def send_whatsapp_media(media_url, caption=""):
    for number in WHATSAPP_NUMBERS:
        url = f"https://api.ultramsg.com/{WHATSAPP_INSTANCE_ID}/messages/image"
        data = {
            "token": WHATSAPP_TOKEN,
            "to": number,
            "image": media_url,
            "caption": caption
        }
        response = requests.post(url, json=data)
        status = "✅ Berhasil" if response.status_code == 200 else "❌ Gagal"
        write_log(f"{status} Media dikirim ke {number}")

# 🔹 Jalankan Telegram Client
client = TelegramClient(PHONE_NUMBER, API_ID, API_HASH)

# 🔹 Menangkap pesan dari grup tertentu berdasarkan ID
@client.on(events.NewMessage(chats=TELEGRAM_GROUP_IDS))
async def forward_to_whatsapp(event):
    sender = await event.get_sender()
    sender_info = f"{sender.username} (ID: {sender.id})" if hasattr(sender, 'username') and sender.username else f"ID: {sender.id}"
    
    # 🔹 Jika pesan berisi teks
    if event.message.text:
        message = event.message.text
        write_log(f"📩 Pesan dari {sender_info}: \"{message}\"")
        send_whatsapp_text(f"📢 Dari {sender_info}:\n{message}")
    
    # 🔹 Jika pesan berisi media (gambar, video, voice, dokumen)
    if event.message.media:
        file_path = await event.message.download_media()
        write_log(f"📷 Media dari {sender_info}: {file_path}")
        
        # 🔹 Upload media ke server (Agar bisa dikirim ke WhatsApp)
        with open(file_path, "rb") as file:
            url_upload = f"https://api.ultramsg.com/{WHATSAPP_INSTANCE_ID}/upload"
            files = {"file": file}
            headers = {"token": WHATSAPP_TOKEN}
            response = requests.post(url_upload, files=files, headers=headers)
            if response.status_code == 200:
                media_url = response.json().get("url", "")
                caption = event.message.text if event.message.text else ""
                send_whatsapp_media(media_url, caption)
            else:
                write_log(f"❌ Gagal mengupload media dari {sender_info}")

client.start()
write_log("🚀 Bot Telegram ke WhatsApp dimulai...")
client.run_until_disconnected()
