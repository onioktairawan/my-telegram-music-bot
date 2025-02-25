import logging
import asyncio
import os
from telethon import TelegramClient
from dotenv import load_dotenv

# 🔹 Load konfigurasi dari .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

SOURCE_CHANNELS = list(map(int, os.getenv("SOURCE_CHANNELS").split(",")))
TARGET_CHATS = list(map(int, os.getenv("TARGET_CHATS").split(",")))

# 🔹 Konfigurasi Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# 🔹 Buat sesi Telethon tanpa bot_token (akun pribadi)
client = TelegramClient("session_name", API_ID, API_HASH)

# 🔹 Variabel untuk menyimpan ID pesan terakhir yang sudah diteruskan
last_message_ids = {channel_id: 0 for channel_id in SOURCE_CHANNELS}


async def check_new_messages():
    """Scrape pesan baru dari channel sumber dan kirim ke grup tujuan."""
    while True:
        for channel_id in SOURCE_CHANNELS:
            try:
                # 🔹 Ambil 5 pesan terbaru
                messages = await client.get_messages(channel_id, limit=5)
                for message in reversed(messages):
                    if message.id > last_message_ids[channel_id]:  # Cek apakah pesan baru
                        log_message = f"📩 Pesan baru dari {channel_id}:\n"

                        if message.text:
                            log_message += f"📝 {message.text[:100]}...\n"

                        if message.media:
                            log_message += f"📷 Media: {type(message.media).__name__}\n"

                        logging.info(log_message)

                        for chat_id in TARGET_CHATS:
                            try:
                                if message.media:
                                    await client.send_file(chat_id, message.media, caption=message.text[:1024])
                                else:
                                    await client.send_message(chat_id, message.text[:4096])

                                logging.info(f"✅ Pesan diteruskan ke {chat_id}")

                            except Exception as e:
                                logging.error(f"❌ Gagal meneruskan pesan ke {chat_id}: {e}")

                        # 🔹 Simpan ID pesan terakhir yang sudah diteruskan
                        last_message_ids[channel_id] = message.id

                await asyncio.sleep(5)  # 🔹 Delay antar pengecekan biar gak spam

            except Exception as e:
                logging.error(f"❌ Error saat membaca channel {channel_id}: {e}")

        await asyncio.sleep(10)  # 🔹 Tunggu sebelum mengecek ulang


async def start_bot():
    """Menjalankan bot dalam loop."""
    logging.info("🚀 Bot berjalan, mulai scrape pesan...")
    await check_new_messages()


with client:
    client.loop.run_until_complete(start_bot())
