import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import yt_dlp
import os
from youtubesearchpython import VideosSearch

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Fungsi untuk mencari video di YouTube berdasarkan judul
def search_youtube(query):
    search = VideosSearch(query, limit=1)
    results = search.result()
    if results['result']:
        return results['result'][0]['link']  # Mengambil URL video pertama
    else:
        return None

# Fungsi untuk mendownload video/audio dari YouTube
def download_media(url, is_audio=True):
    # Membuat direktori 'downloads' jika belum ada
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    ydl_opts = {
        'format': 'bestaudio/best' if is_audio else 'bestvideo+bestaudio',
        'extractaudio': is_audio,  # Ekstrak audio saja
        'audioquality': 1,         # Kualitas terbaik
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Lokasi penyimpanan file
        'postprocessors': [{
            'key': 'FFmpegAudioConvertor',
            'preferredcodec': 'mp3' if is_audio else 'mp4',  # Konversi ke MP3 atau MP4
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        file_path = os.path.join('downloads', f"{info_dict['id']}.mp3" if is_audio else f"{info_dict['id']}.mp4")
        logger.info(f"Downloaded file: {file_path}")
        return file_path

# Fungsi untuk memulai percakapan
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Send me a YouTube link or a song title, and I\'ll send you the full video or audio!')

# Fungsi untuk perintah /play
async def play_music(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        await update.message.reply_text('Please provide a song title to play.')
        return

    song_title = ' '.join(context.args)  # Gabungkan argumen menjadi satu string
    url = search_youtube(song_title)
    if not url:
        await update.message.reply_text("Sorry, I couldn't find that song.")
        return

    await update.message.reply_text("Downloading the media...")
    try:
        # Tentukan apakah kita ingin mendownload audio saja atau video lengkap
        is_audio = 'audio' in song_title
        file_path = download_media(url, is_audio)

        # Periksa apakah file ada sebelum mengirimnya
        if os.path.exists(file_path):
            logger.info(f"Sending file: {file_path}")
            # Kirim file
            if is_audio:
                await update.message.reply_audio(open(file_path, 'rb'))
            else:
                await update.message.reply_video(open(file_path, 'rb'))
            os.remove(file_path)  # Hapus file setelah dikirim
        else:
            await update.message.reply_text("Error: File not found.")
    except Exception as e:
        await update.message.reply_text("Error downloading or sending the media.")
        logger.error(e)

def main():
    # Ganti 'YOUR_TOKEN' dengan token botmu
    application = Application.builder().token("7715591819:AAH3-WTeOy0fygSxoq7dO8nlPJ7JgwPnOnU").build()
    
    # Handler untuk perintah /start
    application.add_handler(CommandHandler("start", start))
    
    # Handler untuk perintah /play
    application.add_handler(CommandHandler("play", play_music))
    
    # Handler untuk menangani pesan teks (URL YouTube atau judul lagu)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, play_music))
    
    # Jalankan bot
    application.run_polling()

if __name__ == '__main__':
    main()
