from flask import Flask
from bot import send_daily_report, send_crypto_news
import threading

app = Flask(__name__)

@app.route("/")
def hello():
    return "👋 Bot is alive!"

@app.route("/run")
def run_daily():
    threading.Thread(target=send_daily_report).start()
    return "📊 Daily report launched!", 200

@app.route("/run_news")
def run_news():
    threading.Thread(target=send_crypto_news).start()
    return "📰 News launched!", 200

@app.route("/ping")
def ping():
    return "✅ Ping OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
