import requests
from bs4 import BeautifulSoup
from telegram import Bot
import schedule
import time
import os
import json
import re

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@top10trendingprojects"
ZENROWS_KEY = "10c4e0d5c0b7bdfe0cc22cabd16fe9a22d62ba94"

bot = Bot(token=BOT_TOKEN)

def get_trending_projects():
    url = (
        f"https://api.zenrows.com/v1/?apikey={ZENROWS_KEY}"
        f"&url=https://skynet.certik.com/leaderboards/trending&js_render=true"
    )

    try:
        response = requests.get(url)
        print(f"🔍 ZenRows status: {response.status_code}")
        html = response.text

        # Извлекаем window.__NUXT__ = {...}
        match = re.search(r"window\.__NUXT__=(\{.*?\})</script>", html, re.DOTALL)
        if not match:
            print("❌ Не найден window.__NUXT__ блок")
            return "⚠️ CertiK не вернул встроенные данные. Структура могла измениться."

        nuxt_data = json.loads(match.group(1))
        projects = nuxt_data["data"][0]["leaderboard"]
        print(f"🔎 Извлечено проектов: {len(projects)}")
    except Exception as e:
        print(f"❌ Ошибка при извлечении JSON из DOM: {e}")
        return "⚠️ CertiK не вернул проекты."

    output = []
    for i, project in enumerate(projects[:10]):
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
    print("📡 Получаю проекты с CertiK через ZenRows...")
    try:
        message = "🔥 *Top 10 Trending Projects on CertiK Skynet:*\n\n" + get_trending_projects()
        bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="Markdown")
        print("✅ Отправлено в Telegram")
    except Exception as e:
        print(f"❌ Ошибка при отправке в Telegram: {e}")

# Ежедневно в 09:00 UTC
schedule.every().day.at("09:00").do(send_daily_report)

# Ручной тест
send_daily_report()

while True:
    schedule.run_pending()
    time.sleep(60)
