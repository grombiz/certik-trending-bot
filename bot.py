import requests
from bs4 import BeautifulSoup
from telegram import Bot
import schedule
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@top10trendingprojects"
bot = Bot(token=BOT_TOKEN)

def get_trending_projects():
    url = "https://skynet.certik.com/leaderboards/trending"
    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"🔍 HTML Response status: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.select('div.table-row')
        print(f"🔎 Найдено карточек: {len(cards)}")
    except Exception as e:
        print(f"❌ Ошибка при запросе или парсинге: {e}")
        return "⚠️ CertiK HTML не удалось загрузить."

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
        return "⚠️ CertiK не вернул проектов (вёрстка могла измениться)."

    return '\n'.join(projects)

def send_daily_report():
    print("📡 Начинаю сбор проектов...")
    try:
        message = "🔥 *Top 10 Trending Projects on CertiK Skynet:*\n\n" + get_trending_projects()
        bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="Markdown")
        print("✅ Сообщение отправлено")
    except Exception as e:
        print(f"❌ Ошибка при отправке в Telegram: {e}")

# Расписание — каждый день в 09:00 по UTC
schedule.every().day.at("09:00").do(send_daily_report)

# Ручной запуск для теста
send_daily_report()

# Цикл
while True:
    schedule.run_pending()
    time.sleep(60)
