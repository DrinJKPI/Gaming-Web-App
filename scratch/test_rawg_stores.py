import requests
import os
from dotenv import load_dotenv

load_dotenv()
RAWG_API_KEY = os.getenv("RAWG_API_KEY")
RAWG_BASE_URL = "https://api.rawg.io/api"

def test_rawg_stores(game_title):
    params = {
        "key": RAWG_API_KEY,
        "search": game_title,
        "page_size": 1
    }
    response = requests.get(f"{RAWG_BASE_URL}/games", params=params)
    data = response.json()
    if data['results']:
        game = data['results'][0]
        print(f"Game: {game['name']}")
        print(f"ID: {game['id']}")
        
        # Get details for stores
        detail_response = requests.get(f"{RAWG_BASE_URL}/games/{game['id']}/stores", params={"key": RAWG_API_KEY})
        stores_data = detail_response.json()
        print("\nStores:")
        for s in stores_data.get('results', []):
            store_name = s.get('store_id') # This is just an ID usually
            # Better way is to look at store object
            print(f"- Store ID: {s.get('store_id')}, URL: {s.get('url')}")

if __name__ == "__main__":
    test_rawg_stores("Cyberpunk 2077")
