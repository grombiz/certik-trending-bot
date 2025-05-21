import requests
import schedule
import time
import random
import os
import re
from telegram import Bot

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@toptrendingprojects"
bot = Bot(token=BOT_TOKEN)

def clean_description(desc):
    """Обрезает до нормального предложения или 160 символов по словам"""
    if not desc or not isinstance(desc, str):
        return "Too early to say – DYOR 🔍"

    desc = re.sub("<.*?>", "", desc.strip())  # убираем HTML

    # Пытаемся найти полноценное предложение
    sentences = re.split(r'\.\s+', desc)
    for sentence in sentences:
        clean = sentence.strip()
        if len(clean) >= 40 and clean[-1].isalnum():
            result = clean + "."
            break
    else:
        # fallback: аккуратная обрезка по словам
        if len(desc) > 160:
            result = desc[:157]
            result = result.rsplit(" ", 1)[0].strip() + "..."
        else:
            result = desc

    if not result.endswith((".", "...", "!", "?", "…")):
        result += "."

    return result

def assess_risk(volume, market_cap):
    """Оценивает уровень риска по капе и объему"""
    try:
        if market_cap is None or volume is None:
            return "Unknown"
        if market_cap < 1e7 or volume < 1e6:
            return "High"
        elif market_cap < 1e9 or volume < 1e7:
            return "Medium"
        else:
            return "Low"
    except:
        return "Unknown"

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
                round(item.get("price_change_percentage_24h", 0), 2),
                item.get("total_volume", None),
                item.get("market_cap", None)
            )
            for item in market_data
        }

        result = []
        for i, coin in enumerate(trending_data):
            item = coin["item"]
            coin_id = item["id"]
            symbol = item.get("symbol", "???").upper()
            rank = item.get("market_cap_rank", "?")
            price, change, volume, market_cap = price_info.get(coin_id, ("?", "?", None, None))

            # Получаем описание
            try:
                desc_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                desc_data = requests.get(desc_url, timeout=10).json()
                raw_desc = desc_data.get("description", {}).get("en", "")
                description = clean_description(raw_desc)
            except:
                description = "Too early to say – DYOR 🔍"

            # Риск
            risk = assess_risk(volume, market_cap)

            # Формат
            price_str = format_price(price)
            if isinstance(change, float):
                trend = "🔼" if change >= 0 else "🔻"
                change_str = f"{trend} {abs(change)}%"
            else:
                change_str = "?"

            result.append(
                f"{i+1}. ${symbol} — Rank #{rank}\n"
                f"💰 Price: {price_str} — {change_str}\n"
                f"📊 Risk: {risk}\n"
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

# Планировщик (UTC = 2 часа раньше Брюсселя)
schedule.every().day.at("06:00").do(send_daily_report)
schedule.every().day.at("18:00").do(send_daily_report)

if __name__ == "__main__":
    send_daily_report()
    while True:
        schedule.run_pending()
        time.sleep(60)
