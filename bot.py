import requests
from telegram import Bot
import schedule
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@top10trendingprojects"

bot = Bot(token=BOT_TOKEN)

def get_trending_projects():
    url = "https://api.coingecko.com/api/v3/search/trending"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        coins = data.get("coins", [])[:7]
    except Exception as e:
        print(f"❌ Ошибка получения трендов с CoinGecko: {e}")
        return "⚠️ CoinGecko не вернул данные."

    if not coins:
        return "⚠️ CoinGecko не вернул трендовые монеты."

    result = []
    for i, coin in enumerate(coins):
        item = coin.get("item", {})
        name = item.get("name", "Unknown")
        symbol = item.get("symbol", "???")
        rank = item.get("market_cap_rank", "?")
        result.append(f"{i+1}. {name} ({symbol}) – Rank: {rank}")

    return "\n".join(result)

def send_daily_report():
    print("📡 Получаю тренды с CoinGecko...")
    try:
        message = "🔥 *Top Trending Coins on CoinGecko:*\n\n" + get_trending_projects()
        bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="Markdown")
        print("✅ Отправлено в Telegram")
    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")

# Периодическая рассылка
schedule.every().day.at("09:00").do(send_daily_report)

# Разовый ручной запуск
send_daily_report()

while True:
    schedule.run_pending()
    time.sleep(60)
