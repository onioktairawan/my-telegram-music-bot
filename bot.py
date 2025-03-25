import os
import json
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events, functions

# Load konfigurasi dari .env
load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE_NUMBER = os.getenv("TELEGRAM_PHONE")

client = TelegramClient("session", API_ID, API_HASH)

PROFILE_BACKUP_FILE = "profile_backup.json"

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def save_backup(data):
    """Menyimpan data profil lama sebelum cloning."""
    try:
        with open(PROFILE_BACKUP_FILE, "w") as f:
            json.dump(data, f)
        logging.info("✅ Data profil lama berhasil disimpan sebelum cloning.")
    except Exception as e:
        logging.error(f"❌ Gagal menyimpan data profil lama: {str(e)}")

def load_backup():
    """Memuat data profil lama."""
    if os.path.exists(PROFILE_BACKUP_FILE):
        try:
            with open(PROFILE_BACKUP_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"❌ Gagal membaca file backup: {str(e)}")
    return None

@client.on(events.NewMessage(pattern="(?i)gclone(?:\s+(.+))?"))
async def clone_profile(event):
    user_input = event.pattern_match.group(1)
    
    try:
        if event.is_reply:
            reply_message = await event.get_reply_message()
            user = await client.get_entity(reply_message.sender_id)
        elif user_input:
            if user_input.isdigit():
                user = await client.get_entity(int(user_input))
            else:
                user = await client.get_entity(user_input)
        else:
            await event.reply("❌ Tolong reply pesan atau masukkan username/ID!")
            return

        logging.info(f"📥 Menyalin profil dari: {user.first_name} ({user.id})")

        # Perbaikan: Ambil profil lengkap dengan `UserFull`
        full_user = await client(functions.users.GetFullUserRequest(user.id))

        # Simpan data profil lama
        old_profile = full_user  # Simpan objek UserFull
        old_first_name = old_profile.user.first_name or ""
        old_last_name = old_profile.user.last_name or ""
        old_bio = old_profile.about or ""

        old_photos = await client.get_profile_photos("me")
        old_photo_id = old_photos[0].id if old_photos else None

        save_backup({
            "first_name": old_first_name,
            "last_name": old_last_name,
            "bio": old_bio,
            "photo_id": old_photo_id
        })

        # Clone foto profil
        photos = await client.get_profile_photos(user)
        if photos:
            file = await client.download_media(photos[0], "profile.jpg")
            await client(functions.photos.UploadProfilePhotoRequest(file=await client.upload_file(file)))
            logging.info("✅ Foto profil berhasil disalin.")
        else:
            logging.warning("⚠️ Pengguna tidak memiliki foto profil.")

        # Clone bio jika ada
        about = getattr(full_user, "about", None)  # Perbaikan akses bio
        if about:
            await client(functions.account.UpdateProfileRequest(about=about))
            logging.info("✅ Bio berhasil disalin.")
        else:
            logging.warning("⚠️ Pengguna tidak memiliki bio.")

        # Clone nama depan & belakang
        first_name = user.first_name if user.first_name else ""
        last_name = user.last_name if hasattr(user, "last_name") and user.last_name else ""

        await client(functions.account.UpdateProfileRequest(
            first_name=first_name,
            last_name=last_name
        ))
        logging.info("✅ Nama depan dan belakang berhasil disalin.")

        await event.reply(f"✅ Berhasil menyalin profil dari {user.first_name} ({user.id})\n⚠️ *Username tidak bisa di-clone karena bersifat unik!*")

    except Exception as e:
        logging.error(f"❌ Gagal menyalin profil: {str(e)}")
        await event.reply(f"❌ Gagal menyalin profil: {str(e)}")

@client.on(events.NewMessage(pattern="(?i)gunclone"))
async def unclone_profile(event):
    try:
        backup = load_backup()
        if not backup:
            await event.reply("⚠️ Tidak ada data profil sebelumnya. Tidak bisa mengembalikan!")
            logging.warning("⚠️ Tidak ada data profil sebelumnya.")
            return

        logging.info("🔄 Mengembalikan profil ke sebelum cloning...")

        # Kembalikan nama & bio
        await client(functions.account.UpdateProfileRequest(
            first_name=backup["first_name"],
            last_name=backup["last_name"],
            about=backup["bio"]
        ))
        logging.info("✅ Nama dan bio berhasil dikembalikan.")

        # Kembalikan foto profil jika ada
        if backup["photo_id"]:
            old_photos = await client.get_profile_photos("me")
            for photo in old_photos:
                if photo.id != backup["photo_id"]:
                    await client(functions.photos.DeletePhotosRequest([photo]))
            logging.info("✅ Foto profil dikembalikan ke yang sebelumnya.")
        else:
            await client(functions.photos.DeletePhotosRequest(await client.get_profile_photos("me")))
            logging.info("✅ Foto profil dihapus karena sebelumnya tidak ada.")

        await event.reply("✅ Profil berhasil dikembalikan ke sebelum cloning!")
    
        # Hapus file backup setelah dikembalikan
        os.remove(PROFILE_BACKUP_FILE)
        logging.info("🗑️ File backup dihapus setelah gunclone.")

    except Exception as e:
        logging.error(f"❌ Gagal mengembalikan profil: {str(e)}")
        await event.reply(f"❌ Gagal mengembalikan profil: {str(e)}")

async def main():
    await client.start(phone=PHONE_NUMBER)
    logging.info("✅ Bot Telegram siap!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
