import schedule
import time
import random
import requests
import feedparser
from telegram import Bot
from telegram.error import TelegramError
from config import BOT_TOKEN, CHAT_ID

# Инициализация бота
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

# Исключения
EXCLUDED_SYMBOLS = {"BTC", "ETH", "USDT", "USDC", "BUSD", "FDUSD", "TUSD", "DAI", "XRP", "WBNB", "DOGE", "WETH", "BNB", "TRX"}
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

NEWS_FEEDS = [
    "https://forklog.com/feed",
    "https://bits.media/rss/news/",
    "https://rssexport.rbc.ru/rbcnews/cryptonews.rss"
]

def get_crypto_news():
    for url in random.sample(NEWS_FEEDS, len(NEWS_FEEDS)):
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                entry = feed.entries[0]
                title = str(entry.get("title", "Без названия")).strip()
                link = str(entry.get("link", "")).strip()
                return [f"📰 {title}\n🔗 {link}"]
        except Exception:
            continue
    return ["⚠️ Нет новостей в RSS-источниках."]

def send_message_safe(text, parse_mode="Markdown"):
    try:
        msg = bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=parse_mode)
        print(f"[✅] Message sent: ID {msg.message_id}")
    except TelegramError as e:
        print(f"[❌] Telegram error: {e}")

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
    send_message_safe(message)

def send_crypto_news():
    print("[📢] Публикуем свежие новости...")
    news_items = get_crypto_news()
    for news in news_items:
        send_message_safe(news)

# Планировщик
schedule.every().day.at("06:00").do(send_daily_report)
schedule.every().day.at("10:00").do(send_crypto_news)
schedule.every().day.at("14:00").do(send_crypto_news)
schedule.every().day.at("16:00").do(send_crypto_news)

if __name__ == "__main__":
    send_daily_report()
    send_crypto_news()
    while True:
        schedule.run_pending()
        time.sleep(60)
