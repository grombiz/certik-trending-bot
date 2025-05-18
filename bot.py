from telegram import Bot
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@top10trendingprojects"

bot = Bot(token=BOT_TOKEN)
bot.send_message(chat_id=CHANNEL_USERNAME, text="✅ Бот работает! Render запущен и может слать сообщения.")
