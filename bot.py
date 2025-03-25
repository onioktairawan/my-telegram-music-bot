from telethon import TelegramClient, events, functions, types
import os
from dotenv import load_dotenv

# Load konfigurasi dari .env
load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE_NUMBER = os.getenv("TELEGRAM_PHONE")

client = TelegramClient("userbot", API_ID, API_HASH)

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

        # Clone foto profil
        photos = await client.get_profile_photos(user)
        if photos:
            file = await client.download_media(photos[0], "profile.jpg")
            await client(functions.photos.UploadProfilePhotoRequest(file=await client.upload_file(file)))

        # Clone bio jika ada
        about = getattr(user, "about", "Tidak ada bio.")
        if about:
            await client(functions.account.UpdateProfileRequest(about=about))

        # Clone nama depan & belakang
        first_name = user.first_name if user.first_name else ""
        last_name = user.last_name if hasattr(user, "last_name") and user.last_name else ""
        await client(functions.account.UpdateProfileRequest(first_name=first_name, last_name=last_name))

        await event.reply(f"✅ Berhasil menyalin profil dari {user.first_name} ({user.id})\n⚠️ *Username tidak bisa di-clone karena bersifat unik!*")

    except Exception as e:
        await event.reply(f"❌ Gagal menyalin profil: {str(e)}")

client.start(phone=PHONE_NUMBER)
client.run_until_disconnected()
