import requests
from bs4 import BeautifulSoup
from telegram import Bot
import schedule
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@top10trendingprojects"

def get_trending_projects():
    url = "https://skynet.certik.com/leaderboards/trending"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    cards = soup.select('div.table-row')[:10]
    projects = []

    for card in cards:
        name = card.select_one('a').text.strip() if card.select_one('a') else "Unknown"
        score = card.select_one('.trust-score').text.strip() if card.select_one('.trust-score') else "?"
        kyc = "✅" if 'kyc' in card.text.lower() else "❌"
        projects.append(f"{name} – Trust: {score} – KYC: {kyc}")

    return '\n'.join([f"{i+1}. {p}" for i, p in enumerate(projects)])

def send_to_telegram(text):
    bot = Bot(token=8162237917:AAHfqZuXZfJ5ysQX3qywQ5HTz1XleP8DcvU)
    bot.send_message(chat_id=CHANNEL_USERNAME, text=text)

def job():
    print("Sending CertiK top-10...")
    message = "🔥 Top 10 Trending Projects on CertiK Skynet:\n\n" + get_trending_projects()
    send_to_telegram(message)

schedule.every().day.at("09:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
