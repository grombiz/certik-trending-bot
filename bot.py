import requests
import schedule
import time
import random
import os
from telegram import Bot

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@toptrendingprojects"
bot = Bot(token=BOT_TOKEN)

def get_trending_projects():
    try:
        trending_url = "https://api.coingecko.com/api/v3/search/trending"
        trending_response = requests.get(trending_url, timeout=10)
        trending_data = trending_response.json().get("coins", [])[:7]

        ids = [coin["item"]["id"] for coin in trending_data]
        ids_param = ",".join(ids)

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

        # Получение кратких описаний
        descriptions = {}
        for coin_id in ids:
            try:
                detail_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                detail_data = requests.get(detail_url, timeout=10).json()
                raw_desc = detail_data.get("description", {}).get("en", "").strip()

                first_sentence = raw_desc.split(". ")[0].strip()
                short_desc = (first_sentence + ".") if first_sentence else "Too early to say – DYOR 🔍"
                if len(short_desc) > 160:
                    short_desc = short_desc[:157] + "..."
                descriptions[coin_id] = short_desc

            except:
                descriptions[coin_id] = "Too early to say – DYOR 🔍"

        result = []
        for i, coin in enumerate(trending_data):
            item = coin["item"]
            coin_id = item["id"]
            name = item.get("name", "Unknown")
            symbol = item.get("symbol", "???").upper()
            rank = item.get("market_cap_rank", "?")
            price, change = price_info.get(coin_id, ("?", "?"))
            desc = descriptions.get(coin_id, "Too early to say – DYOR 🔍")

            if isinstance(price, (float, int)):
                if price < 0.01:
                    price_str = f"${price:.8f}"
                elif price < 1:
                    price_str = f"${price:.4f}"
                else:
                    price_str = f"${price:,.2f}"
            else:
                price_str = "?"

            if isinstance(change, float):
                trend = "🔼" if change >= 0 else "🔻"
                change_str = f"{trend} {abs(change)}%"
            else:
                change_str = "?"

            result.append(
                f"*{i+1}. ${symbol}* — Rank #{rank}\n"
                f"💰 Price: {price_str} — {change_str}\n"
                f"🧠 {desc}\n"
            )

        return "\n".join(result)

    except Exception as e:
        return f"⚠️ Error fetching data from CoinGecko: {e}"

def send_daily_report():
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{now}] 📡 Fetching CoinGecko trends...")

    try:
        headers = [
            "📊 *Top 7 trending altcoins worth watching today:*",
            "🚀 *Looking for momentum? These altcoins are on fire:*",
            "🔍 *Most searched tokens on CoinGecko — updated every 12h:*",
            "💡 *Curious what's hot in crypto? Here's the list:*",
            "🔥 *Daily trend check — posted every 12 hours:*"
        ]
        intro = random.choice(headers)
        message = f"{intro}\n\n{get_trending_projects()}"
        bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="Markdown")
        print(f"[{now}] ✅ Sent to Telegram")

    except Exception as e:
        print(f"[{now}] ❌ Telegram send error: {e}")

# Планировщик по UTC (06:00 и 18:00 = 08:00 и 20:00 Brussels)
schedule.every().day.at("06:00").do(send_daily_report)
schedule.every().day.at("18:00").do(send_daily_report)

# Тест при запуске
if __name__ == "__main__":
    send_daily_report()
    while True:
        schedule.run_pending()
        time.sleep(60)
