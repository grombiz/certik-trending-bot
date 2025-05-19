import requests
from telegram import Bot
import schedule
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@top10trendingprojects"
ZENROWS_KEY = "10c4e0d5c0b7bdfe0cc22cabd16fe9a22d62ba94"

bot = Bot(token=BOT_TOKEN)

def get_trending_projects():
    url = (
        f"https://api.zenrows.com/v1/?apikey={ZENROWS_KEY}"
        f"&url=https://skynet.certik.com/api/leaderboards/trending"
        f"&js_render=true&premium_proxy=true"
    )

    try:
        response = requests.get(url)
        print(f"🔍 ZenRows status: {response.status_code}")
        data = response.json()
        projects = data.get("data", [])[:10]
        print(f"🔎 Получено проектов: {len(projects)}")
    except Exception as e:
        print(f"❌ Ошибка при парсинге JSON: {e}")
        return "⚠️ CertiK API вернул некорректный ответ."

    output = []
    for i, project in enumerate(projects):
        try:
            name = project.get("name", "Unknown")
            score = project.get("security_score", "?")
            kyc = "✅" if project.get("kyc", {}).get("status") == "Approved" else "❌"
            output.append(f"{i+1}. {name} – Trust: {score} – KYC: {kyc}")
        except Exception as e:
            print(f"⚠️ Ошибка в проекте #{i+1}: {e}")
            continue

    return "\n".join(output)

def send_daily_report():
    print("📡 Получаю проекты через ZenRows JSON API...")
    try:
        message = "🔥 *Top 10 Trending Projects on CertiK Skynet:*\n\n" + get_trending_projects()
        bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="Markdown")
        print("✅ Отправлено в Telegram")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

# Периодический запуск
schedule.every().day.at("09:00").do(send_daily_report)
send_daily_report()

while True:
    schedule.run_pending()
    time.sleep(60)
