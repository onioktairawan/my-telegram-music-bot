import os
import logging
import requests
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram API credentials
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
TELEGRAM_CHANNEL_ID = int(os.getenv("TELEGRAM_CHANNEL_ID"))

# UltraMSG API credentials
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")
WHATSAPP_TO_NUMBER = os.getenv("WHATSAPP_TO_NUMBER")

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Telegram client
telegram_client = TelegramClient(TELEGRAM_PHONE, TELEGRAM_API_ID, TELEGRAM_API_HASH)

@telegram_client.on(events.NewMessage(chats=TELEGRAM_CHANNEL_ID))
async def forward_to_whatsapp(event):
    try:
        message_text = event.message.message
        sender = await event.get_sender()
        sender_name = sender.title if sender else "Unknown Channel"
        
        # Format the message
        formatted_message = f"{sender_name}: {message_text}"
        
        # Send message to WhatsApp using UltraMSG
        url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
        payload = {
            "token": ULTRAMSG_TOKEN,
            "to": WHATSAPP_TO_NUMBER,
            "body": formatted_message
        }
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            logging.info(f"Forwarded message from Telegram Channel to WhatsApp: {formatted_message}")
        else:
            logging.error(f"Failed to send message. Response: {response.text}")
    except Exception as e:
        logging.error(f"Error forwarding message: {str(e)}")

async def main():
    await telegram_client.start()
    logging.info("Telegram client started.")
    await telegram_client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
