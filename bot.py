import requests
from bs4 import BeautifulSoup
from telegram import Bot
import schedule
import time
import os

# Получаем токен из переменной окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@top10trendingprojects"

bot = Bot(token=BOT_TOKEN)

def get_trending_projects():
    url = "https://skynet.certik.com/leaderboards/trending"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    cards = soup.select('div.table-row')[:10]
    projects = []

    for card in cards:
        name = card.select_one('a').text.strip() if card.select_one('a') else "Unknown"
        score = card.select_one('.trust-score').text.strip() if card.select_one('.trust-score') else "?"
        kyc = "✅" if 'kyc' in card.text.lower() else "❌"
        projects.append(f"{name} – Trust: {score} – KYC: {kyc}")

    return '\n'.join([f"{i+1}. {p}" for i, p in enumerate(projects)])

def send_daily_report():
    print("📡 Fetching CertiK trending projects...")
    try:
        message = "🔥 *Top 10 Trending Projects on CertiK Skynet:*\n\n" + get_trending_projects()
        bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="Markdown")
        print("✅ Sent to Telegram")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")

# 🔁 Расписание: каждый день в 09:00 по UTC
schedule.every().day.at("09:00").do(send_daily_report)

# 🧪 Временный ручной запуск для проверки (можно удалить позже)
send_daily_report()

# 🔄 Основной бесконечный цикл
while True:
    schedule.run_pending()
    time.sleep(60)
