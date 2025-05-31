import schedule
import time
import random
import requests
import os
import feedparser
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

# Получение трендовых проектов из Coinpaprika
EXCLUDED_SYMBOLS = {"BTC", "ETH", "USDT", "USDC", "BUSD", "FDUSD", "TUSD", "DAI", "XRP", "WBNB", "DOGE", "WETH", "BNB", "TRX"}

# Фильтрация мемкойнов и NFT/DeFi-токенов
MEME_KEYWORDS = ["dog", "inu", "pepe", "meme", "elon"]
NFT_DEFI_KEYWORDS = ["nft", "defi", "swap", "dex"]

def is_meme_or_nft(token):
    name = token.get("name", "").lower()
    return any(k in name for k in MEME_KEYWORDS + NFT_DEFI_KEYWORDS)

def get_trending_projects():
    try:
        url = "https://api.coinpaprika.com/v1/tickers"
        response = requests.get(url, timeout=10)
        data = response.json()

        filtered_data = [
            token for token in data
            if token.get("symbol") not in EXCLUDED_SYMBOLS and not is_meme_or_nft(token)
        ]

        sorted_data = sorted(
            filtered_data,
            key=lambda x: x.get("quotes", {}).get("USD", {}).get("volume_24h", 0),
            reverse=True
        )[:7]

        result = []
        hashtags = []

        for i, token in enumerate(sorted_data):
            symbol = token.get("symbol", "???")
            name = token.get("name", "???")
            rank = token.get("rank", "?")
            quotes = token.get("quotes", {}).get("USD", {})
            price = quotes.get("price", "?")
            change = quotes.get("percent_change_24h", 0)
            volume = quotes.get("volume_24h", None)
            market_cap = quotes.get("market_cap", None)

            risk = assess_risk(volume, market_cap)
            price_str = format_price(price)
            volume_str = format_volume(volume)
            trend = "🔼" if isinstance(change, float) and change >= 0 else "🔻"
            change_str = f"{trend} {abs(change):.2f}%" if isinstance(change, float) else "?"

            result.append(
                f"{i+1}. ${symbol} — Ранг #{rank}\n"
                f"💰 Цена: {price_str} — {change_str}\n"
                f"📉 Объём (24ч): {volume_str}\n"
                f"📊 Риск: {risk}"
            )
            hashtags.append(f"#{symbol}")

        return "\n\n".join(result), " ".join(hashtags)

    except Exception as e:
        return f"⚠️ Ошибка при загрузке с Coinpaprika: {e}", ""

# Загрузка новостей через RSS (вместо CryptoPanic API)
def get_crypto_news():
    try:
        feed = feedparser.parse("https://cryptopanic.com/feed")
        news = []
        for entry in feed.entries[:3]:
            title = entry.get("title", "Без названия")
            link = entry.get("link", "")
            news.append(f"📰 {title}\n🔗 {link}")
        return news
    except Exception as e:
        return [f"⚠️ Ошибка загрузки новостей: {e}"]

# Календарь криптособытий

def get_crypto_events():
    try:
        url = "https://api.coinpaprika.com/v1/events"
        response = requests.get(url, timeout=10)

        if "application/json" not in response.headers.get("Content-Type", ""):
            return f"⚠️ Ошибка: неожиданный ответ от Coinpaprika (не JSON)."

        events = response.json()[:3]

        result = ["📅 Календарь ближайших криптособытий:"]
        for event in events:
            name = event.get("name", "Без названия")
            date = event.get("date", "Дата неизвестна")
            link = event.get("proof", "")
            result.append(f"📌 {name} — {date}\n🔗 {link if link else '—'}")

        return "\n\n".join(result)
    except Exception as e:
        return f"⚠️ Ошибка загрузки событий: {e}"

# Отправка трендов
def send_daily_report():
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{now}] Получаем тренды Coinpaprika...")
    headers = [
        "📊 *7 самых популярных альткоинов по версии Coinpaprika:*",
        "🚀 *Топ альткоинов, которые на слуху сегодня:*",
        "🔍 *Самые частые поиски по Coinpaprika — обновление раз в сутки:*",
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

# Отправка календаря событий
def send_crypto_events():
    print("[📅] Публикуем криптособытия...")
    events_message = get_crypto_events()
    bot.send_message(chat_id=CHANNEL_USERNAME, text=events_message)

# Планировщик (по UTC)
schedule.every().day.at("06:00").do(send_daily_report)    # 08:00 Brussels
schedule.every().day.at("10:00").do(send_crypto_news)      # 12:00 Brussels
schedule.every().day.at("14:00").do(send_crypto_news)      # 16:00 Brussels
schedule.every().day.at("16:00").do(send_crypto_events)    # 18:00 Brussels

# Запуск
if __name__ == "__main__":
    send_daily_report()
    send_crypto_news()  # <-- временный запуск для теста новостей
    while True:
        schedule.run_pending()
        time.sleep(60)
