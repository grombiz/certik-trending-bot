import requests
from bs4 import BeautifulSoup
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
        f"&url=https://skynet.certik.com/leaderboards/trending&js_render=true"
    )
    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"🔍 ZenRows status: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.select('div.table-row')
        print(f"🔎 Найдено карточек: {len(cards)}")
    except Exception as e:
        print(f"❌ Ошибка парсинга ZenRows: {e}")
        return "⚠️ Не удалось получить проекты с CertiK."

    projects = []

    for i, card in enumerate(cards[:10]):
        try:
            name = card.select_one('a').text.strip()
            score_tag = card.select_one('.trust-score')
            score = score_tag.text.strip() if score_tag else "?"
            kyc = "✅" if 'kyc' in card.text.lower() else "❌"
            projects.append(f"{i+1}. {name} – Trust: {score} – KYC: {kyc}")
        except Exception as e:
            print(f"⚠️ Ошибка в карточке #{i+1}: {e}")
            continue

    if not projects:
        return "⚠️ CertiK не вернул проектов. Структура могла измениться."

    return "\n".join(projects)

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

# Ручной запуск (удалишь позже)
send_daily_report()

# Основной цикл
while True:
    schedule.run_pending()
    time.sleep(60)
