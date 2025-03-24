from telethon.sync import TelegramClient, events
import requests

# 🔹 Konfigurasi Telegram
api_id = "23581804"  # Ganti dengan API ID dari my.telegram.org
api_hash = "49fd7d9ac9aecb487c343a0c1156f8d2"  # Ganti dengan API Hash dari my.telegram.org
phone = "+6285880486495"  # Format: +62XXXXXXXXXX
channel_id = -1002415431014  # Ganti dengan ID channel Telegram

# 🔹 Konfigurasi UltraMSG (WhatsApp)
WHATSAPP_INSTANCE_ID = "instance111416"
WHATSAPP_TOKEN = "x95wf7vxck5jya3k"
WHATSAPP_NUMBER = "+6281387628476"  # Nomor WhatsApp tujuan

def send_whatsapp_message(message):
    url = f"https://api.ultramsg.com/{WHATSAPP_INSTANCE_ID}/messages/chat"
    data = {
        "token": WHATSAPP_TOKEN,
        "to": WHATSAPP_NUMBER,
        "body": message
    }
    response = requests.post(url, json=data)
    print(response.json())  # Cek respons dari UltraMSG

# 🔹 Jalankan Telegram Client
client = TelegramClient(phone, api_id, api_hash)

@client.on(events.NewMessage(chats=channel_id))  # Pakai ID channel
async def forward_to_whatsapp(event):
    message = event.message.message
    print(f"Meneruskan ke WhatsApp: {message}")
    send_whatsapp_message(message)

client.start()
client.run_until_disconnected()
