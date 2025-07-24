from flask import Flask
from bot import send_daily_report, send_crypto_news
import threading

app = Flask(__name__)

@app.route("/")
def hello():
    return "👋 Bot is alive!"

@app.route("/run")
def run_bot():
    threading.Thread(target=send_daily_report).start()
    threading.Thread(target=send_crypto_news).start()
    return "🚀 Bot is working!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
