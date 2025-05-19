import requests
from telegram import Bot
import schedule
import time
import os

# Получаем токен из переменной окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@top10trendingprojects"

bot = Bot(token=BOT_TOKEN)

def get_trending_projects():
    url = "https://skynet.certik.com/api/projects?trend=1&limit=10"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    try:
        data = response.json()
    except Exception as e:
        print(f"❌ JSON decode error: {e}")
        return "⚠️ CertiK API вернул некорректный ответ."

    projects = []

    for i, project in enumerate(data.get("data", [])):
        name = project.get("name", "Unknown")
        score = project.get("security_score", "?")
        kyc = "✅" if project.get("kyc", {}).get("status") == "Approved" else "❌"
        projects.append(f"{i+1}. {name} – Trust: {score} – KYC: {kyc}")

    if not projects:
        return "⚠️ Не удалось получить проекты. CertiK API вернул пустой список."

    return "\n".join(projects)

def send_daily_report():
    print("📡 Fetching CertiK trending projects...")
    try:
        message = "🔥 *Top 10 Trending Projects on CertiK Skynet:*\n\n" + get_trending_projects()
        bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="Markdown")
        print("✅ Sent to Telegram")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")

# Расписание: каждый день в 09:00 (UTC)
schedule.every().day.at("09:00").do(send_daily_report)

# Временный ручной запуск (можно убрать после проверки)
send_daily_report()

# Цикл
while True:
    schedule.run_pending()
    time.sleep(60)
