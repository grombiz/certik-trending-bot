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

def clean_description(desc):
    """Обрезает до полного предложения или максимум 160 символов"""
    if not desc:
        return "Too early to say – DYOR 🔍"
    sentences = desc.strip().split(". ")
    for s in sentences:
        if len(s.strip()) > 30:  # пропускаем мусор типа "what is it?"
            result = s.strip()
            break
    else:
        result = sentences[0].strip()
    final = result + "." if not result.endswith(".") else result
    return final[:157] + "..." if len(final) > 160 else final

def format_price(price):
    if isinstance(price, (float, int)):
        if price < 0.01:
            return f"${price:.8f}"
        elif price < 1:
            return f"${price:.4f}"
        else:
            return f"${price:,.2f}"
    return "?"

def get_trending_projects():
    try:
        trending_url = "https://api.coingecko.com/api/v3/search/trending"
        trending_response = requests.get(trending_url, timeout=10)
        trending_data = trending_response.json().get("coins", [])[:7]

        ids = [coin["item"]["id"] for coin in trending_data]
        tickers = [f"#{coin['item']['symbol'].upper()}" for coin in trending_data]
        hashtags = " ".join(tickers)

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

        result = []
        for i, coin in enumerate(trending_data):
            item = coin["item"]
            coin_id = item["id"]
            symbol = item.get("symbol", "???").upper()
            rank = item.get("market_cap_rank", "?")
            price, change = price_info.get(coin_id, ("?", "?"))

            # Получаем описание
            try:
                desc_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                desc_data = requests.get(desc_url, timeout=10).json()
                raw_desc = desc_data.get("description", {}).get("en", "")
                description = clean_description(raw_desc)
            except:
                description = "Too early to say – DYOR 🔍"

            # Форматирование
            price_str = format_price(price)
            if isinstance(change, float):
                trend = "🔼" if change >= 0 else "🔻"
                change_str = f"{trend} {abs(change)}%"
            else:
                change_str = "?"

            result.append(
                f"{i+1}. ${symbol} — Rank #{rank}\n"
                f"💰 Price: {price_str} — {change_str}\n"
                f"🧠 {description}"
            )

        return "\n\n".join(result), hashtags

    except Exception as e:
        return f"⚠️ Error fetching data from CoinGecko: {e}", ""

def send_daily_report():
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{now}] 📡 Fetching CoinGecko trends...")

    headers = [
        "📊 *Top 7 trending altcoins worth watching today:*",
        "🚀 *Looking for momentum? These altcoins are on fire:*",
        "🔍 *Most searched tokens on CoinGecko — updated every 12h:*",
        "💡 *Curious what's hot in crypto? Here's the list:*",
        "🔥 *Daily trend check — posted every 12 hours:*"
    ]

    try:
        body, hashtags = get_trending_projects()
        intro = random.choice(headers)
        full_message = f"{intro}\n\n{body}\n\n{hashtags}"

        bot.send_message(chat_id=CHANNEL_USERNAME, text=full_message, parse_mode="Markdown")
        print(f"[{now}] ✅ Sent to Telegram")

    except Exception as e:
        print(f"[{now}] ❌ Telegram send error: {e}")

# Планировщик по UTC (06:00 и 18:00 = 08:00 и 20:00 Brussels)
schedule.every().day.at("06:00").do(send_daily_report)
schedule.every().day.at("18:00").do(send_daily_report)

if __name__ == "__main__":
    send_daily_report()
    while True:
        schedule.run_pending()
        time.sleep(60)
