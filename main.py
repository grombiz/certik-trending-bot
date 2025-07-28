from flask import Flask
from bot import send_daily_report, send_crypto_news
import threading
import schedule
import time

app = Flask(__name__)

@app.route("/")
def hello():
    return "👋 Bot is alive!"

@app.route("/run")
def run_report():
    threading.Thread(target=send_daily_report).start()
    return "📊 Daily report sent!"

@app.route("/run_news")
def run_news():
    threading.Thread(target=send_crypto_news).start()
    return "📰 News launched!"

# 🔁 Планировщик в отдельном потоке
def run_scheduler():
    schedule.every().day.at("06:00").do(send_daily_report)
    schedule.every().day.at("10:00").do(send_crypto_news)
    schedule.every().day.at("14:00").do(send_crypto_news)
    schedule.every().day.at("16:00").do(send_crypto_news)

    while True:
        schedule.run_pending()
        time.sleep(60)

# Запуск планировщика
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

# Запуск Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
