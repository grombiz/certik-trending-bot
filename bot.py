from zenrows import ZenRowsClient
from telegram import Bot
import schedule
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@top10trendingprojects"
ZENROWS_KEY = "10c4e0d5c0b7bdfe0cc22cabd16fe9a22d62ba94"

bot = Bot(token=BOT_TOKEN)
client = ZenRowsClient(ZENROWS_KEY)

def get_trending_projects():
    try:
        url = "https://skynet.certik.com/api/leaderboards/trending"
        params = {
            "js_render": "true",
            "premium_proxy": "true"
        }

        response = client.get(url, params=params)
        print(f"🔍 ZenRows status: {response.status_code}")
        data = response.json()
        projects = data.get("data", [])[:10]
        print(f"🔎 Найдено проектов: {len(projects)}")

    except Exception as e:
        print(f"❌ Ошибка парсинга JSON от ZenRows: {e}")
        return "⚠️ CertiK не дал проектов (ошибка запроса)."

    result = []
    for i, project in enumerate(projects):
        try:
            name = project.get("name", "Unknown")
            score = project.get("security_score", "?")
            kyc = "✅" if project.get("kyc", {}).get("status") == "Approved" else "❌"
            result.append(f"{i+1}. {name} – Trust: {score} – KYC: {kyc}")
        except Exception as e:
            print(f"⚠️ Ошибка проекта #{i+1}: {e}")
            continue

    return "\n".join(result)

def send_daily_report():
    print("📡 Получаю проекты через ZenRows SDK...")
    try:
        message = "🔥 *Top 10 Trending Projects on CertiK Skynet:*\n\n" + get_trending_projects()
        bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="Markdown")
        print("✅ Отправлено в канал")
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")

schedule.every().day.at("09:00").do(send_daily_report)

# Ручной запуск
send_daily_report()

while True:
    schedule.run_pending()
    time.sleep(60)
