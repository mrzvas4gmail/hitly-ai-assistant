import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
PARTNER_LINK = os.getenv("PARTNER_LINK", "https://hitly.ru/register?ref=KHbU5Q8Y").strip()
YOUR_TELEGRAM = os.getenv("YOUR_TELEGRAM", "https://t.me/mrzvas4").strip()
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "").strip()
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip().rstrip("/")
