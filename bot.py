import schedule
import time
import random
import requests
import os
from telegram import Bot

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@toptrendingdev1"
bot = Bot(token=BOT_TOKEN)

# Функция оценки риска
def assess_risk(volume, market_cap):
    if market_cap is None or volume is None:
        return "Неизвестен"
    if market_cap < 1e7 or volume < 1e6:
        return "Высокий"
    elif market_cap < 1e9 or volume < 1e7:
        return "Средний"
    else:
        return "Низкий"

# Форматирование чисел
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

# Получение трендовых проектов
def get_trending_projects():
    try:
        trending_url = "https://api.coingecko.com/api/v3/search/trending"
        trending_data = requests.get(trending_url, timeout=10).json().get("coins", [])[:7]
        ids = [coin["item"]["id"] for coin in trending_data]
        tickers = [f"#{coin['item']['symbol'].upper()}" for coin in trending_data]
        hashtags = " ".join(tickers)

        ids_param = ",".join(ids)
        market_url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={ids_param}&price_change_percentage=24h"
        market_response = requests.get(market_url, timeout=10)
        try:
            market_data = market_response.json()
            if not isinstance(market_data, list):
                raise ValueError(f"Неверный ответ от CoinGecko: {market_data}")
        except Exception as e:
            return f"⚠️ Ошибка получения данных с CoinGecko: {e}", ""

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

            trend = "🔼" if isinstance(change, float) and change >= 0 else "🔻"
            change_str = f"{trend} {abs(change)}%" if isinstance(change, float) else "?"

            result.append(
                f"{i+1}. ${symbol} — Ранг #{rank}\n"
                f"💰 Цена: {price_str} — {change_str}\n"
                f"📉 Объём (24ч): {volume_str}\n"
                f"📊 Риск: {risk}"
            )

        return "\n\n".join(result), hashtags
    except Exception as e:
        return f"⚠️ Ошибка при загрузке: {e}", ""

# Загрузка новостей (мок)
def get_crypto_news():
    news = [
        "📰 [BTC] BlackRock запускает новый биткоин-ETF — ожидается рост интереса инвесторов\n🔗 https://www.coindesk.com/article1",
        "📰 [ETH] Ethereum планирует обновление сети до версии Pectra в июне\n🔗 https://www.cointelegraph.com/article2",
        "📰 [SOL] Solana объединилась с Shopify для внедрения NFT-оплаты\n🔗 https://cryptoslate.com/article3"
    ]
    return random.sample(news, 2)

# Отправка трендов
def send_daily_report():
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{now}] Получаем тренды CoinGecko...")
    headers = [
        "📊 *7 самых популярных альткоинов по версии CoinGecko:*",
        "🚀 *Топ альткоинов, которые на слуху сегодня:*",
        "🔍 *Самые частые поиски на CoinGecko — обновление раз в сутки:*",
        "💡 *Что в тренде? Список горячих альтов:*",
        "🔥 *Тренды крипторынка — свежая сводка:*"
    ]
    body, hashtags = get_trending_projects()
    intro = random.choice(headers)
    message = f"{intro}\n\n{body}\n\n{hashtags}"
    bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="Markdown")

# Отправка новостей
def send_crypto_news():
    print("[📢] Публикуем свежие новости...")
    news_items = get_crypto_news()
    for news in news_items:
        bot.send_message(chat_id=CHANNEL_USERNAME, text=news)

# Планировщик (по UTC)
schedule.every().day.at("06:00").do(send_daily_report)    # 08:00 Brussels
schedule.every().day.at("10:00").do(send_crypto_news)      # 12:00 Brussels
schedule.every().day.at("14:00").do(send_crypto_news)      # 16:00 Brussels

# Запуск
if __name__ == "__main__":
    send_daily_report()  # тест при старте
    while True:
        schedule.run_pending()
        time.sleep(60)
