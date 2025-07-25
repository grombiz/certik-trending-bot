import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("📦 [config] BOT_TOKEN:", f"...{BOT_TOKEN[-6:]}" if BOT_TOKEN else "❌ НЕ НАЙДЕН")
print("📦 [config] CHAT_ID:", CHAT_ID if CHAT_ID else "❌ НЕ НАЙДЕН")
