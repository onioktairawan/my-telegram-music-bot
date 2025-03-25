import os
import json
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events, functions, types

# Load konfigurasi dari .env
load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE_NUMBER = os.getenv("TELEGRAM_PHONE")

client = TelegramClient("session", API_ID, API_HASH)

PROFILE_BACKUP_FILE = "profile_backup.json"
PROFILE_PHOTO_BACKUP = "old_profile.jpg"

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def save_backup(data):
    """Simpan data profil lama sebelum cloning."""
    try:
        with open(PROFILE_BACKUP_FILE, "w") as f:
            json.dump(data, f)
        logging.info("✅ Data profil lama disimpan.")
    except Exception as e:
        logging.error(f"❌ Gagal menyimpan backup: {str(e)}")

def load_backup():
    """Muat data profil lama."""
    if os.path.exists(PROFILE_BACKUP_FILE):
        try:
            with open(PROFILE_BACKUP_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"❌ Gagal membaca backup: {str(e)}")
    return None

@client.on(events.NewMessage(pattern="(?i)gclone(?:\s+(.+))?"))
async def clone_profile(event):
    user_input = event.pattern_match.group(1)

    try:
        if event.is_reply:
            reply_message = await event.get_reply_message()
            target_id = reply_message.sender_id
        elif user_input:
            target_id = user_input
        else:
            await event.reply("❌ Tolong reply pesan atau masukkan username/ID!")
            return

        # Ambil info lengkap user
        full_user = await client(functions.users.GetFullUserRequest(target_id))
        user_data = full_user.users[0]

        logging.info(f"📥 Menyalin profil dari: {user_data.first_name} ({user_data.id})")

        # Simpan data lama sebelum cloning
        old_user = await client(functions.users.GetFullUserRequest("me"))
        old_data = old_user.users[0]

        # Simpan foto profil lama
        old_photos = await client.get_profile_photos("me")
        if old_photos:
            await client.download_media(old_photos[0], PROFILE_PHOTO_BACKUP)
            logging.info("✅ Foto profil lama disimpan.")

        save_backup({
            "first_name": old_data.first_name or "",
            "last_name": old_data.last_name or "",
            "bio": old_user.full_user.about or "",
            "photo": PROFILE_PHOTO_BACKUP if old_photos else None
        })

        # Clone foto profil
        photos = await client.get_profile_photos(target_id)
        if photos:
            file = await client.download_media(photos[0], "profile.jpg")
            await client(functions.photos.UploadProfilePhotoRequest(file=await client.upload_file(file)))
            logging.info("✅ Foto profil berhasil disalin.")
        else:
            logging.warning("⚠️ Tidak ada foto profil untuk disalin.")

        # Clone nama & bio
        await client(functions.account.UpdateProfileRequest(
            first_name=user_data.first_name or "",
            last_name=user_data.last_name or "",
            about=full_user.full_user.about or ""
        ))
        logging.info("✅ Nama dan bio berhasil disalin.")

        await event.reply(f"✅ Berhasil menyalin profil dari {user_data.first_name} ({user_data.id})\n⚠️ *Username tidak bisa diclone karena unik!*")

    except Exception as e:
        logging.error(f"❌ Gagal menyalin profil: {str(e)}")
        await event.reply(f"❌ Gagal menyalin profil: {str(e)}")

@client.on(events.NewMessage(pattern="(?i)gunclone"))
async def unclone_profile(event):
    try:
        backup = load_backup()
        if not backup:
            await event.reply("⚠️ Tidak ada data profil sebelumnya!")
            return

        logging.info("🔄 Mengembalikan profil...")

        await client(functions.account.UpdateProfileRequest(
            first_name=backup["first_name"],
            last_name=backup["last_name"],
            about=backup["bio"]
        ))
        logging.info("✅ Nama dan bio dikembalikan.")

        # Kembalikan foto profil jika ada
        if backup.get("photo") and os.path.exists(backup["photo"]):
            await client(functions.photos.UploadProfilePhotoRequest(file=await client.upload_file(backup["photo"])))
            logging.info("✅ Foto profil dikembalikan.")
        else:
            await client(functions.photos.DeletePhotosRequest(await client.get_profile_photos("me")))
            logging.info("✅ Foto profil dihapus karena sebelumnya tidak ada.")

        await event.reply("✅ Profil dikembalikan!")

        os.remove(PROFILE_BACKUP_FILE)

    except Exception as e:
        logging.error(f"❌ Gagal mengembalikan profil: {str(e)}")
        await event.reply(f"❌ Gagal mengembalikan profil: {str(e)}")

async def main():
    await client.start(phone=PHONE_NUMBER)
    logging.info("✅ Bot siap!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
