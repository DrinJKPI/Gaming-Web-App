import requests
import os
from dotenv import load_dotenv
from app import create_app
from app.game_metadata_service import get_all_games_from_mongodb, update_game_in_mongodb
import time

load_dotenv()
RAWG_API_KEY = os.getenv("RAWG_API_KEY")
RAWG_BASE_URL = "https://api.rawg.io/api"


def fetch_game_metadata(game_title):
    """Fetch metadata and Steam URL from RAWG API"""
    try:
        params = {
            "key": RAWG_API_KEY,
            "search": game_title,
            "page_size": 1
        }

        response = requests.get(f"{RAWG_BASE_URL}/games", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get('results'):
            print(f"No results found")
            return None

        game_data = data['results'][0]
        game_id = game_data['id']

        # Filter English-only tags (no Cyrillic characters)
        all_tags = game_data.get('tags', [])
        english_tags = [
            t['name'] for t in all_tags
            if t.get('language') == 'eng' or not any(ord(char) > 127 for char in t['name'])
        ][:10]

        # Extract basic metadata
        metadata = {
            "description": game_data.get('description_raw', '') or game_data.get('description', '')[
                :500] or "No description available.",
            "genres": [g['name'] for g in game_data.get('genres', [])][:5],
            "tags": english_tags,
            "rating": game_data.get('rating'),
            "metacritic_score": game_data.get('metacritic'),
            "background_image": game_data.get('background_image'),
            "developer": [d['name'] for d in game_data.get('developers', [])][:3],
            "publisher": [p['name'] for p in game_data.get('publishers', [])][:3],
            "esrb_rating": game_data.get('esrb_rating', {}).get('name') if game_data.get('esrb_rating') else None,
            "playtime": game_data.get('playtime'),
            "steam_url": None
        }

        # Fetch Store Links
        try:
            stores_response = requests.get(f"{RAWG_BASE_URL}/games/{game_id}/stores", params={"key": RAWG_API_KEY}, timeout=5)
            stores_data = stores_response.json()
            for store_entry in stores_data.get('results', []):
                if store_entry.get('store_id') == 1: # Steam
                    metadata["steam_url"] = store_entry.get('url')
                    break
        except Exception as store_err:
            print(f"  Warning: Could not fetch store links: {store_err}")

        return metadata

    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":  # <--- Add this line here
    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("ENRICHING GAME METADATA FROM RAWG API")
        print("=" * 60)

        games = get_all_games_from_mongodb()
        print(f"\nFound {len(games)} games in MongoDB\n")

        success_count = 0

        for i, game in enumerate(games, 1):
            print(f"[{i}/{len(games)}] {game['title']}...")
            metadata = fetch_game_metadata(game['title'])

            if metadata:
                if update_game_in_mongodb(game['mysql_game_id'], metadata):
                    print(f"Updated with metadata")
                    success_count += 1
                else:
                    print(f"Failed to save")

            time.sleep(0.5)

        print("\n" + "=" * 60)
        print(f"ENRICHMENT COMPLETE")
        print(f"Enriched: {success_count}/{len(games)}")
        print("=" * 60)