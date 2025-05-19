import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import schedule
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@top10trendingprojects"
ZENROWS_API_KEY = "10c4e0d5c0b7bdfe0cc22cabd16fe9a22d62ba94"

def get_trending_projects():
    try:
        url = (
            f"https://api.zenrows.com/v1/"
            f"?apikey={ZENROWS_API_KEY}"
            f"&url=https://skynet.certik.com/leaderboards/trending"
            f"&js_render=true"
        )
        response = requests.get(url, timeout=15)
        print(f"🔍 ZenRows status: {response.status_code}")

        if response.status_code != 200:
            return "⚠️ CertiK API вернул некорректный ответ."

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("div.table-row")[:10]

        if not rows:
            return "⚠️ CertiK не вернул проектов (вёрстка могла измениться)."

        result = []
        for i, row in enumerate(rows):
            name = row.select_one("a").text.strip() if row.select_one("a") else "Unknown"
            score = row.select_one(".trust-score").text.strip() if row.select_one(".trust-score") else "?"
            kyc = "✅" if "kyc" in row.text.lower() else "❌"
            result.append(f"{i+1}. {name} – Trust: {score} – KYC: {kyc}")

        return "\n".join(result)

    except Exception as e:
        return f"⚠️ Ошибка получения данных: {e}"

def send_to_telegram():
    bot = Bot(token=BOT_TOKEN)
    message = f"🔥 *Top 10 Trending Projects on CertiK Skynet:*\n\n{get_trending_projects()}"
    bot.send_message(chat_id=CHANNEL, text=message, parse_mode="Markdown")

# Ручной запуск (удали после теста)
send_to_telegram()

# Автозапуск каждый день в 09:00 (UTC)
# schedule.every().day.at("09:00").do(send_to_telegram)
# while True:
#     schedule.run_pending()
#     time.sleep(60)
