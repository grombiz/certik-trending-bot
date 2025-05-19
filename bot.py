import requests
from telegram import Bot
import schedule
import time
import os

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@top10trendingprojects"
bot = Bot(token=BOT_TOKEN)

def get_trending_projects():
    try:
        # 1. Получаем trending монеты
        trending_url = "https://api.coingecko.com/api/v3/search/trending"
        trending_response = requests.get(trending_url, timeout=10)
        trending_data = trending_response.json().get("coins", [])[:7]

        ids = [coin["item"]["id"] for coin in trending_data]
        ids_param = ",".join(ids)

        # 2. Получаем цены и 24ч изменения
        market_url = (
            f"https://api.coingecko.com/api/v3/coins/markets"
            f"?vs_currency=usd&ids={ids_param}&price_change_percentage=24h"
        )
        market_data = requests.get(market_url, timeout=10).json()

        price_info = {
            item["id"]: (
                item.get("current_price", "?"),
                round(item.get("price_change_percentage_24h", 0), 2)
            )
            for item in market_data
        }

        # 3. Формируем список
        result = []
        for i, coin in enumerate(trending_data):
            item = coin["item"]
            coin_id = item["id"]
            name = item.get("name", "Unknown")
            symbol = item.get("symbol", "???")
            rank = item.get("market_cap_rank", "?")
            price, change = price_info.get(coin_id, ("?", "?"))

            # Эмодзи тренда
            if isinstance(change, float):
                trend = "🔼" if change >= 0 else "🔻"
                change_str = f"{trend} {abs(change)}%"
            else:
                change_str = "?"

            result.append(f"{i+1}. {name} ({symbol}) – Rank: {rank} – ${price} – {change_str}")

        return "\n".join(result)

    except Exception as e:
        return f"⚠️ Ошибка получения CoinGecko данных: {e}"

def send_daily_report():
    print("📡 Получаю CoinGecko тренды...")
    try:
        message = "🔥 *Top Trending Coins on CoinGecko:*\n\n" + get_trending_projects()
        bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="Markdown")
        print("✅ Отправлено в Telegram")
    except Exception as e:
        print(f"❌ Ошибка при отправке в Telegram: {e}")

# 🕗 Публикации дважды в день по Брюсселю (UTC+2 → UTC)
schedule.every().day.at("06:00").do(send_daily_report)  # 08:00 по Брюсселю
schedule.every().day.at("18:00").do(send_daily_report)  # 20:00 по Брюсселю

# 🔁 Первый запуск вручную
send_daily_report()

# ⏳ Цикл
while True:
    schedule.run_pending()
    time.sleep(60)
