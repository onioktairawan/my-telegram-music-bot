from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from newsapi import NewsApiClient
import logging
import asyncio
import logging
from telethon import TelegramClient, events
from telegram import Bot
from telegram.error import TelegramError

# Konfigurasi API
NEWS_API_KEY = '7da3292df394438fab6518ff0cd8d96c'  # API key NewsAPI
TELEGRAM_BOT_TOKEN = '7500495219:AAGiGwm4yFkH79jE_kpxTdHg4d2M8DKfKzE'  # Token Telegram Bot

# Setup logging untuk debug
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Inisialisasi NewsApiClient
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

# Variabel untuk menyimpan chat_id grup
group_chat_id = None

# Fungsi untuk mendapatkan berita Forex dan cryptocurrency
def get_news():
    # Mengambil berita terkait forex dan cryptocurrency
    top_headlines = newsapi.get_top_headlines(q='forex OR cryptocurrency',
                                              language='en',
                                              page_size=5)  # Mengambil 5 berita terbaru

    # Memeriksa apakah ada artikel
    if top_headlines['status'] == 'ok' and top_headlines['totalResults'] > 0:
        articles = top_headlines['articles']
        news_list = []
        for article in articles:
            title = article['title']
            url = article['url']
            news_list.append(f"{title}\n{url}")
        
        return "\n\n".join(news_list)  # Mengembalikan berita dalam format teks
    else:
        return "Tidak ada berita terbaru saat ini."

# Fungsi untuk menangani update (termasuk ketika bot ditambahkan ke grup)
async def handle_updates(update, context):
    global group_chat_id

    # Jika pesan datang dari grup
    if update.message.chat.type in ['group', 'supergroup']:
        # Cek apakah bot ditambahkan ke grup (join)
        if update.message.new_chat_members:
            for member in update.message.new_chat_members:
                if member.id == context.bot.id:  # Jika bot yang baru saja ditambahkan
                    group_chat_id = update.message.chat.id  # Simpan chat_id grup
                    await context.bot.send_message(chat_id=group_chat_id, text="Bot berhasil bergabung dengan grup!")

# Fungsi untuk mengirimkan berita otomatis ke grup
async def send_news_to_group(context):
    if group_chat_id:
        news = get_news()  # Ambil berita terbaru
        await context.bot.send_message(chat_id=group_chat_id, text=news)  # Kirim berita ke grup
    else:
        print("Grup tidak ditemukan!")

# Fungsi untuk perintah /berita
async def berita(update: Update, context):
    news = get_news()  # Ambil berita terbaru
    await update.message.reply_text(news)  # Kirimkan berita langsung ke pengguna

# Fungsi untuk memulai bot
async def start(update, context):
    await update.message.reply_text(
        "Halo! Saya bot berita ekonomi. Ketik /berita untuk mendapatkan berita terbaru tentang forex dan cryptocurrency."
    )

# Setup untuk bot Telegram
def main():
    # Inisialisasi Application (ganti dengan versi terbaru)
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Handler untuk command /start
    application.add_handler(CommandHandler('start', start))

    # Handler untuk command /berita
    application.add_handler(CommandHandler('berita', berita))  # Ini yang baru ditambahkan

    # Handler untuk menerima semua pesan dan memproses update
    application.add_handler(MessageHandler(filters.ALL, handle_updates))

    # Set interval pengiriman berita otomatis (misalnya setiap 1 jam)
    job_queue = application.job_queue
    job_queue.run_repeating(send_news_to_group, interval=3600, first=0)

    # Mulai polling untuk bot (tanpa menggunakan asyncio.run)
    application.run_polling()

if __name__ == '__main__':
    main()

# Konfigurasi logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# API ID & API HASH dari my.telegram.org
API_ID = 23581804  # Ganti dengan API ID-mu
API_HASH = "49fd7d9ac9aecb487c343a0c1156f8d2"  # Ganti dengan API HASH-mu

# Token bot dari BotFather (PASTIKAN TOKEN BARU)
BOT_TOKEN = "7783954036:AAGWsD-9G3BfnSPysEAKqN30OfiKonfTUV4"

# ID Channel sumber (format -100XXXXXXXXXX)
CHANNEL_SOURCE_ID = -1002156702383  # ID channel sumber

# ID Grup atau Channel tujuan (format -100XXXXXXXXXX)
TARGET_CHAT_ID = -1002325511325  # ID grup/channel tujuan

# Inisialisasi Telethon Client
client = TelegramClient("session_name", API_ID, API_HASH)
bot = Bot(token=BOT_TOKEN)

@client.on(events.NewMessage(chats=CHANNEL_SOURCE_ID))
async def forward_message(event):
    """ Mengambil pesan dari channel sumber dan meneruskannya ke tujuan """
    message = event.message.text
    if message:
        logging.info(f"Pesan diterima dari {CHANNEL_SOURCE_ID}: {message}")
        try:
            await bot.send_message(chat_id=TARGET_CHAT_ID, text=message)
            logging.info(f"✅ Pesan berhasil diteruskan ke {TARGET_CHAT_ID}")
        except TelegramError as e:
            logging.error(f"❌ Gagal mengirim pesan ke {TARGET_CHAT_ID}: {e}")

async def main():
    """Menjalankan bot"""
    logging.info("🚀 Bot berjalan, menunggu pesan baru...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
