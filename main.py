from flask import Flask
import asyncio
from bot import send_daily_report, send_crypto_news, send_message_safe

app = Flask(__name__)

@app.route("/")
def home():
    return "👋 CertiK Trending Bot is alive!"

@app.route("/ping")
def ping():
    print("📡 /ping called")
    asyncio.run(send_message_safe("✅ Ping: бот онлайн и отвечает!"))
    return "✅ Ping sent to Telegram"

@app.route("/test")
def test_message():
    print("🧪 /test triggered")
    asyncio.run(send_message_safe("🧪 Тестовое сообщение: бот работает и отправляет!"))
    return "✅ Test message sent"

@app.route("/run")
def run_bot():
    print("⚙️ /run endpoint triggered")

    try:
        print("📊 Sending daily report...")
        send_daily_report()

        print("📰 Sending crypto news...")
        send_crypto_news()

        return "🚀 Bot tasks completed!"
    except Exception as e:
        print(f"[❌] Error while running bot: {e}")
        return f"❌ Bot failed: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
