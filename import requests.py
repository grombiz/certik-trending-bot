import requests

def get_trending_preview():
    try:
        trending_url = "https://api.coingecko.com/api/v3/search/trending"
        trending_response = requests.get(trending_url, timeout=10)
        trending_data = trending_response.json().get("coins", [])[:7]

        ids = [coin["item"]["id"] for coin in trending_data]
        ids_param = ",".join(ids)

        market_url = (
            f"https://api.coingecko.com/api/v3/coins/markets"
            f"?vs_currency=usd&ids={ids_param}&price_change_percentage=24h"
        )
        market_data = requests.get(market_url, timeout=10).json()

        price_info = {
            item["id"]: (
                item.get("current_price", "?"),
                round(item.get("price_change_percentage_24h", 0), 2)
            )
            for item in market_data
        }

        result = []
        for i, coin in enumerate(trending_data):
            item = coin["item"]
            coin_id = item["id"]
            name = item.get("name", "Unknown")
            symbol = item.get("symbol", "???")
            rank = item.get("market_cap_rank", "?")
            price, change = price_info.get(coin_id, ("?", "?"))

            result.append(f"{i+1}. {name} ({symbol}) – Rank: {rank} – ${price} – Δ24h: {change}%")

        print("🔍 Предпросмотр сообщения:")
        print("🔥 *Top Trending Coins on CoinGecko:*\n")
        print("\n".join(result))

    except Exception as e:
        print(f"⚠️ Ошибка получения CoinGecko данных: {e}")

if __name__ == "__main__":
    get_trending_preview()
