import requests
import schedule
import time
import random
import os
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@toptrendingprojects"
bot = Bot(token=BOT_TOKEN)

def assess_risk(volume, market_cap):
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

def format_volume(volume):
    if isinstance(volume, (float, int)):
        return f"${volume:,.0f}"
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

        market_response = requests.get(market_url, timeout=10)
        try:
            market_data = market_response.json()
            if not isinstance(market_data, list):
                raise ValueError("Invalid market data structure")
        except Exception as e:
            return f"⚠️ Error fetching data from CoinGecko: {e}", ""

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

            risk = assess_risk(volume, market_cap)
            price_str = format_price(price)
            volume_str = format_volume(volume)

            if isinstance(change, float):
                trend = "🔼" if change >= 0 else "🔻"
                change_str = f"{trend} {abs(change)}%"
            else:
                change_str = "?"

            result.append(
                f"{i+1}. ${symbol} — Rank #{rank}\n"
                f"💰 Price: {price_str} — {change_str}\n"
                f"📉 Volume (24h): {volume_str}\n"
                f"📊 Risk: {risk}"
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

# Планировщик (UTC)
schedule.every().day.at("06:00").do(send_daily_report)
schedule.every().day.at("18:00").do(send_daily_report)

if __name__ == "__main__":
    send_daily_report()
    while True:
        schedule.run_pending()
        time.sleep(60)
